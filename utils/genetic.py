import random
import statistics
import sys
import time
from bisect import bisect_left
from enum import Enum, IntEnum
from math import exp


def _generate_parent(length, gene_set, get_fitness):
    genes = []
    while len(genes) < length:
        sample_size = min(length - len(genes), len(gene_set))
        genes.extend(random.sample(gene_set, sample_size))
    fitness = get_fitness(genes)
    return Chromosome(genes, fitness, Strategies.Create)


def _mutate(parent, gene_set, get_fitness):
    child_genes = parent.Genes[:]
    index = random.randrange(0, len(parent.Genes))
    new_gene, alternate = random.sample(gene_set, 2)
    child_genes[index] = alternate if new_gene == child_genes[index] else new_gene
    fitness = get_fitness(child_genes)
    return Chromosome(child_genes, fitness, Strategies.Mutate)


def _mutate_custom(parent, custom_mutate, get_fitness):
    child_genes = parent.Genes[:]
    custom_mutate(child_genes)
    fitness = get_fitness(child_genes)
    return Chromosome(child_genes, fitness, Strategies.Mutate)


def _crossover(
    parent_genes, index, parents, get_fitness, crossover, mutate, generate_parent
):
    donor_index = random.randrange(0, len(parents))
    if donor_index == index:
        donor_index = (donor_index + 1) % len(parents)
    child_genes = crossover(parent_genes, parents[donor_index].Genes)
    if child_genes is None:
        # parent and donor are indistinguishable
        parents[donor_index] = generate_parent()
        return mutate(parents[index])
    fitness = get_fitness(child_genes)
    return Chromosome(child_genes, fitness, Strategies.Crossover)


def _get_improvement(new_child, generate_parent, max_age, pool_size, max_seconds):
    start_time = time.time()
    best_parent = generate_parent()
    yield (
        max_seconds is not None and time.time() - start_time > max_seconds, best_parent
    )
    parents = [best_parent]
    historical_fitnesses = [best_parent.Fitness]
    for _ in range(pool_size - 1):
        parent = generate_parent()
        if max_seconds is not None and time.time() - start_time > max_seconds:
            yield True, parent
        if parent.Fitness > best_parent.Fitness:
            yield False, parent
            best_parent = parent
            historical_fitnesses.append(parent.Fitness)
        parents.append(parent)
    last_parent_index = pool_size - 1
    p_index = 1
    while True:
        if max_seconds is not None and time.time() - start_time > max_seconds:
            yield True, best_parent
        p_index = p_index - 1 if p_index > 0 else last_parent_index
        parent = parents[p_index]
        child = new_child(parent, p_index, parents)
        if parent.Fitness > child.Fitness:
            if max_age is None:
                continue
            parent.Age += 1
            if max_age > parent.Age:
                continue
            index = bisect_left(
                historical_fitnesses, child.Fitness, 0, len(historical_fitnesses)
            )
            difference = len(historical_fitnesses) - index
            proportion_similar = difference / len(historical_fitnesses)
            if random.random() < exp(-proportion_similar):
                parents[p_index] = child
                continue
            parents[p_index] = best_parent
            parent.Age = 0
            continue
        if not child.Fitness > parent.Fitness:
            # same fitness
            child.Age = parent.Age + 1
            parents[p_index] = child
            continue
        parents[p_index] = child
        parent.Age = 0
        if child.Fitness > best_parent.Fitness:
            yield False, child
            best_parent = child
            historical_fitnesses.append(child.Fitness)


