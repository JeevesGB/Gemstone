# gemstone/demo.py
import pygame
from .engine import Scene
from .util import draw_text

class DemoScene(Scene):
    def __init__(self):
        super().__init__()
        self.sprite = None
        self.pos = [300, 300]
        self.speed = 180

    def on_enter(self, sprite_surface=None):
        # sprite_surface should be a pygame.Surface with per-pixel alpha
        if sprite_surface is not None:
            self.sprite = sprite_surface
        # else keep last one
        self.pos = [300, 300]

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.engine.set_scene("editor")

    def update(self, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: self.pos[0] -= self.speed * dt
        if keys[pygame.K_RIGHT]: self.pos[0] += self.speed * dt
        if keys[pygame.K_UP]: self.pos[1] -= self.speed * dt
        if keys[pygame.K_DOWN]: self.pos[1] += self.speed * dt

    def draw(self, surface):
        surface.fill((20, 26, 36))
        draw_text(surface, "Gemstone Demo — Arrow keys to move | Esc to return to Editor", (20, 16), (240,240,240), 20)
        if self.sprite:
            rect = self.sprite.get_rect(center=(int(self.pos[0]), int(self.pos[1])))
            surface.blit(self.sprite, rect)
        else:
            draw_text(surface, "No sprite yet. Press Esc to return and draw one!", (20, 60), (200,200,200), 18)
