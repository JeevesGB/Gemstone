import pygame
from gemstone.animation_manager import Animation

class PixelEditor:
    """
    Pixel art editor with animation frame support. Integrates with existing Gemstone UI.
    """

    def __init__(self, screen):
        self.screen = screen  # main Pygame screen
        self.canvas_size = (128, 128)  # default canvas (can be changed up to 256)
        # Initialize animation model with one empty frame
        self.animation = Animation(self.canvas_size)
        initial_frame = pygame.Surface(self.canvas_size, flags=pygame.SRCALPHA)
        initial_frame.fill((0, 0, 0, 0))
        self.animation.frames.append(initial_frame)
        self.current_color = (255, 255, 255)  # example drawing color
        self._setup_ui()

    def _setup_ui(self):
        """
        Define UI element rectangles (buttons, sliders, etc.).
        """
        # Example button positions (these would fit into existing layout)
        self.btn_add = pygame.Rect(10, 10, 80, 30)     # "Add Frame"
        self.btn_dup = pygame.Rect(100, 10, 100, 30)   # "Duplicate Frame"
        self.btn_del = pygame.Rect(210, 10, 80, 30)    # "Delete Frame"
        self.btn_export = pygame.Rect(10, 50, 150, 30) # "Export Sprite Sheet"
        self.fps_slider = pygame.Rect(10, 90, 200, 20) # FPS slider area (for example)
        # ... define frame thumbnail panel position, preview panel, etc.

    def handle_event(self, event):
        """
        Handle Pygame events: mouse clicks, key presses.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if self.btn_add.collidepoint(mx, my):
                self.animation.new_frame(copy_current=False)
            elif self.btn_dup.collidepoint(mx, my):
                self.animation.new_frame(copy_current=True)
            elif self.btn_del.collidepoint(mx, my):
                self.animation.remove_frame()
            elif self.btn_export.collidepoint(mx, my):
                # Export sprite sheet as "animation.png"
                self.animation.export_sprite_sheet("animation.png")
            # Handle thumbnail clicks: (assuming thumbnails at bottom)
            # e.g., if click in thumbnail i: self.animation.current_index = i
            # Handle FPS slider drag to adjust self.animation.fps
            # Handle onion skin toggle key or button (not shown).
        # Also handle drawing input (e.g., brush) on current frame surface
        if event.type == pygame.MOUSEMOTION:
            if event.buttons[0]:  # left button held -> draw
                x, y = event.pos
                # Convert to canvas coordinates if canvas is scaled
                # For simplicity, assume 1:1
                if 0 <= x < self.canvas_size[0] and 0 <= y < self.canvas_size[1]:
                    frame = self.animation.frames[self.animation.current_index]
                    frame.set_at((x, y), self.current_color)

    def draw(self):
        """
        Draw the editor UI: canvas, thumbnails, preview, and buttons.
        """
        # 1. Draw current frame canvas
        canvas_surface = self.animation.frames[self.animation.current_index]
        # Blit the canvas onto the screen (it is already a Surface)
        self.screen.blit(canvas_surface, (0, 0))

        # 2. Draw UI buttons (simple filled rect as example)
        pygame.draw.rect(self.screen, (200, 200, 200), self.btn_add)
        pygame.draw.rect(self.screen, (200, 200, 200), self.btn_dup)
        pygame.draw.rect(self.screen, (200, 200, 200), self.btn_del)
        pygame.draw.rect(self.screen, (200, 200, 200), self.btn_export)
        # (Would also render text labels on them)

        # 3. Draw frame thumbnails at bottom
        thumb_size = (32, 32)
        padding = 5
        for i, frame in enumerate(self.animation.frames):
            thumb = pygame.transform.scale(frame, thumb_size)
            thumb_x = 10 + i * (thumb_size[0] + padding)
            thumb_y = self.canvas_size[1] + 10
            self.screen.blit(thumb, (thumb_x, thumb_y))
            # Highlight current frame
            if i == self.animation.current_index:
                pygame.draw.rect(self.screen, (255, 0, 0), 
                                 (thumb_x-2, thumb_y-2, thumb_size[0]+4, thumb_size[1]+4), 2)

        # 4. Draw playback preview
        # For simplicity, show frame sequence vertically
        preview_x = self.canvas_size[0] + 10
        preview_y = 10
        max_preview_frames = 5  # show up to 5 frames in preview window
        for j in range(min(len(self.animation.frames), max_preview_frames)):
            frame = self.animation.frames[j]
            small = pygame.transform.scale(frame, (16, 16))
            self.screen.blit(small, (preview_x, preview_y + j * 18))
        # Draw a border around preview area (optional)

        # 5. Draw FPS slider background (placeholder)
        pygame.draw.rect(self.screen, (100,100,100), self.fps_slider)
        # (We would draw slider knob and current FPS value here)

    def update(self, dt):
        """
        Update logic per frame. dt is elapsed time in seconds.
        Could be used to update playback animation timer, etc.
        """
        pass  # (In a full implementation, we might advance preview here.)

# Example integration with main loop (pseudocode, not full app):
#
# screen = pygame.display.set_mode((800, 600))
# editor = PixelEditor(screen)
# clock = pygame.time.Clock()
# running = True
# while running:
#     dt = clock.tick(60) / 1000.0
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False
#         editor.handle_event(event)
#     editor.draw()
#     pygame.display.flip()
