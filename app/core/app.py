import io
import pygame
import pickle

from app.scenes.game import Game
from app.scenes.menu import Menu
from app.scenes.scores import Scores


class App:
    def __init__(self):
        self.running = True
        self.screen = None
        self.scene = None
        self.records = {}
        self.assets = {}
        self.player = ''
        self.game = None

    def show_scene_(self, scene):
        self.scene = scene

    def show_game(self):
        self.scene = self.game

    def show_menu(self):
        self.game = Game(self)
        self.show_scene_(Menu(self))
        self.game.load()

    def show_scores(self):
        self.show_scene_(Scores(self))

    def close(self):
        if self.records:
            with open('records', 'wb') as r:
                pickle.dump(self.records, r)
        self.running = False

    def music_update(self):
        if pygame.mixer.music.get_busy():
            if pygame.mixer.music.get_pos() > 224250:
                pygame.mixer.music.stop()
                pygame.mixer.music.play(1, 59.8)

    def launch(self):
        try:
            with open('records', 'rb') as r:
                self.records = pickle.load(r)
        except:
            self.records = {}

        try:
            with open('assets', 'rb') as a:
                self.assets = pickle.load(a)
        except:
            return

        sounds = [key for key in self.assets.keys() if key.endswith('.wav')]
        for key in sounds:
            self.assets[key] = pygame.mixer.Sound(self.assets[key])

        music_file_stream = io.BytesIO(self.assets['main_theme.mp3'])
        pygame.mixer.music.load(music_file_stream, 'mp3')
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)

        self.screen = pygame.display.set_mode((608, 608))
        clock = pygame.time.Clock()
        self.show_menu()

        while self.running:
            self.music_update()
            self.screen.fill((0, 0, 0))
            changes = self.scene.update()
            pygame.display.update(changes)
            clock.tick(40)

        music_file_stream.close()