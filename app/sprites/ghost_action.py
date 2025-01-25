class GhostAction:
    def __init__(self, action):
        self.action = action


GOING_HOME = GhostAction('going-home')
BLINKING = GhostAction('blinking')
WALKING = GhostAction('walking')
IDLE = GhostAction('')
