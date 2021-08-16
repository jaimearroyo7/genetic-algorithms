import datetime
import random
import unittest

from genetic_algorithms.utils import genetic


class EquationGenerationTests(unittest.TestCase):
    def test_benchmark(self):
        genetic.Benchmark.run(lambda: self.test_exponent())

    def test_addition(self):
        operations = ["+", "-"]
        prioritized_operations = [{"+": add, "-": subtract}]
        optimal_length_solution = [7, "+", 7, "+", 7, "+", 7, "+", 7, "-", 6]
        self.solve(operations, prioritized_operations, optimal_length_solution)

    def test_multiplication(self):
        operations = ["+", "-", "*"]
        prioritized_operations = [{"*": multiply}, {"+": add, "-": subtract}]
        optimal_length_solution = [6, "*", 3, "*", 3, "*", 6, "-", 7]
        self.solve(operations, prioritized_operations, optimal_length_solution)

    def test_exponent(self):
        operations = ["^", "+", "-", "*"]
        prioritized_operations = [
            {"^": lambda a, b: a ** b},
            {"*": multiply},
            {"+": add, "-": subtract},
        ]
        optimal_length_solution = [6, "^", 3, "*", 2, "-", 5]
        self.solve(operations, prioritized_operations, optimal_length_solution)

    def solve(self, operations, prioritized_operations, optimal_length_solution):
        numbers = [1, 2, 3, 4, 5, 6, 7]
        expected_total = evaluate(optimal_length_solution, prioritized_operations)
        min_numbers = (1 + len(optimal_length_solution)) / 2
        max_numbers = 6 * min_numbers
        start_time = datetime.datetime.now()

        def fn_display(candidate):
            display(candidate, start_time)

        def fn_evaluate(genes):
            return evaluate(genes, prioritized_operations)

        def fn_get_fitness(genes):
            return get_fitness(genes, expected_total, fn_evaluate)

        def fn_create():
            return create(numbers, operations, min_numbers, max_numbers)

        def fn_mutate(child):
            mutate(child, numbers, operations, min_numbers, max_numbers, fn_get_fitness)

        optimal_fitness = fn_get_fitness(optimal_length_solution)
        best = genetic.get_best(
            fn_get_fitness,
            None,
            optimal_fitness,
            None,
            fn_display,
            fn_mutate,
            fn_create,
            max_age=50,
        )
        self.assertTrue(not optimal_fitness > best.Fitness)


def create(numbers, operations, min_numbers, max_numbers):
    genes = [random.choice(numbers)]
    count = random.randint(min_numbers, 1 + max_numbers)
    while count > 1:
        count -= 1
        genes.append(random.choice(operations))
        genes.append(random.choice(numbers))
    return genes


def get_fitness(genes, expected_total, fn_evaluate):
    result = fn_evaluate(genes)
    return (
        expected_total - abs(result - expected_total)
        if result != expected_total
        else 1000 - len(genes)
    )


def mutate(genes, numbers, operations, min_numbers, max_numbers, fn_get_fitness):
    count = random.randint(1, 10)
    initial_fitness = fn_get_fitness(genes)
    while count > 0:
        count -= 1
        if fn_get_fitness(genes) > initial_fitness:
            return
        number_count = (1 + len(genes)) / 2
        adding = number_count < max_numbers and random.randint(0, 100) == 0
        if adding:
            genes.append(random.choice(operations))
            genes.append(random.choice(numbers))
            continue

        removing = number_count > min_numbers and random.randint(0, 20) == 0
        if removing:
            index = random.randrange(0, len(genes) - 1)
            del genes[index]
            del genes[index]
            continue

        index = random.randrange(0, len(genes))
        genes[index] = (
            random.choice(operations) if (index & 1) == 1 else random.choice(numbers)
        )


def display(candidate, start_time):
    time_diff = datetime.datetime.now() - start_time
    print(
        "{}\t{}\t{}".format(
            (" ".join(map(str, [i for i in candidate.Genes]))),
            candidate.Fitness,
            time_diff,
        )
    )


def evaluate(genes, prioritized_operations):
    equation = genes[:]
    for operationSet in prioritized_operations:
        i_offset = 0
        for i in range(1, len(equation), 2):
            i += i_offset
            op_token = equation[i]
            if op_token in operationSet:
                left_operand = equation[i - 1]
                right_operand = equation[i + 1]
                equation[i - 1] = operationSet[op_token](left_operand, right_operand)
                del equation[i + 1]
                del equation[i]
                i_offset += -2
    return equation[0]


def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b
