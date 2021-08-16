import datetime
import random
import sys
import unittest

from genetic_algorithms.utils import genetic


class KnapsackTests(unittest.TestCase):
    def test_cookies(self):
        items = [
            Resource("Flour", 1680, 0.265, 0.41),
            Resource("Butter", 1440, 0.5, 0.13),
            Resource("Sugar", 1840, 0.441, 0.29),
        ]
        max_weight = 10
        max_volume = 4

        optimal = get_fitness(
            [
                ItemQuantity(items[0], 1),
                ItemQuantity(items[1], 14),
                ItemQuantity(items[2], 6),
            ]
        )
        self.fill_knapsack(items, max_weight, max_volume, optimal)

    def test_exnsd16(self):
        problem_info = load_data("exnsd16.ukp")
        items = problem_info.Resources
        max_weight = problem_info.max_weight
        max_volume = 0
        optimal = get_fitness(problem_info.Solution)
        self.fill_knapsack(items, max_weight, max_volume, optimal)

    def fill_knapsack(self, items, max_weight, max_volume, optimal_fitness):
        start_time = datetime.datetime.now()
        window = Window(1, max(1, int(len(items) / 3)), int(len(items) / 2))
        sorted_items = sorted(items, key=lambda item: item.Value)

        def fnDisplay(candidate):
            display(candidate, start_time)

        def fnGetFitness(genes):
            return get_fitness(genes)

        def fnCreate():
            return create(items, max_weight, max_volume)

        def fnMutate(genes):
            mutate(genes, sorted_items, max_weight, max_volume, window)

        best = genetic.get_best(
            fnGetFitness,
            None,
            optimal_fitness,
            None,
            fnDisplay,
            fnMutate,
            fnCreate,
            max_age=50,
        )
        self.assertTrue(not optimal_fitness > best.Fitness)


class Window:
    Min = None
    Max = None
    Size = None

    def __init__(self, minimum, maximum, size):
        self.Min = minimum
        self.Max = maximum
        self.Size = size

    def slide(self):
        self.Size = self.Size - 1 if self.Size > self.Min else self.Max


class Resource:
    Name = None
    Value = None
    Weight = None
    Volume = None

    def __init__(self, name, value, weight, volume):
        self.Name = name
        self.Value = value
        self.Weight = weight
        self.Volume = volume


class ItemQuantity:
    Item = None
    Quantity = None

    def __init__(self, item, quantity):
        self.Item = item
        self.Quantity = quantity

    def __eq__(self, other):
        return self.Item == other.Item and self.Quantity == other.Quantity


class Fitness:
    total_weight = None
    total_volume = None
    total_value = None

    def __init__(self, total_weight, total_volume, total_value):
        self.total_weight = total_weight
        self.total_volume = total_volume
        self.total_value = total_value

    def __gt__(self, other):
        return self.total_value > other.total_value

    def __str__(self):
        return "wt: {0:0.2f} vol: {1:0.2f} value: {2}".format(
            self.total_weight, self.total_volume, self.total_value
        )


def max_quantity(item, max_weight, max_volume):
    return min(
        int(max_weight / item.Weight) if item.Weight > 0 else sys.maxsize,
        int(max_volume / item.Volume) if item.Volume > 0 else sys.maxsize,
    )


