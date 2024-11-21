import pygame


class Timer:
  def __init__(self, duration, action):
    self.start = pygame.time.get_ticks()
    self.duration = duration
    self.action = action
    self.active = True

  def update(self):
    if self.active:
      time = pygame.time.get_ticks()
      if time - self.start >= self.duration:
        self.active = False
        self.action()
    return self
