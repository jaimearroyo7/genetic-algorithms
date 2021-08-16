import unittest
import datetime
import math
import random
import time
import sys
from genetic_algorithms.utils import genetic


class ApproximatePiTests(unittest.TestCase):
    def test_benchmark(self):
        genetic.Benchmark.run(
            lambda: self.test([45, 26, 289, 407, 70, 82, 45, 240, 412, 260])
        )

    def test_optimize(self):
        geneset = [i for i in range(1, 512 + 1)]
        length = 10
        maxSeconds = 2

        # stout suppression not working
        def fnGetFitness(genes):
            startTime = time.time()
            count = 0
            # stdout = sys.stdout
            # sys.stdout = None
            while time.time() - startTime < maxSeconds:
                if self.test(genes, maxSeconds):
                    count += 1
            # sys.stdout = stdout
            distance = abs(sum(genes) - 1023)
            fraction = 1 / distance if distance > 0 else distance
            count += round(fraction, 4)
            return count

        def fnDisplay(chromosome):
            print("{}\t{}".format(chromosome.Genes, chromosome.Fitness))

        initial = [512, 256, 128, 64, 32, 16, 8, 4, 2, 1]
        print("initial:", initial, fnGetFitness(initial))

        optimalFitness = 10 * maxSeconds
        genetic.get_best(
            fnGetFitness, length, optimalFitness, geneset, fnDisplay, maxSeconds=600
        )
        self.assertTrue(True)

    def test_find_top_10_approximations(self):
        best = {}
        for numerator in range(1, 1024):
            for denominator in range(1, 1024):
                ratio = numerator / denominator
                piDist = math.pi - abs(math.pi - ratio)
                if piDist not in best or best[piDist][0] > numerator:
                    best[piDist] = [numerator, denominator]
        bestApproximations = list(reversed(sorted(best.keys())))
        for i in range(10):
            ratio = bestApproximations[i]
            nd = best[ratio]
            print("%i / %i\t%f" % (nd[0], nd[1], ratio))

    def test(self, bitValues=[512, 256, 128, 64, 32, 16, 8, 4, 2, 1], maxSeconds=None):
        geneset = [i for i in range(2)]
        bitValues = [
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
        startTime = datetime.datetime.now()

        def fnDisplay(candidate):
            display(candidate, startTime, bitValues)

        def fnGetFitness(genes):
            return get_fitness(genes, bitValues)

        def fnMutate(genes):
            mutate(genes, len(bitValues))

        length = 2 * len(bitValues)
        optimalFitness = 3.14159
        best = genetic.get_best(
            fnGetFitness,
            length,
            optimalFitness,
            geneset,
            fnDisplay,
            fnMutate,
            max_age=250,
            maxSeconds=maxSeconds,
        )
        self.assertTrue(not optimalFitness > best.Fitness)


def get_fitness(genes, bitValues):
    denominator = get_denominator(genes, bitValues)
    if denominator == 0:
        return 0
    ratio = get_numerator(genes, bitValues) / denominator
    return math.pi - math.fabs(math.pi - ratio)


def mutate(genes, numBits):
    numeratorIndex, denominatorIndex = (
        random.randrange(0, numBits),
        random.randrange(numBits, len(genes)),
    )
    genes[numeratorIndex] = 1 - genes[numeratorIndex]
    genes[denominatorIndex] = 1 - genes[denominatorIndex]


def display(candidate, startTime, bitValues):
    timeDiff = datetime.datetime.now() - startTime
    numerator = get_numerator(candidate.Genes, bitValues)
    denominator = get_denominator(candidate.Genes, bitValues)
    print(
        "{0}/{1}\t{2}\t{3}".format(numerator, denominator, candidate.Fitness, timeDiff)
    )


def bits_to_int(bits, bitValues):
    result = 0
    for i, bit in enumerate(bits):
        if bit == 0:
            continue
        result += bitValues[i]
    return result


def get_numerator(genes, bitValues):
    return 1 + bits_to_int(genes[: len(bitValues)], bitValues)


def get_denominator(genes, bitValues):
    return 1 + bits_to_int(genes[len(bitValues) :], bitValues)


if __name__ == "__main__":
    unittest.main()
