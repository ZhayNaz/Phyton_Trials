from enum import Enum

TABLE_SIZE = 5

class Direction(str, Enum):
    NORTH = "NORTH"
    EAST = "EAST"
    SOUTH = "SOUTH"
    WEST = "WEST"

DIRECTION_ORDER = [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]

class Robot:
    def __init__(self):
        self.x = None
        self.y = None
        self.face = None

    def is_placed(self):
        return self.x is not None and self.y is not None and self.face is not None

    def place(self, x: int, y: int, face: Direction):
        if 0 <= x < TABLE_SIZE and 0 <= y < TABLE_SIZE:
            self.x, self.y, self.face = x, y, face
        else:
            raise ValueError("Invalid placement: outside table bounds")

    def move(self):
        if not self.is_placed():
            return
        dx, dy = 0, 0
        if self.face == Direction.NORTH:
            dy = 1
        elif self.face == Direction.SOUTH:
            dy = -1
        elif self.face == Direction.EAST:
            dx = 1
        elif self.face == Direction.WEST:
            dx = -1

        new_x, new_y = self.x + dx, self.y + dy
        if 0 <= new_x < TABLE_SIZE and 0 <= new_y < TABLE_SIZE:
            self.x, self.y = new_x, new_y

    def left(self):
        if not self.is_placed():
            return
        idx = DIRECTION_ORDER.index(self.face)
        self.face = DIRECTION_ORDER[(idx - 1) % 4]

    def right(self):
        if not self.is_placed():
            return
        idx = DIRECTION_ORDER.index(self.face)
        self.face = DIRECTION_ORDER[(idx + 1) % 4]

    def report(self):
        if not self.is_placed():
            return None
        return {"x": self.x, "y": self.y, "face": self.face}
