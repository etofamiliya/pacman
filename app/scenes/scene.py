from pygame.locals import *
from app.core.timer import Timer
from app.core.event_handler import EventHandler


class Scene:
    def __init__(self, app, sprites):
        self.app = app
        self.timers = []
        self.sprites = sprites
        self.full_redraw = True
        self.events = EventHandler(app)
        self.events.add_observer(self, KEYDOWN, KEYUP, QUIT)

    def get_rendering_area(self):
        if self.full_redraw:
            self.full_redraw = False
            return self.app.screen.get_rect()
        return self.sprites.draw(self.app.screen)

    def after_delay(self, duration, action):
        timer = Timer(duration, action)
        self.timers.append(timer)
        return timer

    def service_update(self):
        self.events.handle()
        self.timers = [tm.update() for tm in self.timers if tm.active]
        return self.get_rendering_area()

    def update(self):
        self.sprites.update()
        return self.service_update()

