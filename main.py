# main.py
from gemstone.engine import GameEngine
from gemstone.editor import EditorScene
from gemstone.demo import DemoScene

def main():
    engine = GameEngine()
    engine.add_scene("editor", EditorScene())
    engine.add_scene("demo", DemoScene())
    engine.run("editor")

if __name__ == "__main__":
    main()
