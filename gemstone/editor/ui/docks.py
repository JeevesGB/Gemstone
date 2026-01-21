from PyQt6.QtWidgets import QDockWidget
from PyQt6.QtCore import Qt
from editor.widgets.texture_browser import TextureBrowserWidget

def build_docks(window):
    texture_dock = QDockWidget("Textures", window)
    texture_dock.setAllowedAreas(
        Qt.DockWidgetArea.BottomDockWidgetArea |
        Qt.DockWidgetArea.LeftDockWidgetArea |
        Qt.DockWidgetArea.RightDockWidgetArea
    )

    texture_browser = TextureBrowserWidget()
    texture_dock.setWidget(texture_browser)

    window.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, texture_dock)
