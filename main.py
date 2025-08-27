# main.py
from gemstone.engine import GameEngine
from gemstone.editor import EditorScene
from gemstone.demo import DemoScene
from gemstone.pixel_editor import PixelEditor
from gemstone.animation_manager import Animation
from gemstone.animation_editor import AnimationEditor
from gemstone.menu import MainMenu   # your menu scene

def main():
    engine = GameEngine()
    
    # Register all scenes
    engine.add_scene("menu", MainMenu())       # ✅ now registered
    engine.add_scene("editor", EditorScene())
    engine.add_scene("demo", DemoScene())
    engine.add_scene("anim", AnimationEditor())
    
    # Start at the menu
    engine.run("menu")

if __name__ == "__main__":
    main()
