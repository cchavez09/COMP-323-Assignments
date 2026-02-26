# Week 7 Example — Scenes + Modules + Spawn Patterns

This example supports the Week 7 slides as a basic example of *modules*, *scenes*, *mobs*, and *relative projectiles*.

## Learning goals

- Implement a minimal scene interface (`handle_event/update/draw`)
- Switch scenes: title → play → game over
- Use sprite groups for many objects (mobs)
- Spawn relative objects (projectiles from player position)
- Clean up objects (`kill()` for projectiles; respawn mobs)

## Run

From this folder:

- (Recommended) create and use a virtual environment so you install `pygame` into the same Python you run:
	- `python3 -m venv .venv`
	- `source .venv/bin/activate`
	- `python -m pip install pygame`
	- `python main.py`

If you already have `pygame` installed in a different interpreter, use that interpreter consistently for both install and run.

## Controls

- Arrow keys / WASD: move (play only)
- `Space`: start / fire / restart (depends on scene)
- `Esc`: quit

## What to change first

- Add a pause scene
- Add a second enemy type with different movement
- Add a reload/cooldown HUD element
