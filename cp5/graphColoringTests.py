import csv


def load_data(localFileName):
    """ expects: AA,BB;CC where BB and CC are the initial column values in
     other rows
    """
    with open(localFileName, mode='r') as infile:
        reader = csv.reader(infile)
        lookup = {row[0]: row[1].split(';') for row in reader if row}
    return lookup


class Rule:
    Node = None
    Adjacent = None

    def __init__(self, node, adjacent):
        if node < adjacent:
            node, adjacent = adjacent, node
        self.Node = node
        self.Adjacent = adjacent
