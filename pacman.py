# etofamiliya, 2017-2024

import json
import os, os.path
import contextlib
with contextlib.redirect_stdout(None):
  import pygame
  import pygame.math
  import pygame.gfxdraw

from pygame.locals import *
from random import shuffle, randint


class GridCell(object):
  def __init__(self, tilesize, row, col, cell, cost):
    self.tilesize = tilesize
    self.cell = cell
    self.cost = cost
    self.row = row
    self.col = col
    self.reset()
    
  def get_pos(self):
    return self.col * self.tilesize, self.row * self.tilesize
    
  def __eq__(self, other):
    return (self.row == other.row) and (self.col == other.col)
    
  def reset(self):
    self.parent = None
    self.g = 0
    self.h = 0
    self.f = 0


class Grid(object):
  def __init__(self, grid, tilesize):
    rows = len(grid)
    cols = len(grid[0])
    self.grid = [[0 for _ in range(cols)] for _ in range(rows)]
    
    for row, line in enumerate(grid):
      for col, typ in enumerate(line):
        gametype = GameTypes.fullname(typ)
        cost = GameTypes.get_pathing_cost(gametype)
        cell = GridCell(tilesize, row, col, gametype, cost)
        self.grid[row][col] = cell
    
    self.tilesize = tilesize
    self.rows = rows - 1
    self.cols = cols - 1
    
  def get_by_pos(self, pos):
    col, row = [int(v / self.tilesize) for v in pos]
    return self.get(row, col)
    
  def get(self, row, col):
    if row < 0 or row > self.rows or col < 0 or col > self.cols:
      return GridCell(self.tilesize, row, col, 'tunnel', 0)
    return self.grid[row][col]
    
  def get_neighbors(self, cell):
    if cell.cell == 'tunnel':
      row, col = cell.row, cell.col
      impassable = lambda r, c: GridCell(self.tilesize, r, c, 'impassable', 999)
      if col < 0:
        return {
          'up': impassable(row-1, col),
          'down': impassable(row+1, col),
          'left': self.get(row, 19),
          'right': self.get(row, 0)
        }
      elif col > self.cols:
        return {
          'up': impassable(row-1, col),
          'down': impassable(row+1, col),
          'left': self.get(row, 18),
          'right': self.get(row, -1)
        }
      return {}
  
    row, col = cell.row, cell.col
    neighbors = {
      'up': self.get(row - 1, col),
      'down': self.get(row + 1, col),
      'left': self.get(row, col - 1),
      'right': self.get(row, col + 1)
    }    
    return neighbors

  def pathfind(self, start_pos, goal_pos): 
    for line in self.grid:
      [cell.reset() for cell in line]
      
    start = self.get_by_pos(start_pos)
    goal = self.get_by_pos(goal_pos)
    
    manhattan = lambda s, g: abs(s.row - g.row) + abs(s.col - g.col)
    start.h = manhattan(start, goal)
    start.f = start.h

    closed = []
    opened = [start]

    while opened:
      opened = sorted(opened, key = lambda cel: cel.f)
      cell = opened.pop(0)
      closed.append(cell)
      if cell == goal:
        path = []
        while cell:
          path.insert(0, cell)
          cell = cell.parent
        return path
        
      neighbors = self.get_neighbors(cell)
      for neighbor in list(neighbors.values()):
        if neighbor not in closed:
          newg = cell.g + neighbor.cost
          
          if neighbor not in opened:
            opened.append(neighbor)
          elif newg >= neighbor.g:
            continue
                    
          neighbor.g = newg
          neighbor.h = manhattan(neighbor, goal)
          neighbor.f = neighbor.g + neighbor.h
          neighbor.parent = cell
          
    return []


class Timer(object):
  def __init__(self, duration, action):
    self.start = pygame.time.get_ticks()
    self.duration = duration
    self.action = action
    self.active = True
    
  def update(self):
    if self.active:
      time = pygame.time.get_ticks()
      if time - self.start >= self.duration:
        self.active = False
        self.action()
    return self


class Animation(object):
  def __init__(self, frames, delay, repeat = True):
    self.frames = frames
    self.repeat = repeat
    self.delay = delay
    self.timer = None
    self.frame = 0

  @property
  def finished(self):
    return self.frame + 1 == len(self.frames)
    
  def rewind(self):
    self.timer = None
    self.frame = 0
    
  def next_frame(self):
    if self.repeat or not self.finished:
      self.timer = Timer(self.delay, self.next_frame)
      self.frame = 0 if self.finished else self.frame + 1

  def update(self):
    if self.timer:
      self.timer.update()
    else:
      self.timer = Timer(self.delay, self.next_frame)
    return self.frames[self.frame]


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


