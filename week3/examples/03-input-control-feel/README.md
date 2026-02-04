# Week 3 Example — Input + Control Feel

This example supports the Week 3 slides.

## Learning goals
- Use events for discrete actions (dash/jump/toggles)
- Use key-state for continuous movement intent
- Normalize 8-direction movement to avoid diagonal speed bugs
- Tune feel with small parameter presets

## Run
From this folder:

- `python3 -m pip install pygame`
- `python3 main.py`

## Controls
- Arrow keys / WASD: move (top-down)
- `P`: toggle platformer mode (jump + gravity)
- `Up` / `W` / `Space`: jump (platformer mode)
- `Left Shift`: dash (cooldown)
- `1` / `2` / `3`: feel preset (tight/floaty/heavy)
- `C`: cycle control scheme (WASD / arrows / IJKL)
- `F1`: toggle debug overlay
- `Tab`: cycle boundary mode (clamp/wrap/bounce)
- `R`: reset
- `Space`: start (from title)
- `Esc`: quit

## What to change first
- Try editing preset values in `input_control_feel/game.py`:
  - accel / friction / max speed
  - gravity / jump speed
- Try changing dash cooldown or dash impulse
