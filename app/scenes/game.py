from random import randint
from pygame.locals import *
from app.pathing.grid import Grid
from app.scenes.scene import Scene
from app.core.gametypes import GameTypes

from app.sprites.other import *
from app.sprites.ghost import Ghost
from app.sprites.timed_sprite import TimedSprite


class Game(Scene):
  def __init__(self, app):
    super().__init__(app, pygame.sprite.LayeredDirty())
    self.from_layer = self.sprites.get_sprites_from_layer
    self.channel = pygame.mixer.find_channel()
    self.starter = None
    self.lives = 3
    self.score = 0

  def react(self, app, event):
    if event.type == KEYDOWN:
      alt_f4 = event.key == K_F4 and bool(event.mod & KMOD_ALT)
      if alt_f4:
        app.close()
      elif event.key == K_ESCAPE:
        app.after_delay(200, app.show_menu)
    elif event.type == QUIT:
      app.close()

  def on_collision(self, sprite):
    if isinstance(sprite, Dot):
      eating_sound = self.app.media('eating', 'wav')
      self.channel.queue(eating_sound)
      self.score += 10
      sprite.kill()
      self.bonus_spawn_check()
      self.last_dot_check()

    elif isinstance(sprite, Energizer):
      eating_bonus = self.app.media('eating_bonus', 'wav')
      self.channel.play(eating_bonus)
      for ghost in list(self.ghosts.values()):
        ghost.frighten()
      self.bonus = 200
      self.score += 50
      sprite.kill()
      self.bonus_spawn_check()
      self.last_dot_check()
      self.ghosts_check()

    elif isinstance(sprite, Fruit):
      eating_bonus = self.app.media('eating_bonus', 'wav')
      self.channel.play(eating_bonus)
      self.score += 500
      sprite.kill()

    elif isinstance(sprite, Ghost):
      if sprite.is_vulnerable():
        ts_name = str(min(self.bonus, 1600))
        ts_score = TimedSprite(sprite.get_pos(), self.app, ts_name, 800)
        self.sprites.add(ts_score, layer=GameTypes.timed_layer)

        eating_ghosts = self.app.media('eating_ghosts', 'wav')
        self.channel.play(eating_ghosts)
        self.score += self.bonus
        sprite.send_to_home()
        self.bonus *= 2

      elif sprite.mode in ['scattering', 'chasing']:
        death_sound = self.app.media('death', 'wav')
        self.channel.play(death_sound)
        for ghost in list(self.ghosts.values()):
          ghost.reset()
        self.pacman.kill()
        self.lives -= 1

  def bonus_spawn_check(self):
    dots = len(self.from_layer(GameTypes.dots_layer))
    if dots in [60, 120]:
        bonus_name = 'bonus' + str(randint(1, 5))
        bonus = Fruit(self.pacman.initial_pos, self.app, bonus_name, 8000)
        self.sprites.add(bonus, layer=GameTypes.timed_layer)

  def last_dot_check(self):
    dots = self.from_layer(GameTypes.dots_layer)
    if len(dots) == 0:
      self.app.after_delay(200, self.app.show_scores)

  def end_game_check(self):
    if self.lives > 0:
      for ghost in list(self.ghosts.values()):
        ghost.set_pos(ghost.initial_pos)
      for tm in self.from_layer(GameTypes.timed_layer):
        tm.kill()
      self.starter = self.app.after_delay(500, self.start)
    else:
      self.app.after_delay(200, self.app.show_scores)

  def ghosts_check(self):
    for ghost in list(self.ghosts.values()):
      if ghost.is_vulnerable():
        ghosts_scared = self.app.media('ghosts_scared', 'wav')
        self.app.after_delay(ghosts_scared.get_length(), self.ghosts_check)
        self.channel.queue(ghosts_scared)
        break

  def start(self):
    self.starter = None
    self.pacman.respawn()
    for ghost in list(self.ghosts.values()):
      ghost.animate()

  def load(self):
    plan = [
      'wwwwwwwwwwwwwwwwwww',
      'wedddddddwdddddddew',
      'wdwwdwwddwddwwdwwdw',
      'wdwwdwdddddddwdwwdw',
      'wddddddwwwwwddddddw',
      'wdwwdwdddwdddwdwwdw',
      'wddddwdddbdddwddddw',
      'wwwwdwdwwowwdwdwwww',
      'dddddddw_n_wddddddd',
      'wwwwdwdwi_cwdwdwwww',
      'wddddwdwwwwwdwddddw',
      'wdwwdwdddpdddwdwwdw',
      'wddwdddwwwwwdddwddw',
      'wwdwdwdddwdddwdwdww',
      'wwdddddddddddddddww',
      'wddwwddwwwwwddwwddw',
      'wdwwwwdddwdddwwwwdw',
      'wedddddddddddddddew',
      'wwwwwwwwwwwwwwwwwww'
    ]
    adjust = self.app.adjust
    tilesize = self.app.tilesize
    self.grid = Grid(plan, tilesize)

    for row, line in enumerate(plan):
      for col, typ in enumerate(line):
        gametype = GameTypes.fullname(typ)
        if gametype:
          pos = adjust(col), adjust(row)
          sprite = GameTypes.create(gametype, pos, self.app)
          self.sprites.add(sprite, layer=GameTypes.layer(gametype))

    ghosts = self.from_layer(GameTypes.ghosts_layer)
    self.ghosts = dict([(g.name, g) for g in ghosts])
    self.pacman = self.from_layer(GameTypes.pacman_layer)[0]
    self.events.add_observer(self.pacman, KEYDOWN)
    self.starter = self.app.after_delay(800, self.start)

  def update(self):
    if self.starter:
      self.events.handle()
      return self.get_rendering_area()
    return super().update()
