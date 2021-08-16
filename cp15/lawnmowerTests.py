import datetime
import random
import unittest

import lawnmower

from genetic_algorithms.utils import genetic


def get_fitness(genes, fn_evaluate):
    field, mower, _ = fn_evaluate(genes)
    return Fitness(field.count_mowed(), len(genes), mower.StepCount)


def display(candidate, start_time, fn_evaluate):
    field, mower, program = fn_evaluate(candidate.Genes)
    time_diff = datetime.datetime.now() - start_time
    field.display(mower)
    print("{}\t{}".format(candidate.Fitness, time_diff))
    program.print()


def mutate(genes, gene_set, min_genes, max_genes, fn_get_fitness, max_rounds):
    count = random.randint(1, max_rounds)
    initial_fitness = fn_get_fitness(genes)
    while count > 0:
        count -= 1
        if fn_get_fitness(genes) > initial_fitness:
            return

        adding = len(genes) == 0 or (
            len(genes) < max_genes and random.randint(0, 5) == 0
        )
        if adding:
            genes.append(random.choice(gene_set)())
            continue

        removing = len(genes) > min_genes and random.randint(0, 50) == 0
        if removing:
            index = random.randrange(0, len(genes))
            del genes[index]
            continue

        index = random.randrange(0, len(genes))
        genes[index] = random.choice(gene_set)()


def create(gene_set, min_genes, max_genes):
    num_genes = random.randint(min_genes, max_genes)
    genes = [random.choice(gene_set)() for _ in range(1, num_genes)]
    return genes


def crossover(parent, other_parent):
    child_genes = parent[:]
    if len(parent) <= 2 or len(other_parent) < 2:
        return child_genes
    length = random.randint(1, len(parent) - 2)
    start = random.randrange(0, len(parent) - length)
    child_genes[start: start + length] = other_parent[start: start + length]
    return child_genes


