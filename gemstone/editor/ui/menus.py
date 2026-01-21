def build_menus(window):
    menu = window.menuBar()

    file_menu = menu.addMenu("File")
    file_menu.addAction("New")
    file_menu.addAction("Open")
    file_menu.addAction("Save")

    edit_menu = menu.addMenu("Edit")
    edit_menu.addAction("Undo")
    edit_menu.addAction("Redo")

    build_menu = menu.addMenu("Build")
    build_menu.addAction("Compile")
