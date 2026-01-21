from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QSplitter
)
from PyQt6.QtCore import Qt

from editor.viewports.perspective_view import PerspectiveView
from editor.viewports.ortho_view import OrthoView
from editor.ui.menus import build_menus
from editor.ui.toolbars import build_toolbars
from editor.ui.docks import build_docks


class EditorMainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Gemstone Level Editor")
        self.resize(1600, 900)

        build_menus(self)
        build_toolbars(self)
        self._build_central_views()
        build_docks(self)

    def _build_central_views(self):
        central = QWidget()
        self.setCentralWidget(central)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.view3d = PerspectiveView()
        splitter.addWidget(self.view3d)

        ortho_split = QSplitter(Qt.Orientation.Vertical)
        self.view_top = OrthoView("top")
        self.view_side = OrthoView("side")

        ortho_split.addWidget(self.view_top)
        ortho_split.addWidget(self.view_side)

        splitter.addWidget(ortho_split)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(splitter)

        central.setLayout(layout)
