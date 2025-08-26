import pygame
import json
import os

class Animation:
    """
    Manages a list of frames (pygame.Surface) for frame-by-frame animation.
    """

    def __init__(self, canvas_size=(32, 32)):
        self.canvas_size = canvas_size  # (width, height)
        self.frames = []
        self.current_index = 0
        self.fps = 12  # default playback speed
        self.onion_skin = False  # flag for onion skin preview

    def new_frame(self, copy_current=False):
        """
        Add a new frame after the current one. If copy_current is True,
        duplicate the current frame's content; otherwise create a blank frame.
        """
        if copy_current and self.frames:
            # Duplicate current frame
            new_surface = self.frames[self.current_index].copy()
        else:
            # Create blank transparent frame
            new_surface = pygame.Surface(self.canvas_size, flags=pygame.SRCALPHA)
            new_surface.fill((0, 0, 0, 0))
        insert_pos = self.current_index + 1
        self.frames.insert(insert_pos, new_surface)
        self.current_index = insert_pos

    def remove_frame(self):
        """Remove the current frame."""
        if not self.frames:
            return
        del self.frames[self.current_index]
        # Adjust current index if needed
        if self.current_index >= len(self.frames):
            self.current_index = max(0, len(self.frames) - 1)

    def duplicate_frame(self):
        """Duplicate the current frame (insert copy after current)."""
        if not self.frames:
            return
        new_surface = self.frames[self.current_index].copy()
        insert_pos = self.current_index + 1
        self.frames.insert(insert_pos, new_surface)
        self.current_index = insert_pos

    def reorder_frame(self, old_index, new_index):
        """
        Move a frame from old_index to new_index in the list.
        Adjust current_index accordingly.
        """
        n = len(self.frames)
        if 0 <= old_index < n and 0 <= new_index < n and old_index != new_index:
            frame = self.frames.pop(old_index)
            self.frames.insert(new_index, frame)
            # Update current index if needed
            if self.current_index == old_index:
                self.current_index = new_index
            elif old_index < self.current_index <= new_index:
                self.current_index -= 1
            elif new_index <= self.current_index < old_index:
                self.current_index += 1

    def export_sprite_sheet(self, filename):
        """
        Combine all frames into one horizontal sprite sheet and save as PNG.
        All frames must be same size (self.canvas_size).
        """
        if not self.frames:
            return
        w, h = self.canvas_size
        sheet_width = w * len(self.frames)
        sheet = pygame.Surface((sheet_width, h), flags=pygame.SRCALPHA)
        # Blit each frame side-by-side
        for i, frame in enumerate(self.frames):
            sheet.blit(frame, (i * w, 0))
        # Save the sprite sheet image
        pygame.image.save(sheet, filename)

    def save_to_file(self, filename):
        """
        Save animation to a directory: PNG frames + animation.json.
        filename is base name (e.g. "walk_cycle.anim"), without extension.
        A folder is created containing frames and JSON.
        """
        base_name = os.path.splitext(filename)[0]
        folder = base_name
        os.makedirs(folder, exist_ok=True)
        data = {
            "canvas_size": list(self.canvas_size),
            "fps": self.fps,
            "frames": []
        }
        for i, frame in enumerate(self.frames):
            frame_filename = f"frame_{i}.png"
            path = os.path.join(folder, frame_filename)
            pygame.image.save(frame, path)
            data["frames"].append(frame_filename)
        # Write JSON metadata
        json_path = os.path.join(folder, "animation.json")
        with open(json_path, "w") as f:
            json.dump(data, f, indent=4)

    def load_from_file(self, filename):
        """
        Load animation from a directory containing animation.json and frame PNGs.
        """
        base_name = os.path.splitext(filename)[0]
        folder = base_name
        json_path = os.path.join(folder, "animation.json")
        if not os.path.exists(json_path):
            return  # no animation file
        with open(json_path, "r") as f:
            data = json.load(f)
        self.canvas_size = tuple(data.get("canvas_size", self.canvas_size))
        self.fps = data.get("fps", self.fps)
        self.frames = []
        for frame_filename in data.get("frames", []):
            path = os.path.join(folder, frame_filename)
            if os.path.exists(path):
                image = pygame.image.load(path).convert_alpha()
                self.frames.append(image)
        self.current_index = 0
