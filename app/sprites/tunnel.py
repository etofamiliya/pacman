import pygame

from app.sprites.sprite import Sprite


class Tunnel(Sprite):
    def __init__(self, game, pos, args):
        sizes = [game.tilesize] * 2
        image = pygame.Surface(sizes)
        super().__init__(pos, image)
        exit_cell = args['exit_cell']
        self.direction = args['direction']
        self.exit_pos = game.get_cell_pos_(*exit_cell)

