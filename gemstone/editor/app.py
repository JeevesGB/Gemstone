import sys
from PyQt6.QtWidgets import QApplication
from editor.main_window import EditorMainWindow

def run_editor():
    app = QApplication(sys.argv)

    window = EditorMainWindow()
    window.show()

    sys.exit(app.exec())
