import pickle
from random import randint

from pygame.locals import *

from app.pathing.grid import Grid
from app.scenes.scene import Scene
from app.core.gametypes import GameTypes
from app.pathing.grid_cell import GridCell

from app.sprites.other import *
from app.sprites.ghost import Ghost
from app.sprites.pacman import Pacman
from app.sprites.timed_sprite import TimedSprite
from app.sprites.ghost_mode import SCATTERING, CHASING


class Game(Scene):
    def __init__(self, app):
        super().__init__(app, pygame.sprite.LayeredDirty())
        self.channel = pygame.mixer.find_channel()
        self.tilesize: int = 32
        self.starter = None
        self.pacman = None
        self.router = None
        self.ghosts = {}
        self.grid = None
        self.lives = 3
        self.bonus = 0
        self.score = 0

    def get_assets(self, assets_id):
        return self.app.assets[assets_id]

    def get_image(self, image_id):
        return self.get_assets(image_id).image

    def get_cell_pos_(self, row: int, col: int) -> tuple[int, int]:
        return col * self.tilesize, row * self.tilesize

    def get_cell_pos(self, cell: GridCell) -> tuple[int, int]:
        return self.get_cell_pos_(cell.row, cell.col)

    def get_cell_by_pos(self, pos) -> GridCell:
        col, row = [int(v / self.tilesize) for v in pos]
        return self.grid.get(row, col)

    def react(self, app, event):
        if event.type == KEYDOWN:
            alt_f4 = event.key == K_F4 and bool(event.mod & KMOD_ALT)
            if alt_f4:
                app.close()
            elif event.key == K_ESCAPE:
                self.after_delay(200, app.show_menu)
        elif event.type == QUIT:
            app.close()

    def add_sprite(self, sprite):
        layer = GameTypes.get_layer(type(sprite))
        self.sprites.add(sprite, layer=layer)

    def get_sprites_of_class(self, sprite_class) -> list:
        layer = GameTypes.get_layer(sprite_class)
        return self.sprites.get_sprites_from_layer(layer)

    def on_collision(self, sprite):
        if isinstance(sprite, Dot):
            eating_sound = self.get_assets('eating.wav')
            self.channel.queue(eating_sound)
            self.score += 10
            sprite.kill()
            self.bonus_spawn_check()
            self.last_dot_check()

        elif isinstance(sprite, Energizer):
            eating_bonus = self.get_assets('eating_bonus.wav')
            self.channel.play(eating_bonus)
            for ghost in list(self.ghosts.values()):
                ghost.frighten()
            self.bonus = 200
            self.score += 50
            sprite.kill()
            self.bonus_spawn_check()
            self.last_dot_check()
            self.play_scared_sound()

        elif isinstance(sprite, Fruit):
            eating_bonus = self.get_assets('eating_bonus.wav')
            self.channel.play(eating_bonus)
            self.score += 500
            sprite.kill()

        elif isinstance(sprite, Ghost):
            if sprite.is_vulnerable():
                ts_name = str(min(self.bonus, 1600))
                ts_score = TimedSprite(self, sprite.get_pos(), ts_name, 800)
                self.add_sprite(ts_score)

                eating_ghosts = self.get_assets('eating_ghosts.wav')
                self.channel.play(eating_ghosts)
                self.score += self.bonus
                sprite.send_to_home()
                self.bonus *= 2

            elif sprite.mode in [SCATTERING, CHASING]:
                death_sound = self.get_assets('death.wav')
                self.channel.play(death_sound)
                for ghost in list(self.ghosts.values()):
                    ghost.reset()
                self.pacman.kill()
                self.lives -= 1

    def bonus_spawn_check(self):
        dots = len(self.get_sprites_of_class(Dot))
        if dots in [60, 120]:
            bonus_name = 'bonus' + str(randint(1, 5))
            bonus = Fruit(self, self.pacman.initial_pos, bonus_name, 8000)
            self.add_sprite(bonus)

    def last_dot_check(self):
        dots = self.get_sprites_of_class(Dot)
        if len(dots) == 0:
            self.after_delay(200, self.app.show_scores)

    def end_game_check(self):
        if self.lives > 0:
            for ghost in list(self.ghosts.values()):
                ghost.set_pos(ghost.initial_pos)
            for tm in self.get_sprites_of_class(TimedSprite):
                tm.kill()
            self.starter = self.after_delay(500, self.start)
        else:
            self.after_delay(200, self.app.show_scores)

    def play_scared_sound(self):
        for ghost in list(self.ghosts.values()):
            if ghost.is_vulnerable():
                ghosts_scared = self.get_assets('ghosts_scared.wav')
                self.after_delay(ghosts_scared.get_length(), self.play_scared_sound)
                self.channel.queue(ghosts_scared)
                break

    def start(self):
        self.starter = None
        self.pacman.respawn()
        for ghost in list(self.ghosts.values()):
            ghost.animate()

    def pathfind(self, sprite, start, goal):
        sprite.follow_path(self.grid.pathfind(start, goal))

    def load(self):
        level_file = None
        try:
            level_file = open('level1', 'rb')  #  list[PickledSprite], cells: dict[str, GridCell]
            objects = pickle.load(level_file)
            for obj in objects:
                self.add_sprite(obj.create(self))

            self.grid = Grid()
            self.grid.cells = pickle.load(level_file)

        except FileNotFoundError as e:
            self.app.close()
            return
        finally:
            level_file.close()

        ghosts = self.get_sprites_of_class(Ghost)
        self.ghosts = dict([(g.name, g) for g in ghosts])
        self.pacman = self.get_sprites_of_class(Pacman).pop()
        self.events.add_observer(self.pacman, KEYDOWN)
        self.starter = self.after_delay(800, self.start)

    def update(self):
        if self.starter:
            return self.service_update()
        return super().update()