import io
import pygame
import pickle
from pickle import UnpicklingError

from app.core.timer import Timer
from app.scenes.game import Game
from app.scenes.menu import Menu
from app.scenes.scores import Scores


class App:
  def __init__(self):
    self.adjust = lambda r: r * self.tilesize
    self.running = True
    self.tilesize = 32
    self.screen = None
    self.scene = None
    self.records = {}
    self.assets = {}
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

  def get_image(self, image_id):
    return self.assets[image_id].image

  def launch(self):
    try:
      with open('records', 'rb') as r:
        self.records = pickle.load(r)
    except Exception as e:
      self.records = {}

    try:
      with open('assets', 'rb') as a:
        self.assets = pickle.load(a)
    except UnpicklingError as e:
      print(f'86: {e}')

    sounds = [key for key in self.assets.keys() if key.endswith('.wav')]
    for key in sounds:
      self.assets[key] = pygame.mixer.Sound(self.assets[key])

    music_file_stream = io.BytesIO(self.assets['main_theme.mp3'])
    pygame.mixer.music.load(music_file_stream, 'mp3')
    pygame.mixer.music.set_volume(0.1)
    pygame.mixer.music.play(-1)

    self.screen = pygame.display.set_mode((608, 608))
    clock = pygame.time.Clock()
    self.scene = Menu(self)

    while self.running:
      self.music_update()
      self.screen.fill((0, 0, 0))
      changes = self.scene.update()
      pygame.display.update(changes)
      self.timers = [tm.update() for tm in self.timers if tm.active]
      clock.tick(40)

    music_file_stream.close()