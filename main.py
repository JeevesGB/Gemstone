# main.py
from gemstone.engine import GameEngine
from gemstone.editor import EditorScene
from gemstone.demo import DemoScene
from gemstone.pixel_editor import PixelEditor
from gemstone.animation_manager import Animation
from gemstone.animation_editor import AnimationEditorScene

def main():
    engine = GameEngine()
    engine.add_scene("editor", EditorScene())
    engine.add_scene("demo", DemoScene())
    engine.add_scene("anim", AnimationEditorScene())
    engine.run("editor")

if __name__ == "__main__":
    main()
