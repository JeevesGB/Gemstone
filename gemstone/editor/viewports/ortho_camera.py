import numpy as np

class OrthoCamera:
    def __init__(self):
        self.zoom = 1.0
        self.offset = np.array([0.0, 0.0])

    def world_to_screen(self, p):
        return (p + self.offset) * self.zoom

    def screen_to_world(self, p):
        return p / self.zoom - self.offset
