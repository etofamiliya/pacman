from pygame.locals import *

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'
ALL_DIRECTIONS = [
    UP, DOWN, LEFT, RIGHT
]

opposite_direction = {
    UP: DOWN,
    DOWN: UP,
    LEFT: RIGHT,
    RIGHT: LEFT
}

key_to_direction = {
    K_w: UP,
    K_s: DOWN,
    K_a: LEFT,
    K_d: RIGHT,
    K_UP: UP,
    K_DOWN: DOWN,
    K_LEFT: LEFT,
    K_RIGHT: RIGHT
}