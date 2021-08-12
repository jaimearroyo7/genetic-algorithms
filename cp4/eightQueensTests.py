import datetime
import unittest

from genetic_algorithms.utils import genetic


class EightQueensTests(unittest.TestCase):
    def test(self, size=8):
        gene_set = [i for i in range(size)]
        start_time = datetime.datetime.now()

        def fn_display(candidate):
            display(candidate, start_time, size)

        def fn_get_fitness(genes):
            return get_fitness(genes, size)

        optimal_fitness = Fitness(0)
        best = genetic.get_best(fn_get_fitness, 2 * size,
                                optimal_fitness, gene_set, fn_display)
        self.assertTrue(not optimal_fitness > best.Fitness)

    def test_benchmark(self):
        genetic.Benchmark.run(lambda: self.test(20))


class Board:
    def __init__(self, genes, size):
        board = [['.'] * size for _ in range(size)]
        for index in range(0, len(genes), 2):
            row = genes[index]
            column = genes[index + 1]
            board[column][row] = 'Q'
        self._board = board

    def get(self, row, column):
        return self._board[column][row]

    def print(self):
        # 0,0 prints in bottom left corner
        for i in reversed(range(0, len(self._board))):
            print(' '.join(self._board[i]))


class Fitness:
    Total = None

    def __init__(self, total):
        self.Total = total

    def __gt__(self, other):
        return self.Total < other.Total

    def __str__(self):
        return "{0}".format(self.Total)


def get_fitness(genes, size):
    board = Board(genes, size)
    rows_with_queens = set()
    cols_with_queens = set()
    north_east_diagonals_with_queens = set()
    south_east_diagonals_with_queens = set()
    for row in range(size):
        for col in range(size):
            if board.get(row, col) == 'Q':
                rows_with_queens.add(row)
                cols_with_queens.add(col)
                north_east_diagonals_with_queens.add(row + col)
                south_east_diagonals_with_queens.add(size - 1 - row + col)

    total = size - len(rows_with_queens) \
        + size - len(cols_with_queens) \
        + size - len(north_east_diagonals_with_queens) \
        + size - len(south_east_diagonals_with_queens)

    return Fitness(total)


def display(candidate, start_time, size):
    time_diff = datetime.datetime.now() - start_time
    board = Board(candidate.Genes, size)
    board.print()
    print("{0}\t- {1}\t{2}".format(
        ' '.join(map(str, candidate.Genes)),
        candidate.Fitness,
        str(time_diff))
    )
