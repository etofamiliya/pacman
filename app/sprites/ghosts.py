from app.sprites.ghost import Ghost


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
