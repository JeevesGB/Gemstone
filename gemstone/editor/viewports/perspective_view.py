from OpenGL.GL import *
from OpenGL.GLU import *
from editor.viewports.base_view import BaseView

class PerspectiveView(BaseView):
    def initializeGL(self):
        super().initializeGL()
        glClearColor(0.15, 0.15, 0.18, 1)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, self.width() / max(1, self.height()), 1, 10000)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0, -128, -512)
