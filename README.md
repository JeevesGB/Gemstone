# Gemstone

Gemstone is a tiny Python 2D game engine with an **integrated pixel editor** (built on pygame).
It runs on Windows/Mac/Linux/Chromebooks (via Linux/Crostini).

## Features
- Game engine core: window, scenes, input, timing (60 FPS target)
- Scene system: switch between editor / game
- Sprite Editor:
  - Grid-based pixel art canvas (default 32x32)
  - Pencil, Eraser, Fill (bucket)
  - Color palette + color picker (eyedropper)
  - Zoom (1x, 2x, 4x, 8x preview)
  - Undo / Redo
  - Save / Load PNG
  - Export to engine sprite (used in Demo scene)
- Simple demo scene showing how to use the created sprite

## Quick start
```bash
python3 -m venv venv
source venv/bin/activate  # (Windows: venv\Scripts\activate)
pip install -r requirements.txt
python main.py
```

## Controls (Editor)
- **Left Click**: draw with current tool/color
- **Right Click**: secondary tool (Eraser)
- **Tools**: [1]=Pencil, [2]=Eraser, [3]=Fill, [4]=Eyedropper
- **Palette**: click a color box to select
- **Zoom**: Z switches between 1x/2x/4x/8x (preview scale)
- **Undo / Redo**: Ctrl+Z / Ctrl+Y
- **Save PNG**: Ctrl+S → saves to `assets/sprites/sprite.png`
- **Load PNG**: Ctrl+O → loads `assets/sprites/sprite.png` (must match canvas size)
- **Export to Game**: Enter → switches to Demo scene using your current canvas
- **New Canvas**: Ctrl+N → clears
- **Grid Toggle**: G
- **Quit**: Esc

## Controls (Demo scene)
- Arrow keys to move the sprite
- Esc to return to editor

## Notes
- PNG loads should match the editor canvas size (default 32x32). You can change the size in `config.py`.
- This is a starter engine meant to be hacked and expanded.
