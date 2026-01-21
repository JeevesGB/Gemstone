from OpenGL.GL import *
from PyQt6.QtCore import Qt
from editor.viewports.base_view import BaseView
from editor.state import STATE
from editor.geometry.brush import Brush


class OrthoView(BaseView):
    def __init__(self, axis):
        super().__init__()
        self.axis = axis  # "Top", "Side", "Front"
        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0

        self.drag_start = None
        self.drag_current = None
        self.panning = False

    # -----------------------------
    # Coordinate helpers
    # -----------------------------

    def screen_to_world(self, x, y):
        w, h = self.width(), self.height()
        wx = (x - w / 2) / self.zoom + self.offset_x
        wy = (h / 2 - y) / self.zoom + self.offset_y
        return wx, wy

    def snap(self, v):
        g = STATE.grid_size
        return round(v / g) * g

    # -----------------------------
    # Mouse handling
    # -----------------------------

    def mousePressEvent(self, event):
        if event.buttons() & Qt.MouseButton.MiddleButton:
            self.panning = True
            self.last_mouse = event.position()
            return

        if STATE.active_tool == "brush" and event.buttons() & Qt.MouseButton.LeftButton:
            x, y = self.screen_to_world(event.position().x(), event.position().y())
            if STATE.snap:
                x, y = self.snap(x), self.snap(y)
            self.drag_start = (x, y)
            self.drag_current = (x, y)

    def mouseMoveEvent(self, event):
        if self.panning:
            delta = event.position() - self.last_mouse
            self.offset_x -= delta.x() / self.zoom
            self.offset_y += delta.y() / self.zoom
            self.last_mouse = event.position()
            self.update()
            return

        if self.drag_start:
            x, y = self.screen_to_world(event.position().x(), event.position().y())
            if STATE.snap:
                x, y = self.snap(x), self.snap(y)
            self.drag_current = (x, y)
            self.update()

    def mouseReleaseEvent(self, event):
        self.panning = False

        if self.drag_start and self.drag_current:
            self.commit_brush()
            self.drag_start = None
            self.drag_current = None
            self.update()

    def wheelEvent(self, event):
        delta = event.angleDelta().y() / 120
        self.zoom *= 1.1 ** delta
        self.update()

    # -----------------------------
    # Brush creation
    # -----------------------------

    def commit_brush(self):
        (x0, y0) = self.drag_start
        (x1, y1) = self.drag_current

        minx, maxx = min(x0, x1), max(x0, x1)
        miny, maxy = min(y0, y1), max(y0, y1)

        thickness = STATE.grid_size

        if self.axis == "Top":
            min_pt = (minx, miny, 0)
            max_pt = (maxx, maxy, thickness)

        elif self.axis == "Side":
            min_pt = (0, miny, minx)
            max_pt = (thickness, maxy, maxx)

        else:  # Front
            min_pt = (minx, 0, miny)
            max_pt = (maxx, thickness, maxy)

        brush = Brush(min_pt, max_pt)
        STATE.brushes.append(brush)

    # -----------------------------
    # Rendering
    # -----------------------------

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT)

        w, h = self.width(), self.height()
        hw = w / (2 * self.zoom)
        hh = h / (2 * self.zoom)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(
            -hw + self.offset_x,
             hw + self.offset_x,
            -hh + self.offset_y,
             hh + self.offset_y,
            -1, 1
        )

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        self.draw_grid()
        self.draw_brushes()
        self.draw_preview()

    def draw_grid(self):
        grid = STATE.grid_size
        extent = 8192

        glColor3f(0.25, 0.25, 0.25)
        glBegin(GL_LINES)
        for i in range(-extent, extent + 1, grid):
            glVertex2f(i, -extent)
            glVertex2f(i, extent)
            glVertex2f(-extent, i)
            glVertex2f(extent, i)
        glEnd()

    def draw_brushes(self):
        glColor3f(0.8, 0.8, 0.2)

        for brush in STATE.brushes:
            self.draw_brush_wire(brush)

    def draw_preview(self):
        if not self.drag_start or not self.drag_current:
            return

        glColor3f(0.2, 0.8, 1.0)
        glLineWidth(2)
        glBegin(GL_LINE_LOOP)

        x0, y0 = self.drag_start
        x1, y1 = self.drag_current

        glVertex2f(x0, y0)
        glVertex2f(x1, y0)
        glVertex2f(x1, y1)
        glVertex2f(x0, y1)

        glEnd()
        glLineWidth(1)

    def draw_brush_wire(self, brush):
        verts = brush.vertices()

        # project into this ortho plane
        def proj(v):
            x, y, z = v
            if self.axis == "Top":
                return x, y
            if self.axis == "Side":
                return z, y
            return x, z

        edges = [
            (0,1),(1,2),(2,3),(3,0),
            (4,5),(5,6),(6,7),(7,4),
            (0,4),(1,5),(2,6),(3,7)
        ]

        glBegin(GL_LINES)
        for a, b in edges:
            ax, ay = proj(verts[a])
            bx, by = proj(verts[b])
            glVertex2f(ax, ay)
            glVertex2f(bx, by)
        glEnd()
