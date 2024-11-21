from pygame.locals import *
from app.core.event_handler import EventHandler


class Scene:
  def __init__(self, app, sprites):
    self.app = app
    self.sprites = sprites
    self.full_redraw = True
    self.events = EventHandler(app)
    self.events.add_observer(self, KEYDOWN, KEYUP, QUIT)

  def get_rendering_area(self):
    if self.full_redraw:
      self.full_redraw = False
      return self.app.screen.get_rect()
    return self.sprites.draw(self.app.screen)

  def update(self):
    self.events.handle()
    self.sprites.update()
    return self.get_rendering_area()
