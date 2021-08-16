from enum import Enum


class FieldContents(Enum):
    Grass = " #"
    Mowed = " ."
    Mower = "M"

    def __str__(self):
        return self.value


class Direction:
    def __init__(self, index, x_offset, y_offset, symbol):
        self.Index = index
        self.X_offset = x_offset
        self.Y_offset = y_offset
        self.Symbol = symbol

    def move_from(self, location, distance=1):
        return Location(
            location.X + distance * self.X_offset, location.Y + distance * self.Y_offset
        )


class Directions(Enum):
    North = Direction(0, 0, -1, "^")
    East = Direction(1, 1, 0, ">")
    South = Direction(2, 0, 1, "v")
    West = Direction(3, -1, 0, "<")

    @staticmethod
    def get_direction_after_turn_left_90_degrees(direction):
        new_index = direction.Index - 1 if direction.Index > 0 else len(Directions) - 1
        new_direction = next(i for i in Directions if i.value.Index == new_index)
        return new_direction.value

    @staticmethod
    def get_direction_after_turn_right_90_degrees(direction):
        new_index = direction.Index + 1 if direction.Index < len(Directions) - 1 else 0
        new_direction = next(i for i in Directions if i.value.Index == new_index)
        return new_direction.value


class Location:
    def __init__(self, x, y):
        self.X, self.Y = x, y

    def move(self, x_offset, y_offset):
        return Location(self.X + x_offset, self.Y + y_offset)


class Mower:
    def __init__(self, location, direction):
        self.Location = location
        self.Direction = direction
        self.StepCount = 0

    def turn_left(self):
        self.StepCount += 1
        self.Direction = Directions.get_direction_after_turn_left_90_degrees(
            self.Direction
        )

    def mow(self, field):
        new_location = self.Direction.move_from(self.Location)
        new_location, is_valid = field.fix_location(new_location)
        if is_valid:
            self.Location = new_location
            self.StepCount += 1
            field.set(
                self.Location,
                self.StepCount if self.StepCount > 9 else " {}".format(self.StepCount),
            )

    def jump(self, field, forward, right):
        new_location = self.Direction.move_from(self.Location, forward)
        right_direction = Directions.get_direction_after_turn_right_90_degrees(
            self.Direction
        )
        new_location = right_direction.move_from(new_location, right)
        new_location, is_valid = field.fix_location(new_location)
        if is_valid:
            self.Location = new_location
            self.StepCount += 1
            field.set(
                self.Location,
                self.StepCount if self.StepCount > 9 else " {}".format(self.StepCount),
            )


class Field:
    def __init__(self, width, height, initial_content):
        self.Field = [[initial_content] * width for _ in range(height)]
        self.Width = width
        self.Height = height

    def set(self, location, symbol):
        self.Field[location.Y][location.X] = symbol

    def count_mowed(self):
        return sum(
            1
            for row in range(self.Height)
            for column in range(self.Width)
            if self.Field[row][column] != FieldContents.Grass
        )

    def display(self, mower):
        for rowIndex in range(self.Height):
            if rowIndex != mower.Location.Y:
                row = " ".join(map(str, self.Field[rowIndex]))
            else:
                r = self.Field[rowIndex][:]
                r[mower.Location.X] = "{}{}".format(
                    FieldContents.Mower, mower.Direction.Symbol
                )
                row = " ".join(map(str, r))
            print(row)


class ValidatingField(Field):
    def __init__(self, width, height, initial_content):
        super().__init__(width, height, initial_content)

    def fix_location(self, location):
        if (
            location.X >= self.Width
            or location.X < 0
            or location.Y >= self.Height
            or location.Y < 0
        ):
            return None, False
        return location, True


class ToroidField(Field):
    def __init__(self, width, height, initial_content):
        super().__init__(width, height, initial_content)

    def fix_location(self, location):
        new_location = Location(location.X, location.Y)
        if new_location.X < 0:
            new_location.X += self.Width
        elif new_location.X >= self.Width:
            new_location.X %= self.Width

        if new_location.Y < 0:
            new_location.Y += self.Height
        elif new_location.Y >= self.Height:
            new_location.Y %= self.Height

        return new_location, True
