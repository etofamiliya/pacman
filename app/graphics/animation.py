from app.core.timer import Timer
from app.graphics.pickled_image import PickledImage


class Animation:
    def __init__(self, frames, delay, repeat = True):
        self.frames = frames
        self.repeat = repeat
        self.delay = delay
        self.timer = None
        self.frame = 0

    def __getstate__(self):
        state = self.__dict__.copy()
        state['frames'] = [PickledImage(s) for s in self.frames]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.frames = [f.image for f in self.frames]

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
