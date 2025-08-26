# gemstone/engine.py
import pygame
from .config import WINDOW_WIDTH, WINDOW_HEIGHT, TITLE, TARGET_FPS

class GameEngine:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.scenes = {}
        self._current = None
        self.dt = 0

    def add_scene(self, name, scene):
        scene.engine = self
        self.scenes[name] = scene

    def set_scene(self, name, *args, **kwargs):
        if self._current:
            self._current.on_exit()
        self._current = self.scenes[name]
        self._current.on_enter(*args, **kwargs)

    def run(self, start_scene):
        self.set_scene(start_scene)
        while self.running:
            self.dt = self.clock.tick(TARGET_FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    if self._current:
                        self._current.handle_event(event)
            if self._current:
                self._current.update(self.dt)
                self._current.draw(self.screen)
            pygame.display.flip()
        pygame.quit()

class Scene:
    def __init__(self):
        self.engine = None

    # Hooks
    def on_enter(self, *args, **kwargs): pass
    def on_exit(self): pass
    def handle_event(self, event): pass
    def update(self, dt): pass
    def draw(self, surface): pass