def get_best(
    get_fitness,
    target_len,
    optimal_fitness,
    gene_set,
    display,
    custom_mutate=None,
    custom_create=None,
    max_age=None,
    pool_size=1,
    crossover=None,
    max_seconds=None,
):
    random.seed()

    if custom_mutate is None:

        def fn_mutate(parent):
            return _mutate(parent, gene_set, get_fitness)

    else:

        def fn_mutate(parent):
            return _mutate_custom(parent, custom_mutate, get_fitness)

    if custom_create is None:

        def fn_generate_parent():
            return _generate_parent(target_len, gene_set, get_fitness)

    else:

        def fn_generate_parent():
            genes = custom_create()
            return Chromosome(genes, get_fitness(genes), Strategies.Create)

    strategy_lookup = {
        Strategies.Create: lambda p, i, o: fn_generate_parent(),
        Strategies.Mutate: lambda p, i, o: fn_mutate(p),
        Strategies.Crossover: lambda p, i, o: _crossover(
            p.Genes, i, o, get_fitness, crossover, fn_mutate, fn_generate_parent
        ),
    }

    used_strategies = [strategy_lookup[Strategies.Mutate]]
    if crossover is not None:
        used_strategies.append(strategy_lookup[Strategies.Crossover])

        def fn_new_child(parent, index, parents):
            return random.choice(used_strategies)(parent, index, parents)

    else:

        def fn_new_child(parent, _, __):
            return fn_mutate(parent)

    for timedOut, improvement in _get_improvement(
        fn_new_child, fn_generate_parent, max_age, pool_size, max_seconds
    ):
        if timedOut:
            return improvement
        display(improvement)
        if not optimal_fitness > improvement.Fitness:
            return improvement


def hill_climbing(
    optimization_function,
    is_improvement,
    is_optimal,
    get_next_feature_value,
    display,
    initial_feature_value,
):
    best = optimization_function(initial_feature_value)
    stdout = sys.stdout
    sys.stdout = None
    while not is_optimal(best):
        feature_value = get_next_feature_value(best)
        child = optimization_function(feature_value)
        if is_improvement(best, child):
            best = child
            sys.stdout = stdout
            display(best, feature_value)
            sys.stdout = None
    sys.stdout = stdout
    return best


def tournament(
    generate_parent,
    crossover,
    compete,
    display,
    sort_key,
    num_parents=10,
    max_generations=100,
):
    pool = [
        [generate_parent(), [0, 0, 0]] for _ in range(1 + num_parents * num_parents)
    ]
    best, best_score = pool[0]

    def get_sort_key(x):
        return sort_key(
            x[0],
            x[1][CompetitionResult.Win],
            x[1][CompetitionResult.Tie],
            x[1][CompetitionResult.Loss],
        )

    generation = 0
    while generation < max_generations:
        generation += 1
        for i in range(0, len(pool)):
            for j in range(0, len(pool)):
                if i == j:
                    continue
                player_a, score_a = pool[i]
                player_b, score_b = pool[j]
                result = compete(player_a, player_b)
                score_a[result] += 1
                score_b[2 - result] += 1

        pool.sort(key=get_sort_key, reverse=True)
        if get_sort_key(pool[0]) > get_sort_key([best, best_score]):
            best, best_score = pool[0]
            display(
                best,
                best_score[CompetitionResult.Win],
                best_score[CompetitionResult.Tie],
                best_score[CompetitionResult.Loss],
                generation,
            )

        parents = [pool[i][0] for i in range(num_parents)]
        pool = [
            [crossover(parents[i], parents[j]), [0, 0, 0]]
            for i in range(len(parents))
            for j in range(len(parents))
            if i != j
        ]
        pool.extend([parent, [0, 0, 0]] for parent in parents)
        pool.append([generate_parent(), [0, 0, 0]])
    return best


class CompetitionResult(IntEnum):
    Loss = (0,)
    Tie = (1,)
    Win = (2,)


class Strategies(Enum):
    Create = 0
    Mutate = 1
    Crossover = 2


class Chromosome:
    Genes = None
    Fitness = None
    Age = 0
    Strategy = None

    def __init__(self, genes, fitness, strategy):
        self.Genes = genes
        self.Fitness = fitness
        self.Strategy = strategy


class Benchmark:
    @staticmethod
    def run(function):
        timings = []
        stdout = sys.stdout
        for i in range(100):
            sys.stdout = None
            start_time = time.time()
            function()
            seconds = time.time() - start_time
            sys.stdout = stdout
            timings.append(seconds)
            mean = statistics.mean(timings)
            if i < 10 or i % 10 == 9:
                print(
                    "{0} {1:3.2f} {2:3.2f}".format(
                        1 + i, mean, statistics.stdev(timings, mean) if i > 1 else 0
                    )
                )
