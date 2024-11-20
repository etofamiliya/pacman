from pygame.locals import *

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

opposite_direction = {
  UP: DOWN,
  DOWN: UP,
  LEFT: RIGHT,
  RIGHT: LEFT
}

key_to_direction = {
	K_UP: UP,
	K_DOWN: DOWN,
	K_LEFT: LEFT,
	K_RIGHT: RIGHT
}