from app.sprites.other import *
from app.sprites.ghost import Ghost
from app.sprites.pacman import Pacman
from app.sprites.tunnel import Tunnel


class GameTypes:
    '''
      Pacman      = 10
      Ghost       = 9
      TimedSprite = 8
      Fruit       = 7
      Energizer   = 6
      Dot         = 5
      Wall        = 4
      Door        = 3
      Tunnel      = 2
    '''
    layers = {
        TimedSprite: 8,
        Energizer: 6,
        Pacman: 10,
        Tunnel: 2,
        Ghost: 9,
        Fruit: 7,
        Wall: 4,
        Door: 3,
        Dot: 5
    }

    @classmethod
    def get_layer(cls, sprite_class) -> int:
        return cls.layers.get(sprite_class)