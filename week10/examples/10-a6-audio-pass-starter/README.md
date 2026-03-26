# Week 10 Assignment Starter — A6 Audio Pass

This starter is meant to be a clean base for A6, not a finished submission.

It already includes:

- a small scenes-based `pygame` app
- a centralized audio helper with safe mixer setup
- generated placeholder tones for `start`, `scan`, and background loops
- a mute toggle and separate music/SFX volume constants
- an explicit cooldown on the scan action so they have one anti-spam example to build from

## Run

From this folder:

- `python3 -m venv .venv`
- `source .venv/bin/activate`
- `python -m pip install -r requirements.txt`
- `python main.py`

## Controls

- `WASD` or arrow keys: move
- `Space`: scan pulse
- `M`: mute / unmute
- `Esc`: quit
- `F1`: increase volume excluding sfx
- `F2`: decrease volume excluding sfx

## Starter design

- `title` scene: looping title ambience and start transition
- `play` scene: collect blue nodes, avoid red hazards, use scan pulse on cooldown
- `end` scene: restart flow and space for students to add success/fail cues

## Audio Map
- Title has music playing to set ambience of the game
- During play state when player takes damage, a negative sfx will be played to portray that hazards are bad
- When player collects a collectible, a more high pitch sfx will be played in attempt to portray positivity with collectibles
- If player loses, a lose sfx will be played to indicate player has not succeeded
- If player wins, a win sfx will be played to indicate player has won

## Tuning
When I added damage sfx and pickup, I explored what each wave sounded like. I tried damges sound with a 250 frequency and sine but wanted to be more negative so I dropped the frequency to 85 and made wave square for an arcadey negative sfx. I also tried saw with pickup but didn't like the amount of static on it so kept sine and settled with a frequency of 4125. I also wanted to add music to title screen. I also changed music_volume to 0.2 to start so when I added the ability to change volume of music_volume on each scene, it was more consistent using base of 0.05

# Brief note
For in game it didnt make sense to add music if the focus was on pickup and damage sfx so I wanted player to focus on that. I also only made it where player can control the title scene and end scene music/sfx that way if they felt the sfx was too much in comparable to the ingame sfx they can lower it. 

# Asset Resources
Title Music
   Royalty Free Music: Bensound.com/royalty-free-music
    License code: NV2BGVMUV3OB1QY6
    Artist: : Vital

Losing scene
https://pixabay.com/sound-effects/film-special-effects-losing-horn-313723/ 

Win scene
https://pixabay.com/sound-effects/film-special-effects-level-up-05-326133/