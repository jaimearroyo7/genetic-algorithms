import unittest
import datetime
import operator
import functools
import random
from genetic_algorithms.utils import genetic


class CardTests(unittest.TestCase):
    def test(self):
        gene_set = [i + 1 for i in range(10)]
        startTime = datetime.datetime.now()

        def fnDisplay(candidate):
            display(candidate, startTime)

        def fnGetFitness(genes):
            return get_fitness(genes)

        def fnMutate(genes):
            mutate(genes, gene_set)

        optimalFitness = Fitness(36, 360, 0)
        best = genetic.get_best(
            fnGetFitness, 10, optimalFitness,
            gene_set, fnDisplay, custom_mutate=fnMutate
        )
        self.assertTrue(not optimalFitness > best.Fitness)

    def test_benchmark(self):
        genetic.Benchmark.run(lambda: self.test())


class Fitness:
    Group1Sum = None
    Group2Product = None
    TotalDifference = None
    DuplicateCount = None

    def __init__(self, group1Sum, group2Product, duplicateCount):
        self.Group1Sum = group1Sum
        self.Group2Product = group2Product
        sumDifference = abs(36 - group1Sum)
        productDifference = abs(360 - group2Product)
        self.TotalDifference = sumDifference + productDifference
        self.DuplicateCount = duplicateCount

    def __gt__(self, other):
        if self.DuplicateCount != other.DuplicateCount:
            return self.DuplicateCount < other.DuplicateCount
        return self.TotalDifference < other.TotalDifference

    def __str__(self):
        return "sum: {0} prod: {1} dups: {2}".format(
            self.Group1Sum,
            self.Group2Product,
            self.DuplicateCount
        )


def mutate(genes, gene_set):
    if len(genes) == len(set(genes)):
        count = random.randint(1, 4)
        while count > 0:
            count -= 1
            indexA, indexB = random.sample(range(len(genes)), 2)
            genes[indexA], genes[indexB] = genes[indexB], genes[indexA]
    else:
        indexA = random.randrange(0, len(genes))
        indexB = random.randrange(0, len(gene_set))
        genes[indexA] = gene_set[indexB]


def get_fitness(genes):
    group1Sum = sum(genes[0:5])
    group2Product = functools.reduce(operator.mul, genes[5:10])
    duplicateCount = (len(genes) - len(set(genes)))
    return Fitness(group1Sum, group2Product, duplicateCount)


def display(candidate, startTime):
    timeDiff = datetime.datetime.now() - startTime
    print("{0} - {1}\t{2}\t{3}".format(
        ', '.join(map(str, candidate.Genes[0:5])),
        ', '.join(map(str, candidate.Genes[5:10])),
        candidate.Fitness,
        str(timeDiff))
    )
