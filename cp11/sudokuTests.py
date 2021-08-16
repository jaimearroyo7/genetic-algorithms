import datetime
import random
import unittest

from genetic_algorithms.utils import genetic


class SudokuTests(unittest.TestCase):
    def test_benchmark(self):
        genetic.Benchmark.run(lambda: self.test())

    def test(self):
        gene_set = [i for i in range(1, 9 + 1)]
        start_time = datetime.datetime.now()
        optimal_value = 100
        validation_rules = build_validation_rules()

        def fnCreate():
            return random.sample(gene_set * 9, 81)

        def fnMutate(genes):
            mutate(genes, validation_rules)

        def fnDisplay(candidate):
            display(candidate, start_time)

        def fnGetFitness(genes):
            return get_fitness(genes, validation_rules)

        best = genetic.get_best(
            fnGetFitness,
            None,
            optimal_value,
            None,
            fnDisplay,
            fnMutate,
            fnCreate,
            max_age=50,
        )
        self.assertEqual(best.Fitness, optimal_value)


def shuffle_in_place(genes, first, last):
    while first < last:
        index = random.randint(first, last)
        genes[first], genes[index] = genes[index], genes[first]
        first += 1


def mutate(genes, validation_rules):
    selectedRule = next(
        rule for rule in validation_rules if genes[rule.Index] == genes[rule.OtherIndex]
    )

    if selectedRule is None:
        return

    if index_row(selectedRule.OtherIndex) % 3 == 2 and random.randint(0, 10) == 0:
        sectionStart = section_start(selectedRule.Index)
        current = selectedRule.OtherIndex
        while selectedRule.OtherIndex == current:
            shuffle_in_place(genes, sectionStart, 80)
            selectedRule = next(
                rule
                for rule in validation_rules
                if genes[rule.Index] == genes[rule.OtherIndex]
            )
        return
    row = index_row(selectedRule.OtherIndex)
    start = row * 9
    indexA = selectedRule.OtherIndex
    indexB = random.randrange(start, len(genes))
    genes[indexA], genes[indexB] = genes[indexB], genes[indexA]


def get_fitness(genes, validation_rules):
    try:
        first_failing_rule = next(
            rule
            for rule in validation_rules
            if genes[rule.Index] == genes[rule.OtherIndex]
        )
    except StopIteration:
        fitness = 100
    else:
        fitness = (1 + index_row(first_failing_rule.OtherIndex)) * 10 + (
            1 + index_column(first_failing_rule.OtherIndex)
        )
    return fitness


def display(candidate, start_time):
    time_diff = datetime.datetime.now() - start_time
    for row in range(9):
        line = " | ".join(
            " ".join(str(i) for i in candidate.Genes[row * 9 + i : row * 9 + i + 3])
            for i in [0, 3, 6]
        )
        print("", line)
        if row < 8 and row % 3 == 2:
            print(" ----- + ----- + -----")
    print(" - = - - = - - = - {0}\t{1}\n".format(candidate.Fitness, str(time_diff)))


class Rule:
    Index = None
    OtherIndex = None

    def __init__(self, it, other):
        if it > other:
            it, other = other, it
        self.Index = it
        self.OtherIndex = other

    def __eq__(self, other):
        return self.Index == other.Index and self.OtherIndex == other.OtherIndex

    def __hash__(self):
        return self.Index * 100 + self.OtherIndex


def build_validation_rules():
    rules = []
    for index in range(80):
        its_row = index_row(index)
        its_column = index_column(index)
        its_section = row_column_section(its_row, its_column)
        for index2 in range(index + 1, 81):
            other_row = index_row(index2)
            other_column = index_column(index2)
            other_section = row_column_section(other_row, other_column)
            if (
                its_row == other_row
                or its_column == other_column
                or its_section == other_section
            ):
                rules.append(Rule(index, index2))
    rules.sort(key=lambda x: x.OtherIndex * 100 + x.Index)
    return rules


def index_row(index):
    return int(index / 9)


def index_column(index):
    return int(index % 9)


def row_column_section(row, column):
    return int(row / 3) * 3 + int(column / 3)


def index_section(index):
    return row_column_section(index_row(index), index_column(index))


def section_start(index):
    return int((index_row(index) % 9) / 3) * 27 + int(index_column(index) / 3) * 3
