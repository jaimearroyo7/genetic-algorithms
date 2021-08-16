import datetime
import random
import unittest

from genetic_algorithms.utils import genetic


class KnightsTests(unittest.TestCase):
    def test_3x4(self):
        width = 4
        height = 3
        # 1,0 2,0 3,0
        # 0,2 1,2 2,0
        # 2   N N N .
        # 1   . . . .
        # 0   . N N N
        #     0 1 2 3
        self.find_knight_positions(width, height, 6)

    def test_8x8(self):
        width = 8
        height = 8
        self.find_knight_positions(width, height, 14)

    def test_10x10(self):
        width = 8
        height = 8
        self.find_knight_positions(width, height, 22)

    def test_benchmark(self):
        genetic.Benchmark.run(lambda: self.test_10x10())

    def find_knight_positions(self, board_width, board_height, expected_knights):
        start_time = datetime.datetime.now()

        def fn_display(candidate):
            display(candidate, start_time, board_width, board_height)

        def fn_get_fitness(genes):
            return get_fitness(genes, board_width, board_height)

        all_positions = [
            Position(x, y) for y in range(board_height) for x in range(board_width)
        ]

        if board_width < 6 or board_height < 6:
            non_edge_positions = all_positions
        else:
            non_edge_positions = [
                i
                for i in all_positions
                if 0 < i.X < board_width - 1 and 0 < i.Y < board_height - 1
            ]

        def fn_get_random_position():
            return random.choice(non_edge_positions)

        def fn_mutate(genes):
            mutate(genes, board_width, board_height, all_positions, non_edge_positions)

        def fn_create():
            return create(fn_get_random_position, expected_knights)

        optimal_fitness = board_width * board_height
        best = genetic.get_best(
            fn_get_fitness, None, optimal_fitness, None,
            fn_display, fn_mutate, fn_create
        )
        self.assertTrue(not optimal_fitness > best.Fitness)


class Position:
    X = None
    Y = None

    def __init__(self, x, y):
        self.X = x
        self.Y = y

    def __str__(self):
        return "{0},{1}".format(self.X, self.Y)

    def __eq__(self, other):
        return self.X == other.X and self.Y == other.Y

    def __hash__(self):
        return self.X * 1000 + self.Y


class Board:
    def __init__(self, positions, width, height):
        board = [["."] * width for _ in range(height)]
        for index in range(len(positions)):
            knight_position = positions[index]
            board[knight_position.Y][knight_position.X] = "N"
        self._board = board
        self._width = width
        self._height = height

    def print(self):
        # 0,0 prints in bottom left corner
        for i in reversed(range(self._height)):
            print(i, "\t", " ".join(self._board[i]))
        print(" \t", " ".join(map(str, range(self._width))))


def create(fn_get_random_position, expected_knights):
    genes = [fn_get_random_position() for _ in range(expected_knights)]
    return genes


def mutate(genes, board_width, board_height, all_positions, non_edge_positions):
    count = 2 if random.randint(0, 10) == 0 else 1
    while count > 0:
        count -= 1
        position_to_knight_indexes = dict((p, []) for p in all_positions)
        for i, knight in enumerate(genes):
            for position in get_attacks(knight, board_width, board_height):
                position_to_knight_indexes[position].append(i)
        knight_indexes = set(i for i in range(len(genes)))
        unattacked = []
        for kvp in position_to_knight_indexes.items():
            if len(kvp[1]) > 1:
                continue
            if len(kvp[1]) == 0:
                unattacked.append(kvp[0])
                continue
            for p in kvp[1]:  # len == 1
                if p in knight_indexes:
                    knight_indexes.remove(p)

        potential_knight_positions = (
            [
                p
                for positions in map(
                    lambda x: get_attacks(x, board_width, board_height), unattacked
                )
                for p in positions
                if p in non_edge_positions
            ]
            if len(unattacked) > 0
            else non_edge_positions
        )

        gene_index = (
            random.randrange(0, len(genes))
            if len(knight_indexes) == 0
            else random.choice([i for i in knight_indexes])
        )

        position = random.choice(potential_knight_positions)
        genes[gene_index] = position


def get_fitness(genes, board_width, board_height):
    attacked = set(
        pos for kn in genes for pos in get_attacks(kn, board_width, board_height)
    )
    return len(attacked)


def display(candidate, start_time, board_width, board_height):
    time_diff = datetime.datetime.now() - start_time
    board = Board(candidate.Genes, board_width, board_height)
    board.print()
    print(
        "{0}\n\t{1}\t{2}".format(
            " ".join(map(str, candidate.Genes)), candidate.Fitness, str(time_diff)
        )
    )


def get_attacks(location, board_width, board_height):
    return [
        i
        for i in set(
            Position(x + location.X, y + location.Y)
            for x in [-2, -1, 1, 2]
            if 0 <= x + location.X < board_width
            for y in [-2, -1, 1, 2]
            if 0 <= y + location.Y < board_height and abs(y) != abs(x)
        )
    ]
