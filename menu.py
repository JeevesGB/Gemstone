import pygame
import sys


class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 40)

        self.buttons = [
            {"text": "Start Editor", "rect": pygame.Rect(300, 200, 200, 60)},
            {"text": "Quit", "rect": pygame.Rect(300, 300, 200, 60)},
        ]

        self.selected_index = 0  # first button highlighted by default

    def run(self):
        running = True
        while running:
            self.screen.fill((30, 30, 30))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        self.selected_index = (self.selected_index + 1) % len(self.buttons)
                    elif event.key == pygame.K_UP:
                        self.selected_index = (self.selected_index - 1) % len(self.buttons)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.activate_button(self.buttons[self.selected_index])

            self.draw_buttons()
            pygame.display.flip()
            self.clock.tick(60)

    def draw_buttons(self):
        mouse_pos = pygame.mouse.get_pos()
        for i, button in enumerate(self.buttons):
            # Default color
            color = (100, 100, 100)

            # Hover effect with mouse
            if button["rect"].collidepoint(mouse_pos):
                color = (150, 150, 150)

            # Keyboard-selected button gets highlight
            if i == self.selected_index:
                color = (200, 200, 0)

            pygame.draw.rect(self.screen, color, button["rect"])
            text_surf = self.font.render(button["text"], True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=button["rect"].center)
            self.screen.blit(text_surf, text_rect)

    def handle_click(self, pos):
        for i, button in enumerate(self.buttons):
            if button["rect"].collidepoint(pos):
                self.selected_index = i
                self.activate_button(button)

    def activate_button(self, button):
        if button["text"] == "Start Editor":
            print("Editor will start (not implemented yet)")
        elif button["text"] == "Quit":
            pygame.quit()
            sys.exit()
