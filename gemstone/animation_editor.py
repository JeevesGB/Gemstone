import pygame
import os
import json
from typing import List
from gemstone.animation_manager import Animation, Frame, AnimationManager
from gemstone.engine import Scene  # assuming your engine provides this

# constants for layout
TIMELINE_HEIGHT = 96
THUMB_SIZE = 64
PADDING = 8

class AnimationEditor(Scene):
    def __init__(self, project_dir: str = "animations"):
        super().__init__()
        self.project_dir = project_dir

        self.manager = AnimationManager()
        self.current_anim: Animation = Animation("new", loop=True)
        self.manager.register(self.current_anim)

        self.selected_frame = 0
        self.playing = False
        self.play_fps = 8
        self.preview_elapsed = 0
        self.onion_skin = False

        # UI
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 14)

        # guarantee at least one frame
        if not self.current_anim.frames:
            self.add_blank_frame()

    # === frame ops ===
    def add_blank_frame(self):
        w, h = 32, 32
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))
        frm = Frame(surf, duration=int(1000 / self.play_fps))
        self.current_anim.add_frame(frm)
        self.selected_frame = len(self.current_anim.frames) - 1

    def duplicate_frame(self):
        if 0 <= self.selected_frame < len(self.current_anim.frames):
            self.current_anim.duplicate_frame(self.selected_frame)

    def delete_frame(self):
        if len(self.current_anim.frames) <= 1:
            return
        if 0 <= self.selected_frame < len(self.current_anim.frames):
            self.current_anim.remove_frame(self.selected_frame)
            self.selected_frame = max(0, self.selected_frame - 1)

    # === timeline ===
    def draw_timeline(self, screen: pygame.Surface):
        sw, sh = screen.get_size()
        rect = pygame.Rect(0, sh - TIMELINE_HEIGHT, sw, TIMELINE_HEIGHT)
        pygame.draw.rect(screen, (40, 40, 40), rect)

        x = PADDING
        y = sh - TIMELINE_HEIGHT + PADDING
        for i, f in enumerate(self.current_anim.frames):
            thumb = pygame.transform.scale(f.surface, (THUMB_SIZE, THUMB_SIZE))
            trect = pygame.Rect(x, y, THUMB_SIZE, THUMB_SIZE)
            color = (200, 200, 60) if i == self.selected_frame else (140, 140, 140)
            pygame.draw.rect(screen, color, trect.inflate(4, 4), 2)
            screen.blit(thumb, (x, y))
            lbl = self.font.render(str(i), True, (220, 220, 220))
            screen.blit(lbl, (x, y + THUMB_SIZE + 2))
            x += THUMB_SIZE + PADDING

    def draw_canvas(self, screen: pygame.Surface):
        sw, sh = screen.get_size()
        canvas_rect = pygame.Rect(0, 0, sw, sh - TIMELINE_HEIGHT)
        pygame.draw.rect(screen, (20, 20, 20), canvas_rect)

        if not self.current_anim.frames:
            return

        surf = self.current_anim.frames[self.selected_frame].surface
        cx, cy = sw // 2, (sh - TIMELINE_HEIGHT) // 2

        if self.onion_skin and len(self.current_anim.frames) > 1:
            prev_idx = (self.selected_frame - 1) % len(self.current_anim.frames)
            next_idx = (self.selected_frame + 1) % len(self.current_anim.frames)
            for idx, offset in [(prev_idx, -10), (next_idx, 10)]:
                s = self.current_anim.frames[idx].surface.copy()
                s.set_alpha(80)
                screen.blit(s, (cx - s.get_width() // 2 + offset, cy - s.get_height() // 2))

        draw_surf = pygame.transform.scale(
            surf, (max(32, surf.get_width() * 4), max(32, surf.get_height() * 4))
        )
        screen.blit(draw_surf, (cx - draw_surf.get_width() // 2, cy - draw_surf.get_height() // 2))

    # === playback ===
    def play_toggle(self):
        self.playing = not self.playing
        self.preview_elapsed = 0

    def update_playback(self, dt: int):
        if not self.playing or not self.current_anim.frames:
            return
        self.preview_elapsed += dt
        cur_frame = self.current_anim.frames[self.selected_frame]
        if self.preview_elapsed >= cur_frame.duration:
            self.preview_elapsed -= cur_frame.duration
            self.selected_frame = (self.selected_frame + 1) % len(self.current_anim.frames)

    # === persistence ===
    def save_animation(self, out_dir: str):
        os.makedirs(out_dir, exist_ok=True)
        anim = self.current_anim
        json_path = os.path.join(out_dir, anim.name + ".json")
        frames_meta = []
        for i, fr in enumerate(anim.frames):
            fname = f"{anim.name}_frame_{i}.png"
            pygame.image.save(fr.surface, os.path.join(out_dir, fname))
            frames_meta.append({"file": fname, "duration": fr.duration, "pivot": fr.pivot})
        data = {"name": anim.name, "loop": anim.loop, "frames": frames_meta}
        with open(json_path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
        print("Saved animation to", json_path)

    def load_animation(self, json_path: str):
        base = os.path.dirname(json_path)
        with open(json_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        anim = Animation(data.get("name", "anim"), data.get("loop", True))
        for fr in data.get("frames", []):
            if "file" in fr:
                surf = pygame.image.load(os.path.join(base, fr["file"])).convert_alpha()
                anim.add_frame(Frame(surf, fr.get("duration", 100), tuple(fr.get("pivot", (0, 0)))))
        self.current_anim = anim
        self.manager.register(anim)
        self.selected_frame = 0

    # === Scene hooks ===
    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.engine.change_scene("menu")
            elif event.key == pygame.K_SPACE:
                self.play_toggle()
            elif event.key == pygame.K_a:
                self.add_blank_frame()
            elif event.key == pygame.K_d:
                self.delete_frame()
            elif event.key == pygame.K_c:
                self.duplicate_frame()
            elif event.key == pygame.K_o:
                self.onion_skin = not self.onion_skin
            elif event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                self.save_animation(self.project_dir)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            sw, sh = self.engine.screen.get_size()
            if my >= sh - TIMELINE_HEIGHT:
                rel_x = mx - PADDING
                idx = rel_x // (THUMB_SIZE + PADDING)
                if 0 <= idx < len(self.current_anim.frames):
                    self.selected_frame = idx

    def update(self, dt: int):
        self.update_playback(dt)

    def draw(self, screen: pygame.Surface):
        screen.fill((30, 30, 30))
        self.draw_canvas(screen)
        self.draw_timeline(screen)
        sw, sh = screen.get_size()
        hint = "Space:Play | A:Add | C:Duplicate | D:Delete | O:Onion Skin | Ctrl+S:Save | Esc:Menu"
        lbl = self.font.render(hint, True, (200, 200, 200))
        screen.blit(lbl, (10, sh - 20))
