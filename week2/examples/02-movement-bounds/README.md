# Week 2 Example — Movement + Boundaries

This example supports the Week 2 slides.

## Learning goals
- Define a playfield separate from the HUD
- Update movement with dt and a velocity vector
- Implement boundary rules (clamp/wrap/bounce)
- Add a simple goal loop (reach target) + a second object (teleporter)

## Run
From this folder:

- `python3 -m pip install pygame`
- `python3 main.py`

## Controls
- Arrow keys / WASD: move
- `Tab`: cycle boundary mode
- `P`: toggle platformer mode (jump + gravity)
- `Up` / `W`: jump (platformer mode)
- `R`: reset level
- `Space`: start (from title)
- `Esc`: quit

## What to change first
- `PLAYFIELD_PADDING`, `PLAYER_MAX_SPEED`, `TIMER_SECONDS`
- Try swapping boundary mode defaults
- Try making the teleporter a hazard instead

## Assignment 2 What I added
- I made the original teleporter to be the height of the playfield. I then wanted to add a second teleporter as a "barrier" 
so I had to modify the teleporter to be a list and modify the code that interacted with teleporter to iterate as a list rather 
than a singular object. 

## Log
- Altered Radius of goal
- Made the teleporter barries thinner to anticipate overlap of goal and teleporter
- Created 2 teleporter barries in list
- Iterated through these teleporters in necessary locations
- Every 5 levels decrease timer by 5 seconds until 5 seconds is reached where it'll stay the same until game is over
- Starting mode is Wrap since 