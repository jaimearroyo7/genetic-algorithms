import datetime
import random
import unittest
from functools import partial

from genetic_algorithms.utils import genetic


def get_fitness(genes):
    local_copy = genes[:]
    fitness = get_fitness_for_games(local_copy)
    fitness.GeneCount = len(genes)
    return fitness


squareIndexes = [1, 2, 3, 4, 5, 6, 7, 8, 9]


def play1on1(x_genes, _genes):
    board = dict((i, Square(i, ContentType.Empty)) for i in range(1, 9 + 1))
    empties = [v for v in board.values() if v.Content == ContentType.Empty]
    round_data = [
        [
            x_genes,
            ContentType.Mine,
            genetic.CompetitionResult.Loss,
            genetic.CompetitionResult.Win,
        ],
        [
            _genes,
            ContentType.Opponent,
            genetic.CompetitionResult.Win,
            genetic.CompetitionResult.Loss,
        ],
    ]
    player_index = 0

    while len(empties) > 0:
        player_data = round_data[player_index]
        player_index = 1 - player_index
        genes, piece, loss_result, win_result = player_data

        move_and_rule_index = get_move(genes, board, empties)
        if move_and_rule_index is None:  # could not find a move
            return loss_result

        index = move_and_rule_index[0]
        board[index] = Square(index, piece)

        most_recent_move_only = [board[index]]
        if (
            len(RowContentFilter(piece, 3).get_matches(
                board, most_recent_move_only)) > 0
            or len(ColumnContentFilter(piece, 3).get_matches(
                board, most_recent_move_only))
            > 0
            or len(
                DiagonalContentFilter(piece, 3).get_matches(
                    board, most_recent_move_only)
            )
            > 0
        ):
            return win_result
        empties = [v for v in board.values() if v.Content == ContentType.Empty]
    return genetic.CompetitionResult.Tie


def get_fitness_for_games(genes):
    def get_board_string(b):
        return "".join(
            map(
                lambda i: "."
                if b[i].Content == ContentType.Empty
                else "x"
                if b[i].Content == ContentType.Mine
                else "o",
                squareIndexes,
            )
        )

    board = dict((i, Square(i, ContentType.Empty)) for i in range(1, 9 + 1))

    queue = [board]
    for square in board.values():
        candidate_copy = board.copy()
        candidate_copy[square.Index] = Square(square.Index, ContentType.Opponent)
        queue.append(candidate_copy)

    winning_rules = {}
    wins = ties = losses = 0

    while len(queue) > 0:
        board = queue.pop()
        board_string = get_board_string(board)
        empties = [v for v in board.values() if v.Content == ContentType.Empty]

        if len(empties) == 0:
            ties += 1
            continue

        candidate_index_and_rule_index = get_move(genes, board, empties)

        if candidate_index_and_rule_index is None:  # could not find a move
            # there are empties but didn't find a move
            losses += 1
            # go to next board
            continue

        # found at least one move
        index = candidate_index_and_rule_index[0]
        board[index] = Square(index, ContentType.Mine)
        # newBoardString = get_board_string(board)

        # if we now have three MINE in any ROW, COLUMN or DIAGONAL, we won
        most_recent_move_only = [board[index]]
        if (
            len(iHaveThreeInRow.get_matches(board, most_recent_move_only)) > 0
            or len(iHaveThreeInColumn.get_matches(board, most_recent_move_only)) > 0
            or len(iHaveThreeInDiagonal.get_matches(board, most_recent_move_only)) > 0
        ):
            rule_id = candidate_index_and_rule_index[1]
            if rule_id not in winning_rules:
                winning_rules[rule_id] = list()
            winning_rules[rule_id].append(board_string)
            wins += 1
            # go to next board
            continue

        # we lose if any empties have two OPPONENT pieces in ROW, COL or DIAG
        empties = [v for v in board.values() if v.Content == ContentType.Empty]
        if len(opponentHasTwoInARow.get_matches(board, empties)) > 0:
            losses += 1
            # go to next board
            continue

        # queue all possible OPPONENT responses
        for square in empties:
            candidate_copy = board.copy()
            candidate_copy[square.Index] = Square(square.Index, ContentType.Opponent)
            queue.append(candidate_copy)

    return Fitness(wins, ties, losses, len(genes))


