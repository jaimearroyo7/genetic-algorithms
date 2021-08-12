import datetime
import unittest

from genetic_algorithms.utils import genetic


class SortedNumbersTests(unittest.TestCase):
    def test_sort_10_numbers(self):
        self.sort_numbers(10)

    def test_benchmark(self):
        genetic.Benchmark.run(lambda: self.sort_numbers(40))

    def sort_numbers(self, total_numbers):
        gene_set = [i for i in range(100)]
        start_time = datetime.datetime.now()
        
        def fn_display(candidate):
            display(candidate, start_time)
            
        def fn_get_fitness(genes):
            return get_fitness(genes)
        
        optimal_fitness = Fitness(total_numbers, 0)
        best = genetic.get_best(
            fn_get_fitness,
            total_numbers,
            optimal_fitness,
            gene_set,
            fn_display
        )
        self.assertTrue(not optimal_fitness > best.Fitness)


class Fitness:
    numbers_in_sequence_count = None
    total_gap = None

    def __init__(self, numbers_in_sequence_count, total_gap):
        self.numbers_in_sequence_count = numbers_in_sequence_count
        self.total_gap = total_gap

    def __gt__(self, other):
        if self.numbers_in_sequence_count != other.numbers_in_sequence_count:
            return self.numbers_in_sequence_count >\
                   other.numbers_in_sequence_count
        return self.total_gap < other.total_gap

    def __str__(self):
        return "{0} Sequential, {1} Total Gap".format(
            self.numbers_in_sequence_count,
            self.total_gap)


def get_fitness(genes):
    fitness = 1
    gap = 0
    for i in range(1, len(genes)):
        if genes[i] > genes[i - 1]:
            fitness += 1
        else:
            gap += genes[i - 1] - genes[i]
    return Fitness(fitness, gap)


def display(candidate, start_time):
    time_diff = datetime.datetime.now() - start_time
    print("{0}\t=> {1}\t{2}".format(', '.join(map(str, candidate.Genes)),
                                    candidate.Fitness, str(time_diff)))
