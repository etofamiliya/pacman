import threading
from typing import Union

from app.pathing.directions import *
from app.pathing.grid_cell import GridCell


class Grid:
    def __init__(self):
        self.cells: dict[str, GridCell] = {}
        self.pathing_lock = threading.Lock()

    def set(self, row, col, cost: int, neighbors: dict = None):
        key = f'{row} {col}'
        self.cells[key] = GridCell(row, col, cost, neighbors)

    def get(self, row, col) -> GridCell:
        key = f'{row} {col}'
        return self.cells.get(key, GridCell.impassable_at(row, col))

    def get_neighbors(self, cell: GridCell) -> dict[str, GridCell]:
        if len(cell.neighbors) == len(ALL_DIRECTIONS):
            return cell.neighbors

        row, col = cell
        neighbors = {
            UP: self.get(row - 1, col),
            DOWN: self.get(row + 1, col),
            LEFT: self.get(row, col - 1),
            RIGHT: self.get(row, col + 1)
        }
        neighbors.update(cell.neighbors)
        cell.neighbors.update(neighbors)
        return cell.neighbors

    def pathfind(self, start, goal) -> list:
        with self.pathing_lock:
            return self.pathfind_(start, goal)

    def pathfind_(self, start, goal) -> list:
        for cell in self.cells.values():
            cell.reset()

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
            for neighbor in neighbors.values():
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