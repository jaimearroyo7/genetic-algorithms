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
        
        def fnDisplay(candidate):
            display(candidate, start_time)
            
        def fnGetFitness(genes):
            return get_fitness(genes)
        
        optimal_fitness = Fitness(total_numbers, 0)
        best = genetic.get_best(
            fnGetFitness,
            total_numbers,
            optimal_fitness,
            gene_set,
            fnDisplay
        )
        self.assertTrue(not optimal_fitness > best.Fitness)


class Fitness:
    NumbersInSequenceCount = None
    TotalGap = None

    def __init__(self, numbersInSequenceCount, totalGap):
        self.NumbersInSequenceCount = numbersInSequenceCount
        self.TotalGap = totalGap

    def __gt__(self, other):
        if self.NumbersInSequenceCount != other.NumbersInSequenceCount:
            return self.NumbersInSequenceCount > other.NumbersInSequenceCount
        return self.TotalGap < other.TotalGap

    def __str__(self):
        return "{0} Sequential, {1} Total Gap".format(
            self.NumbersInSequenceCount,
            self.TotalGap)


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
