import random
import statistics
import time
import sys


def _generate_parent(length, gene_set, get_fitness):
    genes = []
    while len(genes) < length:
        samplesize = min(length - len(genes), len(gene_set))
        genes.extend(random.sample(gene_set, samplesize))
    fitness = get_fitness(genes)
    return Chromosome(genes, fitness)


def _mutate(parent, gene_set, get_fitness):
    childgenes = parent.Genes[:]
    index = random.randrange(0, len(parent.Genes))
    newgene, alternate = random.sample(gene_set, 2)
    childgenes[index] = alternate if newgene == childgenes[index] else newgene
    fitness = get_fitness(childgenes)
    return Chromosome(childgenes, fitness)


def _get_improvement(new_child, generate_parent):
    best_parent = generate_parent()
    yield best_parent
    while True:
        child = new_child(best_parent)
        if best_parent.Fitness > child.Fitness:
            continue
        if not child.Fitness > best_parent.Fitness:
            best_parent = child
            continue
        yield child
        best_parent = child


def get_best(get_fitness, target_len, optimal_fitness, gene_set, display):
    random.seed()

    def fnMutate(parent):
        return _mutate(parent, gene_set, get_fitness)

    def fnGenerateParent():
        return _generate_parent(target_len, gene_set, get_fitness)

    for improvement in _get_improvement(fnMutate, fnGenerateParent):
        display(improvement)
        if not optimal_fitness > improvement.Fitness:
            return improvement


class Chromosome:
    Genes = None
    Fitness = None

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
