import datetime
import random
import unittest

from genetic_algorithms.utils import genetic


class EquationGenerationTests(unittest.TestCase):
    def test_benchmark(self):
        genetic.Benchmark.run(lambda: self.test_exponent())

    def test_addition(self):
        operations = ['+', '-']
        prioritizedOperations = [{'+': add,
                                  '-': subtract}]
        optimalLengthSolution = [7, '+', 7, '+', 7, '+', 7, '+', 7, '-', 6]
        self.solve(operations, prioritizedOperations, optimalLengthSolution)

    def test_multiplication(self):
        operations = ['+', '-', '*']
        prioritizedOperations = [{'*': multiply},
                                 {'+': add,
                                  '-': subtract}]
        optimalLengthSolution = [6, '*', 3, '*', 3, '*', 6, '-', 7]
        self.solve(operations, prioritizedOperations, optimalLengthSolution)

    def test_exponent(self):
        operations = ['^', '+', '-', '*']
        prioritizedOperations = [{'^': lambda a, b: a ** b},
                                 {'*': multiply},
                                 {'+': add,
                                  '-': subtract}]
        optimalLengthSolution = [6, '^', 3, '*', 2, '-', 5]
        self.solve(operations, prioritizedOperations, optimalLengthSolution)

    def solve(self, operations, prioritizedOperations,
              optimalLengthSolution):
        numbers = [1, 2, 3, 4, 5, 6, 7]
        expectedTotal = evaluate(optimalLengthSolution,
                                 prioritizedOperations)
        minNumbers = (1 + len(optimalLengthSolution)) / 2
        maxNumbers = 6 * minNumbers
        startTime = datetime.datetime.now()

        def fnDisplay(candidate):
            display(candidate, startTime)

        def fnEvaluate(genes):
            return evaluate(genes, prioritizedOperations)

        def fnGetFitness(genes):
            return get_fitness(genes, expectedTotal, fnEvaluate)

        def fnCreate():
            return create(numbers, operations, minNumbers, maxNumbers)

        def fnMutate(child):
            mutate(child, numbers, operations, minNumbers, maxNumbers,
                   fnGetFitness)

        optimalFitness = fnGetFitness(optimalLengthSolution)
        best = genetic.get_best(fnGetFitness, None, optimalFitness, None,
                                fnDisplay, fnMutate, fnCreate, max_age=50)
        self.assertTrue(not optimalFitness > best.Fitness)


def create(numbers, operations, minNumbers, maxNumbers):
    genes = [random.choice(numbers)]
    count = random.randint(minNumbers, 1 + maxNumbers)
    while count > 1:
        count -= 1
        genes.append(random.choice(operations))
        genes.append(random.choice(numbers))
    return genes


def get_fitness(genes, expectedTotal, fnEvaluate):
    result = fnEvaluate(genes)
    return expectedTotal - abs(result - expectedTotal)\
        if result != expectedTotal else 1000 - len(genes)


def mutate(genes, numbers, operations, minNumbers, maxNumbers,
           fnGetFitness):
    count = random.randint(1, 10)
    initialFitness = fnGetFitness(genes)
    while count > 0:
        count -= 1
        if fnGetFitness(genes) > initialFitness:
            return
        numberCount = (1 + len(genes)) / 2
        adding = numberCount < maxNumbers and random.randint(0, 100) == 0
        if adding:
            genes.append(random.choice(operations))
            genes.append(random.choice(numbers))
            continue

        removing = numberCount > minNumbers and random.randint(0, 20) == 0
        if removing:
            index = random.randrange(0, len(genes) - 1)
            del genes[index]
            del genes[index]
            continue

        index = random.randrange(0, len(genes))
        genes[index] = random.choice(operations) \
            if (index & 1) == 1 else random.choice(numbers)


def display(candidate, startTime):
    timeDiff = datetime.datetime.now() - startTime
    print("{}\t{}\t{}".format(
        (' '.join(map(str, [i for i in candidate.Genes]))),
        candidate.Fitness,
        timeDiff))


def evaluate(genes, prioritizedOperations):
    equation = genes[:]
    for operationSet in prioritizedOperations:
        iOffset = 0
        for i in range(1, len(equation), 2):
            i += iOffset
            opToken = equation[i]
            if opToken in operationSet:
                leftOperand = equation[i - 1]
                rightOperand = equation[i + 1]
                equation[i - 1] = operationSet[opToken](leftOperand,
                                                        rightOperand)
                del equation[i + 1]
                del equation[i]
                iOffset += -2
    return equation[0]


def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b