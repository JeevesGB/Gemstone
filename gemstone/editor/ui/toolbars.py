from PyQt6.QtWidgets import QToolBar

def build_toolbars(window):
    toolbar = QToolBar("Tools")
    toolbar.addAction("Select")
    toolbar.addAction("Brush")
    toolbar.addAction("Face")
    toolbar.addSeparator()
    toolbar.addAction("Grid +")
    toolbar.addAction("Grid -")

    window.addToolBar(toolbar)
