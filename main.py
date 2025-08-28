import pygame
from menu import Menu
from gemstone.sprite_creator import SpriteEditor

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Gemstone")

    running = True
    current_scene = "menu"

    while running:
        if current_scene == "menu":
            menu = Menu(screen)
            next_scene = menu.run()
            current_scene = next_scene
        elif current_scene == "editor":
            editor = SpriteEditor(screen)
            next_scene = editor.run()
            current_scene = next_scene
        elif current_scene == "quit":
            running = False

    pygame.quit()


if __name__ == "__main__":
    main()
