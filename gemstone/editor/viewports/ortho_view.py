from PyQt6.QtCore import Qt, QPoint
from OpenGL.GL import *
import numpy as np

class OrthoView(BaseView):

    def __init__(self, axis):
        super().__init__()
        self.axis = axis
        self.camera = OrthoCamera()
        self.last_mouse = QPoint()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        factor = 1.1 if delta > 0 else 0.9
        self.camera.zoom *= factor
        self.update()

    def mousePressEvent(self, event):
        self.last_mouse = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.MiddleButton:
            delta = event.pos() - self.last_mouse
            self.camera.offset += np.array([delta.x(), -delta.y()]) / self.camera.zoom
            self.last_mouse = event.pos()
            self.update()
def draw_grid(self):
    spacing = 64
    size = 4096

    glColor3f(0.25, 0.25, 0.25)
    glBegin(GL_LINES)

    for i in range(-size, size, spacing):
        glVertex2f(i, -size)
        glVertex2f(i, size)
        glVertex2f(-size, i)
        glVertex2f(size, i)

    glEnd()
