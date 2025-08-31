import pygame

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 40)

        self.buttons = [
            {"text": "Sprite Editor", "rect": pygame.Rect(300, 100, 200, 60)},
            {"text": "DAW - alpha 0.00", "rect": pygame.Rect(100, 200, 150, 60)},
            {"text": "Quit", "rect": pygame.Rect(600, 200, 200, 60)},
        ]
        self.selected_index = 0

    def run(self):
        while True:
            self.screen.fill((30, 30, 30))
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    return self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        self.selected_index = (self.selected_index + 1) % len(self.buttons)
                    elif event.key == pygame.K_UP:
                        self.selected_index = (self.selected_index - 1) % len(self.buttons)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        return self.activate_button(self.buttons[self.selected_index])

            # Draw buttons
            for i, button in enumerate(self.buttons):
                color = (100, 100, 100)
                if button["rect"].collidepoint(mouse_pos):
                    color = (150, 150, 150)
                if i == self.selected_index:
                    color = (200, 200, 0)

                pygame.draw.rect(self.screen, color, button["rect"])
                text_surf = self.font.render(button["text"], True, (255, 255, 255))
                self.screen.blit(text_surf, text_surf.get_rect(center=button["rect"].center))

            pygame.display.flip()
            self.clock.tick(60)

    def handle_click(self, pos):
        for i, button in enumerate(self.buttons):
            if button["rect"].collidepoint(pos):
                self.selected_index = i
                return self.activate_button(button)
        return "menu"

    def activate_button(self, button):
        if button["text"] == "Sprite Editor":
            return "editor"
        elif button["text"] == "Quit":
            return "quit"
        return "menu"