class TimedSprite(Sprite):
  def __init__(self, pos, app, name, duration):
    image = app.textures[name]
    super().__init__(pos, image)
    self.timer = Timer(duration, self.kill)
    self.update = self.timer.update
    self.dirty = 2


class Fruit(TimedSprite):
  def __init__(self, pos, app, name, duration):
    super().__init__(pos, app, name, duration)


class Dot(Sprite):
  def __init__(self, pos, app):
    image = app.textures['dot']
    super().__init__(pos, image)


class Wall(Sprite):
  def __init__(self, pos, app):
    sizes = [app.tilesize] * 2
    image = pygame.Surface(sizes)
    image.fill((0, 50, 80))
    super().__init__(pos, image)    


class Door(Sprite):
  def __init__(self, pos, app):
    tsize = app.tilesize
    image = pygame.Surface((tsize, tsize))
    door = pygame.Rect(0, tsize/4, tsize, tsize/2)
    image.fill((0, 50, 80), door)
    super().__init__(pos, image)


class Energizer(Sprite):
  def __init__(self, pos, app):
    image = app.textures['energizer']
    super().__init__(pos, image)
    self.app = app
    self.blink()
    
  def blink(self):
    self.app.set_timer(350, self.blink)
    self.visible = not self.visible
      

class Ghost(Sprite):
  def __init__(self, pos, app, name):
    image = app.textures[name]
    super().__init__(pos, image)
    self.new_direction = True
    self.direction = 'right'
    self.animation = None
    self.game = app.game
    self.name = name
    self.action = ''
    self.timers = []
    self.speed = 0
    self.dirty = 2
    self.app = app
    self.mode = ''
    self.path = []
    
  def is_at_home(self):
    return self.get_pos() == self.get_home_pos()
    
  def get_home_pos(self):
    return self.initial_pos      
    
  def is_walkable(self, cell):
    return cell.cell not in ('wall', 'door', 'impassable')
    
  def is_vulnerable(self):
    return self.mode == 'frightened' and self.action != 'going-home'
    
  def change_animation(self):
    animation_name = self.name + '-' + self.direction
    if self.mode == 'frightened':
      actions = {
        'blinking': 'ghost-blinking',
        'walking': 'ghost-frightened',
        'going-home': 'eyes-' + self.direction,
      }
      animation_name = actions[self.action]
    self.animation = self.app.animations.get(animation_name)
    self.animation.rewind()
  
  def redraw(self):
    self.image = self.animation.update()
    
  def change_direction(self, direction):
    self.direction = direction
    self.change_animation()
      
  def pathfind(self, goal_pos):
    return self.game.grid.pathfind(self.get_pos(), goal_pos)
    
  def make_one_step(self, neighbors):
    opposite = {
      'up': 'down',
      'down': 'up',
      'left': 'right',
      'right': 'left'
    }
    
    directions = list(neighbors.keys())
    shuffle(directions)
    
    for new_direction in directions:
      if new_direction == opposite[self.direction]:
        continue
      
      neighbor = neighbors.get(new_direction)
      if neighbor and self.is_walkable(neighbor):
        self.path = [neighbor]
        break
    
  def change_action(self, newaction):
    self.action = newaction
    self.change_animation()
    
  def send_to_home(self): 
    self.change_action('going-home')
    self.reset_timers()
    self.speed = 5
    
  def animate(self):
    self.reset()
    self.switch_mode()
    
  def add_timer(self, duration, action):
    self.timers.append(self.app.set_timer(duration, action))
    
  def reset_timers(self):
    for tm in self.timers:
      tm.active = False
    self.timers = []
    
  def switch_mode(self):
    if self.mode == 'scattering':
      self.mode = 'chasing'
    else:
      self.mode = 'scattering'
      
    self.add_timer(5000, self.switch_mode)
    self.change_action('walking')
    self.path = self.path[:1]
    self.speed = 3
      
  def frighten(self):
    self.reset_timers()
    blink = lambda: self.change_action('blinking')
    self.add_timer(8000, self.switch_mode)
    self.add_timer(6500, blink)
    self.mode = 'frightened'
    self.change_action('walking')
    self.path = self.path[:1]
    self.speed = 2

  def reset(self):
    self.mode = ''
    self.change_action('')
    self.reset_timers()
    self.speed = 0
    self.path = []

  def update(self):  
    grid = self.app.game.grid
    
    x, y = self.get_pos()
    position = pygame.math.Vector2((x, y))
    ghost_cell = grid.get_by_pos((x, y))
    neighbors = grid.get_neighbors(ghost_cell)
    
    if self.path:
      target_cell = self.path[0]
      
      if self.new_direction:
        for new_direction in neighbors:
          if neighbors[new_direction] == target_cell:
            self.change_direction(new_direction)
            self.new_direction = False
            break

      target_x, target_y = target_cell.get_pos()
      destination = pygame.math.Vector2(target_x, target_y)
      
      direction = destination - position
      distance = direction.length()
      if distance:
        speed = min(self.speed, distance)
        shift = direction.normalize() * speed
        shift.xy = [round(v) for v in shift]
        if abs(shift.x) < abs(shift.y):
          shift.x = 0
        else:
          shift.y = 0
        
        newpos = (position + shift)
        self.set_pos(newpos)
      else:  
        if target_cell.cell == 'tunnel':
          neighbors = grid.get_neighbors(target_cell)
          ghost_cell = neighbors[self.direction]
          x, y = ghost_cell.get_pos()
          self.set_pos((x, y))
          
        self.new_direction = True
        self.path.pop(0)

    else:    
      if self.mode == 'frightened':
        if self.action == 'going-home':
          if self.is_at_home():
            self.animate()
          else:
            self.path = self.pathfind(self.get_home_pos())
        else:
          self.make_one_step(neighbors)

      elif self.mode == 'scattering':
        if self.is_at_home():
          blinky = self.app.game.ghosts['blinky']
          self.path = self.pathfind(blinky.initial_pos)  
        else:
          self.make_one_step(neighbors)

      elif self.mode == 'chasing':
        self.path = self.pathfind(self.game.pacman.get_pos())
    self.redraw()
      

