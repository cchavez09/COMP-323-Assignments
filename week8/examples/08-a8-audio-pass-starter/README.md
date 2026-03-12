# Week 8 Assignment Starter — A8 Audio Pass

This starter is meant to be a clean base for A8, not a finished submission.

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

## Starter design

- `title` scene: looping title ambience and start transition
- `play` scene: collect blue nodes, avoid red hazards, use scan pulse on cooldown
- `end` scene: restart flow and space for students to add success/fail cues