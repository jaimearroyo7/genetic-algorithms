import datetime
import unittest

from genetic_algorithms.utils import genetic


class GraphColoringTests(unittest.TestCase):
    def test_states(self):
        self.color("adjacent_states.col", ["Orange", "Yellow", "Green", "Blue"])

    def test_R100_1gb(self):
        self.color(
            "R100_1gb.col", ["Red", "Orange", "Yellow", "Green", "Blue", "Indigo"]
        )

    def test_benchmark(self):
        genetic.Benchmark.run(lambda: self.test_R100_1gb())

    def color(self, file, colors):
        rules, nodes = load_data(file)
        optimal_value = len(rules)
        color_lookup = {color[0]: color for color in colors}
        gene_set = list(color_lookup.keys())
        start_time = datetime.datetime.now()
        node_index_lookup = {key: index for index, key in enumerate(sorted(nodes))}

        def fn_display(candidate):
            display(candidate, start_time)

        def fn_get_fitness(genes):
            return get_fitness(genes, rules, node_index_lookup)

        best = genetic.get_best(
            fn_get_fitness, len(nodes), optimal_value, gene_set, fn_display
        )
        self.assertTrue(not optimal_value > best.Fitness)

        keys = sorted(nodes)
        for index in range(len(nodes)):
            print(keys[index] + " is " + color_lookup[best.Genes[index]])


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

    def is_valid(self, genes, node_index_lookup):
        index = node_index_lookup[self.Node]
        adjacent_state_index = node_index_lookup[self.Adjacent]
        return genes[index] != genes[adjacent_state_index]


def load_data(local_file_name):
    """expects: T D1 [D2 ... DN]
    where T is the record type
    and D1 .. DN are record-type appropriate data elements
    """
    rules = set()
    nodes = set()
    with open(local_file_name, mode="r") as infile:
        content = infile.read().splitlines()
    for row in content:
        if row[0] == "e":  # e aa bb, aa and bb are node ids
            node_ids = row.split(" ")[1:3]
            rules.add(Rule(node_ids[0], node_ids[1]))
            nodes.add(node_ids[0])
            nodes.add(node_ids[1])
            continue
        if row[0] == "n":  # n aa ww, aa is a node id, ww is a weight
            node_ids = row.split(" ")
            nodes.add(node_ids[1])
    return rules, nodes


def build_rules(items):
    rules_added = {}
    for state, adjacent in items.items():
        for adjacentState in adjacent:
            if adjacentState == "":
                continue
            rule = Rule(state, adjacentState)
            if rule in rules_added:
                rules_added[rule] += 1
            else:
                rules_added[rule] = 1
    for k, v in rules_added.items():
        if v != 2:
            print("rule {0} is not bidirectional".format(k))
    return rules_added.keys()


def get_fitness(genes, rules, state_index_lookup):
    rules_that_pass = sum(
        1 for rule in rules if rule.is_valid(genes, state_index_lookup)
    )
    return rules_that_pass


def display(candidate, start_time):
    time_diff = datetime.datetime.now() - start_time
    print(
        "{0}\t{1}\t{2}".format(
            "".join(map(str, candidate.Genes)), candidate.Fitness, str(time_diff)
        )
    )
