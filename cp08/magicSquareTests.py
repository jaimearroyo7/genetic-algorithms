import datetime
import random
import unittest

from genetic_algorithms.utils import genetic


class MagicSquareTests(unittest.TestCase):
    def test_size_3(self):
        self.generate(3, 50)

    def test_size_5(self):
        self.generate(5, 500)

    def test_size_10(self):
        self.generate(10, 5000)

    def test_size_4(self):
        self.generate(4, 50)

    def test_benchmark(self):
        genetic.Benchmark.run(self.test_size_4)

    def generate(self, diagonal_size, max_age):
        n_squared = diagonal_size * diagonal_size

        gene_set = [i for i in range(1, n_squared + 1)]
        expected_sum = diagonal_size * (n_squared + 1) / 2

        def fn_get_fitness(genes):
            return get_fitness(genes, diagonal_size, expected_sum)

        def fn_display(candidate):
            display(candidate, diagonal_size, start_time)

        gene_indexes = [i for i in range(0, len(gene_set))]

        def fn_mutate(genes):
            mutate(genes, gene_indexes)

        def fn_custom_create():
            return random.sample(gene_set, len(gene_set))

        optimal_value = Fitness(0)
        start_time = datetime.datetime.now()
        best = genetic.get_best(
            fn_get_fitness,
            n_squared,
            optimal_value,
            gene_set,
            fn_display,
            fn_mutate,
            fn_custom_create,
            max_age,
        )

        self.assertTrue(not optimal_value > best.Fitness)


class Fitness:
    SumOfDifferences = None

    def __init__(self, sum_of_differences):
        self.SumOfDifferences = sum_of_differences

    def __gt__(self, other):
        return self.SumOfDifferences < other.SumOfDifferences

    def __str__(self):
        return "{0}".format(self.SumOfDifferences)


def mutate(genes, indexes):
    index_a, index_b = random.sample(indexes, 2)
    genes[index_a], genes[index_b] = genes[index_b], genes[index_a]


def get_fitness(genes, diagonal_size, expected_sum):
    rows, columns, northeast_diagonal_sum, southeast_diagonal_sum = get_sums(
        genes, diagonal_size
    )

    sum_of_differences = sum(
        int(abs(s - expected_sum))
        for s in rows + columns + [southeast_diagonal_sum, northeast_diagonal_sum]
        if s != expected_sum
    )

    return Fitness(sum_of_differences)


def get_sums(genes, diagonal_size):
    rows = [0 for _ in range(diagonal_size)]
    columns = [0 for _ in range(diagonal_size)]
    southeast_diagonal_sum = 0
    northeast_diagonal_sum = 0
    for row in range(diagonal_size):
        for column in range(diagonal_size):
            value = genes[row * diagonal_size + column]
            rows[row] += value
            columns[column] += value
        southeast_diagonal_sum += genes[row * diagonal_size + row]
        northeast_diagonal_sum += genes[row * diagonal_size + (diagonal_size - 1 - row)]
    return rows, columns, northeast_diagonal_sum, southeast_diagonal_sum


def display(candidate, diagonal_size, start_time):
    time_diff = datetime.datetime.now() - start_time
    rows, columns, northeast_diagonal_sum, southeast_diagonal_sum = get_sums(
        candidate.Genes, diagonal_size
    )
    for rowNumber in range(diagonal_size):
        row = candidate.Genes[
              rowNumber * diagonal_size: (rowNumber + 1) * diagonal_size
              ]
        print("\t ", row, "=", rows[rowNumber])
    print(northeast_diagonal_sum, "\t", columns, "\t", southeast_diagonal_sum)
    print(" - - - - - - - - - - -", candidate.Fitness, str(time_diff))
