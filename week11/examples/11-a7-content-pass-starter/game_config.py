# game_config.py — A7 Content Pass Starter
# TODO: Move all hardcoded difficulty values from main.py into this file.
# Then reference these constants from gameplay code.
#
# Example structure:
#
# WIN_WIDTH = 480
# WIN_HEIGHT = 640
# FPS = 60
#
# PLAYER_SPEED = 5
# PLAYER_HEALTH = 100
#
# ENEMY_SPEED_MIN = 1.0
# ENEMY_SPEED_MAX = 7.0
# ENEMY_DAMAGE = 20
#
# SPAWN_DELAY_MS = 800
# MAX_ENEMIES = 15
#
# Add your own variables as needed.

WIN_WIDTH = 480
WIN_HEIGHT = 640
FPS = 60

# Altered player speed from 5 to 4
PLAYER_SPEED = 4
PLAYER_HEALTH = 100

# Dropped MAX enemy speed from 7 to 3 for difficulty tuning
# While also dropping enemy damage from 20 to 10
ENEMY_SPEED_MIN = 1
ENEMY_SPEED_MAX = 3
ENEMY_DAMAGE = 10
SPAWN_DELAY = 800

FIRE_COOLDOWN = 200

# Difficulty function with global variables to allow main loop to adjust difficulty as score increases
def difficulty(score):
    global ENEMY_SPEED_MIN, ENEMY_SPEED_MAX, SPAWN_DELAY
    if score >= 100:
        ENEMY_SPEED_MAX = 5
    if score >= 200:
        ENEMY_SPEED_MIN = 2
        ENEMY_SPEED_MAX = 6
    if score >= 400:
        ENEMY_SPEED_MIN = 3
        ENEMY_SPEED_MAX = 7
        SPAWN_DELAY = 600

