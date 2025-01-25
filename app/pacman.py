# etofamiliya, 2017-2025

import os.path
import contextlib

with contextlib.redirect_stdout(None):
    import pygame.gfxdraw

from core.app import App

if __name__ == '__main__':
    pygame.init()
    pygame.mixer.init()
    pygame.key.set_repeat(150, 1)
    pygame.mouse.set_visible(False)
    pygame.display.set_caption('Pacman')
    os.environ["SDL_VIDEO_CENTERED"] = '1'

    App().launch()

    pygame.mixer.quit()
    pygame.quit()