class Blinky(Ghost):
  def __init__(self, pos, app):
    super().__init__(pos, app, 'blinky') 
    
  def get_home_pos(self):
    return self.app.game.ghosts['pinky'].initial_pos
    
class Clyde(Ghost):
  def __init__(self, pos, app):
    super().__init__(pos, app, 'clyde')
    
class Pinky(Ghost):
  def __init__(self, pos, app):
    super().__init__(pos, app, 'pinky')
    
class Inky(Ghost):
  def __init__(self, pos, app):
    super().__init__(pos, app, 'inky')

    
class Pacman(Sprite):
  def __init__(self, pos, app):
    image = app.textures['pacman']
    super().__init__(pos, image)
    self.sprites = app.game.sprites.sprites
    self.new_direction = None
    self.direction = 'right'
    self.animation = None
    self.game = app.game
    self.dying = False
    self.speed = 0
    self.dirty = 2
    self.app = app
        
  def is_walkable(self, cell):
    return cell.cell not in ('wall', 'door', 'impassable')
  
  def can_move_to(self, cell, direction):
    neighbors = self.game.grid.get_neighbors(cell)      
    return self.is_walkable(neighbors[direction])
  
  def redraw(self):
    if self.animation:
      self.image = self.animation.update()
          
  def kill(self):
    self.dying = True
    self.change_animation()
    
  def change_animation(self):
    if self.dying:
      self.animation = self.app.animations['pacman-dying-' + self.direction]
    else:
      self.animation = self.app.animations['pacman-' + self.direction]
    self.animation.rewind()
    
  def respawn(self):
    self.set_pos(self.initial_pos)
    self.image = self.app.textures['pacman']
    self.animation = None
    self.dying = False
    self.speed = 0
  
  def react(self, app, event):
    if event.type == KEYDOWN:
      if event.key in [K_UP, K_DOWN, K_LEFT, K_RIGHT]:
        converter = {
          K_UP: 'up',
          K_DOWN: 'down',
          K_LEFT: 'left',
          K_RIGHT: 'right'
        }
        self.new_direction = converter[event.key]
        self.speed = 3
    
  def update(self):
    if self.dying:
      if self.animation.finished:
        self.app.game.end_game_check()
      self.redraw()
      return     
    
    x, y = self.get_pos()
    cell = self.game.grid.get_by_pos((x, y))
    tilesize = self.app.tilesize
    if self.new_direction:
      multiple_of = lambda v: (v % tilesize) <= self.speed
      can_turn_to = multiple_of(x) and multiple_of(y) 
      can_move_to = self.can_move_to(cell, self.new_direction)

      if can_turn_to and can_move_to:
        self.direction = self.new_direction
        self.new_direction = None
        self.change_animation()
        
    shift = {
      'up': (x, y - self.speed),
      'down': (x, y + self.speed),
      'left': (x - self.speed, y),
      'right': (x + self.speed, y)
    }
    
    pacman_vec = pygame.math.Vector2((x, y))
    for sprite in self.sprites():
      sprite_pos = sprite.get_pos()
      sprite_vec = pygame.math.Vector2(sprite_pos)
      distance = pacman_vec.distance_to(sprite_vec)
      collided = distance <= (tilesize / 2)
          
      if isinstance(sprite, (Door, Wall)):
        sizes = [tilesize - self.speed] * 2
        topleft = shift[self.direction]
        rect = pygame.Rect(topleft, sizes)
        if rect.colliderect(sprite.rect):
          shift[self.direction] = (x, y)
            
      elif collided:
        self.game.on_collision(sprite)
        
    if self.speed:
      if cell.cell == 'tunnel':
        tunnel_exit = self.game.grid.get_neighbors(cell)[self.direction]
        x, y = tunnel_exit.get_pos()
      else:
        x, y = shift[self.direction]
      self.set_pos((x, y))
    self.redraw()
      