class LawnmowerTests(unittest.TestCase):
    def test_mow_turn(self):
        width = height = 8
        gene_set = [lambda: Mow(), lambda: Turn()]
        min_genes = width * height
        max_genes = int(1.5 * min_genes)
        max_mutation_rounds = 3
        expected_number_of_instructions = 78

        def fn_create_field():
            return lawnmower.ToroidField(width, height, lawnmower.FieldContents.Grass)

        self.run_with(
            gene_set,
            width,
            height,
            min_genes,
            max_genes,
            expected_number_of_instructions,
            max_mutation_rounds,
            fn_create_field,
            expected_number_of_instructions,
        )

    def test_mow_turn_jump(self):
        width = height = 8
        gene_set = [
            lambda: Mow(),
            lambda: Turn(),
            lambda: Jump(
                random.randint(0, min(width, height)),
                random.randint(0, min(width, height)),
            ),
        ]
        min_genes = width * height
        max_genes = int(1.5 * min_genes)
        max_mutation_rounds = 1
        expected_number_of_instructions = 64

        def fn_create_field():
            return lawnmower.ToroidField(width, height, lawnmower.FieldContents.Grass)

        self.run_with(
            gene_set,
            width,
            height,
            min_genes,
            max_genes,
            expected_number_of_instructions,
            max_mutation_rounds,
            fn_create_field,
            expected_number_of_instructions,
        )

    def test_mow_turn_jump_validating(self):
        width = height = 8
        gene_set = [
            lambda: Mow(),
            lambda: Turn(),
            lambda: Jump(
                random.randint(0, min(width, height)),
                random.randint(0, min(width, height)),
            ),
        ]
        min_genes = width * height
        max_genes = int(1.5 * min_genes)
        max_mutation_rounds = 3
        expected_number_of_instructions = 79

        def fn_create_field():
            return lawnmower.ValidatingField(
                width, height, lawnmower.FieldContents.Grass
            )

        self.run_with(
            gene_set,
            width,
            height,
            min_genes,
            max_genes,
            expected_number_of_instructions,
            max_mutation_rounds,
            fn_create_field,
            expected_number_of_instructions,
        )

    def test_mow_turn_repeat(self):
        width = height = 8
        gene_set = [
            lambda: Mow(),
            lambda: Turn(),
            lambda: Repeat(random.randint(0, 8), random.randint(0, 8)),
        ]
        min_genes = 3
        max_genes = 20
        max_mutation_rounds = 3
        expected_number_of_instructions = 9
        expected_number_of_steps = 88

        def fn_create_field():
            return lawnmower.ToroidField(width, height, lawnmower.FieldContents.Grass)

        self.run_with(
            gene_set,
            width,
            height,
            min_genes,
            max_genes,
            expected_number_of_instructions,
            max_mutation_rounds,
            fn_create_field,
            expected_number_of_steps,
        )

    def test_mow_turn_jump_func(self):
        width = height = 8
        gene_set = [
            lambda: Mow(),
            lambda: Turn(),
            lambda: Jump(
                random.randint(0, min(width, height)),
                random.randint(0, min(width, height)),
            ),
            lambda: Func(),
        ]
        min_genes = 3
        max_genes = 20
        max_mutation_rounds = 3
        expected_number_of_instructions = 18
        expected_number_of_steps = 65

        def fn_create_field():
            return lawnmower.ToroidField(width, height, lawnmower.FieldContents.Grass)

        self.run_with(
            gene_set,
            width,
            height,
            min_genes,
            max_genes,
            expected_number_of_instructions,
            max_mutation_rounds,
            fn_create_field,
            expected_number_of_steps,
        )

    def test_mow_turn_jump_call(self):
        width = height = 8
        gene_set = [
            lambda: Mow(),
            lambda: Turn(),
            lambda: Jump(
                random.randint(0, min(width, height)),
                random.randint(0, min(width, height)),
            ),
            lambda: Func(expect_call=True),
            lambda: Call(random.randint(0, 5)),
        ]
        min_genes = 3
        max_genes = 20
        max_mutation_rounds = 3
        expected_number_of_instructions = 18
        expected_number_of_steps = 65

        def fn_create_field():
            return lawnmower.ToroidField(width, height, lawnmower.FieldContents.Grass)

        self.run_with(
            gene_set,
            width,
            height,
            min_genes,
            max_genes,
            expected_number_of_instructions,
            max_mutation_rounds,
            fn_create_field,
            expected_number_of_steps,
        )

    def run_with(
        self,
        gene_set,
        width,
        height,
        min_genes,
        max_genes,
        expected_number_of_instructions,
        max_mutation_rounds,
        fn_create_field,
        expected_number_of_steps,
    ):
        mower_start_location = lawnmower.Location(int(width / 2), int(height / 2))
        mower_start_direction = lawnmower.Directions.South.value

        def fn_create():
            return create(gene_set, 1, height)

        def fn_evaluate(instructions):
            program = Program(instructions)
            mower = lawnmower.Mower(mower_start_location, mower_start_direction)
            field = fn_create_field()
            try:
                program.evaluate(mower, field)
            except RecursionError:
                pass
            return field, mower, program

        def fn_get_fitness(genes):
            return get_fitness(genes, fn_evaluate)

        start_time = datetime.datetime.now()

        def fn_display(candidate):
            display(candidate, start_time, fn_evaluate)

        def fn_mutate(child):
            mutate(child, gene_set, min_genes,
                   max_genes, fn_get_fitness, max_mutation_rounds)

        optimal_fitness = Fitness(
            width * height, expected_number_of_instructions, expected_number_of_steps
        )

        best = genetic.get_best(
            fn_get_fitness,
            None,
            optimal_fitness,
            None,
            fn_display,
            fn_mutate,
            fn_create,
            max_age=None,
            poolSize=10,
            crossover=crossover,
        )

        self.assertTrue(not optimal_fitness > best.Fitness)


class Mow:
    def __init__(self):
        pass

    @staticmethod
    def execute(mower, field):
        mower.mow(field)

    def __str__(self):
        return "mow"


class Turn:
    def __init__(self):
        pass

    @staticmethod
    def execute(mower, _):
        mower.turn_left()

    def __str__(self):
        return "turn"