def mutate(genes, items, max_weight, max_volume, window):
    window.slide()
    fitness = get_fitness(genes)
    remaining_weight = max_weight - fitness.total_weight
    remaining_volume = max_volume - fitness.total_volume

    removing = len(genes) > 1 and random.randint(0, 10) == 0
    if removing:
        index = random.randrange(0, len(genes))
        iq = genes[index]
        item = iq.Item
        remaining_weight += item.Weight * iq.Quantity
        remaining_volume += item.Volume * iq.Quantity
        del genes[index]

    adding = (remaining_weight > 0 or remaining_volume > 0) and (
        len(genes) == 0 or (len(genes) < len(items) and random.randint(0, 100) == 0)
    )
    if adding:
        new_gene = add(genes, items, remaining_weight, remaining_volume)
        if new_gene is not None:
            genes.append(new_gene)
            return

    index = random.randrange(0, len(genes))
    iq = genes[index]
    item = iq.Item
    remaining_weight += item.Weight * iq.Quantity
    remaining_volume += item.Volume * iq.Quantity
    change_item = len(genes) < len(items) and random.randint(0, 4) == 0
    if change_item:
        item_index = items.index(iq.Item)
        start = max(1, item_index - window.Size)
        stop = min(len(items) - 1, item_index + window.Size)
        item = items[random.randint(start, stop)]
    max_qty = max_quantity(item, remaining_weight, remaining_volume)
    if max_qty > 0:
        genes[index] = ItemQuantity(
            item, max_qty if (window.Size > 1) else random.randint(1, max_qty)
        )
    else:
        del genes[index]


def add(genes, items, max_weight, max_volume):
    used_items = {iq.Item for iq in genes}
    item = random.choice(items)
    while item in used_items:
        item = random.choice(items)
    max_qty = max_quantity(item, max_weight, max_volume)
    return ItemQuantity(item, max_qty) if max_qty > 0 else None


def create(items, max_weight, max_volume):
    genes = []
    remaining_weight, remaining_volume = max_weight, max_volume
    for i in range(random.randrange(1, len(items))):
        new_gene = add(genes, items, remaining_weight, remaining_volume)
        if new_gene is not None:
            genes.append(new_gene)
            remaining_weight -= new_gene.Quantity * new_gene.Item.Weight
            remaining_volume -= new_gene.Quantity * new_gene.Item.Volume
    return genes


def get_fitness(genes):
    total_weight = 0
    total_volume = 0
    total_value = 0
    for iq in genes:
        count = iq.Quantity
        total_weight += iq.Item.Weight * count
        total_volume += iq.Item.Volume * count
        total_value += iq.Item.Value * count
    return Fitness(total_weight, total_volume, total_value)


def display(candidate, start_time):
    time_diff = datetime.datetime.now() - start_time
    genes = candidate.Genes[:]
    genes.sort(key=lambda iq: iq.Quantity, reverse=True)
    descriptions = [str(iq.Quantity) + "x" + iq.Item.Name for iq in genes]
    if len(descriptions) == 0:
        descriptions.append("Empty")
    print(
        "{0}\t{1}\t{2}".format(
            ", ".join(descriptions), candidate.Fitness, str(time_diff)
        )
    )


class KnapsackProblemData:

    Resources = None
    max_weight = None
    Solution = None

    def __init__(self):
        self.Resources = []
        self.max_weight = 0
        self.Solution = []


def load_data(local_file_name):
    with open(local_file_name, mode="r") as infile:
        lines = infile.read().splitlines()

    data = KnapsackProblemData()
    f = find_constraint

    for line in lines:
        f = f(line.strip(), data)
        if f is None:
            break
    return data


def find_constraint(line, data):
    parts = line.split(" ")
    if parts[0] != "c:":
        return find_constraint
    data.max_weight = int(parts[1])
    return find_data_start


def find_data_start(line, data):
    if line != "begin data":
        return find_data_start
    return read_resource_or_find_data_end


def read_resource_or_find_data_end(line, data):
    if line == "end data":
        return find_solution_start
    parts = line.split("\t")
    resource = Resource(
        "R" + str(1 + len(data.Resources)), int(parts[1]), int(parts[0]), 0
    )
    data.Resources.append(resource)
    return read_resource_or_find_data_end


def find_solution_start(line, data):
    if line == "sol:":
        return read_solution_resource_or_find_solution_end
    return find_solution_start


def read_solution_resource_or_find_solution_end(line, data):
    if line == "":
        return None
    parts = [p for p in line.split("\t") if p != ""]
    resource_index = int(parts[0]) - 1  # make it 0 based
    resource_quantity = int(parts[1])
    data.Solution.append(
        ItemQuantity(data.Resources[resource_index], resource_quantity)
    )
    return read_solution_resource_or_find_solution_end