class Tileset(object):
  def __init__(self, path, tilesize):
    self.image = pygame.image.load(path)
    if self.image.get_alpha():
      self.image = self.image.convert_alpha()
    else:
      self.image = self.image.convert()
      self.image.set_colorkey(self.image.get_at((0, 0)))
    self.tilesize = tilesize
    
  def crop(self, x, y):
    tsize = [self.tilesize] * 2
    result = self.image.subsurface(pygame.Rect((x, y), tsize)).copy()
    return result


class GameTypes(object):
  pacman_layer = 6
  ghosts_layer = 5
  timed_layer  = 4
  walls_layer  = 3
  dots_layer   = 2
  door_layer   = 1

  @staticmethod
  def fullname(char):
    converter = {
      'e': 'energizer',
      'p': 'pacman',
      'b': 'blinky',
      'c': 'clyde',
      'n': 'pinky',
      'i': 'inky',
      'o': 'door',
      'w': 'wall',
      'd': 'dot'
    }
    return converter.get(char, '')
  
  @classmethod
  def layer(cls, gametype):  
    layers = {
      'energizer': cls.dots_layer,
      'pacman': cls.pacman_layer,
      'blinky': cls.ghosts_layer,
      'clyde': cls.ghosts_layer,
      'pinky': cls.ghosts_layer,
      'inky': cls.ghosts_layer,
      'wall': cls.walls_layer,
      'door': cls.door_layer,
      'dot': cls.dots_layer
    }
    return layers.get(gametype, 0)
    
  @staticmethod
  def get_pathing_cost(gametype):
    costs = {
      'default': 1,
      'wall': 100
    }
    return costs.get(gametype, 1)
  
  @staticmethod
  def create(gametype, pos, app):
    factory = {
      'energizer': Energizer,
      'pacman': Pacman,
      'blinky': Blinky,
      'clyde': Clyde,
      'pinky': Pinky,
      'inky': Inky,
      'door': Door,
      'wall': Wall,
      'dot': Dot
    }
    return factory[gametype](pos, app)


class TextLabel(Sprite):
  def __init__(self, font, text, x_center, y_offset, color):
    super().__init__((0, 0), pygame.Surface((0, 0)))
    self.redraw = lambda t: font.render(t, True, color)
    self.newpos = lambda i: (x_center - (i.get_width() / 2), y_offset)
    self.set_text(text)
    
  def set_text(self, text):
    self.image = self.redraw(text)
    self.set_pos(self.newpos(self.image))
    self.text = text


class EventHandler(object):
  def __init__(self, app):
    self.observers = {}
    self.clear = self.observers.clear
    self.app = app
    
  def add_observer(self, obs, *types):
    for event_type in types:
      if event_type in self.observers:
        self.observers[event_type].append(obs)
      else:
        self.observers[event_type] = [obs]
    
  def handle(self):
    for event in pygame.event.get():
      for obs in self.observers.get(event.type, []):
        obs.react(self.app, event)


class Scene(object):
  def __init__(self, app, sprites):
    self.app = app
    self.sprites = sprites
    self.full_redraw = True
    self.events = EventHandler(app)
    self.events.add_observer(self, KEYDOWN, KEYUP, QUIT)
  
  def get_rendering_area(self):
    if self.full_redraw:
      self.full_redraw = False
      return self.app.screen.get_rect()
    return self.sprites.draw(self.app.screen)

  def update(self):
    self.events.handle()
    self.sprites.update()
    return self.get_rendering_area()


