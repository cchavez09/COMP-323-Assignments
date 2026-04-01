# A7 Content Pass Starter

Starting point for Assignment A7 — Content pass + tuning notes.

## How to run

From this folder:

- `python3 -m venv .venv`
- `source .venv/bin/activate`
- `python -m pip install -r requirements.txt`
- `python main.py`

## Controls

- Arrow keys: move left/right
- Space: fire
- Escape: quit

## Your task

This game has hardcoded difficulty values scattered through the code. Your assignment:

1. **Extract** all difficulty values into `game_config.py`
2. **Create** a content map for the first 60 seconds
3. **Tune** at least 3 values with before/after documentation
4. **Document** everything in this README

Look for `# TODO: move to config` comments in `main.py` for the values to extract.

## Content map

| Time (sec) | What happens | Difficulty lever | Current value | Assessment |
|---|---|---|---|---|
| 0 - 1 sec| Player spawns | - | - | - |
| 1 - 5 sec | First enemy spawns | spawn delay | 800ms | about right
| 5 - 30 sec | More enemy spawns | spawn delay | 800ms | too hard (slow enemies = overwhelm)
| 30 - 45 | Player shoots | shoot cooldown | 200ms | about right
| 45 - 60 | Player takes damage | health drop | -20 | too hard 

## Tuning log

| Variable | Before | After | Why | Result |
|---|---|---|---|---|
| Spawn Delay | 800 | 600 (difficulty ramp) | Felt underwhelming | Player has good # of enemies on screen |
| Player speed | 5 | 4 | Felt too fast | Player can dodge enemies too easily | Player more likely to take damage |
| Enemey Damage | 20 | 10| Felt too harsh on player | Player can play longer (ties in with player speed) |

## Intended difficulty curve
I intended to use a staircase difficulty curve to have 3 change in difficulty upon reaching a new score. For 100+ score the enemies larger range of their speed with their max speed increased while keeping base min speed. 200+ increases both min and max enemy speed by 1, that way there is a balance between slow and fast enemies. 400+ increased by 1 on both while also decreasing spawn delay. This is because enemies are faster so they go off screen faster, so enemies need to spawn in faster in order to still have a decent # of enemies on screen.

(Describe your target difficulty progression here)
