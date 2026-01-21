from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget

class TextureBrowserWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.list = QListWidget()
        self.list.addItems(["grass", "stone", "metal", "wood"])
        layout.addWidget(self.list)
