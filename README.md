# Gemstone

**Gemstone** is a compact, Python-based 2D game engine with an integrated pixel editor, built using Pygame. It functions on Windows, macOS, Linux, and Chromebooks (via Crostini).

##  Features

- **Scene System**
  - Seamlessly switch between Editor and Game (Demo) scenes  
- **Sprite Editor**
  - Grid-based canvas (default 32×32)
  - Tools: Pencil, Eraser, Fill (bucket)
  - Color palette + Eyedropper tool
  - Zoom levels: 1×, 2×, 4×, 8× preview
  - Undo / Redo  
  - Save / Load PNG  
  - Export sprite to engine scene for instant use  

  
##  Quick Start
```bash
python3 -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

<<<<<<< HEAD
## Notes
- More features *TBC* 


## Credits 
- JEJ 
=======
##  Editor Controls

- **Left Click**: Draw using selected tool  
- **Right Click**: Use secondary tool (Eraser)  
- **Tool Keys**:
  - `1` → Pencil  
  - `2` → Eraser  
  - `3` → Fill  
  - `4` → Eyedropper  
- **Palette**: Click a color box to select color  
- **Zoom**: Press `Z` to cycle through zoom levels (1× → 2× → 4× → 8×)  
- **Undo / Redo**: `Ctrl+Z` / `Ctrl+Y`  
- **Save PNG**: `Ctrl+S` → saves to `assets/sprites/sprite.png`  
- **Load PNG**: `Ctrl+O` → loads from `assets/sprites/sprite.png` (must match canvas size)  
- **Export to Game**: `Enter` → switch to Demo scene using your sprite  
- **New Canvas**: `Ctrl+N` → clear canvas  
- **Grid Toggle**: `G` → show/hide grid  
- **Quit**: `Esc`

##  Demo (Game) Controls

- Use **Arrow Keys** to move the sprite  
- Press **Esc** to return to the Editor

---

##  Notes

- PNG loading requires images that match the canvas size (default: 32×32). You can customize the canvas size via `config.py`.  
- Gemstone is designed as a starter engine—feel free to hack, extend, and innovate!

---

##  Contributing

We welcome contributions! Here’s how to get started:

### Getting Started

1. **Fork the repository**  
2. **Clone your fork**:
   ```bash
   git clone https://github.com/<your-username>/Gemstone.git
   cd Gemstone
   ```
3. **Set up a virtual environment and install dependencies**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
4. **Create a new branch** for your feature or fix:
   ```bash
   git checkout -b feature/my-awesome-feature
   ```

### Development Workflow

- Implement your changes.
- Test thoroughly (especially across platforms if applicable).
- Format code and ensure consistency with existing style.
- Commit with clear, descriptive message.

### Submitting Changes

1. Push your branch:
   ```bash
   git push origin feature/my-awesome-feature
   ```
2. Open a **Pull Request** via GitHub.
3. In your PR, include:
   - A summary of your changes.
   - Any screenshots or GIFs (if appropriate).
   - Test instructions or notes.
4. Await review. Feel free to address feedback—it’s all part of the process!

### Contribution Guidelines

- New features should be optional or toggleable to maintain the “tiny engine” ethos.
- Keep dependencies minimal to ease installation and usage.
- Document new functionality in the README.
- Use conventional commits or at least clear messages (e.g. `fix:`, `feat:`, `docs:`).

---

##  License & Acknowledgments

*(If your project has a license, insert it here—e.g., MIT License.)*

Built with Python and Pygame. Inspired by minimal game engines and pixel art tooling. Great for learning, prototyping, and expanding!

---

Thanks for contributing to **Gemstone**!
>>>>>>> e7e60b7f4d47b7080a5a4d4bed82417ded99ceb0
