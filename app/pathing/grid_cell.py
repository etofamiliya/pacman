
class GridCell:
  def __init__(self, tilesize, row, col, cell, cost):
    self.tilesize = tilesize
    self.parent = None
    self.cell = cell
    self.cost = cost
    self.row = row
    self.col = col
    self.g = 0
    self.h = 0
    self.f = 0

  def get_pos(self):
    return self.col * self.tilesize, self.row * self.tilesize

  def __eq__(self, other):
    return (self.row == other.row) and (self.col == other.col)

  def reset(self):
    self.parent = None
    self.g = 0
    self.h = 0
    self.f = 0