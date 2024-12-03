import pygame

from app.sprites.sprite import Sprite
from app.sprites.ghost_action import *
from app.sprites.ghost_mode import *
from app.pathing.directions import *
from random import shuffle


class Ghost(Sprite):
  def __init__(self, pos, app, name):
    image = app.get_image(name)
    super().__init__(pos, image)
    self.new_direction = True
    self.direction = RIGHT
    self.animation = None
    self.game = app.game
    self.action = IDLE
    self.name = name
    self.mode = INIT
    self.timers = []
    self.speed = 0
    self.dirty = 2
    self.app = app
    self.path = []

  def is_at_home(self):
    return self.get_pos() == self.get_home_pos()

  def get_home_pos(self):
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
    self.animation = self.app.assets[animation_name]
    self.animation.rewind()

  def redraw(self):
    self.image = self.animation.update()

  def change_direction(self, direction):
    self.direction = direction
    self.change_animation()

  def pathfind(self, goal_pos):
    return self.game.grid.pathfind(self.get_pos(), goal_pos)

  def make_one_step(self, neighbors):
    directions = list(neighbors.keys())
    shuffle(directions)

    for new_direction in directions:
      if new_direction == opposite_direction[self.direction]:
        continue

      neighbor = neighbors.get(new_direction)
      if neighbor and self.is_walkable(neighbor):
        self.path = [neighbor]
        break

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
    self.timers.append(self.app.after_delay(duration, action))

  def reset_timers(self):
    for tm in self.timers:
      tm.active = False
    self.timers = []

  def switch_mode(self):
    if self.mode is SCATTERING:
      self.mode = CHASING
    else:
      self.mode = SCATTERING

    self.add_timer(5000, self.switch_mode)
    self.change_action(WALKING)
    self.path = self.path[:1]
    self.speed = 3

  def frighten(self):
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
    grid = self.app.game.grid

    x, y = self.get_pos()
    position = pygame.math.Vector2((x, y))
    ghost_cell = grid.get_by_pos((x, y))
    neighbors = grid.get_neighbors(ghost_cell)

    if self.path:
      target_cell = self.path[0]

      if self.new_direction:
        for new_direction in neighbors:
          if neighbors[new_direction] == target_cell:
            self.change_direction(new_direction)
            self.new_direction = False
            break

      target_x, target_y = target_cell.get_pos()
      destination = pygame.math.Vector2(target_x, target_y)

      direction = destination - position
      distance = direction.length()
      if distance:
        speed = min(self.speed, distance)
        shift = direction.normalize() * speed
        shift.xy = [round(v) for v in shift]
        if abs(shift.x) < abs(shift.y):
          shift.x = 0
        else:
          shift.y = 0

        newpos = (position + shift)
        self.set_pos(newpos)
      else:
        if target_cell.cell == 'tunnel':
          neighbors = grid.get_neighbors(target_cell)
          ghost_cell = neighbors[self.direction]
          x, y = ghost_cell.get_pos()
          self.set_pos((x, y))

        self.new_direction = True
        self.path.pop(0)

    else:
      if self.mode is FRIGHTENED:
        if self.action is GOING_HOME:
          if self.is_at_home():
            self.animate()
          else:
            self.path = self.pathfind(self.get_home_pos())
        else:
          self.make_one_step(neighbors)

      elif self.mode is SCATTERING:
        if self.is_at_home():
          blinky = self.app.game.ghosts['blinky']
          self.path = self.pathfind(blinky.initial_pos)
        else:
          self.make_one_step(neighbors)

      elif self.mode is CHASING:
        self.path = self.pathfind(self.game.pacman.get_pos())
    self.redraw()
