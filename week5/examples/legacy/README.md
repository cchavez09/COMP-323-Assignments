# Week 5 — Pygame examples Extra

These are curated extra examples to support Week 5 (sprites, animation, and feedback-related patterns).

## Contents

### `animating-example1/`
- `animatingsprites1.py`: rotating “mob” sprites using a *pristine* original image (`image_original`) + rect-centre preservation.

### `animating-example2/`
- `animatingsprites2.py`: same as example 1, plus random selection from multiple mob images.

### `sprites-basic/`
- `basicsprites1.py`: minimal `Sprite` + `Group` draw/update loop.
- `basicsprites3.py`: player movement via `key.get_pressed()` + boundary clamping.
- `basicsprites4.py`: multiple mobs with randomised start positions + velocities.

### `shooter-0.6/`
- `shooter0.6.py`: “shoot em up” slice using sprite groups + `groupcollide`, with rotating asteroid mobs.

### `shooter-0.7/`
- `shooter0.7.py`: `shooter0.6`, plus random selection from multiple asteroid images.

## How to run

From inside any example folder:

- `python3 <script>.py`

Each example uses an `assets/` folder next to the script (so it should be run with the example folder as the working directory).
