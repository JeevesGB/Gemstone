from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *

class BaseView(QOpenGLWidget):

    def initializeGL(self):
        glClearColor(0.2, 0.2, 0.2, 1.0)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
