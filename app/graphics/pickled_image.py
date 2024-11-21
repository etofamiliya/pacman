import pygame


class PickledImage:
  def __init__(self, image):
    self.image = image

  def __getstate__(self):
    state = self.__dict__.copy()
    state['image'] = (pygame.image.tobytes(self.image, 'RGBA'), self.image.get_size())
    return state

  def __setstate__(self, state):
    self.__dict__.update(state)
    saved_image_tuple = state['image']
    state['image'] = pygame.image.frombytes(*saved_image_tuple)
