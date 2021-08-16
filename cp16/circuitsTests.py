import datetime
import random
import unittest

import circuits

from genetic_algorithms.utils import genetic


def get_fitness(genes, rules, inputs):
    circuit = nodes_to_circuit(genes)[0]
    source_labels = "ABCD"
    rules_passed = 0
    for rule in rules:
        inputs.clear()
        inputs.update(zip(source_labels, rule[0]))
        if circuit.get_output() == rule[1]:
            rules_passed += 1
    return rules_passed


def display(candidate, start_time):
    circuit = nodes_to_circuit(candidate.Genes)[0]
    time_diff = datetime.datetime.now() - start_time
    print("{}\t{}\t{}".format(circuit, candidate.Fitness, time_diff))


def create_gene(index, gates, sources):
    if index < len(sources):
        gate_type = sources[index]
    else:
        gate_type = random.choice(gates)
    index_a = index_b = None
    if gate_type[1].input_count() > 0:
        index_a = random.randint(0, index)
    if gate_type[1].input_count() > 1:
        index_b = random.randint(0, index)
        if index_b == index_a:
            index_b = random.randint(0, index)
    return Node(gate_type[0], index_a, index_b)


def mutate(child_genes, fn_create_gene, fn_get_fitness, source_count):
    count = random.randint(1, 5)
    initial_fitness = fn_get_fitness(child_genes)
    while count > 0:
        count -= 1
        indexes_used = [
            i for i in nodes_to_circuit(child_genes)[1] if i >= source_count
        ]
        if len(indexes_used) == 0:
            return
        index = random.choice(indexes_used)
        child_genes[index] = fn_create_gene(index)
        if fn_get_fitness(child_genes) > initial_fitness:
            return


class CircuitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = dict()
        cls.gates = [
            [circuits.And, circuits.And],
            [lambda i1, i2: circuits.Not(i1), circuits.Not],
        ]
        cls.sources = [
            [lambda i1, i2: circuits.Source("A", cls.inputs), circuits.Source],
            [lambda i1, i2: circuits.Source("B", cls.inputs), circuits.Source],
        ]

    def test_generate_OR(self):
        rules = [
            [[False, False], False],
            [[False, True], True],
            [[True, False], True],
            [[True, True], True],
        ]

        optimal_length = 6
        self.find_circuit(rules, optimal_length)

    def test_generate_XOR(self):
        rules = [
            [[False, False], False],
            [[False, True], True],
            [[True, False], True],
            [[True, True], False],
        ]
        self.find_circuit(rules, 9)

    def test_generate_AxBxC(self):
        rules = [
            [[False, False, False], False],
            [[False, False, True], True],
            [[False, True, False], True],
            [[False, True, True], False],
            [[True, False, False], True],
            [[True, False, True], False],
            [[True, True, False], False],
            [[True, True, True], True],
        ]
        self.sources.append(
            [lambda l, r: circuits.Source("C", self.inputs), circuits.Source]
        )
        self.gates.append([circuits.Or, circuits.Or])
        self.find_circuit(rules, 12)

    def get_2_bit_adder_rules_for_bit(self, bit):
        rules = [
            [[0, 0, 0, 0], [0, 0, 0]],  # 0 + 0 = 0
            [[0, 0, 0, 1], [0, 0, 1]],  # 0 + 1 = 1
            [[0, 0, 1, 0], [0, 1, 0]],  # 0 + 2 = 2
            [[0, 0, 1, 1], [0, 1, 1]],  # 0 + 3 = 3
            [[0, 1, 0, 0], [0, 0, 1]],  # 1 + 0 = 1
            [[0, 1, 0, 1], [0, 1, 0]],  # 1 + 1 = 2
            [[0, 1, 1, 0], [0, 1, 1]],  # 1 + 2 = 3
            [[0, 1, 1, 1], [1, 0, 0]],  # 1 + 3 = 4
            [[1, 0, 0, 0], [0, 1, 0]],  # 2 + 0 = 2
            [[1, 0, 0, 1], [0, 1, 1]],  # 2 + 1 = 3
            [[1, 0, 1, 0], [1, 0, 0]],  # 2 + 2 = 4
            [[1, 0, 1, 1], [1, 0, 1]],  # 2 + 3 = 5
            [[1, 1, 0, 0], [0, 1, 1]],  # 3 + 0 = 3
            [[1, 1, 0, 1], [1, 0, 0]],  # 3 + 1 = 4
            [[1, 1, 1, 0], [1, 0, 1]],  # 3 + 2 = 5
            [[1, 1, 1, 1], [1, 1, 0]],
        ]  # 3 + 3 = 6
        bit_n_rules = [[rule[0], rule[1][2 - bit]] for rule in rules]
        self.gates.append([circuits.Or, circuits.Or])
        self.gates.append([circuits.Xor, circuits.Xor])
        self.sources.append(
            [lambda l, r: circuits.Source("C", self.inputs), circuits.Source]
        )
        self.sources.append(
            [lambda l, r: circuits.Source("D", self.inputs), circuits.Source]
        )
        return bit_n_rules

    def test_2_bit_adder_1s_bit(self):
        rules = self.get_2_bit_adder_rules_for_bit(0)
        self.find_circuit(rules, 3)

    def test_2_bit_adder_2s_bit(self):
        rules = self.get_2_bit_adder_rules_for_bit(1)
        self.find_circuit(rules, 7)

    def test_2_bit_adder_4s_bit(self):
        rules = self.get_2_bit_adder_rules_for_bit(2)
        self.find_circuit(rules, 9)

    def find_circuit(self, rules, expected_length):
        start_time = datetime.datetime.now()

        def fn_display(candidate, length=None):
            if length is not None:
                print(
                    "-- distinct nodes in circuit:",
                    len(nodes_to_circuit(candidate.Genes)[1]),
                )
            display(candidate, start_time)

        def fn_get_fitness(genes):
            return get_fitness(genes, rules, self.inputs)

        def fn_create_gene(index):
            return create_gene(index, self.gates, self.sources)

        def fn_mutate(genes):
            mutate(genes, fn_create_gene, fn_get_fitness, len(self.sources))

        max_length = 50

        def fn_create():
            return [fn_create_gene(i) for i in range(max_length)]

        def fn_optimization_function(variable_length):
            nonlocal max_length
            max_length = variable_length
            return genetic.get_best(
                fn_get_fitness,
                None,
                len(rules),
                None,
                fn_display,
                fn_mutate,
                fn_create,
                poolSize=3,
                max_seconds=30,
            )

        def fn_is_improvement(current_best, child):
            return child.Fitness == len(rules) and len(
                nodes_to_circuit(child.Genes)[1]
            ) < len(nodes_to_circuit(current_best.Genes)[1])

        def fn_is_optimal(child):
            return (
                child.Fitness == len(rules)
                and len(nodes_to_circuit(child.Genes)[1]) <= expected_length
            )

        def fn_get_next_feature_value(current_best):
            return len(nodes_to_circuit(current_best.Genes)[1])

        best = genetic.hill_climbing(
            fn_optimization_function,
            fn_is_improvement,
            fn_is_optimal,
            fn_get_next_feature_value,
            fn_display,
            max_length,
        )
        self.assertTrue(best.Fitness == len(rules))
        self.assertFalse(len(nodes_to_circuit(best.Genes)[1]) > expected_length)


def nodes_to_circuit(genes):
    circuit = []
    used_indexes = []
    for i, node in enumerate(genes):
        used = {i}
        input_a = input_b = None
        if node.index_a is not None and i > node.index_a:
            input_a = circuit[node.index_a]
            used.update(used_indexes[node.index_a])
            if node.index_b is not None and i > node.index_b:
                input_b = circuit[node.index_b]
                used.update(used_indexes[node.index_b])
        circuit.append(node.CreateGate(input_a, input_b))
        used_indexes.append(used)
    return circuit[-1], used_indexes[-1]


class Node:
    def __init__(self, create_gate, index_a=None, index_b=None):
        self.CreateGate = create_gate
        self.index_a = index_a
        self.index_b = index_b
