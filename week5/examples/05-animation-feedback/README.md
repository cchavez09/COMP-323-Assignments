# Week 5 Example — Animation + Feedback

This example supports the Week 5 slides (animation states, dt-driven frame timers, and feedback bundles).

## Learning goals

- Implement a basic animation timer (dt-driven)
- Choose animation by state (idle/run/hurt)
- Keep motion smooth with float positions + `Rect`
- Add a small feedback bundle (flash/shake/hitstop/particles)
- Handle rotation without drift (`get_rect(center=...)`)

## Run
From this folder:

- `pip install -r requirements.txt`
- `python main.py`

## Controls
- Arrow keys / WASD: move
- `Space`: start / restart
- `F1`: toggle debug overlay (hitboxes)
- `R`: reset level
- `1`: toggle flash cue
- `2`: toggle screen shake cue
- `3`: toggle hitstop cue
- `4`: toggle particles cue
- `5`: toggle damage sound cue
- `Esc`: quit

## What to change first
- Change animation speed (fps) in `anim_feedback/game.py`
- Add one more state (e.g., `hurt` animation)
- Add a new event and choose a feedback bundle for it

# What I added
- Damage sound effect (Sound effect by DRAGON-STUDIO from Pixabay https://pixabay.com/users/dragon-studio-38165424/?utm_source=link-attribution&utm_medium=referral&utm_campaign=music&utm_content=431475) and menu toggle option
- Added dead state to create x for eyes on player on death and death animation before game over game state
- Added death sound effect to dead state (Sound effect by floraphonic from Pixabay https://pixabay.com/users/floraphonic-38928062/?utm_source=link-attribution&utm_medium=referral&utm_campaign=music&utm_content=224421)

# Game loop
- Player spawns in playfield to randomized coin positions and fixed hazards with 3 lives. If player touches coin increase score, if player touches hazard lose a life, if player loses all 3 lives play death animation and return to gameover screen with option to restart.


# Tuning Notes
- First playthrough: Player is difficult to see and hard to see the running animation
- Changed player's sprite leg & arm color from grey to black to create better sprite model visibility
- Changed leg_y in draw player frame: body.bottom - 2 => body.bottom (Connect legs to body)
- Second playthrough: Player is much more visible and can be seen running, screen shakes when collecting coins which does not seem not a reasonable feature in relation with the cue
- _cue_coin: had self.cue_shake => removed self.cue_shake
- Feels less overwhelming without the shake on coin pickup
- Third Playthrough: Applied death animation with dead state and display game is over. Does not feel as negative when dying so going to add sound effect on death animation
- Death sound indicates better result, but to confirm changed GAME OVER to YOU DIED to display the reason for the game being over