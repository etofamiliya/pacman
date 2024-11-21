from app.core.gametypes import GameTypes
from app.pathing.directions import *
from app.pathing.grid_cell import GridCell


class Grid:
  def __init__(self, grid, tilesize):
    rows = len(grid)
    cols = len(grid[0])
    self.grid = [[0 for _ in range(cols)] for _ in range(rows)]

    for row, line in enumerate(grid):
      for col, typ in enumerate(line):
        gametype = GameTypes.fullname(typ)
        cost = GameTypes.get_pathing_cost(gametype)
        cell = GridCell(tilesize, row, col, gametype, cost)
        self.grid[row][col] = cell

    self.tilesize = tilesize
    self.rows = rows - 1
    self.cols = cols - 1

  def get_by_pos(self, pos):
    col, row = [int(v / self.tilesize) for v in pos]
    return self.get(row, col)

  def get(self, row, col):
    if row < 0 or row > self.rows or col < 0 or col > self.cols:
      return GridCell(self.tilesize, row, col, 'tunnel', 0)
    return self.grid[row][col]

  def get_neighbors(self, cell):
    if cell.cell == 'tunnel':
      row, col = cell.row, cell.col
      impassable = lambda r, c: GridCell(self.tilesize, r, c, 'impassable', 999)
      if col < 0:
        return {
          UP: impassable(row-1, col),
          DOWN: impassable(row+1, col),
          LEFT: self.get(row, 19),
          RIGHT: self.get(row, 0)
        }
      elif col > self.cols:
        return {
          UP: impassable(row-1, col),
          DOWN: impassable(row+1, col),
          LEFT: self.get(row, 18),
          RIGHT: self.get(row, -1)
        }
      return {}

    row, col = cell.row, cell.col
    neighbors = {
      UP: self.get(row - 1, col),
      DOWN: self.get(row + 1, col),
      LEFT: self.get(row, col - 1),
      RIGHT: self.get(row, col + 1)
    }
    return neighbors

  def pathfind(self, start_pos, goal_pos):
    for line in self.grid:
      [cell.reset() for cell in line]

    start = self.get_by_pos(start_pos)
    goal = self.get_by_pos(goal_pos)

    manhattan = lambda s, g: abs(s.row - g.row) + abs(s.col - g.col)
    start.h = manhattan(start, goal)
    start.f = start.h

    closed = []
    opened = [start]

    while opened:
      opened = sorted(opened, key = lambda cel: cel.f)
      cell = opened.pop(0)
      closed.append(cell)
      if cell == goal:
        path = []
        while cell:
          path.insert(0, cell)
          cell = cell.parent
        return path

      neighbors = self.get_neighbors(cell)
      for neighbor in list(neighbors.values()):
        if neighbor not in closed:
          newg = cell.g + neighbor.cost

          if neighbor not in opened:
            opened.append(neighbor)
          elif newg >= neighbor.g:
            continue

          neighbor.g = newg
          neighbor.h = manhattan(neighbor, goal)
          neighbor.f = neighbor.g + neighbor.h
          neighbor.parent = cell

    return []