class Menu(Scene):
  def __init__(self, app):
    super().__init__(app, pygame.sprite.RenderUpdates())
    app.player = ''
    
    x_center = app.screen.get_width() / 2

    firenight = app.media('Firenight-Regular', 'otf')
    firenight_60 = pygame.font.Font(firenight, 60)
    firenight_36 = pygame.font.Font(firenight, 36)
    
    inconsolata = app.media('Inconsolata', 'otf')
    inconsolata_18 = pygame.font.Font(inconsolata, 18)
    inconsolata_14 = pygame.font.Font(inconsolata, 14)
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
    
  def react(self, app, event):
    if event.type == KEYDOWN:
      alt_f4 = event.key == K_F4 and bool(event.mod & KMOD_ALT)
      escape = event.key == K_ESCAPE
      if escape or alt_f4:
        app.close()
    elif event.type == QUIT:
      app.close()
      
  def show_game(self):
    self.app.show_scene(Game)()
    self.app.game = self.app.scene
    self.app.game.load()
    
  def input_box_react(self, app, event):
    if event.key == K_RETURN:
      if len(app.player):
        app.set_timer(200, self.show_game)
    elif event.key == K_BACKSPACE:
      app.player = app.player[:-1]
    else:
      char = chr(event.key)
      if char.isascii():
        upper = event.mod & (KMOD_SHIFT | KMOD_CAPS)
        app.player += char.upper() if upper else char
        app.player = app.player[:12]

    self.input_box.set_text(app.player.ljust(12, '_'))

  def add_label(self, font, text, x_center, y_offset, color=(222, 222, 222)):
    sprite = TextLabel(font, text, x_center, y_offset, color)
    self.sprites.add(sprite)
    return sprite
    

class Scores(Scene):
  def __init__(self, app):
    super().__init__(app, pygame.sprite.RenderUpdates())
    
    x_center = app.screen.get_width() / 2
    inconsolata = app.media('Inconsolata', 'otf')
    inconsolata_14 = pygame.font.Font(inconsolata, 14)
    inconsolata_12 = pygame.font.Font(inconsolata, 12)

    scores_text = 'Your scores: ' + str(app.game.score)
    anykey_text = 'Press any key to continue'
    
    self.add_label(inconsolata_14, scores_text, x_center, 200)
    self.add_label(inconsolata_12, anykey_text, x_center, 225)
    app.records[app.player] = app.game.score

  def add_label(self, font, text, x_center, y_offset, color=(222, 222, 222)):
    sprite = TextLabel(font, text, x_center, y_offset, color)
    self.sprites.add(sprite)

  def react(self, app, event):
    if event.type == KEYUP:
      alt_f4 = event.key == K_F4 and bool(event.mod & KMOD_ALT)
      if alt_f4:
        app.close()
      else:
        app.set_timer(200, app.show_scene(Menu))
    elif event.type == QUIT:
      app.close()


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
        app.set_timer(200, app.show_scene(Menu))
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
      self.app.set_timer(200, self.app.show_scene(Scores))
    
  def end_game_check(self):
    if self.lives > 0:
      for ghost in list(self.ghosts.values()):
        ghost.set_pos(ghost.initial_pos)
      for tm in self.from_layer(GameTypes.timed_layer):
        tm.kill()
      self.starter = self.app.set_timer(500, self.start)
    else:
      self.app.set_timer(200, self.app.show_scene(Scores))
      
  def ghosts_check(self):
    for ghost in list(self.ghosts.values()):
      if ghost.is_vulnerable():
        ghosts_scared = self.app.media('ghosts_scared', 'wav')
        self.app.set_timer(ghosts_scared.get_length(), self.ghosts_check)
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
    self.starter = self.app.set_timer(800, self.start)  

  def update(self):
    if self.starter:
      self.events.handle()
      return self.get_rendering_area()
    return super().update()


class App(object):
  def __init__(self):
    self.animations = {}
    self.textures = {}
    self.files = {}

    self.tilesize = 32
    self.adjust = lambda r: r * self.tilesize
    self.running = True
    self.records = {}
    self.timers = []
    self.player = ''   
    self.game = None

  def show_scene(self, scene):
    def show_scene_():
      for tm in self.timers:
        tm.active = False
      self.scene = scene(self)
    return show_scene_
    
  def close(self):
    if self.records:
      with open(self.media('records', 'txt'), 'w') as r:
        records = ['{}: {}'.format(*z) for z in list(self.records.items())]
        r.write('\n'.join(records))
    self.running = False
        
  def set_timer(self, duration, action):
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

    def records_txt_handler(fullpath):
      with open(fullpath) as r:
        lines = r.readlines()
        if len(lines):
          for line in lines:
            name, score = line.split(':')
            self.records[name] = max(int(score), self.records.get(name, 0))
      return fullpath

    handlers = {
      'records.txt': records_txt_handler,
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