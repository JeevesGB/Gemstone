from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QSplitter
)
from PyQt6.QtCore import Qt

from editor.ui.menus import build_menus
from editor.ui.toolbars import build_toolbars
from editor.ui.docks import build_docks
from editor.viewports.perspective_view import PerspectiveView
from editor.viewports.ortho_view import OrthoView


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

        main_split = QSplitter(Qt.Orientation.Horizontal)

    # Left: 3D view
        self.view_3d = PerspectiveView()
        main_split.addWidget(self.view_3d)

    # Right: ortho views (Top / Front / Side)
        ortho_split = QSplitter(Qt.Orientation.Vertical)

        self.view_top = OrthoView("Top")
        self.view_front = OrthoView("Front")
        self.view_side = OrthoView("Side")

        ortho_split.addWidget(self.view_top)
        ortho_split.addWidget(self.view_front)
        ortho_split.addWidget(self.view_side)

        main_split.addWidget(ortho_split)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(main_split)

        central.setLayout(layout)

