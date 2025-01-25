import pygame.sprite

class Sprite(pygame.sprite.DirtySprite):
    def __init__(self, pos, image):
        super().__init__()
        self.rect = image.get_rect()
        self.rect.topleft = pos
        self.initial_pos = pos
        self.image = image

    def get_pos(self):
        return self.rect.topleft

    def set_pos(self, newpos):
        self.rect.topleft = newpos

    def react(self, app, event):
        pass
