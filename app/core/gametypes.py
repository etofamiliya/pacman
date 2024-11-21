from app.sprites.other import *
from app.sprites.ghosts import *
from app.sprites.pacman import Pacman


class GameTypes:
  pacman_layer = 6
  ghosts_layer = 5
  timed_layer  = 4
  walls_layer  = 3
  dots_layer   = 2
  door_layer   = 1

  @staticmethod
  def fullname(char):
    converter = {
      'e': 'energizer',
      'p': 'pacman',
      'b': 'blinky',
      'c': 'clyde',
      'n': 'pinky',
      'i': 'inky',
      'o': 'door',
      'w': 'wall',
      'd': 'dot'
    }
    return converter.get(char, '')

  @classmethod
  def layer(cls, gametype):
    layers = {
      'energizer': cls.dots_layer,
      'pacman': cls.pacman_layer,
      'blinky': cls.ghosts_layer,
      'clyde': cls.ghosts_layer,
      'pinky': cls.ghosts_layer,
      'inky': cls.ghosts_layer,
      'wall': cls.walls_layer,
      'door': cls.door_layer,
      'dot': cls.dots_layer
    }
    return layers.get(gametype, 0)

  @staticmethod
  def get_pathing_cost(gametype):
    costs = {
      'default': 1,
      'wall': 100
    }
    return costs.get(gametype, 1)

  @staticmethod
  def create(gametype, pos, app):
    factory = {
      'energizer': Energizer,
      'pacman': Pacman,
      'blinky': Blinky,
      'clyde': Clyde,
      'pinky': Pinky,
      'inky': Inky,
      'door': Door,
      'wall': Wall,
      'dot': Dot
    }
    return factory[gametype](pos, app)
