# RetroRacer

A retro-style 1980s arcade racing game built with Python and Pygame. Dodge oncoming traffic, avoid the road edges, and beat your high score.

![Python](https://img.shields.io/badge/Python-3.9+-blue) ![Pygame](https://img.shields.io/badge/Pygame-2.6-green) ![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)

## Gameplay

- Your car sits in the center of the screen
- The road scrolls toward you — the faster you go, the harder it gets
- Avoid crashing into oncoming cars or hitting the road edges
- Score increases with speed — go fast, live dangerously

## Controls

| Key | Action |
|-----|--------|
| `↑` Up | Accelerate |
| `↓` Down | Brake |
| `←` Left | Steer left |
| `→` Right | Steer right |
| `Enter` | Start / Restart |
| `Esc` | Quit |

## Run from source

**Requirements:** Python 3.9+

```bash
pip install pygame
python game.py
```

## Build the .exe

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --name RetroRacer game.py
```

Output: `dist/RetroRacer.exe` — standalone, no Python required on the target machine.

## System Requirements (for the .exe)

- Windows 7 64-bit or later
- 64 MB RAM
- Any GPU with DirectX 9 / OpenGL 2.0
- 15 MB disk space
- Keyboard
