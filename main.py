import pygame
from menu import Menu


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Gemstone")

    menu = Menu(screen)
    menu.run()

    pygame.quit()


if __name__ == "__main__":
    main()
