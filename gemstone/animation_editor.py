# gemstone/animation_editor.py
import pygame
import os

class AnimationEditorScene:
    def __init__(self, size=(64, 64)):
        self.canvas_size = size
        self.frames = []
        self.current_frame = 0
        self.frame_rate = 6
        self.playing = False
        self.last_update = 0
    

        self.surface = pygame.display.set_mode((512, 512), pygame.RESIZABLE)
        pygame.display.set_caption("Gemstone Animation Editor")

        # start with one blank frame
        self.add_frame(size)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:  # play/pause
                self.playing = not self.playing
            elif event.key == pygame.K_n:  # new blank frame
                self.add_frame(self.canvas_size)
            elif event.key == pygame.K_d:  # duplicate frame
                self.duplicate_frame()
            elif event.key == pygame.K_DELETE:  # delete frame
                self.delete_frame()
            elif event.key == pygame.K_RIGHT:  # next frame
                self.current_frame = (self.current_frame + 1) % len(self.frames)
            elif event.key == pygame.K_LEFT:  # prev frame
                self.current_frame = (self.current_frame - 1) % len(self.frames)
            elif event.key == pygame.K_UP:  # faster playback
                self.frame_rate = min(60, self.frame_rate + 1)
            elif event.key == pygame.K_DOWN:  # slower playback
                self.frame_rate = max(1, self.frame_rate - 1)
            elif event.key == pygame.K_e:  # export sprite sheet
                self.export_spritesheet()

    def update(self, dt):
        if self.playing and len(self.frames) > 0:
            self.last_update += dt
            if self.last_update >= 1000 // self.frame_rate:
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.last_update = 0

    def draw(self):
        self.surface.fill((30, 30, 30))

        if self.frames:
            frame = self.frames[self.current_frame]
            rect = frame.get_rect(center=(256, 256))
            self.surface.blit(frame, rect)

        # show frame index and frame rate
        font = pygame.font.SysFont("Arial", 18)
        text = font.render(
            f"Frame {self.current_frame+1}/{len(self.frames)}  FPS:{self.frame_rate}",
            True,
            (255, 255, 255),
        )
        self.surface.blit(text, (10, 10))

        pygame.display.flip()

    def add_frame(self, size=(64, 64)):
        w, h = size
        w = min(w, 256)
        h = min(h, 256)
        surface = pygame.Surface((w, h))
        surface.fill((255, 255, 255))  # blank
        self.frames.append(surface)
        self.current_frame = len(self.frames) - 1

    def duplicate_frame(self):
        if self.frames:
            copy = self.frames[self.current_frame].copy()
            self.frames.insert(self.current_frame + 1, copy)
            self.current_frame += 1

    def delete_frame(self):
        if self.frames:
            self.frames.pop(self.current_frame)
            self.current_frame = max(0, self.current_frame - 1)

    def export_spritesheet(self, filename="spritesheet.png"):
        if not self.frames:
            return

        frame_w, frame_h = self.frames[0].get_size()
        sheet_w = frame_w * len(self.frames)
        sheet_h = frame_h

        sheet = pygame.Surface((sheet_w, sheet_h), pygame.SRCALPHA)
        for i, frame in enumerate(self.frames):
            sheet.blit(frame, (i * frame_w, 0))

        os.makedirs("exports", exist_ok=True)
        path = os.path.join("exports", filename)
        pygame.image.save(sheet, path)
        print(f"[Gemstone] Exported sprite sheet -> {path}")
