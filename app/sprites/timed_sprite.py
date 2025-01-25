from app.core.timer import Timer
from app.sprites.sprite import Sprite


class TimedSprite(Sprite):
    def __init__(self, game, pos, name, duration):
        image = game.get_image(name)
        super().__init__(pos, image)
        self.timer = Timer(duration, self.kill)
        self.update = self.timer.update
        self.dirty = 2
