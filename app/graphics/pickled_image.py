import pygame


class PickledImage:
  def __init__(self, image):
    self.image = image

  def __getstate__(self):
    bytes_ = pygame.image.tobytes(self.image, 'RGBA')
    size = self.image.get_size()

    state = self.__dict__.copy()
    state['image'] = (bytes_, size)
    return state

  def __setstate__(self, state):
    self.__dict__.update(state)
    bytes_, size = state['image']
    self.image = pygame.image.frombytes(bytes_, size,'RGBA')
