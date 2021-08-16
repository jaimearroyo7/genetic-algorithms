import datetime
import functools
import operator
import random
import unittest

from genetic_algorithms.utils import genetic


class CardTests(unittest.TestCase):
    def test(self):
        gene_set = [i + 1 for i in range(10)]
        start_time = datetime.datetime.now()

        def fn_display(candidate):
            display(candidate, start_time)

        def fn_get_fitness(genes):
            return get_fitness(genes)

        def fn_mutate(genes):
            mutate(genes, gene_set)

        optimal_fitness = Fitness(36, 360, 0)
        best = genetic.get_best(
            fn_get_fitness,
            10,
            optimal_fitness,
            gene_set,
            fn_display,
            custom_mutate=fn_mutate,
        )
        self.assertTrue(not optimal_fitness > best.Fitness)

    def test_benchmark(self):
        genetic.Benchmark.run(lambda: self.test())


class Fitness:
    Group1Sum = None
    Group2Product = None
    TotalDifference = None
    DuplicateCount = None

    def __init__(self, group_1_sum, group_2_product, duplicate_count):
        self.Group1Sum = group_1_sum
        self.Group2Product = group_2_product
        sum_difference = abs(36 - group_1_sum)
        product_difference = abs(360 - group_2_product)
        self.TotalDifference = sum_difference + product_difference
        self.DuplicateCount = duplicate_count

    def __gt__(self, other):
        if self.DuplicateCount != other.DuplicateCount:
            return self.DuplicateCount < other.DuplicateCount
        return self.TotalDifference < other.TotalDifference

    def __str__(self):
        return "sum: {0} prod: {1} dups: {2}".format(
            self.Group1Sum, self.Group2Product, self.DuplicateCount
        )


def mutate(genes, gene_set):
    if len(genes) == len(set(genes)):
        count = random.randint(1, 4)
        while count > 0:
            count -= 1
            index_a, index_b = random.sample(range(len(genes)), 2)
            genes[index_a], genes[index_b] = genes[index_b], genes[index_a]
    else:
        index_a = random.randrange(0, len(genes))
        index_b = random.randrange(0, len(gene_set))
        genes[index_a] = gene_set[index_b]


def get_fitness(genes):
    group_1_sum = sum(genes[0:5])
    group_2_product = functools.reduce(operator.mul, genes[5:10])
    duplicate_count = len(genes) - len(set(genes))
    return Fitness(group_1_sum, group_2_product, duplicate_count)


def display(candidate, start_time):
    time_diff = datetime.datetime.now() - start_time
    print(
        "{0} - {1}\t{2}\t{3}".format(
            ", ".join(map(str, candidate.Genes[0:5])),
            ", ".join(map(str, candidate.Genes[5:10])),
            candidate.Fitness,
            str(time_diff),
        )
    )
