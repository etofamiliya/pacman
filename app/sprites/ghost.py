import pygame

from random import shuffle

from app.sprites.ghost_mode import *
from app.pathing.directions import *
from app.sprites.tunnel import Tunnel
from app.sprites.sprite import Sprite
from app.sprites.ghost_action import *
from app.pathing.grid_cell import GridCell
from app.sprites.timed_sprite import TimedSprite
from app.graphics.pickled_image import PickledImage


class Ghost(Sprite):
    def __init__(self, game, pos, args):
        name = args['name']
        image = game.get_image(name)
        super().__init__(pos, image)
        self.new_direction = True
        self.direction = RIGHT
        self.animation = None
        self.action = IDLE
        self.game = game
        self.name = name
        self.mode = INIT
        self.timers = []
        self.speed = 0
        self.dirty = 2
        self.path = []

    def is_at_home(self):
        return self.get_pos() == self.get_home_pos()

    def get_home_pos(self):
        if self.name == 'blinky':
            return self.game.ghosts['pinky'].initial_pos
        return self.initial_pos

    def is_vulnerable(self):
        return self.mode is FRIGHTENED and self.action is not GOING_HOME

    def change_animation(self):
        animation_name = self.name + '-' + self.direction
        if self.mode is FRIGHTENED:
            actions = {
                BLINKING: 'ghost-blinking',
                WALKING: 'ghost-frightened',
                GOING_HOME: 'eyes-' + self.direction,
            }
            animation_name = actions[self.action]
        self.animation = self.game.get_assets(animation_name)
        self.animation.rewind()

    def redraw(self):
        self.image = self.animation.update()

    def change_direction(self, direction):
        self.direction = direction
        self.change_animation()

    def pathfind(self, goal_pos):
        start = self.game.get_cell_by_pos(self.get_pos())
        goal = self.game.get_cell_by_pos(goal_pos)
        self.game.pathfind(self, start, goal)

    def follow_path(self, path: list[GridCell]):
        self.path = path

    def step_to_random_direction(self, neighbors) -> list[GridCell]:
        directions = list(neighbors.keys())
        shuffle(directions)

        for new_direction in directions:
            if new_direction == opposite_direction[self.direction]:
                continue

            neighbor = neighbors.get(new_direction)
            if neighbor and neighbor.is_passable:
                return [neighbor]
        return []

    def change_action(self, action):
        self.action = action
        self.change_animation()

    def send_to_home(self):
        self.change_action(GOING_HOME)
        self.reset_timers()
        self.speed = 5

    def animate(self):
        self.reset()
        self.switch_mode()

    def add_timer(self, duration, action):
        self.timers.append(self.game.after_delay(duration, action))

    def reset_timers(self):
        for tm in self.timers:
            tm.active = False
        self.timers = []

    def switch_mode(self):
        if self.mode is SCATTERING:
            self.add_timer(5000, self.switch_mode)
            self.mode = CHASING
        else:
            self.mode = SCATTERING
            self.add_timer(4000, self.switch_mode)

        self.change_action(WALKING)
        self.speed = 3

    def frighten(self):
        if self.action == GOING_HOME:
            return

        self.reset_timers()
        blink = lambda: self.change_action(BLINKING)
        self.add_timer(8000, self.switch_mode)
        self.add_timer(6500, blink)
        self.mode = FRIGHTENED
        self.change_action(WALKING)
        self.path = self.path[:1]
        self.speed = 2

    def reset(self):
        self.mode = INIT
        self.change_action(IDLE)
        self.reset_timers()
        self.speed = 0
        self.path = []

    def update(self):
        grid = self.game.grid

        x, y = self.get_pos()
        position = pygame.math.Vector2((x, y))
        ghost_cell = self.game.get_cell_by_pos((x, y))
        neighbors = grid.get_neighbors(ghost_cell)

        if self.path:
            target_cell = self.path[0]

            if self.new_direction:
                for new_direction in neighbors:
                    if neighbors[new_direction] == target_cell:
                        self.change_direction(new_direction)
                        self.new_direction = False
                        break

            target_x, target_y = self.game.get_cell_pos(target_cell)
            destination = pygame.math.Vector2(target_x, target_y)

            direction = destination - position
            distance = direction.length()
            if distance:
                speed = min(float(self.speed), distance)
                shift = direction.normalize() * speed
                shift = pygame.math.Vector2([round(v) for v in shift])
                if abs(shift.x) < abs(shift.y):
                    shift.x = 0
                else:
                    shift.y = 0

                newpos = (position + shift)
                self.set_pos(newpos)
            else:
                tunnels = self.game.get_sprites_of_class(Tunnel)
                for tunnel in tunnels:
                    collided = tunnel.rect.contains(self.rect)
                    if collided and tunnel.direction == self.direction:
                        self.set_pos(tunnel.exit_pos)
                        break

                self.new_direction = True
                self.path.pop(0)

        else:
            self.path += self.step_to_random_direction(neighbors)

            if self.mode is FRIGHTENED:
                if self.action is GOING_HOME:
                    if self.is_at_home():
                        self.animate()
                        blinky = self.game.ghosts['blinky']
                        self.pathfind(blinky.initial_pos)
                    else:
                        self.pathfind(self.get_home_pos())

            elif self.mode is SCATTERING:
                if self.is_at_home():
                    blinky = self.game.ghosts['blinky']
                    self.pathfind(blinky.initial_pos)

            elif self.mode is CHASING:
                self.pathfind(self.game.pacman.get_pos())
        self.redraw()

