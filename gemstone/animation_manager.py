import os
import json
import pygame
from typing import List, Dict, Optional, Tuple

class Frame:
    def __init__(self, surface: pygame.Surface, duration: int = 100, pivot: Tuple[int,int]=(0,0)):
        """
        duration in milliseconds
        pivot is optional anchor point
        """
        self.surface = surface
        self.duration = duration
        self.pivot = pivot

class Animation:
    def __init__(self, name: str, loop: bool = True):
        self.name = name
        self.frames: List[Frame] = []
        self.loop = loop

    def add_frame(self, frame: Frame, index: Optional[int] = None):
        if index is None:
            self.frames.append(frame)
        else:
            self.frames.insert(index, frame)

    def remove_frame(self, index: int):
        if 0 <= index < len(self.frames):
            del self.frames[index]

    def duplicate_frame(self, index: int):
        if 0 <= index < len(self.frames):
            src = self.frames[index]
            dup_surface = src.surface.copy()
            dup = Frame(dup_surface, src.duration, src.pivot)
            self.frames.insert(index+1, dup)

class AnimationInstance:
    """
    Runtime controller for a single animated entity.
    Keeps playback state: current frame index, elapsed time.
    """
    def __init__(self, animation: Animation):
        self.animation = animation
        self.current = 0
        self.elapsed = 0
        self.playing = True

    def reset(self):
        self.current = 0
        self.elapsed = 0
        self.playing = True

    def set_animation(self, animation: Animation):
        self.animation = animation
        self.reset()

    def update(self, dt_ms: int):
        if not self.playing or not self.animation.frames:
            return
        self.elapsed += dt_ms
        while self.elapsed >= self.animation.frames[self.current].duration:
            self.elapsed -= self.animation.frames[self.current].duration
            self.current += 1
            if self.current >= len(self.animation.frames):
                if self.animation.loop:
                    self.current = 0
                else:
                    self.current = len(self.animation.frames) - 1
                    self.playing = False
                    break

    def get_surface(self) -> Optional[pygame.Surface]:
        if not self.animation.frames:
            return None
        return self.animation.frames[self.current].surface

class AnimationManager:
    def __init__(self):
        self.animations: Dict[str, Animation] = {}

    def register(self, animation: Animation):
        self.animations[animation.name] = animation

    def get(self, name: str) -> Optional[Animation]:
        return self.animations.get(name)

    def unregister(self, name: str):
        if name in self.animations:
            del self.animations[name]

    # Serialization helpers
    def save_animation_json(self, animation_name: str, out_json_path: str, spritesheet_path: Optional[str]=None):
        """
        Save animation metadata to JSON. If spritesheet_path is provided, this function assumes
        the frames are arranged in a spritesheet and will record their rects. Otherwise frame
        images are saved individually next to the json.
        """
        anim = self.get(animation_name)
        if not anim:
            raise ValueError("Unknown animation: " + animation_name)

        data = {
            "name": anim.name,
            "loop": anim.loop,
            "frames": []
        }

        base_dir = os.path.dirname(out_json_path)
        os.makedirs(base_dir, exist_ok=True)

        # If a spritesheet was provided, reference it and write rects. Otherwise save each frame as png.
        if spritesheet_path:
            data["spritesheet"] = os.path.basename(spritesheet_path)
            # This function doesn't pack a spritesheet automatically. Use editor's packer for that.
            for i, f in enumerate(anim.frames):
                data["frames"].append({
                    "index": i,
                    "duration": f.duration,
                    "pivot": f.pivot
                })
        else:
            # Save frame PNGs next to JSON
            for i, f in enumerate(anim.frames):
                fname = f"{anim.name}_frame_{i}.png"
                full = os.path.join(base_dir, fname)
                pygame.image.save(f.surface, full)
                data["frames"].append({
                    "file": fname,
                    "duration": f.duration,
                    "pivot": f.pivot
                })

        with open(out_json_path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)

    def load_animation_json(self, json_path: str, base_path: Optional[str] = None) -> Animation:
        """Load an animation JSON created by save_animation_json."""
        base = base_path or os.path.dirname(json_path)
        with open(json_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)

        anim = Animation(data.get("name", "anim"), data.get("loop", True))
        frames = data.get("frames", [])

        spritesheet = None
        if "spritesheet" in data:
            spritesheet = pygame.image.load(os.path.join(base, data["spritesheet"])).convert_alpha()

        for fr in frames:
            if spritesheet and "rect" in fr:
                # rect: [x,y,w,h]
                x, y, w, h = fr["rect"]
                surf = pygame.Surface((w, h), pygame.SRCALPHA)
                surf.blit(spritesheet, (0, 0), (x, y, w, h))
                duration = fr.get("duration", 100)
                pivot = tuple(fr.get("pivot", (0, 0)))
                anim.add_frame(Frame(surf, duration, pivot))
            elif "file" in fr:
                surf = pygame.image.load(os.path.join(base, fr["file"])).convert_alpha()
                duration = fr.get("duration", 100)
                pivot = tuple(fr.get("pivot", (0, 0)))
                anim.add_frame(Frame(surf, duration, pivot))
            else:
                # fallback: skip
                continue

        self.register(anim)
        return anim