def get_move(rule_set, board, empties, starting_rule_index=0):
    rule_set_copy = rule_set[:]

    for ruleIndex in range(starting_rule_index, len(rule_set_copy)):
        gene = rule_set_copy[ruleIndex]
        matches = gene.get_matches(board, empties)
        if len(matches) == 0:
            continue
        if len(matches) == 1:
            return [list(matches)[0], ruleIndex]
        if len(empties) > len(matches):
            empties = [e for e in empties if e.Index in matches]

    return None


def display(candidate, start_time):
    time_diff = datetime.datetime.now() - start_time
    local_copy = candidate.Genes[:]
    for i in reversed(range(len(local_copy))):
        local_copy[i] = str(local_copy[i])

    print(
        "\t{}\n{}\n{}".format(
            "\n\t".join([d for d in local_copy]), candidate.Fitness, time_diff
        )
    )


def mutate_add(genes, gene_set):
    index = random.randrange(0, len(genes) + 1) if len(genes) > 0 else 0
    genes[index:index] = [random.choice(gene_set)]
    return True


def mutate_remove(genes):
    if len(genes) < 1:
        return False
    del genes[random.randrange(0, len(genes))]
    if len(genes) > 1 and random.randint(0, 1) == 1:
        del genes[random.randrange(0, len(genes))]
    return True


def mutate_replace(genes, gene_set):
    if len(genes) < 1:
        return False
    index = random.randrange(0, len(genes))
    genes[index] = random.choice(gene_set)
    return True


def mutate_swap_adjacent(genes):
    if len(genes) < 2:
        return False
    index = random.choice(range(len(genes) - 1))
    genes[index], genes[index + 1] = genes[index + 1], genes[index]
    return True


def mutate_move(genes):
    if len(genes) < 3:
        return False
    start = random.choice(range(len(genes)))
    stop = start + random.randint(1, 2)
    to_move = genes[start:stop]
    genes[start:stop] = []
    index = random.choice(range(len(genes)))
    if index >= start:
        index += 1
    genes[index:index] = to_move
    return True


def mutate(genes, fn_get_fitness, mutation_operators, mutation_round_counts):
    initial_fitness = fn_get_fitness(genes)
    count = random.choice(mutation_round_counts)
    for i in range(1, count + 2):
        copy = mutation_operators[:]
        func = random.choice(copy)
        while not func(genes):
            copy.remove(func)
            func = random.choice(copy)
        if fn_get_fitness(genes) > initial_fitness:
            mutation_round_counts.append(i)
            return


def create_gene_set():
    options = [[ContentType.Opponent, [0, 1, 2]], [ContentType.Mine, [0, 1, 2]]]
    gene_set = [
        RuleMetadata(RowContentFilter, options),
        RuleMetadata(lambda expected_content, count: TopRowFilter(), options),
        RuleMetadata(lambda expected_content, count: MiddleRowFilter(), options),
        RuleMetadata(lambda expected_content, count: BottomRowFilter(), options),
        RuleMetadata(ColumnContentFilter, options),
        RuleMetadata(lambda expected_content, count: LeftColumnFilter(), options),
        RuleMetadata(lambda expected_content, count: MiddleColumnFilter(), options),
        RuleMetadata(lambda expected_content, count: RightColumnFilter(), options),
        RuleMetadata(DiagonalContentFilter, options),
        RuleMetadata(lambda expected_content, count: DiagonalLocationFilter(), options),
        RuleMetadata(lambda expected_content, count: CornerFilter()),
        RuleMetadata(lambda expected_content, count: SideFilter()),
        RuleMetadata(lambda expected_content, count: CenterFilter()),
        RuleMetadata(
            lambda expected_content, count: RowOppositeFilter(expected_content),
            options,
            needs_specific_content=True,
        ),
        RuleMetadata(
            lambda expected_content, count: ColumnOppositeFilter(expected_content),
            options,
            needs_specific_content=True,
        ),
        RuleMetadata(
            lambda expected_content, count: DiagonalOppositeFilter(expected_content),
            options,
            needs_specific_content=True,
        ),
    ]

    genes = list()
    for gene in gene_set:
        genes.extend(gene.create_rules())

    print("created " + str(len(genes)) + " genes")
    return genes


