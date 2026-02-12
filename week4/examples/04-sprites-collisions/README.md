# Week 4 Example — Sprites + Collisions

This example supports the Week 4 slides (sprites, groups, hitboxes, and collision responses).

## Learning goals
- Use `pygame.sprite.Sprite` and `pygame.sprite.Group`
- Keep a *hitbox* (`rect`) separate from how you draw
- Detect overlaps and handle *responses* (solid walls, triggers, damage)
- Add basic fairness/feel: feedback bundle + short invincibility frames

## Run
From this folder:

- `python3 -m pip install pygame`
- `python3 main.py`

## Controls
- Arrow keys / WASD: move
- `F1`: toggle debug (hitboxes)
- `R`: reset
- `Esc`: quit

## What to change first
- Make the coin smaller/bigger (hitbox vs art) in `sprites_collisions/game.py`
- Change the arena walls layout
- Try different knockback + i-frame timing

# What I added
- Made a vertical moving hazard and an extra wall
- Changed rng variable in coins to allow true randomness 
- Added a star that allows invincibility and a speed boost (State change)
- Made star hitbox smaller than visual for accuracy and fairness (Fairness Rule)
- Made player score in game class for easier reset and tracking between coin resets (State change)
- Implemented a sound effect to give feedback on damage taken (Feedback)

# Game loop
Player spawns in with 3 lives in a set position and must move around collecting 8 coins while avoiding hazards. Level will reset once all 8 coins are collected and score will be kept throughout resets until player resets the game or dies. 

# Tuning Notes
- Playtest with vertical hazard: Created more variety within the game
- Playtest with star: Had it where it lasted 5 seconds with 600 speed, felt like too much so dropped it to 3 seconds with 440
- Playtest with 1 extra wall: Layout felt better with an added wall
- Playtest with 2 extra walls: Feels more complete with the layout
- Decreased default speed from 320 to 300 to make the change in speed with star powerup more noticeable
- Increased hitbox from 28 to 30 on player allow more visual connection to each item