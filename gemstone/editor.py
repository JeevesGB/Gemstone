# gemstone/editor.py
import pygame
from .engine import Scene
from .config import BACKGROUND, GRID_COLOR, CANVAS_W, CANVAS_H, SPRITE_PATH
from .util import draw_text, surface_from_grid, clone_grid, within_rect
import os

TOOL_PENCIL = 0
TOOL_ERASER = 1
TOOL_FILL = 2
TOOL_EYEDROPPER = 3

PALETTE = [
    (0,0,0,255), (255,255,255,255), (255,0,0,255), (0,255,0,255), (0,0,255,255),
    (255,255,0,255), (255,0,255,255), (0,255,255,255),
    (128,128,128,255), (64,64,64,255), (192,192,192,255),
    (139,69,19,255), (255,165,0,255), (255,192,203,255), (173,216,230,255), (124,252,0,255)
]

class EditorScene(Scene):
    def __init__(self):
        super().__init__()
        self.window_size = (800, 600)
        # Get actual window size from engine if available
        if hasattr(self.engine, 'window_size'):
            self.window_size = self.engine.window_size
        
        self.ui_panel_width = 250
        self.zoom_levels = [8, 12, 16, 20]  # pixel size
        self.zoom_index = 0
        self.show_grid = True
        self.canvas_w = CANVAS_W
        self.canvas_h = CANVAS_H
        self.clear_canvas()

        self.primary = PALETTE[0]
        self.secondary = (0,0,0,0)  # transparent
        self.tool = TOOL_PENCIL

        self.undo_stack = []
        self.redo_stack = []

        # UI rectangles (computed in layout)
        self.canvas_rect = pygame.Rect(20, 60, 0, 0)
        self.palette_rects = []
        self.buttons = {}

    def clear_canvas(self):
        self.grid = [[(0,0,0,0) for _ in range(self.canvas_w)] for _ in range(self.canvas_h)]

    # ---- Scene hooks ----
    def on_enter(self):
        self.compute_layout()

    def on_exit(self):
        pass

    # ---- Layout/UI ----
    def compute_layout(self):
        px = self.zoom_levels[self.zoom_index]
        self.canvas_rect.width = self.canvas_w * px
        self.canvas_rect.height = self.canvas_h * px
        
        # Center canvas in the available space (left of UI panel)
        canvas_area_width = self.window_size[0] - self.ui_panel_width
        canvas_center_x = canvas_area_width // 2
        canvas_center_y = self.window_size[1] // 2
        
        # Position canvas centered in left area
        self.canvas_rect.centerx = canvas_center_x
        self.canvas_rect.centery = canvas_center_y
        
        # Ensure canvas doesn't go off-screen
        if self.canvas_rect.left < 20:
            self.canvas_rect.left = 20
        if self.canvas_rect.top < 100:  # Leave room for header text
            self.canvas_rect.top = 100

        # Palette layout - positioned relative to window width
        self.palette_rects = []
        start_x = self.window_size[0] - self.ui_panel_width + 20  # Dynamic positioning
        start_y = 90
        box = 28
        pad = 6
        for i, col in enumerate(PALETTE):
            r = pygame.Rect(start_x + (i%4)*(box+pad), start_y + (i//4)*(box+pad), box, box)
            self.palette_rects.append((r, col))

        # Buttons - positioned relative to window width
        bx = start_x
        by = start_y + 5*(box+pad) + 10
        bw, bh, gap = 120, 30, 8
        labels = [
            ("[1] Pencil", "pencil"),
            ("[2] Eraser", "eraser"),
            ("[3] Fill", "fill"),
            ("[4] Eyedrop", "pick"),
            ("[Enter] Export", "export"),
            ("[Ctrl+S] Save", "save"),
            ("[Ctrl+O] Load", "load"),
            ("[Ctrl+N] New", "new"),
            ("[Z] Zoom", "zoom"),
            ("[G] Grid", "grid"),
        ]
        self.buttons = {}
        row = 0
        for label, key in labels:
            rect = pygame.Rect(bx, by + row*(bh+gap), bw, bh)
            self.buttons[key] = (rect, label)
            row += 1

    # ---- Event handling ----
    def handle_event(self, event):
        mods = pygame.key.get_mods()
        ctrl = mods & pygame.KMOD_CTRL

        if event.type == pygame.VIDEORESIZE:
            # Set minimum size to prevent UI overlap
            min_width = 600
            min_height = 400
            self.window_size = (max(min_width, event.w), max(min_height, event.h))
            # Trigger layout recalculation
            self.compute_layout()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # back to game demo if exists
                self.engine.set_scene("demo", surface_from_grid(self.grid))
            elif ctrl and event.key == pygame.K_s:
                self.save_png()
            elif ctrl and event.key == pygame.K_o:
                self.load_png()
            elif ctrl and event.key == pygame.K_n:
                self.push_undo()
                self.clear_canvas()
            elif ctrl and event.key == pygame.K_z:
                self.undo()
            elif ctrl and event.key == pygame.K_y:
                self.redo()
            elif event.key == pygame.K_z:
                self.zoom_index = (self.zoom_index + 1) % len(self.zoom_levels)
                self.compute_layout()
            elif event.key == pygame.K_g:
                self.show_grid = not self.show_grid
            elif event.key == pygame.K_RETURN:
                self.engine.set_scene("demo", surface_from_grid(self.grid))
            elif event.key == pygame.K_1:
                self.tool = TOOL_PENCIL
            elif event.key == pygame.K_2:
                self.tool = TOOL_ERASER
            elif event.key == pygame.K_3:
                self.tool = TOOL_FILL
            elif event.key == pygame.K_4:
                self.tool = TOOL_EYEDROPPER

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button in (1, 3):
                # Check palette click
                for rect, col in self.palette_rects:
                    if rect.collidepoint(event.pos):
                        self.primary = col
                        return

                # Check buttons
                for key, (rect, label) in self.buttons.items():
                    if rect.collidepoint(event.pos):
                        self.click_button(key)
                        return

                # Canvas painting
                if self.canvas_rect.collidepoint(event.pos):
                    gx, gy = self.screen_to_grid(event.pos)
                    self.push_undo()
                    if event.button == 1:
                        self.paint_at(gx, gy, primary=True)
                    else:
                        self.paint_at(gx, gy, primary=False)

        elif event.type == pygame.MOUSEMOTION:
            if any(pygame.mouse.get_pressed()):
                if self.canvas_rect.collidepoint(event.pos):
                    gx, gy = self.screen_to_grid(event.pos)
                    if pygame.mouse.get_pressed()[0]:
                        self.paint_at(gx, gy, primary=True, dragging=True)
                    elif pygame.mouse.get_pressed()[2]:
                        self.paint_at(gx, gy, primary=False, dragging=True)

    def click_button(self, key):
        if key == "pencil":
            self.tool = TOOL_PENCIL
        elif key == "eraser":
            self.tool = TOOL_ERASER
        elif key == "fill":
            self.tool = TOOL_FILL
        elif key == "pick":
            self.tool = TOOL_EYEDROPPER
        elif key == "export":
            self.engine.set_scene("demo", surface_from_grid(self.grid))
        elif key == "save":
            self.save_png()
        elif key == "load":
            self.load_png()
        elif key == "new":
            self.push_undo()
            self.clear_canvas()
        elif key == "zoom":
            self.zoom_index = (self.zoom_index + 1) % len(self.zoom_levels)
            self.compute_layout()
        elif key == "grid":
            self.show_grid = not self.show_grid

    # ---- Paint ops ----
    def screen_to_grid(self, pos):
        px = self.zoom_levels[self.zoom_index]
        x = (pos[0] - self.canvas_rect.x) // px
        y = (pos[1] - self.canvas_rect.y) // px
        x = max(0, min(self.canvas_w-1, int(x)))
        y = max(0, min(self.canvas_h-1, int(y)))
        return x, y

    def paint_at(self, gx, gy, primary=True, dragging=False):
        if not (0 <= gx < self.canvas_w and 0 <= gy < self.canvas_h):
            return
        color_primary = self.primary
        color_secondary = (0,0,0,0)

        if self.tool == TOOL_PENCIL:
            self.grid[gy][gx] = color_primary if primary else color_secondary
        elif self.tool == TOOL_ERASER:
            self.grid[gy][gx] = (0,0,0,0)
        elif self.tool == TOOL_FILL:
            target = self.grid[gy][gx]
            repl = color_primary
            if target != repl:
                self.flood_fill(gx, gy, target, repl)
        elif self.tool == TOOL_EYEDROPPER:
            self.primary = self.grid[gy][gx]

    def flood_fill(self, x, y, target, repl):
        w, h = self.canvas_w, self.canvas_h
        stack = [(x,y)]
        while stack:
            cx, cy = stack.pop()
            if not (0 <= cx < w and 0 <= cy < h): continue
            if self.grid[cy][cx] != target: continue
            self.grid[cy][cx] = repl
            stack.extend([(cx+1,cy),(cx-1,cy),(cx,cy+1),(cx,cy-1)])

    # ---- Undo/Redo ----
    def push_undo(self):
        self.undo_stack.append(clone_grid(self.grid))
        if len(self.undo_stack) > 50:
            self.undo_stack.pop(0)
        self.redo_stack.clear()

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(clone_grid(self.grid))
            self.grid = self.undo_stack.pop()

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(clone_grid(self.grid))
            self.grid = self.redo_stack.pop()

    # ---- File I/O ----
    def save_png(self):
        surf = surface_from_grid(self.grid)
        os.makedirs(os.path.dirname(SPRITE_PATH), exist_ok=True)
        pygame.image.save(surf, SPRITE_PATH)

    def load_png(self):
        if os.path.exists(SPRITE_PATH):
            img = pygame.image.load(SPRITE_PATH).convert_alpha()
            if img.get_width() == self.canvas_w and img.get_height() == self.canvas_h:
                self.push_undo()
                for y in range(self.canvas_h):
                    for x in range(self.canvas_w):
                        self.grid[y][x] = img.get_at((x,y))
            else:
                print("PNG size does not match canvas. Edit config or resize image.")

    # ---- Update/Draw ----
    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill(BACKGROUND)
        # Title / Help
        draw_text(surface, "Gemstone Editor", (20, 16), (240,240,240), 22)
        draw_text(surface, [
            "Tools: [1] Pencil [2] Eraser [3] Fill [4] Eyedropper",
            "Ctrl+S Save  Ctrl+O Load  Ctrl+N New  Ctrl+Z/Y Undo/Redo",
            "Enter: Export to Demo   Z: Zoom   G: Grid   Esc: Demo",
        ], (20, 32), (180,180,180), 16)

        # Canvas
        px = self.zoom_levels[self.zoom_index]
        for y in range(self.canvas_h):
            for x in range(self.canvas_w):
                color = self.grid[y][x]
                rx = self.canvas_rect.x + x*px
                ry = self.canvas_rect.y + y*px
                pygame.draw.rect(surface, color, (rx, ry, px, px))
        if self.show_grid:
            for y in range(self.canvas_h+1):
                ypix = self.canvas_rect.y + y*px
                pygame.draw.line(surface, GRID_COLOR, (self.canvas_rect.x, ypix), (self.canvas_rect.right, ypix), 1)
            for x in range(self.canvas_w+1):
                xpix = self.canvas_rect.x + x*px
                pygame.draw.line(surface, GRID_COLOR, (xpix, self.canvas_rect.y), (xpix, self.canvas_rect.bottom), 1)

        # Palette
        for rect, col in self.palette_rects:
            pygame.draw.rect(surface, col, rect)
            pygame.draw.rect(surface, (230,230,230), rect, 2)
        if self.palette_rects:  # Only draw label if palette exists
            draw_text(surface, "Palette", (self.palette_rects[0][0].x, self.palette_rects[0][0].y - 22))

        # Buttons
        for key, (rect, label) in self.buttons.items():
            pygame.draw.rect(surface, (55,55,55), rect, border_radius=6)
            pygame.draw.rect(surface, (120,120,120), rect, 1, border_radius=6)
            draw_text(surface, label, (rect.x+8, rect.y+6))

        # Current color preview - positioned relative to window
        cx = self.window_size[0] - self.ui_panel_width + 20
        cy = self.window_size[1] - 90  # 90px from bottom
        swatch = pygame.Rect(cx, cy, 64, 64)
        pygame.draw.rect(surface, self.primary, swatch)
        pygame.draw.rect(surface, (230,230,230), swatch, 2)
        draw_text(surface, "Current", (cx, cy - 20))