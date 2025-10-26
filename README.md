# VOID RUNNER — Bullet Hell (turtle)

A small bullet-hell shooter implemented in pure Python using the standard turtle (Tk) graphics library. Single-file game logic with simple enemy patterns, player shooting, bombs, power-ups, and a dynamic difficulty ramp.

## Files
- src/echo_garden_turtle.py — main game script (VOID RUNNER).

## Features
- Player movement and shooting.
- Multiple enemy types (chaser, sine, turret) with distinct shot patterns.
- Enemy bullets, power-ups (power, bomb, life), and particle explosions.
- Difficulty increases over time.
- HUD with score, lives, bombs, power and level.
- Keyboard controls for play, bombs, pause, restart, and help.

## Controls
- Move: Arrow keys or WASD
- Fire: Space (hold to autofire)
- Bomb: B
- Pause / Resume: P
- Restart (after Game Over): R
- Toggle help overlay: H
- Close window or Ctrl+C in terminal to quit

## Requirements
- Python 3
- Tkinter (usually provided by `python3-tk`)

On Ubuntu 24.04 dev container, install Tkinter if missing:
```bash
sudo apt update
sudo apt install -y python3-tk
```

## Run
From the workspace root:
```bash
cd /workspaces/Assignment-3---Interactive-Experience/echo-garden-turtle
python3 src/echo_garden_turtle.py
```

Notes:
- The game opens a Tk GUI window. If you run inside a headless container, you need X11 forwarding or a virtual display (e.g., run on your host, use `ssh -X`, VNC, or configure Docker with `-e DISPLAY` and X socket).
- Make sure the turtle window has focus for keyboard events to register.

## Troubleshooting
- If keys don't respond, click the game window to give it focus, then press keys.
- If you see an error about Tkinter import, install `python3-tk` as above.
- If performance is choppy, try lowering the window size or run on a machine with a display (headless environments add overhead).

## Assignment mapping
- Language: Python (primary).
- Input: Keyboard.
- Output: Real-time visual feedback (gameplay).
- Demonstrates state management, interactivity, and generative patterns for enemy behavior.

```// filepath: /workspaces/Assignment-3---Interactive-Experience/echo-garden-turtle/README.md
# VOID RUNNER — Bullet Hell (turtle)

A small bullet-hell shooter implemented in pure Python using the standard turtle (Tk) graphics library. Single-file game logic with simple enemy patterns, player shooting, bombs, power-ups, and a dynamic difficulty ramp.

## Files
- src/echo_garden_turtle.py — main game script (VOID RUNNER).

## Features
- Player movement and shooting.
- Multiple enemy types (chaser, sine, turret) with distinct shot patterns.
- Enemy bullets, power-ups (power, bomb, life), and particle explosions.
- Difficulty increases over time.
- HUD with score, lives, bombs, power and level.
- Keyboard controls for play, bombs, pause, restart, and help.

## Controls
- Move: Arrow keys or WASD
- Fire: Space (hold to autofire)
- Bomb: B
- Pause / Resume: P
- Restart (after Game Over): R
- Toggle help overlay: H
- Close window or Ctrl+C in terminal to quit

## Requirements
- Python 3
- Tkinter (usually provided by `python3-tk`)

On Ubuntu 24.04 dev container, install Tkinter if missing:
```bash
sudo apt update
sudo apt install -y python3-tk
```

## Run
From the workspace root:
```bash
cd /workspaces/Assignment-3---Interactive-Experience/echo-garden-turtle
python3 src/echo_garden_turtle.py
```

Notes:
- The game opens a Tk GUI window. If you run inside a headless container, you need X11 forwarding or a virtual display (e.g., run on your host, use `ssh -X`, VNC, or configure Docker with `-e DISPLAY` and X socket).
- Make sure the turtle window has focus for keyboard events to register.

## Troubleshooting
- If keys don't respond, click the game window to give it focus, then press keys.
- If you see an error about Tkinter import, install `python3-tk` as above.
- If performance is choppy, try lowering the window size or run on a machine with a display (headless environments add overhead).

## Assignment mapping
- Language: Python (primary).
- Input: Keyboard.
- Output: Real-time visual feedback (gameplay).
- Demonstrates state management, interactivity, and generative patterns for enemy behavior.
