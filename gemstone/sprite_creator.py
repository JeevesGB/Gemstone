import pygame
import os
from collections import deque

class SpriteEditor:
    def __init__(self, screen, grid_size=32, cell_size=16):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 20)

        # Canvas settings
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.canvas_width = grid_size * cell_size
        self.canvas_height = grid_size * cell_size
        
        # UI layout constants
        self.UI_WIDTH = 500
        self.MARGIN = 50
        
        # Position canvas to leave room for UI on the right
        self.canvas_rect = pygame.Rect(self.MARGIN, self.MARGIN, 
                                     self.canvas_width, self.canvas_height)

        # Canvas grid
        self.grid = [[(255,255,255) for _ in range(grid_size)] for _ in range(grid_size)]

        # Tools and palette
        self.current_color = (0,0,0)
        self.palette = [(0,0,0), (255,0,0), (0,255,0), (0,0,255),
                        (255,255,0), (255,165,0), (255,192,203), (255,255,255)]
        self.tools = ["Pencil", "Eraser", "Fill", "Color Picker"]
        self.current_tool = "Pencil"

        # UI buttons
        self.buttons = []
        self.create_ui_buttons()

        # File input mode
        self.input_mode = None
        self.filename_input = ""

        # Ensure assets/sprites exists
        os.makedirs("assets/sprites", exist_ok=True)

    # ---------------------- Main Loop ----------------------
    def run(self):
        running = True
        mouse_down = False

        while running:
            self.screen.fill((220, 220, 220))
            mx, my = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.input_mode is None:
                        mouse_down = True
                        result = self.handle_mouse(event.pos, event.button)
                        if result:
                            return result
                elif event.type == pygame.MOUSEBUTTONUP:
                    mouse_down = False
                elif event.type == pygame.KEYDOWN:
                    if self.input_mode:
                        self.handle_text_input(event)
                    else:
                        result = self.handle_key_input(event)
                        if result:
                            return result

            if pygame.mouse.get_pressed()[0] and mouse_down and self.input_mode is None:
                self.handle_mouse((mx,my), 1)

            # Draw
            self.draw_canvas()
            self.draw_ui()
            if self.input_mode:
                self.draw_filename_input()

            pygame.display.flip()
            self.clock.tick(60)

    # ---------------------- Input Handlers ----------------------
    def handle_mouse(self, pos, button):
        x, y = pos

        # Check if clicked a button first
        for btn in self.buttons:
            if btn["rect"].collidepoint(pos):
                result = btn["action"]()
                if result:
                    return result

        # Click inside canvas
        if self.canvas_rect.collidepoint(pos):
            col = (x - self.canvas_rect.x) // self.cell_size
            row = (y - self.canvas_rect.y) // self.cell_size
            if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
                if self.current_tool == "Pencil":
                    self.grid[row][col] = self.current_color
                elif self.current_tool == "Eraser":
                    self.grid[row][col] = (255,255,255)
                elif self.current_tool == "Color Picker":
                    self.current_color = self.grid[row][col]
                elif self.current_tool == "Fill":
                    self.flood_fill(row, col, self.grid[row][col], self.current_color)

    def handle_key_input(self, event):
        if event.key == pygame.K_p:
            self.current_tool = "Pencil"
        elif event.key == pygame.K_e:
            self.current_tool = "Eraser"
        elif event.key == pygame.K_f:
            self.current_tool = "Fill"
        elif event.key == pygame.K_c:
            self.current_tool = "Color Picker"
        elif event.key == pygame.K_s:
            self.input_mode = "save"
            self.filename_input = ""
        elif event.key == pygame.K_l:
            self.input_mode = "load"
            self.filename_input = ""
        elif event.key == pygame.K_ESCAPE:
            return "menu"

    def handle_text_input(self, event):
        if event.key == pygame.K_RETURN:
            if self.filename_input.strip():
                if self.input_mode == "save":
                    self.save_sprite(self.filename_input.strip())
                elif self.input_mode == "load":
                    self.load_sprite(self.filename_input.strip())
            self.input_mode = None
        elif event.key == pygame.K_BACKSPACE:
            self.filename_input = self.filename_input[:-1]
        elif event.key == pygame.K_ESCAPE:
            self.input_mode = None
        else:
            if len(self.filename_input) < 20:
                self.filename_input += event.unicode

    # ---------------------- UI ----------------------
    def create_ui_buttons(self):
        # UI panel starts after canvas + margin
        ui_start_x = self.canvas_rect.right + self.MARGIN
        
        # Color palette
        y = 30
        color_size = 24
        colors_per_row = 2
        
        for i, color in enumerate(self.palette):
            col = i % colors_per_row
            row = i // colors_per_row
            rect = pygame.Rect(ui_start_x + col * (color_size + 5), 
                             y + row * (color_size + 5), 
                             color_size, color_size)
            self.buttons.append({"rect": rect, "color": color, "type": "color",
                               "action": lambda c=color: self.select_color(c)})

        # Tools
        tool_y = y + len(self.palette) // colors_per_row * (color_size + 5) + 30
        for i, tool in enumerate(self.tools):
            rect = pygame.Rect(ui_start_x, tool_y + i * 35, 120, 30)
            self.buttons.append({"rect": rect, "text": tool, "type": "tool",
                               "action": lambda t=tool: self.select_tool(t)})

        # Action buttons
        action_y = tool_y + len(self.tools) * 35 + 20
        actions = [
            ("Clear", self.clear_canvas),
            ("Save (S)", lambda: self.start_input_mode("save")),
            ("Load (L)", lambda: self.start_input_mode("load")),
            ("Back", self.back_to_menu)
        ]
        
        for i, (text, action) in enumerate(actions):
            rect = pygame.Rect(ui_start_x, action_y + i * 35, 120, 30)
            self.buttons.append({"rect": rect, "text": text, "type": "action",
                               "action": action})

    def draw_ui(self):
        ui_start_x = self.canvas_rect.right + self.MARGIN
        
        # Draw UI background panel
        ui_rect = pygame.Rect(ui_start_x - 10, 10, self.UI_WIDTH, 
                             self.canvas_height + 20)
        pygame.draw.rect(self.screen, (240, 240, 240), ui_rect)
        pygame.draw.rect(self.screen, (180, 180, 180), ui_rect, 2)
        
        # Title sections
        y_offset = 20
        
        # Colors section
        title_text = pygame.font.SysFont("arial", 16, bold=True).render("Colors", True, (60, 60, 60))
        self.screen.blit(title_text, (ui_start_x, y_offset))
        
        # Tools section
        tools_y = 30 + len(self.palette) // 2 * 29 + 20
        title_text = pygame.font.SysFont("arial", 16, bold=True).render("Tools", True, (60, 60, 60))
        self.screen.blit(title_text, (ui_start_x, tools_y))
        
        # Actions section
        actions_y = tools_y + len(self.tools) * 35 + 10
        title_text = pygame.font.SysFont("arial", 16, bold=True).render("Actions", True, (60, 60, 60))
        self.screen.blit(title_text, (ui_start_x, actions_y))

        # Draw buttons
        for btn in self.buttons:
            rect = btn["rect"]
            
            if btn.get("type") == "color":
                # Color palette buttons
                color = btn.get("color", (100, 100, 100))
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (0, 0, 0), rect, 2)
                # Highlight current color
                if color == self.current_color:
                    pygame.draw.rect(self.screen, (255, 255, 255), rect, 3)
                    
            elif btn.get("type") == "tool":
                # Tool buttons
                is_current = btn["text"] == self.current_tool
                bg_color = (100, 150, 255) if is_current else (200, 200, 200)
                text_color = (255, 255, 255) if is_current else (0, 0, 0)
                
                pygame.draw.rect(self.screen, bg_color, rect)
                pygame.draw.rect(self.screen, (100, 100, 100), rect, 1)
                text_surf = self.font.render(btn["text"], True, text_color)
                text_rect = text_surf.get_rect(center=rect.center)
                self.screen.blit(text_surf, text_rect)
                
            else:
                # Action buttons
                pygame.draw.rect(self.screen, (180, 180, 180), rect)
                pygame.draw.rect(self.screen, (120, 120, 120), rect, 1)
                text_surf = self.font.render(btn["text"], True, (0, 0, 0))
                text_rect = text_surf.get_rect(center=rect.center)
                self.screen.blit(text_surf, text_rect)

        # Status info at bottom
        status_y = self.canvas_rect.bottom - 60
        tool_text = self.font.render(f"Tool: {self.current_tool}", True, (0, 0, 0))
        self.screen.blit(tool_text, (self.MARGIN, status_y))
        
        # Current color indicator
        color_rect = pygame.Rect(self.MARGIN + 120, status_y - 2, 34, 24)
        pygame.draw.rect(self.screen, self.current_color, color_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), color_rect, 2)
        
        # Shortcuts info
        shortcuts_y = status_y + 30
        shortcuts_text = pygame.font.SysFont("arial", 14).render(
            "Shortcuts: P=Pencil E=Eraser F=Fill C=Color Picker S=Save L=Load ESC=Menu", 
            True, (100, 100, 100))
        self.screen.blit(shortcuts_text, (self.MARGIN, shortcuts_y))

    def draw_canvas(self):
        # Draw canvas background
        pygame.draw.rect(self.screen, (255, 255, 255), self.canvas_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), self.canvas_rect, 2)
        
        # Draw grid and pixels
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                rect = pygame.Rect(self.canvas_rect.x + col * self.cell_size,
                                 self.canvas_rect.y + row * self.cell_size,
                                 self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, self.grid[row][col], rect)
                # Light grid lines
                pygame.draw.rect(self.screen, (230, 230, 230), rect, 1)

    def update_layout(self):
        sw, sh = self.screen.get_size()

    # Keep canvas square and centered vertically
        max_canvas_size = min(sw // 2, sh - 2 * self.MARGIN)
        self.cell_size = max_canvas_size // self.grid_size
        self.canvas_width = self.canvas_height = self.cell_size * self.grid_size
        self.canvas_rect = pygame.Rect(
            self.MARGIN,
            (sh - self.canvas_height) // 2,  # center vertically
            self.canvas_width,
            self.canvas_height
        )

    # UI starts to the right of canvas
        self.ui_start_x = self.canvas_rect.right + self.MARGIN
        self.ui_rect = pygame.Rect(self.ui_start_x, self.MARGIN,
                                   sw - self.ui_start_x - self.MARGIN,
                                   sh - 2 * self.MARGIN)

        

    def draw_filename_input(self):
        # Center the input dialog
        dialog_width = 400
        dialog_height = 100
        dialog_x = (self.screen.get_width() - dialog_width) // 2
        dialog_y = (self.screen.get_height() - dialog_height) // 2
        
        # Dialog background
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
        pygame.draw.rect(self.screen, (60, 60, 60), dialog_rect)
        pygame.draw.rect(self.screen, (200, 200, 200), dialog_rect, 3)
        
        # Input field
        input_rect = pygame.Rect(dialog_x + 20, dialog_y + 40, dialog_width - 40, 30)
        pygame.draw.rect(self.screen, (255, 255, 255), input_rect)
        pygame.draw.rect(self.screen, (150, 150, 150), input_rect, 2)
        
        # Labels and text
        label = "Save sprite as:" if self.input_mode == "save" else "Load sprite:"
        label_text = self.font.render(label, True, (255, 255, 255))
        self.screen.blit(label_text, (dialog_x + 20, dialog_y + 15))
        
        input_text = self.font.render(self.filename_input + "|", True, (0, 0, 0))
        self.screen.blit(input_text, (input_rect.x + 5, input_rect.y + 5))
        
        # Instructions
        instruction = "Press Enter to confirm, ESC to cancel"
        inst_text = pygame.font.SysFont("arial", 14).render(instruction, True, (200, 200, 200))
        self.screen.blit(inst_text, (dialog_x + 20, dialog_y + 75))

    # ---------------------- Tool Actions ----------------------
    def select_color(self, color):
        self.current_color = color

    def select_tool(self, tool):
        self.current_tool = tool

    def clear_canvas(self):
        self.grid = [[(255, 255, 255) for _ in range(self.grid_size)] for _ in range(self.grid_size)]

    def start_input_mode(self, mode):
        self.input_mode = mode
        self.filename_input = ""

    def back_to_menu(self):
        return "menu"

    def flood_fill(self, row, col, target_color, replacement_color):
        if target_color == replacement_color:
            return
        q = deque()
        q.append((row, col))
        visited = set()
        
        while q:
            r, c = q.popleft()
            if (r, c) in visited:
                continue
            if not (0 <= r < self.grid_size and 0 <= c < self.grid_size):
                continue
            if self.grid[r][c] != target_color:
                continue
                
            visited.add((r, c))
            self.grid[r][c] = replacement_color
            
            # Add neighbors
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if (nr, nc) not in visited:
                    q.append((nr, nc))

    # ---------------------- File Actions ----------------------
    def save_sprite(self, filename):
        try:
            surface = pygame.Surface((self.grid_size, self.grid_size))
            for r in range(self.grid_size):
                for c in range(self.grid_size):
                    surface.set_at((c, r), self.grid[r][c])
            
            if not filename.endswith(".png"):
                filename += ".png"
            
            filepath = os.path.join("assets/sprites", filename)
            pygame.image.save(surface, filepath)
            print(f"Saved: {filename}")
        except Exception as e:
            print(f"Error saving {filename}: {e}")

    def load_sprite(self, filename):
        try:
            if not filename.endswith(".png"):
                filename += ".png"
            
            path = os.path.join("assets/sprites", filename)
            if os.path.exists(path):
                img = pygame.image.load(path)
                img = pygame.transform.scale(img, (self.grid_size, self.grid_size))
                
                for r in range(self.grid_size):
                    for c in range(self.grid_size):
                        color = img.get_at((c, r))[:3]
                        self.grid[r][c] = color
                        
                print(f"Loaded: {filename}")
            else:
                print(f"File not found: {filename}")
        except Exception as e:
            print(f"Error loading {filename}: {e}")