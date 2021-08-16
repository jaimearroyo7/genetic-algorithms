import datetime
import math
import random
# import sys
import time
import unittest

from genetic_algorithms.utils import genetic


class ApproximatePiTests(unittest.TestCase):
    def test_benchmark(self):
        genetic.Benchmark.run(
            lambda: self.test([45, 26, 289, 407, 70, 82, 45, 240, 412, 260])
        )

    def test_optimize(self):
        gene_set = [i for i in range(1, 512 + 1)]
        length = 10
        max_seconds = 2

        # stout suppression not working
        def fn_get_fitness(genes):
            start_time = time.time()
            count = 0
            # stdout = sys.stdout
            # sys.stdout = None
            while time.time() - start_time < max_seconds:
                if self.test(genes, max_seconds):
                    count += 1
            # sys.stdout = stdout
            distance = abs(sum(genes) - 1023)
            fraction = 1 / distance if distance > 0 else distance
            count += round(fraction, 4)
            return count

        def fn_display(chromosome):
            print("{}\t{}".format(chromosome.Genes, chromosome.Fitness))

        initial = [512, 256, 128, 64, 32, 16, 8, 4, 2, 1]
        print("initial:", initial, fn_get_fitness(initial))

        optimal_fitness = 10 * max_seconds
        genetic.get_best(
            fn_get_fitness, length, optimal_fitness,
            gene_set, fn_display, max_seconds=600
        )
        self.assertTrue(True)

    @staticmethod
    def test_find_top_10_approximations():
        best = {}
        for numerator in range(1, 1024):
            for denominator in range(1, 1024):
                ratio = numerator / denominator
                pi_dist = math.pi - abs(math.pi - ratio)
                if pi_dist not in best or best[pi_dist][0] > numerator:
                    best[pi_dist] = [numerator, denominator]
        best_approximations = list(reversed(sorted(best.keys())))
        for i in range(10):
            ratio = best_approximations[i]
            nd = best[ratio]
            print("%i / %i\t%f" % (nd[0], nd[1], ratio))

    def test(self, bit_values=None, max_seconds=None):
        if bit_values is None:
            bit_values = [512, 256, 128, 64, 32, 16, 8, 4, 2, 1]
        gene_set = [i for i in range(2)]
        bit_values = [
            512,
            512,
            256,
            256,
            128,
            128,
            64,
            64,
            32,
            32,
            16,
            16,
            8,
            8,
            4,
            4,
            2,
            2,
            1,
            1,
        ]
        start_time = datetime.datetime.now()

        def fn_display(candidate):
            display(candidate, start_time, bit_values)

        def fn_get_fitness(genes):
            return get_fitness(genes, bit_values)

        def fn_mutate(genes):
            mutate(genes, len(bit_values))

        length = 2 * len(bit_values)
        optimal_fitness = 3.14159
        best = genetic.get_best(
            fn_get_fitness,
            length,
            optimal_fitness,
            gene_set,
            fn_display,
            fn_mutate,
            max_age=250,
            max_seconds=max_seconds,
        )
        self.assertTrue(not optimal_fitness > best.Fitness)


def get_fitness(genes, bit_values):
    denominator = get_denominator(genes, bit_values)
    if denominator == 0:
        return 0
    ratio = get_numerator(genes, bit_values) / denominator
    return math.pi - math.fabs(math.pi - ratio)


def mutate(genes, num_bits):
    numerator_index, denominator_index = (
        random.randrange(0, num_bits),
        random.randrange(num_bits, len(genes)),
    )
    genes[numerator_index] = 1 - genes[numerator_index]
    genes[denominator_index] = 1 - genes[denominator_index]


def display(candidate, start_time, bit_values):
    time_diff = datetime.datetime.now() - start_time
    numerator = get_numerator(candidate.Genes, bit_values)
    denominator = get_denominator(candidate.Genes, bit_values)
    print(
        "{0}/{1}\t{2}\t{3}".format(numerator, denominator, candidate.Fitness, time_diff)
    )


def bits_to_int(bits, bit_values):
    result = 0
    for i, bit in enumerate(bits):
        if bit == 0:
            continue
        result += bit_values[i]
    return result


def get_numerator(genes, bit_values):
    return 1 + bits_to_int(genes[: len(bit_values)], bit_values)


def get_denominator(genes, bit_values):
    return 1 + bits_to_int(genes[len(bit_values):], bit_values)
