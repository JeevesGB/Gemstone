import pygame
from gemstone.engine import Scene

class MainMenu(Scene):
    def __init__(self):
        super().__init__()
        self.options = ["Editor", "Demo", "Animation Editor", "Quit"]
        self.selected = 0
        self.font = pygame.font.SysFont("Arial", 32)

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                self.activate_option()

    def activate_option(self):
        option = self.options[self.selected]
        if option == "Editor":
            self.engine.change_scene("editor")
        elif option == "Demo":
            self.engine.change_scene("demo")
        elif option == "Animation Editor":
            self.engine.change_scene("anim")
        elif option == "Quit":
            self.engine.quit()

    def update(self, dt: int):
        pass

    def draw(self, screen: pygame.Surface):
        screen.fill((30, 30, 30))
        for i, option in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected else (200, 200, 200)
            text = self.font.render(option, True, color)
            screen.blit(text, (100, 100 + i * 50))


if __name__ == "__main__":
    app = MainMenu()
    app.mainloop()
