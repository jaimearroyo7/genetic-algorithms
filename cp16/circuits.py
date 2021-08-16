class Not:
    def __init__(self, _input):
        self._input = _input

    def get_output(self):
        if self._input is None:
            return None
        value = self._input.get_output()
        if value is None:
            return None
        return not value

    def __str__(self):
        if self._input is None:
            return "Not(?)"
        return "Not({})".format(self._input)

    @staticmethod
    def input_count():
        return 1


class GateWith2Inputs:
    def __init__(self, input_a, input_b, label, fn_test):
        self._input_a = input_a
        self._input_b = input_b
        self._label = label
        self._fnTest = fn_test

    def get_output(self):
        if self._input_a is None or self._input_b is None:
            return None
        a_value = self._input_a.get_output()
        if a_value is None:
            return None
        b_value = self._input_b.get_output()
        if b_value is None:
            return None
        return self._fnTest(a_value, b_value)

    def __str__(self):
        if self._input_a is None or self._input_b is None:
            return "{}(?)".format(self._label)
        return "{}({} {})".format(self._label, self._input_a, self._input_b)

    @staticmethod
    def input_count():
        return 2


class And(GateWith2Inputs):
    def __init__(self, input_a, input_b):
        super().__init__(input_a, input_b, type(self).__name__, lambda a, b: a and b)


class Or(GateWith2Inputs):
    def __init__(self, input_a, input_b):
        super().__init__(input_a, input_b, type(self).__name__, lambda a, b: a or b)


class Xor(GateWith2Inputs):
    def __init__(self, input_a, input_b):
        super().__init__(input_a, input_b, type(self).__name__, lambda a, b: a != b)


class Source:
    def __init__(self, source_id, source_container):
        self._source_id = source_id
        self._source_container = source_container

    def get_output(self):
        return self._source_container[self._source_id]

    def __str__(self):
        return self._source_id

    @staticmethod
    def input_count():
        return 0
