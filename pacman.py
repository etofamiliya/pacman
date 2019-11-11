# etofamiliya, 2017-

import contextlib
with contextlib.redirect_stdout(None):
  import pygame
  import pygame.math
  import pygame.gfxdraw
  
# import pytmx
import json
import os, os.path

# from pytmx.util_pygame import load_pygame
from pygame.locals import *

tilesize = 32

'''
  e => Energizer
  d => Dot
  w => Wall
  p => Pacman
  b => Blinky
  c => Clyde
  n => piNky
  i => Inky
  o => dOor
  _ => empty places
'''
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
































class GridCell(object):
  def __init__(self, row, col, cell, cost):
    self.parent = None
    self.cell = cell
    self.cost = cost
    self.row = row
    self.col = col
    self.g = 0
    self.h = 0
    self.f = 0
    
  def __eq__(self, other):
    return (self.row == other.row) and (self.col == other.col)
    
  def reset(self):
    self.parent = None
    self.g = 0
    self.h = 0
    self.f = 0


class Grid(object):
  def __init__(self, grid, cellsize):
    rows = range(len(grid))
    cols = range(len(grid[0]))
    self.grid = [[0 for _ in cols] for _ in rows]
    
    costs = {
      'other_types_default': 1,
      'w': 100
    }

    for row, line in enumerate(grid):
      for col, typ in enumerate(line):
        self.grid[row][col] = GridCell(row, col, typ, costs.get(typ, 1))
    
    self.cellsize = cellsize
    
    
  def get_by_pos(self, pos):
    col, row = [int(v / self.cellsize) for v in pos]
    return self.get(row, col)
    
  def get(self, row, col):
    """ TODO BOUNDS CHECK """
    return self.grid[row][col]
    
  def get_neighbors(self, cell):
    row, col = cell.row, cell.col
    neighbors = {
      'up': self.get(row - 1, col),
      'down': self.get(row + 1, col),
      'left': self.get(row, col - 1),
      'right': self.get(row, col + 1)
    }
    return neighbors
    
  def can_move_to(self, pos, direction, impassable_types):
    cell = self.get_by_pos(pos)
    neighbors = self.get_neighbors(cell)
    neighbor = neighbors[direction]
    return neighbor.cell not in impassable_types
        

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
      for neighbor in neighbors.values():
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










































class Animation(object):
  def __init__(self, frames, delay, repeat = True):
    self.frames = frames
    self.repeat = repeat
    self.delay = delay
    self.timer = 0
    self.frame = 0

  def get_frame(self):
    return self.frames[self.frame]
    
  def finished(self):
    if self.repeat:
      return False
    return self.frame + 1 == len(self.frames)
    
  def rewind(self):
    self.frame = 0
    
  def update(self):
    time = pygame.time.get_ticks()
    if time >= self.timer:
      self.timer = time + self.delay

      if self.frame + 1 < len(self.frames):
        self.frame += 1
      elif self.repeat:
        self.rewind()
    

class Sprite(pygame.sprite.DirtySprite):
  def __init__(self, pos, image):
    super().__init__()
    self.rect = image.get_rect()
    self.rect.topleft = pos
    self.initial_pos = pos #?
    self.image = image
    
  def get_pos(self):
    return self.rect.topleft
  
  def set_pos(self, newpos):
    self.rect.topleft = newpos
    
    

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
    
  
class Ghost(Sprite):
  def __init__(self, pos, app, name):
    image = app.textures[name]
    super().__init__(pos, image)
    self.mode = 'scattering' # chasing, frightened, scattering
    self.name = name
    self.dirty = 2
    self.speed = 0
    self.app = app
    
    
