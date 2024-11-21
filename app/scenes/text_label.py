import pygame

from app.sprites.sprite import Sprite


class TextLabel(Sprite):
  def __init__(self, font, text, x_center, y_offset, color):
    super().__init__((0, 0), pygame.Surface((0, 0)))
    self.redraw = lambda t: font.render(t, True, color)
    self.newpos = lambda i: (x_center - (i.get_width() / 2), y_offset)
    self.set_text(text)

  def set_text(self, text):
    self.image = self.redraw(text)
    self.set_pos(self.newpos(self.image))
    self.text = text
