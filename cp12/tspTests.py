import datetime
import math
import random
import unittest
from itertools import chain

from genetic_algorithms.utils import genetic


def load_data(local_file_name):
    """expects:
    HE_aDER section before D_aT_a section, all lines start in column 0
    D_aT_a section element all have space in column 0
    <space>1 23.45 67.89
    last line of file is: " EOF"
    """
    with open(local_file_name, mode="r") as infile:
        content = infile.read().splitlines()
    id_to_location_lookup = {}
    for row in content:
        if row[0] != " ":  # HEADERS
            continue
        if row == " EOF":
            break
        identifier, x, y = row.split(" ")[1:4]
        id_to_location_lookup[int(identifier)] = [float(x), float(y)]
    return id_to_location_lookup


class TravelingSalesmanTests(unittest.TestCase):
    def test_benchmark(self):
        genetic.Benchmark.run(lambda: self.test_ulysses16())

    def test_8_queens(self):
        id_to_location_lookup = {
            "A": [4, 7],
            "B": [2, 6],
            "C": [0, 5],
            "D": [1, 3],
            "E": [3, 0],
            "F": [5, 1],
            "G": [7, 2],
            "H": [6, 4],
        }
        optimal_sequence = ["A", "B", "C", "D", "E", "F", "G", "H"]
        self.solve(id_to_location_lookup, optimal_sequence)

    def test_ulysses16(self):
        id_to_location_lookup = load_data("ulysses16.tsp")
        optimal_sequence = [14, 13, 12, 16, 1, 3, 2, 4, 8, 15, 5, 11, 9, 10, 7, 6]
        self.solve(id_to_location_lookup, optimal_sequence)

    def solve(self, id_to_location_lookup, optimal_sequence):
        gene_set = [i for i in id_to_location_lookup.keys()]

        def fn_create():
            return random.sample(gene_set, len(gene_set))

        def fn_display(candidate):
            display(candidate, start_time)

        def fn_get_fitness(genes):
            return get_fitness(genes, id_to_location_lookup)

        def fn_mutate(genes):
            mutate(genes, fn_get_fitness)

        def fn_crossover(parent, donor):
            return crossover(parent, donor, fn_get_fitness)

        optimal_fitness = fn_get_fitness(optimal_sequence)
        start_time = datetime.datetime.now()
        best = genetic.get_best(
            fn_get_fitness,
            None,
            optimal_fitness,
            None,
            fn_display,
            fn_mutate,
            fn_create,
            max_age=500,
            poolSize=25,
            crossover=fn_crossover,
        )
        self.assertTrue(not optimal_fitness > best.Fitness)


def get_distance(location_a, location_b):
    side_a = location_a[0] - location_b[0]
    side_b = location_a[1] - location_b[1]
    side_c = math.sqrt(side_a * side_a + side_b * side_b)
    return side_c


def mutate(genes, fn_get_fitness):
    count = random.randint(2, len(genes))
    initial_itness = fn_get_fitness(genes)
    while count > 0:
        count -= 1
        index_a, index_b = random.sample(range(len(genes)), 2)
        genes[index_a], genes[index_b] = genes[index_b], genes[index_a]
        fitness = fn_get_fitness(genes)
        if fitness > initial_itness:
            return


def crossover(parent_genes, donor_genes, fn_get_fitness):
    pairs = {Pair(donor_genes[0], donor_genes[-1]): 0}

    for i in range(len(donor_genes) - 1):
        pairs[Pair(donor_genes[i], donor_genes[i + 1])] = 0

    temp_genes = parent_genes[:]
    if Pair(parent_genes[0], parent_genes[-1]) in pairs:
        # find a discontinuity
        found = False
        for i in range(len(parent_genes) - 1):
            if Pair(parent_genes[i], parent_genes[i + 1]) in pairs:
                continue
            temp_genes = parent_genes[i + 1:] + parent_genes[: i + 1]
            found = True
            break
        if not found:
            return None
    runs = [[temp_genes[0]]]
    for i in range(len(temp_genes) - 1):
        if Pair(temp_genes[i], temp_genes[i + 1]) in pairs:
            runs[-1].append(temp_genes[i + 1])
            continue
        runs.append([temp_genes[i + 1]])

    initial_itness = fn_get_fitness(parent_genes)
    count = random.randint(2, 20)
    run_indexes = range(len(runs))
    child_genes = None

    while count > 0:
        count -= 1
        for i in run_indexes:
            if len(runs[i]) == 1:
                continue
            if random.randint(0, len(runs)) == 0:
                runs[i] = [n for n in reversed(runs[i])]

        index_a, index_b = random.sample(run_indexes, 2)
        runs[index_a], runs[index_b] = runs[index_b], runs[index_a]
        child_genes = list(chain.from_iterable(runs))
        if fn_get_fitness(child_genes) > initial_itness:
            return child_genes
    return child_genes


def get_fitness(genes, id_to_location_lookup):
    fitness = get_distance(
        id_to_location_lookup[genes[0]], id_to_location_lookup[genes[-1]]
    )
    for i in range(len(genes) - 1):
        start = id_to_location_lookup[genes[i]]
        end = id_to_location_lookup[genes[i + 1]]
        fitness += get_distance(start, end)

    return Fitness(round(fitness, 2))


class Fitness:
    TotalDistance = None

    def __init__(self, total_distance):
        self.TotalDistance = total_distance

    def __gt__(self, other):
        return self.TotalDistance < other.TotalDistance

    def __str__(self):
        return "{0:0.2f}".format(self.TotalDistance)


class Pair:
    Node = None
    Adjacent = None

    def __init__(self, node, adjacent):
        if node < adjacent:
            node, adjacent = adjacent, node
        self.Node = node
        self.Adjacent = adjacent

    def __eq__(self, other):
        return self.Node == other.Node and self.Adjacent == other.Adjacent

    def __hash__(self):
        return hash(self.Node) * 397 ^ hash(self.Adjacent)


def display(candidate, start_time):
    time_diff = datetime.datetime.now() - start_time
    print(
        "{0}\t{1}\t{2}\t{3}".format(
            " ".join(map(str, candidate.Genes)),
            candidate.Fitness,
            candidate.Strategy.name,
            str(time_diff),
        )
    )
