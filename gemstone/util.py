# gemstone/util.py
import pygame

def draw_text(surface, text, pos, color=(230,230,230), size=18):
    font = pygame.font.SysFont("consolas,monospace", size)
    if isinstance(text, str):
        txt = font.render(text, True, color)
        surface.blit(txt, pos)
    else:
        # multiline list
        y = pos[1]
        for line in text:
            txt = font.render(line, True, color)
            surface.blit(txt, (pos[0], y))
            y += txt.get_height() + 2

def surface_from_grid(grid):
    # grid: H x W of (r,g,b,a) or (r,g,b)
    h = len(grid)
    w = len(grid[0])
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        for x in range(w):
            surf.set_at((x,y), grid[y][x])
    return surf

def clone_grid(grid):
    return [row[:] for row in grid]

def within_rect(pos, rect):
    x,y = pos
    rx, ry, rw, rh = rect
    return (rx <= x < rx+rw) and (ry <= y < ry+rh)
