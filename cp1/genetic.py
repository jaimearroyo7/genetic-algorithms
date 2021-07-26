import random
import statistics
import time
import sys


def _generate_parent(length, geneset, get_fitness):
    genes = []
    while len(genes) < length:
        samplesize = min(length - len(genes), len(geneset))
        genes.extend(random.sample(geneset, samplesize))
    genes = ''.join(genes)
    fitness = get_fitness(genes)
    return Chromosome(genes, fitness)


def _mutate(parent, geneset, get_fitness):
    index = random.randrange(0, len(parent.Genes))
    childgenes = list(parent.Genes)
    newgene, alternate = random.sample(geneset, 2)
    childgenes[index] = alternate if newgene == childgenes[index] else newgene
    genes = ''.join(childgenes)
    fitness = get_fitness(genes)
    return Chromosome(genes, fitness)


def get_best(get_fitness, targetlen, optimalfitness, geneset, display):
    random.seed()
    bestparent = _generate_parent(targetlen, geneset, get_fitness)
    display(bestparent)
    if bestparent.Fitness >= optimalfitness:
        return bestparent
    
    while True:
        child = _mutate(bestparent, geneset, get_fitness)
        if bestparent.Fitness >= child.Fitness:
            continue
        display(child)
        if child.Fitness >= optimalfitness:
            return child
        bestparent = child


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
