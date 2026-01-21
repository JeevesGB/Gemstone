def build_menus(window):
    menubar = window.menuBar()

    file_menu = menubar.addMenu("File")
    file_menu.addAction("New")
    file_menu.addAction("Open")
    file_menu.addAction("Save")
    file_menu.addSeparator()
    file_menu.addAction("Exit", window.close)

    edit_menu = menubar.addMenu("Edit")
    edit_menu.addAction("Undo")
    edit_menu.addAction("Redo")

    view_menu = menubar.addMenu("View")
    view_menu.addAction("Center View")
    view_menu.addAction("Toggle Grid")

    build_menu = menubar.addMenu("Build")
    build_menu.addAction("Compile Map")

    help_menu = menubar.addMenu("Help")
    help_menu.addAction("About")