class Blinky(Ghost):
  def __init__(self, pos, app):
    super().__init__(pos, app, 'blinky')
    
    self.animation = self.app.animations['blinky-right']
    self.direction = 'right'
    self.speed = 3
    self.path = []
  
  def redraw(self):
    if self.animation:
      self.animation.update()
      self.image = self.animation.get_frame()
      
      
  def change_direction(self, direction):
    self.animation = self.app.animations[self.name + '-' + direction]
    self.direction = direction
      
  def pathfind(self, goal_pos):
    return self.app.grid.pathfind(self.get_pos(), goal_pos)
    
  def update(self):
    blinky_cell = self.app.grid.get_by_pos(self.get_pos())
    blinky_vec = pygame.math.Vector2(self.get_pos())
    direction_vec = None
    if self.path:
      target_cell = self.path[0]
      target_x = target_cell.col * self.app.tilesize
      target_y = target_cell.row * self.app.tilesize
      target_vec = pygame.math.Vector2(target_x, target_y)
      
      direction_vec = target_vec - blinky_vec
      if direction_vec.length() < self.speed:
        self.path.pop(0)
      
      neighbors = self.app.grid.get_neighbors(blinky_cell)
      for new_direction in neighbors:
        if neighbors[new_direction] == target_cell:
          self.change_direction(new_direction)
          
    else:
      self.path = self.pathfind(self.app.pacman.get_pos())
      
      
    if direction_vec:
        self.speed = 3
        distance = direction_vec.length()
        if distance < self.speed:
          self.speed = distance
        direction_vec.normalize_ip()
        direction_vec *= self.speed
        newpos = blinky_vec + direction_vec
        self.set_pos(newpos)
    self.redraw()
      
      
    
    
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
    self.new_direction = None
    self.direction = 'right'
    self.animation = None
    self.dying = False
    self.speed = 0
    self.dirty = 2
    self.app = app
       
  def change_direction(self, keyname):
    converter = {
      K_UP: 'up',
      K_DOWN: 'down',
      K_LEFT: 'left',
      K_RIGHT: 'right'
    }
    self.new_direction = converter[keyname]
    
    
  def can_move_to(self, direction):
    return self.app.grid.can_move_to(self.get_pos(), direction, 'wo')
  
  def redraw(self):
    if self.animation:
      self.animation.update()
      self.image = self.animation.get_frame()
    
  def update(self):
    if self.dying:
      if self.animation.finished():
        self.set_pos(self.initial_pos)
        self.image = self.app.textures['pacman']
        self.animation.rewind()
        self.animation = None
        self.dying = False
        self.speed = 0
      self.redraw()
      return
    
    x, y = self.get_pos()
    
    if self.new_direction:      
      multiple_of = lambda v: (v % tilesize) <= self.speed
      can_turn_to = multiple_of(x) and multiple_of(y) 
      can_move_to = self.can_move_to(self.new_direction)

      if can_turn_to and can_move_to:
        self.direction = self.new_direction
        self.animation = self.app.animations['pacman-' + self.direction]
        self.new_direction = None
        self.speed = 3

    shift = {
      'up': (x, y - self.speed),
      'down': (x, y + self.speed),
      'left': (x - self.speed, y),
      'right': (x + self.speed, y)
    }
    
    pacman = pygame.math.Vector2(self.get_pos())
    for sprite in self.app.sprites.sprites():
      if sprite in self.app.ghosts:
        if pacman.distance_to(sprite.get_pos()) <= (tilesize / 2):
          self.animation = self.app.animations['pacman-dying-' + self.direction]
          self.dying = True
          self.speed = 0
          break
          
      elif isinstance(sprite, (Door, Wall)):
          sizes = [tilesize - self.speed] * 2
          rect = pygame.Rect(shift[self.direction], sizes)
          if rect.colliderect(sprite.rect):
            shift[self.direction] = (x, y)

      elif isinstance(sprite, Dot):
        if pacman.distance_to(sprite.get_pos()) <= (tilesize / 2):
          sprite.kill()
          
      elif isinstance(sprite, Energizer):
        if pacman.distance_to(sprite.get_pos()) <= (tilesize / 2):
          sprite.kill()
          
    
    newpos = shift[self.direction]
    self.set_pos(newpos)
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


class App(object):
  def __init__(self):
    width = len(plan[0]) * tilesize
    height = len(plan) * tilesize
    self.screen = pygame.display.set_mode((width, height))
    self.sprites = pygame.sprite.LayeredDirty()
    self.tilesize = tilesize
    self.running = True
    self.animations = {}
    self.textures = {}
    
  def launch(self): 
    adjust = lambda r: r * self.tilesize

    media_dir = os.path.join(os.getcwd(), 'media')
    characters_json = os.path.join(media_dir, 'characters.json')
    with open(characters_json) as characters:
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
        
      factory = {
        'e': Energizer,
        'd': Dot,
        'w': Wall,
        'o': Door,
        'i': Inky,
        'n': Pinky,
        'c': Clyde,
        'b': Blinky,
        'p': Pacman
      }
      # sprites = factory.fromkeys doesnt work correct
      sprites = dict([(k, []) for k in factory])
      
      for row, line in enumerate(plan):
        for col, typ in enumerate(line):
          if typ in factory:
            pos = adjust(col), adjust(row)
            sprite = factory[typ](pos, self)
            sprites[typ].append(sprite)
      
      #order important!
      for typ in 'odweincbp':
        [self.sprites.add(s) for s in sprites[typ]]
        
      self.ghosts = [sprites[v][0] for v in 'bnic']
      self.pacman = sprites['p'][0]   

      self.grid = Grid(plan, tilesize)
    
    controls = [K_UP, K_DOWN, K_LEFT, K_RIGHT]
    clock = pygame.time.Clock()
    while self.running:
      for event in pygame.event.get():
        if event.type == KEYDOWN:
          alt_f4 = event.key == K_F4 and bool(event.mod & KMOD_ALT)
          escape = event.key == K_ESCAPE
          if escape or alt_f4:
            self.running = False
            return
          
          elif event.key in controls:
            self.pacman.change_direction(event.key)
            
        elif event.type == QUIT:
          self.running = False
          return
      
      self.sprites.update()
      self.screen.fill((0, 0, 0))
      changes = self.sprites.draw(self.screen)
      pygame.display.update(changes)
      clock.tick(40)



if __name__ == '__main__':
  pygame.init()
  # pygame.mixer.init()
  pygame.key.set_repeat(1, 1)
  pygame.mouse.set_visible(False)
  os.environ["SDL_VIDEO_CENTERED"] = "1"
  pygame.display.set_caption('etofamiliya.Pacman')
  
  App().launch()
  
  # pygame.mixer.quit()
  pygame.quit()