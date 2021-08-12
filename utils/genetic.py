import random
import statistics
import sys
import time
from bisect import bisect_left
from math import exp


def _generate_parent(length, gene_set, get_fitness):
    genes = []
    while len(genes) < length:
        sample_size = min(length - len(genes), len(gene_set))
        genes.extend(random.sample(gene_set, sample_size))
    fitness = get_fitness(genes)
    return Chromosome(genes, fitness)


def _mutate(parent, gene_set, get_fitness):
    child_genes = parent.Genes[:]
    index = random.randrange(0, len(parent.Genes))
    new_gene, alternate = random.sample(gene_set, 2)
    child_genes[index] = alternate if new_gene == child_genes[
        index] else new_gene
    fitness = get_fitness(child_genes)
    return Chromosome(child_genes, fitness)


def _mutate_custom(parent, custom_mutate, get_fitness):
    child_genes = parent.Genes[:]
    custom_mutate(child_genes)
    fitness = get_fitness(child_genes)
    return Chromosome(child_genes, fitness)


def _get_improvement(new_child, generate_parent, max_age):
    parent = best_parent = generate_parent()
    yield best_parent
    historical_fitnesses = [best_parent.Fitness]
    while True:
        child = new_child(parent)
        if parent.Fitness > child.Fitness:
            if max_age is None:
                continue
            parent.Age += 1
            if max_age > parent.Age:
                continue
            index = bisect_left(historical_fitnesses, child.Fitness, 0,
                                len(historical_fitnesses))
            proportion_similar = index / len(historical_fitnesses)
            if random.random() < exp(-proportion_similar):
                parent = child
                continue
            best_parent.Age = 0
            parent = best_parent
            continue
        if not child.Fitness > parent.Fitness:
            # same fitness
            child.Age = parent.Age + 1
            parent = child
            continue
        child.Age = 0
        parent = child
        if child.Fitness > best_parent.Fitness:
            best_parent = child
            yield best_parent
            historical_fitnesses.append(best_parent.Fitness)


def get_best(get_fitness, target_len, optimal_fitness, gene_set,
             display, custom_mutate=None, custom_create=None, max_age=None):
    random.seed()

    if custom_mutate is None:
        def fnMutate(parent):
            return _mutate(parent, gene_set, get_fitness)
    else:
        def fnMutate(parent):
            return _mutate_custom(parent, custom_mutate, get_fitness)

    if custom_create is None:
        def fnGenerateParent():
            return _generate_parent(target_len, gene_set, get_fitness)
    else:
        def fnGenerateParent():
            genes = custom_create()
            return Chromosome(genes, get_fitness(genes))

    for improvement in _get_improvement(fnMutate, fnGenerateParent, max_age):
        display(improvement)
        if not optimal_fitness > improvement.Fitness:
            return improvement


class Chromosome:
    Genes = None
    Fitness = None
    Age = 0

    def __init__(self, genes, fitness):
        self.Genes = genes
        self.Fitness = fitness


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
                print("{0} {1:3.2f} {2:3.2f}".format(
                    1 + i, mean, statistics.stdev(timings, mean) if i > 1 else 0)
                )