class Jump:
    def __init__(self, forward, right):
        self.Forward = forward
        self.Right = right

    def execute(self, mower, field):
        mower.jump(field, self.Forward, self.Right)

    def __str__(self):
        return "jump({},{})".format(self.Forward, self.Right)


class Repeat:
    def __init__(self, op_count, times):
        self.OpCount = op_count
        self.Times = times
        self.ops = []

    def execute(self, mower, field):
        for i in range(self.Times):
            for op in self.ops:
                op.execute(mower, field)

    def __str__(self):
        return "repeat({},{})".format(
            " ".join(map(str, self.ops)) if len(self.ops) > 0 else self.OpCount,
            self.Times,
        )


class Func:
    def __init__(self, expect_call=False):
        self.ops = []
        self.ExpectCall = expect_call
        self.Id = None

    def execute(self, mower, field):
        for op in self.ops:
            op.execute(mower, field)

    def __str__(self):
        return "func{1}: {0}".format(
            " ".join(map(str, self.ops)), self.Id if self.Id is not None else ""
        )


class Call:
    def __init__(self, func_id=None):
        self.FuncId = func_id
        self.Funcs = None

    def execute(self, mower, field):
        func_id = 0 if self.FuncId is None else self.FuncId
        if len(self.Funcs) > func_id:
            self.Funcs[func_id].execute(mower, field)

    def __str__(self):
        return "call-{}".format(self.FuncId if self.FuncId is not None else "func")


class Program:
    def __init__(self, genes):
        temp = genes[:]
        funcs = []

        for index in reversed(range(len(temp))):
            if type(temp[index]) is Repeat:
                start = index + 1
                end = min(index + temp[index].OpCount + 1, len(temp))
                temp[index].ops = temp[start:end]
                del temp[start:end]
                continue

            if type(temp[index]) is Call:
                temp[index].funcs = funcs

            if type(temp[index]) is Func:
                if len(funcs) > 0 and not temp[index].ExpectCall:
                    temp[index] = Call()
                    temp[index].funcs = funcs
                    continue
                start = index + 1
                end = len(temp)
                func = Func()
                if temp[index].ExpectCall:
                    func.Id = len(funcs)
                func.ops = [
                    i
                    for i in temp[start:end]
                    if type(i) is not Repeat or type(i) is Repeat and len(i.ops) > 0
                ]
                funcs.append(func)
                del temp[index:end]

        for func in funcs:
            for index in reversed(range(len(func.ops))):
                if type(func.ops[index]) is Call:
                    func_id = func.ops[index].FuncId
                    if func_id is None:
                        continue
                    if func_id >= len(funcs) or len(funcs[func_id].ops) == 0:
                        del func.ops[index]

        for index in reversed(range(len(temp))):
            if type(temp[index]) is Call:
                func_id = temp[index].FuncId
                if func_id is None:
                    continue
                if func_id >= len(funcs) or len(funcs[func_id].ops) == 0:
                    del temp[index]
        self.Main = temp
        self.Funcs = funcs

    def evaluate(self, mower, field):
        for i, instruction in enumerate(self.Main):
            instruction.execute(mower, field)

    def print(self):
        if self.Funcs is not None:
            for func in self.Funcs:
                if func.Id is not None and len(func.ops) == 0:
                    continue
                print(func)
        print(" ".join(map(str, self.Main)))


class Fitness:
    def __init__(self, total_mowed, total_instructions, step_count):
        self.TotalMowed = total_mowed
        self.TotalInstructions = total_instructions
        self.StepCount = step_count

    def __gt__(self, other):
        if self.TotalMowed != other.TotalMowed:
            return self.TotalMowed > other.TotalMowed
        if self.StepCount != other.StepCount:
            return self.StepCount < other.StepCount
        return self.TotalInstructions < other.TotalInstructions

    def __str__(self):
        return "{} mowed with {} instructions and {} steps".format(
            self.TotalMowed, self.TotalInstructions, self.StepCount
        )