class TicTacToeTests(unittest.TestCase):
    def test_perfect_knowledge(self):
        min_genes = 10
        max_genes = 20
        gene_set = create_gene_set()
        start_time = datetime.datetime.now()

        def fn_display(candidate):
            display(candidate, start_time)

        def fn_get_fitness(genes):
            return get_fitness(genes)

        mutation_round_counts = [1]

        mutation_operators = [
            partial(mutate_add, gene_set=gene_set),
            partial(mutate_replace, gene_set=gene_set),
            mutate_remove,
            mutate_swap_adjacent,
            mutate_move,
        ]

        def fn_mutate(genes):
            mutate(genes, fn_get_fitness, mutation_operators, mutation_round_counts)

        def fn_crossover(parent, donor):
            child = parent[0: int(len(parent) / 2)] + donor[int(len(donor) / 2):]
            fn_mutate(child)
            return child

        def fn_create():
            return random.sample(gene_set, random.randrange(min_genes, max_genes))

        optimal_fitness = Fitness(620, 120, 0, 11)
        best = genetic.get_best(
            fn_get_fitness,
            min_genes,
            optimal_fitness,
            None,
            fn_display,
            fn_mutate,
            fn_create,
            max_age=500,
            pool_size=20,
            crossover=fn_crossover,
        )
        self.assertTrue(not optimal_fitness > best.Fitness)

    @staticmethod
    def test_tournament():
        min_genes = 10
        max_genes = 20
        gene_set = create_gene_set()
        start_time = datetime.datetime.now()

        def fn_display(genes, wins, ties, losses, generation):
            print("-- generation {} --".format(generation))
            display(
                genetic.Chromosome(
                    genes, Fitness(wins, ties, losses, len(genes)), None
                ),
                start_time,
            )

        mutation_round_counts = [1]

        mutation_operators = [
            partial(mutate_add, gene_set=gene_set),
            partial(mutate_replace, gene_set=gene_set),
            mutate_remove,
            mutate_swap_adjacent,
            mutate_move,
        ]

        def fn_mutate(genes):
            mutate(genes, lambda x: 0, mutation_operators, mutation_round_counts)

        def fn_crossover(parent, donor):
            child = parent[0: int(len(parent) / 2)] + donor[int(len(donor) / 2):]
            fn_mutate(child)
            return child

        def fn_create():
            return random.sample(gene_set, random.randrange(min_genes, max_genes))

        def fn_sort_key(genes, _, ties, losses):
            return -1000 * losses - ties + 1 / len(genes)

        genetic.tournament(
            fn_create, fn_crossover, play1on1, fn_display, fn_sort_key, 13)


class ContentType:
    Empty = "EMPTY"
    Mine = "MINE"
    Opponent = "OPPONENT"


class Square:
    def __init__(self, index, content=ContentType.Empty):
        self.Content = content
        self.Index = index
        self.Diagonals = []
        # board layout is
        #   1  2  3
        #   4  5  6
        #   7  8  9
        self.IsCenter = False
        self.IsCorner = False
        self.IsSide = False
        self.IsTopRow = False
        self.IsMiddleRow = False
        self.IsBottomRow = False
        self.IsLeftColumn = False
        self.IsMiddleColumn = False
        self.IsRightColumn = False
        self.Row = None
        self.Column = None
        self.DiagonalOpposite = None
        self.RowOpposite = None
        self.ColumnOpposite = None

        if index == 1 or index == 2 or index == 3:
            self.IsTopRow = True
            self.Row = [1, 2, 3]
        elif index == 4 or index == 5 or index == 6:
            self.IsMiddleRow = True
            self.Row = [4, 5, 6]
        elif index == 7 or index == 8 or index == 9:
            self.IsBottomRow = True
            self.Row = [7, 8, 9]

        if index % 3 == 1:
            self.Column = [1, 4, 7]
            self.IsLeftColumn = True
        elif index % 3 == 2:
            self.Column = [2, 5, 8]
            self.IsMiddleColumn = True
        elif index % 3 == 0:
            self.Column = [3, 6, 9]
            self.IsRightColumn = True

        if index == 5:
            self.IsCenter = True
        else:
            if index == 1 or index == 3 or index == 7 or index == 9:
                self.IsCorner = True
            elif index == 2 or index == 4 or index == 6 or index == 8:
                self.IsSide = True

            if index == 1:
                self.RowOpposite = 3
                self.ColumnOpposite = 7
                self.DiagonalOpposite = 9
            elif index == 2:
                self.ColumnOpposite = 8
            elif index == 3:
                self.RowOpposite = 1
                self.ColumnOpposite = 9
                self.DiagonalOpposite = 7
            elif index == 4:
                self.RowOpposite = 6
            elif index == 6:
                self.RowOpposite = 4
            elif index == 7:
                self.RowOpposite = 9
                self.ColumnOpposite = 1
                self.DiagonalOpposite = 3
            elif index == 8:
                self.ColumnOpposite = 2
            else:  # index == 9
                self.RowOpposite = 7
                self.ColumnOpposite = 3
                self.DiagonalOpposite = 1

        if index == 1 or self.DiagonalOpposite == 1 or self.IsCenter:
            self.Diagonals.append([1, 5, 9])
        if index == 3 or self.DiagonalOpposite == 3 or self.IsCenter:
            self.Diagonals.append([7, 5, 3])


