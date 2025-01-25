from typing import Any, Type


class PickledSprite:
    def __init__(self, cls: Type, row: int, col: int, args: dict[str, Any] = None):
        self.cls: Type = cls
        self.args = args
        self.row = row
        self.col = col

    def create(self, game) -> Any:
        pos = game.get_cell_pos_(self.row, self.col)
        if self.args:
            return self.cls(game, pos, self.args)
        return self.cls(game, pos)
