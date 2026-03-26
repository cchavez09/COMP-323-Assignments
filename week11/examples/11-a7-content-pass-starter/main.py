# A7 Content Pass Starter — Week 11
# This is a simple shooter with hardcoded difficulty values.
# Your task: extract difficulty values into game_config.py,
# tune them, and document your changes.

import pygame
import random
import sys
import os

# ---------------------------------------------------------------------------
# Setup — notice the hardcoded values scattered through the code
# ---------------------------------------------------------------------------
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

WIN_WIDTH = 480
WIN_HEIGHT = 640
FPS = 60

window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("A7 Starter — Content Pass")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 22)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)

# ---------------------------------------------------------------------------
# Player — notice hardcoded speed, health, cooldown
# ---------------------------------------------------------------------------
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 30))
        self.image.fill(CYAN)
        self.rect = self.image.get_rect()
        self.rect.centerx = WIN_WIDTH // 2
        self.rect.bottom = WIN_HEIGHT - 20
        self.speed = 5           # TODO: move to config
        self.health = 100        # TODO: move to config
        self.last_fired = 0

    def update(self):
        keys = pygame.key.get_pressed()
        dx = 0
        if keys[pygame.K_LEFT]:
            dx = -self.speed
        if keys[pygame.K_RIGHT]:
            dx = self.speed
        self.rect.x += dx
        self.rect.clamp_ip(window.get_rect())

    def fire(self, group, all_sprites):
        now = pygame.time.get_ticks()
        if now - self.last_fired > 200:  # TODO: move cooldown to config
            self.last_fired = now
            p = Projectile(self.rect.centerx, self.rect.top)
            group.add(p)
            all_sprites.add(p)

# ---------------------------------------------------------------------------
# Enemy — notice hardcoded speed range
# ---------------------------------------------------------------------------
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        size = random.randint(20, 40)
        self.image = pygame.Surface((size, size))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, WIN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-80, -20)
        self.speed_y = random.randrange(1, 7)  # TODO: move to config

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > WIN_HEIGHT + 10:
            self.kill()

# ---------------------------------------------------------------------------
# Projectile
# ---------------------------------------------------------------------------
class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((4, 14))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed_y = -10

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.bottom < 0:
            self.kill()

# ---------------------------------------------------------------------------
# Main loop — notice hardcoded spawn delay and damage
# ---------------------------------------------------------------------------
def main():
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    projectiles = pygame.sprite.Group()

    player = Player()
    all_sprites.add(player)

    last_spawn = pygame.time.get_ticks()
    spawn_delay = 800  # TODO: move to config
    score = 0
    running = True

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.fire(projectiles, all_sprites)
                elif event.key == pygame.K_ESCAPE:
                    running = False

        # spawn enemies — no cap, no progressive difficulty
        now = pygame.time.get_ticks()
        if now - last_spawn > spawn_delay:
            last_spawn = now
            e = Enemy()
            enemies.add(e)
            all_sprites.add(e)

        all_sprites.update()

        # collision: projectiles vs enemies
        hits = pygame.sprite.groupcollide(enemies, projectiles, True, True)
        for hit in hits:
            score += 10

        # collision: enemies vs player
        damage_hits = pygame.sprite.spritecollide(player, enemies, True)
        for hit in damage_hits:
            player.health -= 20  # TODO: move damage to config
            if player.health <= 0:
                running = False

        # draw
        window.fill(BLACK)
        all_sprites.draw(window)

        # simple HUD
        bar_w = 200
        fill = max(0, (player.health / 100) * bar_w)
        pygame.draw.rect(window, RED, (10, 10, bar_w, 16))
        pygame.draw.rect(window, GREEN, (10, 10, fill, 16))
        txt = font.render(f"Score: {score}", True, WHITE)
        window.blit(txt, (10, 32))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