class Rule:
    def __init__(self, description_prefix, expected_content=None, count=None):
        self.DescriptionPrefix = description_prefix
        self.ExpectedContent = expected_content
        self.Count = count

    def __str__(self):
        result = self.DescriptionPrefix + " "
        if self.Count is not None:
            result += str(self.Count) + " "
        if self.ExpectedContent is not None:
            result += self.ExpectedContent + " "
        return result


class RuleMetadata:
    def __init__(
        self, create, options=None, needs_specific_content=True,
            needs_specific_count=True
    ):
        if options is None:
            needs_specific_content = False
            needs_specific_count = False
        if needs_specific_count and not needs_specific_content:
            raise ValueError(
                "needs_specific_count is only valid if needs_specific_content is true"
            )
        self.create = create
        self.options = options
        self.needs_specific_content = needs_specific_content
        self.needs_specific_count = needs_specific_count

    def create_rules(self):
        option = None
        count = None

        seen = set()
        if self.needs_specific_content:
            rules = list()

            for optionInfo in self.options:
                option = optionInfo[0]
                if self.needs_specific_count:
                    option_counts = optionInfo[1]

                    for count in option_counts:
                        gene = self.create(option, count)
                        if str(gene) not in seen:
                            seen.add(str(gene))
                            rules.append(gene)
                else:
                    gene = self.create(option, None)
                    if str(gene) not in seen:
                        seen.add(str(gene))
                        rules.append(gene)
            return rules
        else:
            return [self.create(option, count)]


class ContentFilter(Rule):
    def __init__(self, description, expected_content,
                 expected_count, get_value_from_square):
        super().__init__(description, expected_content, expected_count)
        self.get_value_from_square = get_value_from_square

    def get_matches(self, board, squares):
        result = set()
        for square in squares:
            m = list(
                map(lambda i: board[i].Content, self.get_value_from_square(square))
            )
            if m.count(self.ExpectedContent) == self.Count:
                result.add(square.Index)
        return result


class RowContentFilter(ContentFilter):
    def __init__(self, expected_content, expected_count):
        super().__init__(
            "its ROW has", expected_content, expected_count, lambda s: s.Row)


class ColumnContentFilter(ContentFilter):
    def __init__(self, expected_content, expected_count):
        super().__init__(
            "its COLUMN has", expected_content, expected_count, lambda s: s.Column
        )


class LocationFilter(Rule):
    def __init__(self, expected_location, container_description, func):
        super().__init__("is in " + expected_location + " " + container_description)
        self.func = func

    def get_matches(self, _, squares):
        result = set()
        for square in squares:
            if self.func(square):
                result.add(square.Index)
        return result


class RowLocationFilter(LocationFilter):
    def __init__(self, expected_location, func):
        super().__init__(expected_location, "ROW", func)


class ColumnLocationFilter(LocationFilter):
    def __init__(self, expected_location, func):
        super().__init__(expected_location, "COLUMN", func)


class TopRowFilter(RowLocationFilter):
    def __init__(self):
        super().__init__("TOP", lambda square: square.IsTopRow)


class MiddleRowFilter(RowLocationFilter):
    def __init__(self):
        super().__init__("MIDDLE", lambda square: square.IsMiddleRow)


class BottomRowFilter(RowLocationFilter):
    def __init__(self):
        super().__init__("BOTTOM", lambda square: square.IsBottomRow)


class LeftColumnFilter(ColumnLocationFilter):
    def __init__(self):
        super().__init__("LEFT", lambda square: square.IsLeftColumn)


class MiddleColumnFilter(ColumnLocationFilter):
    def __init__(self):
        super().__init__("MIDDLE", lambda square: square.IsMiddleColumn)


class RightColumnFilter(ColumnLocationFilter):
    def __init__(self):
        super().__init__("RIGHT", lambda square: square.IsRightColumn)


class DiagonalLocationFilter(LocationFilter):
    def __init__(self):
        super().__init__(
            "DIAGONAL",
            "",
            lambda square: not (square.IsMiddleRow or square.IsMiddleColumn)
            or square.IsCenter,
        )


