from PyQt6.QtWidgets import QToolBar
from editor.state import STATE


def build_toolbars(window):
    toolbar = QToolBar("Tools")

    def set_tool(name):
        STATE.active_tool = name

    toolbar.addAction("Select", lambda: set_tool("select"))
    toolbar.addAction("Brush",  lambda: set_tool("brush"))
    toolbar.addAction("Face",   lambda: set_tool("face"))
    toolbar.addAction("Entity", lambda: set_tool("entity"))

    toolbar.addSeparator()

    toolbar.addAction("Grid +", lambda: setattr(STATE, "grid_size", STATE.grid_size * 2))
    toolbar.addAction("Grid -", lambda: setattr(STATE, "grid_size", max(1, STATE.grid_size // 2)))

    window.addToolBar(toolbar)
