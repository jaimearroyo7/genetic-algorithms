import datetime
import fractions
import random
import unittest

from genetic_algorithms.utils import genetic


class LinearEquationTests(unittest.TestCase):
    def solve_unknowns(self, num_unknowns, gene_set, equations, fn_genes_to_inputs):
        start_time = datetime.datetime.now()
        max_age = 50
        window = Window(
            max(1, int(len(gene_set) / (2 * max_age))),
            max(1, int(len(gene_set) / 3)),
            int(len(gene_set) / 2),
        )
        gene_indexes = [i for i in range(num_unknowns)]
        sorted_gene_set = sorted(gene_set)

        def fn_mutate(genes):
            mutate(genes, sorted_gene_set, window, gene_indexes)

        def fn_display(candidate):
            display(candidate, start_time, fn_genes_to_inputs)

        def fn_get_fitness(genes):
            return get_fitness(genes, equations)

        optimal_fitness = Fitness(0)
        best = genetic.get_best(
            fn_get_fitness,
            num_unknowns,
            optimal_fitness,
            gene_set,
            fn_display,
            fn_mutate,
            max_age=50,
        )
        self.assertTrue(not optimal_fitness > best.Fitness)

    def test_2_unknowns(self):
        gene_set = [i for i in range(-5, 5) if i != 0]

        def fn_genes_to_inputs(genes):
            return genes[0], genes[1]

        def e1(genes):
            x, y = fn_genes_to_inputs(genes)
            return x + 2 * y - 4

        def e2(genes):
            x, y = fn_genes_to_inputs(genes)
            return 4 * x + 4 * y - 12

        equations = [e1, e2]
        self.solve_unknowns(2, gene_set, equations, fn_genes_to_inputs)

    def test_3_unknowns(self):
        gene_range = [i for i in range(-5, 5) if i != 0]
        gene_set = [
            i
            for i in set(
                fractions.Fraction(d, e)
                for d in gene_range
                for e in gene_range
                if e != 0
            )
        ]

        def fn_genes_to_inputs(genes):
            return genes

        def e1(genes):
            x, y, z = genes
            return 6 * x - 2 * y + 8 * z - 20

        def e2(genes):
            x, y, z = genes
            return y + 8 * x * z + 1

        def e3(genes):
            x, y, z = genes
            return 2 * z * fractions.Fraction(6, x) + 3 * fractions.Fraction(y, 2) - 6

        equations = [e1, e2, e3]
        self.solve_unknowns(3, gene_set, equations, fn_genes_to_inputs)

    def test_4_unknowns(self):
        gene_range = [i for i in range(-13, 13) if i != 0]
        gene_set = [
            i
            for i in set(
                fractions.Fraction(d, e)
                for d in gene_range
                for e in gene_range
                if e != 0
            )
        ]

        def fn_genes_to_inputs(genes):
            return genes

        def e1(genes):
            x, y, z, a = genes
            return (
                fractions.Fraction(1, 15) * x
                - 2 * y
                - 15 * z
                - fractions.Fraction(4, 5) * a
                - 3
            )

        def e2(genes):
            x, y, z, a = genes
            return (
                -fractions.Fraction(5, 2) * x
                - fractions.Fraction(9, 4) * y
                + 12 * z
                - a
                - 17
            )

        def e3(genes):
            x, y, z, a = genes
            return (
                -13 * x
                + fractions.Fraction(3, 10) * y
                - 6 * z
                - fractions.Fraction(2, 5) * a
                - 17
            )

        def e4(genes):
            x, y, z, a = genes
            return (
                fractions.Fraction(1, 2) * x
                + 2 * y
                + fractions.Fraction(7, 4) * z
                + fractions.Fraction(4, 3) * a
                + 9
            )

        equations = [e1, e2, e3, e4]
        self.solve_unknowns(4, gene_set, equations, fn_genes_to_inputs)

    def test_benchmark(self):
        genetic.Benchmark.run(lambda: self.test_4_unknowns())


def get_fitness(genes, equations):
    return Fitness(sum(abs(e(genes)) for e in equations))


def mutate(genes, sorted_gene_set, window, gene_indexes):
    indexes = (
        random.sample(gene_indexes, random.randint(1, len(genes)))
        if random.randint(0, 10) == 0
        else [random.choice(gene_indexes)]
    )
    window.slide()
    while len(indexes) > 0:
        index = indexes.pop()
        gene_set_index = sorted_gene_set.index(genes[index])
        start = max(0, gene_set_index - window.Size)
        stop = min(len(sorted_gene_set) - 1, gene_set_index + window.Size)
        gene_set_index = random.randint(start, stop)
        genes[index] = sorted_gene_set[gene_set_index]


def display(candidate, start_time, fn_genes_to_inputs):
    time_diff = datetime.datetime.now() - start_time
    symbols = "xyza"
    result = ", ".join(
        "{0} = {1}".format(s, v)
        for s, v in zip(symbols, fn_genes_to_inputs(candidate.Genes))
    )
    print("{0}\t{1}\t{2}".format(result, candidate.Fitness, str(time_diff)))


class Fitness:
    TotalDifference = None

    def __init__(self, total_difference):
        self.TotalDifference = total_difference

    def __gt__(self, other):
        return self.TotalDifference < other.TotalDifference

    def __str__(self):
        return "diff: {0:0.2f}".format(float(self.TotalDifference))


class Window:
    Min = None
    Max = None
    Size = None

    def __init__(self, minimum, maximum, size):
        self.Min = minimum
        self.Max = maximum
        self.Size = size

    def slide(self):
        self.Size = self.Size - 1 if self.Size > self.Min else self.Max
