from io import BytesIO

import pygame
from pygame.locals import *

from app.scenes.scene import Scene
from app.sprites.text_label import TextLabel


class Scores(Scene):
    def __init__(self, app):
        super().__init__(app, pygame.sprite.RenderUpdates())

        score = app.game.score
        x_center = app.screen.get_width() / 2
        inconsolata = BytesIO(app.assets['inconsolata.otf'])
        inconsolata_14 = pygame.font.Font(inconsolata, 14)
        inconsolata.seek(0)
        inconsolata_12 = pygame.font.Font(inconsolata, 12)

        scores_text = 'Your scores: ' + str(score)
        anykey_text = 'Press any key to continue'

        self.add_label(inconsolata_14, scores_text, x_center, 200)
        self.add_label(inconsolata_12, anykey_text, x_center, 225)
        inconsolata.close()

        if score > app.records.get(app.player, 0):
            app.records[app.player] = score

    def add_label(self, font, text, x_center, y_offset, color=(222, 222, 222)):
        sprite = TextLabel(font, text, x_center, y_offset, color)
        self.sprites.add(sprite)

    def react(self, app, event):
        if event.type == KEYUP:
            alt_f4 = event.key == K_F4 and bool(event.mod & KMOD_ALT)
            if alt_f4:
                app.close()
            else:
                self.after_delay(200, app.show_menu)
        elif event.type == QUIT:
            app.close()
