class EditorState:
    def __init__(self):
        self.active_tool = "select"
        self.grid_size = 64
        self.snap = True

        self.brushes = []
        self.active_brush = None

STATE = EditorState()
