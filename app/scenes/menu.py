import pygame
from io import BytesIO
from pygame.locals import *
from app.scenes.scene import Scene
from app.scenes.text_label import TextLabel


class Menu(Scene):
  def __init__(self, app):
    super().__init__(app, pygame.sprite.RenderUpdates())
    app.player = ''

    x_center = app.screen.get_width() / 2

    firenight = BytesIO(app.assets['firenight.otf'])
    firenight_60 = pygame.font.Font(firenight, 60)
    firenight.seek(0)
    firenight_36 = pygame.font.Font(firenight, 36)

    inconsolata = BytesIO(app.assets['inconsolata.otf'])
    inconsolata_18 = pygame.font.Font(inconsolata, 18)
    inconsolata.seek(0)
    inconsolata_14 = pygame.font.Font(inconsolata, 14)
    inconsolata.seek(0)
    inconsolata_12 = pygame.font.Font(inconsolata, 12)

    self.add_label(firenight_60, 'Pacman', x_center, 15, (255, 255, 0))
    self.add_label(firenight_36, 'Records', x_center, 150, (255, 0, 0))

    records = sorted(list(app.records.items()), key=lambda z: z[1], reverse=True)
    for z, (name, scores) in enumerate(records[:5]):
      scores = str(scores).ljust(5)
      record_txt = '{}) {}  {}'.format(z+1, name.ljust(12), scores)
      self.add_label(inconsolata_18, record_txt, x_center, 200 + z * 20)

    invite_text = 'Type your name to start:'
    self.add_label(inconsolata_14, invite_text, x_center, 350)

    ibx = self.add_label(inconsolata_14, '____________', x_center, 390)
    self.input_box = ibx
    self.input_box.react = self.input_box_react
    self.events.add_observer(ibx, KEYUP)

    arrows_text = "Use Arrow keys to control Pacman's movement."
    self.add_label(inconsolata_14, arrows_text, x_center, 510)

    exit_text = 'Press Alt + F4 or Esc to Exit.'
    self.add_label(inconsolata_14, exit_text, x_center, 540)

    footer_text = 'etofamiliya 2017-2024'
    self.add_label(inconsolata_12, footer_text, x_center, 590)

    # inconsolata.close()
    # firenight.close()

  def react(self, app, event):
    if event.type == KEYDOWN:
      alt_f4 = event.key == K_F4 and bool(event.mod & KMOD_ALT)
      escape = event.key == K_ESCAPE
      if escape or alt_f4:
        app.close()
    elif event.type == QUIT:
      app.close()

  def input_box_react(self, app, event):
    if event.key in [K_RETURN, K_KP_ENTER]:
      if len(app.player):
        app.after_delay(200, app.show_game)

    elif event.key == K_BACKSPACE:
      app.player = app.player[:-1]
    else:
      char = event.unicode
      if char.isalnum():
        upper = event.mod & (KMOD_SHIFT | KMOD_CAPS)
        app.player += char.upper() if upper else char
        app.player = app.player[:12]

    self.input_box.set_text(app.player.ljust(12, '_'))

  def add_label(self, font, text, x_center, y_offset, color=(222, 222, 222)):
    sprite = TextLabel(font, text, x_center, y_offset, color)
    self.sprites.add(sprite)
    return sprite
