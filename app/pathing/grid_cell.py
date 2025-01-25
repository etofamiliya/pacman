PASSABLE_CELL_COST = 1
IMPASSABLE_CELL_COST = 999

class GridCell:
    def __init__(self, row: int, col: int, cost: int, neighbors: dict = None):
        self.neighbors = neighbors or {}
        self.parent = None
        self.cost = cost
        self.row = row
        self.col = col
        self.g = 0
        self.h = 0
        self.f = 0

    def __iter__(self):
        yield self.row
        yield self.col

    def __eq__(self, other):
        return (self.row == other.row) and (self.col == other.col)

    @property
    def is_passable(self):
        return self.cost <= PASSABLE_CELL_COST

    def reset(self):
        self.parent = None
        self.g = 0
        self.h = 0
        self.f = 0

    @classmethod
    def impassable_at(cls, row, col):
        return GridCell(row, col, IMPASSABLE_CELL_COST)