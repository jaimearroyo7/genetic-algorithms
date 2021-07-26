import csv
import unittest
import datetime
from genetic_algorithms.utils import genetic


class GraphColoringTests(unittest.TestCase):
    def test(self):
        states = load_data("adjacent_states.csv")
        rules = build_rules(states)
        optimalValue = len(rules)
        stateIndexLookup = {
            key: index for index, key in enumerate(sorted(states))
        }
        colors = ["Orange", "Yellow", "Green", "Blue"]
        colorLookup = {color[0]: color for color in colors}
        gene_set = list(colorLookup.keys())

        startTime = datetime.datetime.now()

        def fnDisplay(candidate):
            display(candidate, startTime)

        def fnGetFitness(genes):
            return get_fitness(genes, rules, stateIndexLookup)

        best = genetic.get_best(fnGetFitness, len(states),
                                optimalValue, gene_set, fnDisplay)
        self.assertTrue(not optimalValue > best.Fitness)
        keys = sorted(states.keys())
        for index in range(len(states)):
            print(keys[index] + " is " + colorLookup[best.Genes[index]])

    def test_benchmark(self):
        genetic.Benchmark.run(lambda: self.test())


class Rule:
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

    def __str__(self):
        return self.Node + " -> " + self.Adjacent

    def isValid(self, genes, nodeIndexLookup):
        index = nodeIndexLookup[self.Node]
        adjacentStateIndex = nodeIndexLookup[self.Adjacent]
        return genes[index] != genes[adjacentStateIndex]


def load_data(localFileName):
    """ expects: AA,BB;CC where BB and CC are the initial column values in
     other rows
    """
    with open(localFileName, mode='r') as infile:
        reader = csv.reader(infile)
        lookup = {row[0]: row[1].split(';') for row in reader if row}
    return lookup


def build_rules(items):
    rulesAdded = {}
    for state, adjacent in items.items():
        for adjacentState in adjacent:
            if adjacentState == '':
                continue
            rule = Rule(state, adjacentState)
            if rule in rulesAdded:
                rulesAdded[rule] += 1
            else:
                rulesAdded[rule] = 1
    for k, v in rulesAdded.items():
        if v != 2:
            print("rule {0} is not bidirectional".format(k))
    return rulesAdded.keys()


def get_fitness(genes, rules, stateIndexLookup):
    rulesThatPass = sum(1 for rule in rules if rule.isValid(
        genes, stateIndexLookup))
    return rulesThatPass


def display(candidate, startTime):
    timeDiff = datetime.datetime.now() - startTime
    print("{0}\t{1}\t{2}".format(
        ''.join(map(str, candidate.Genes)),
        candidate.Fitness,
        str(timeDiff))
    )
