import os
import json
import pickle
import pygame

from app.core.timer import Timer
from app.scenes.game import Game
from app.scenes.menu import Menu
from app.scenes.scores import Scores
from app.graphics.tileset import Tileset
from app.graphics.animation import Animation


class App:
  def __init__(self):
    self.animations = {}
    self.textures = {}
    self.files = {}

    self.assets = {}

    self.tilesize = 32
    self.adjust = lambda r: r * self.tilesize
    self.running = True
    self.scene = None
    self.records = {}
    self.timers = []
    self.player = ''
    self.game = None

  def show_scene_(self, scene):
    for tm in self.timers:
      tm.active = False
    self.scene = scene

  def show_game(self):
    game = Game(self)
    self.show_scene_(game)
    self.game = game
    game.load()

  def show_menu(self):
    self.show_scene_(Menu(self))

  def show_scores(self):
    self.show_scene_(Scores(self))

  def close(self):
    if self.records:
      with open('records', 'wb') as r:
        pickle.dump(self.records, r)
    self.running = False

  def after_delay(self, duration, action):
    timer = Timer(duration, action)
    self.timers.append(timer)
    return timer

  def music_update(self):
    if pygame.mixer.music.get_busy():
      if pygame.mixer.music.get_pos() > 224250:
        pygame.mixer.music.stop()
        pygame.mixer.music.play(1, 59.8)

  def media(self, filename, extension):
    return self.files[extension][filename]

  def launch(self):
    adjust = self.adjust
    self.screen = pygame.display.set_mode((608, 608))

    try:
      with open('records', 'rb') as r:
        self.records = pickle.load(r)
    except Exception as e:
      self.records = {}

    def characters_json_handler(fullpath):
      with open(fullpath) as characters:
        jsondata = json.load(characters)
        tileset = Tileset(jsondata['filepath'], self.tilesize)

        for key in jsondata['animations']:
          animation = jsondata['animations'][key]
          row = adjust(animation['row'])
          cols = [adjust(col) for col in animation['cols']]
          frames = [tileset.crop(col, row) for col in cols]
          angle = animation.get('angle', 0)
          if angle:
            frames = [pygame.transform.rotate(f, angle) for f in frames]

          delay = animation['delay']
          repeat = animation.get('repeat', True)
          self.animations[key] = Animation(frames, delay, repeat)

        for key in jsondata['textures']:
          row, col = jsondata['textures'][key]
          row, col = adjust(row), adjust(col)
          self.textures[key] = tileset.crop(col, row)
      return fullpath



    handlers = {
      'wav': lambda w: pygame.mixer.Sound(w),
      'characters.json': characters_json_handler
    }

    default_h = lambda fullpath: fullpath
    for path, _, names in os.walk(os.path.join(os.getcwd(), 'media')):
      for name in names:
        fullpath = os.path.join(path, name)
        filename, extension = name.split('.')

        fullname_h = handlers.get(name)
        extension_h = handlers.get(extension)
        handler = fullname_h or extension_h or default_h

        container = self.files.get(extension, {})
        container[filename] = handler(fullpath)
        self.files[extension] = container

    pygame.mixer.music.load(self.media('main_theme', 'mp3'))
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)
    clock = pygame.time.Clock()
    self.scene = Menu(self)

    while self.running:
      self.music_update()
      self.screen.fill((0, 0, 0))
      changes = self.scene.update()
      pygame.display.update(changes)
      self.timers = [tm.update() for tm in self.timers if tm.active]
      clock.tick(40)