class DiagonalContentFilter(Rule):
    def __init__(self, expected_content, count):
        super().__init__("its DIAGONAL has", expected_content, count)

    def get_matches(self, board, squares):
        result = set()
        for square in squares:
            for diagonal in square.Diagonals:
                m = list(map(lambda i: board[i].Content, diagonal))
                if m.count(self.ExpectedContent) == self.Count:
                    result.add(square.Index)
                    break
        return result


class WinFilter(Rule):
    def __init__(self, content):
        super().__init__("WIN" if content == ContentType.Mine else "block OPPONENT WIN")
        self.rowRule = RowContentFilter(content, 2)
        self.columnRule = ColumnContentFilter(content, 2)
        self.diagonalRule = DiagonalContentFilter(content, 2)

    def get_matches(self, board, squares):
        in_diagonal = self.diagonalRule.get_matches(board, squares)
        if len(in_diagonal) > 0:
            return in_diagonal
        in_row = self.rowRule.get_matches(board, squares)
        if len(in_row) > 0:
            return in_row
        in_column = self.columnRule.get_matches(board, squares)
        return in_column


class DiagonalOppositeFilter(Rule):
    def __init__(self, expected_content):
        super().__init__("DIAGONAL-OPPOSITE is", expected_content)

    def get_matches(self, board, squares):
        result = set()
        for square in squares:
            if square.DiagonalOpposite is None:
                continue
            if board[square.DiagonalOpposite].Content == self.ExpectedContent:
                result.add(square.Index)
        return result


class RowOppositeFilter(Rule):
    def __init__(self, expected_content):
        super().__init__("ROW-OPPOSITE is", expected_content)

    def get_matches(self, board, squares):
        result = set()
        for square in squares:
            if square.RowOpposite is None:
                continue
            if board[square.RowOpposite].Content == self.ExpectedContent:
                result.add(square.Index)
        return result


class ColumnOppositeFilter(Rule):
    def __init__(self, expected_content):
        super().__init__("COLUMN-OPPOSITE is", expected_content)

    def get_matches(self, board, squares):
        result = set()
        for square in squares:
            if square.ColumnOpposite is None:
                continue
            if board[square.ColumnOpposite].Content == self.ExpectedContent:
                result.add(square.Index)
        return result


class CenterFilter(Rule):
    def __init__(self):
        super().__init__("is in CENTER")

    @staticmethod
    def get_matches(_, squares):
        result = set()
        for square in squares:
            if square.IsCenter:
                result.add(square.Index)
        return result


class CornerFilter(Rule):
    def __init__(self):
        super().__init__("is a CORNER")

    @staticmethod
    def get_matches(_, squares):
        result = set()
        for square in squares:
            if square.IsCorner:
                result.add(square.Index)
        return result


class SideFilter(Rule):
    def __init__(self):
        super().__init__("is SIDE")

    @staticmethod
    def get_matches(_, squares):
        result = set()
        for square in squares:
            if square.IsSide:
                result.add(square.Index)
        return result


iHaveThreeInRow = RowContentFilter(ContentType.Mine, 3)
iHaveThreeInColumn = ColumnContentFilter(ContentType.Mine, 3)
iHaveThreeInDiagonal = DiagonalContentFilter(ContentType.Mine, 3)
opponentHasTwoInARow = WinFilter(ContentType.Opponent)


class Fitness:
    def __init__(self, wins, ties, losses, gene_count):
        self.Wins = wins
        self.Ties = ties
        self.Losses = losses
        total_games = wins + ties + losses
        percent_wins = 100 * round(wins / total_games, 3)
        percent_losses = 100 * round(losses / total_games, 3)
        percent_ties = 100 * round(ties / total_games, 3)
        self.PercentTies = percent_ties
        self.PercentWins = percent_wins
        self.PercentLosses = percent_losses
        self.GeneCount = gene_count

    def __gt__(self, other):
        if self.PercentLosses != other.PercentLosses:
            return self.PercentLosses < other.PercentLosses

        if self.Losses > 0:
            return False

        if self.Ties != other.Ties:
            return self.Ties < other.Ties
        return self.GeneCount < other.GeneCount

    def __str__(self):
        return "{:.1f}% Losses ({}), {:.1f}% Ties ({}), " \
               "{:.1f}% Wins ({}), {} rules".format(
                self.PercentLosses,
                self.Losses,
                self.PercentTies,
                self.Ties,
                self.PercentWins,
                self.Wins,
                self.GeneCount,
                )
