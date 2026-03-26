# Week 6 Example — HUD + Game States

This example supports the Week 6 slides (HUD text + health bar, plus a small state machine).

## Learning goals

- Render text reliably (score/state/labels)
- Draw a simple status bar (health/shield)
- Implement a state machine: title → play → pause → game over
- Gate input and update logic by state

## Run

From this folder:

- `python3 -m pip install pygame`
- `python3 main.py`

## Controls

- Arrow keys / WASD: move (only in `play`)
- `Space`: start / restart
- `P`: pause / unpause
- `R`: reset level
- `F1`: toggle debug overlay
- `Esc`: quit

## What to change first

- Add a second HUD element (timer, objective text, ammo)
- Add one more state (win screen or settings)
- Improve readability (font size, contrast, layout)

