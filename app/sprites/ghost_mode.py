class GhostMode:
    def __init__(self, mode):
        self.mode = mode

FRIGHTENED = GhostMode('frightened')
SCATTERING = GhostMode('scattering')
CHASING = GhostMode('chasing')
INIT = GhostMode('')
