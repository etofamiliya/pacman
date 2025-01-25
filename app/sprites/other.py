import pygame

from app.sprites.sprite import Sprite
from app.sprites.timed_sprite import TimedSprite


class Fruit(TimedSprite):
    def __init__(self, game, pos, name, duration):
        super().__init__(game, pos, name, duration)


class Dot(Sprite):
    def __init__(self, game, pos):
        image = game.get_image('dot')
        super().__init__(pos, image)


class Wall(Sprite):
    def __init__(self, game, pos):
        sizes = [game.tilesize] * 2
        image = pygame.Surface(sizes)
        image.fill((0, 50, 80))
        super().__init__(pos, image)


class Door(Sprite):
    def __init__(self, game, pos):
        tsize = game.tilesize
        image = pygame.Surface((tsize, tsize))
        door = pygame.Rect(0, tsize/4, tsize, tsize/2)
        image.fill((0, 50, 80), door)
        super().__init__(pos, image)


class Energizer(Sprite):
    def __init__(self, game, pos):
        image = game.get_image('energizer')
        super().__init__(pos, image)
        self.game = game
        self.blink()

    def blink(self):
        self.game.after_delay(350, self.blink)
        self.visible = not self.visible