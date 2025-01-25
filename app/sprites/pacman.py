from app.sprites.other import *
from app.pathing.directions import *
from app.sprites.sprite import Sprite
from app.sprites.tunnel import Tunnel


class Pacman(Sprite):
    def __init__(self, game, pos):
        image = game.get_image('pacman')
        super().__init__(pos, image)
        self.new_direction = None
        self.direction = RIGHT
        self.animation = None
        self.dying = False
        self.game = game
        self.speed = 0
        self.dirty = 2

    def can_move_to(self, cell, direction):
        neighbors = self.game.grid.get_neighbors(cell)
        return neighbors[direction].is_passable

    def redraw(self):
        if self.animation:
            self.image = self.animation.update()

    def kill(self):
        self.dying = True
        self.change_animation()

    def change_animation(self):
        if self.dying:
            self.animation = self.game.get_assets('pacman-dying-' + self.direction)
        else:
            self.animation = self.game.get_assets('pacman-' + self.direction)
        self.animation.rewind()

    def respawn(self):
        self.image = self.game.get_image('pacman')
        self.set_pos(self.initial_pos)
        self.new_direction = None
        self.direction = RIGHT
        self.animation = None
        self.dying = False
        self.speed = 0

    def react(self, app, event):
        if event.type == KEYDOWN:
            if event.key in key_to_direction:
                self.new_direction = key_to_direction[event.key]

    def update(self):
        if self.dying:
            if self.animation.finished:
                self.game.end_game_check()
            self.redraw()
            return

        x, y = self.get_pos()
        cell = self.game.get_cell_by_pos((x, y))
        tilesize = self.game.tilesize
        if self.new_direction:
            multiple_of = lambda v: (v % tilesize) <= self.speed
            can_turn_to = multiple_of(x) and multiple_of(y)
            can_move_to = self.can_move_to(cell, self.new_direction)

            if can_turn_to and can_move_to:
                self.direction = self.new_direction
                self.new_direction = None
                self.change_animation()
                self.speed = 3

        shift = {
            UP: (x, y - self.speed),
            DOWN: (x, y + self.speed),
            LEFT: (x - self.speed, y),
            RIGHT: (x + self.speed, y)
        }

        pacman_vec = pygame.math.Vector2((x, y))
        for sprite in self.game.sprites.sprites():
            sprite_pos = sprite.get_pos()
            sprite_vec = pygame.math.Vector2(sprite_pos)
            distance = pacman_vec.distance_to(sprite_vec)
            collided = distance <= (tilesize / 2)

            if isinstance(sprite, (Door, Wall)):
                sizes = [tilesize - self.speed] * 2
                topleft = shift[self.direction]
                rect = pygame.Rect(topleft, sizes)
                if rect.colliderect(sprite.rect):
                    shift[self.direction] = (x, y)

            if isinstance(sprite, Tunnel):
                if collided and sprite.direction == self.direction:
                    shift[self.direction] = sprite.exit_pos

            elif collided:
                self.game.on_collision(sprite)

        if self.speed:
            x, y = shift[self.direction]
            self.set_pos((x, y))
        self.redraw()
