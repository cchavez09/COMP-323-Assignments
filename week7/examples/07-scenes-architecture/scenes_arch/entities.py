from __future__ import annotations

from dataclasses import dataclass
import random

import pygame


@dataclass
class Bounds:
    rect: pygame.Rect

    def clamp_ip(self, r: pygame.Rect) -> None:
        r.clamp_ip(self.rect)


class Player(pygame.sprite.Sprite):
    def __init__(self, center: tuple[int, int], *, color: pygame.Color, bounds: Bounds) -> None:
        super().__init__()

        self.image = pygame.Surface((44, 26), pygame.SRCALPHA)
        pygame.draw.polygon(
            self.image,
            color,
            [(2, 24), (22, 2), (42, 24)],
        )
        self.rect = self.image.get_rect(center=center)

        self.pos = pygame.Vector2(self.rect.center)
        self.speed = 360.0
        self.bounds = bounds

        self.max_hp = 10
        self.hp = 10

        self.invincible_for = 0.0
        self.invincible_after_hit = 0.65

        self.fire_cooldown = 0.18
        self._fire_for = 0.0

    def can_fire(self) -> bool:
        return self._fire_for <= 0.0

    def mark_fired(self) -> None:
        self._fire_for = self.fire_cooldown

    def update(self, dt: float) -> None:
        if self.invincible_for > 0.0:
            self.invincible_for = max(0.0, self.invincible_for - dt)

        if self._fire_for > 0.0:
            self._fire_for = max(0.0, self._fire_for - dt)

        keys = pygame.key.get_pressed()
        x = 0
        y = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            x -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            x += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            y -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            y += 1

        v = pygame.Vector2(x, y)
        if v.length_squared() > 0:
            v = v.normalize()

        self.pos += v * self.speed * dt
        self.rect.center = (int(round(self.pos.x)), int(round(self.pos.y)))
        self.bounds.clamp_ip(self.rect)
        self.pos.xy = self.rect.center

    @property
    def is_invincible(self) -> bool:
        return self.invincible_for > 0.0

    def take_hit(self, damage: int = 1) -> None:
        if self.is_invincible:
            return
        self.hp = max(0, self.hp - int(damage))
        self.invincible_for = self.invincible_after_hit


class Mob(pygame.sprite.Sprite):
    def __init__(
        self,
        *,
        color: pygame.Color,
        playfield: pygame.Rect,
        rng: random.Random,
    ) -> None:
        super().__init__()
        self.image = pygame.Surface((26, 26), pygame.SRCALPHA)
        pygame.draw.rect(self.image, color, self.image.get_rect(), border_radius=6)
        self.rect = self.image.get_rect()

        self.playfield = playfield
        self.rng = rng

        self.speed_x = 0.0
        self.speed_y = 0.0
        self.respawn()

    def respawn(self) -> None:
        self.rect.x = self.rng.randrange(self.playfield.left, self.playfield.right - self.rect.width)
        self.rect.y = self.rng.randrange(self.playfield.top - 120, self.playfield.top - 30)

        self.speed_x = float(self.rng.randrange(-60, 60))
        self.speed_y = float(self.rng.randrange(120, 260))

    def update(self, dt: float) -> None:
        self.rect.x += int(round(self.speed_x * dt))
        self.rect.y += int(round(self.speed_y * dt))

        if (
            self.rect.top > self.playfield.bottom + 20
            or self.rect.right < self.playfield.left - 20
            or self.rect.left > self.playfield.right + 20
        ):
            self.respawn()


class Projectile(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, *, color: pygame.Color, top_limit: int) -> None:
        super().__init__()
        self.image = pygame.Surface((6, 14), pygame.SRCALPHA)
        pygame.draw.rect(self.image, color, self.image.get_rect(), border_radius=2)
        self.rect = self.image.get_rect()

        self.rect.centerx = x
        self.rect.bottom = y

        self.speed_y = -520.0
        self.top_limit = top_limit

    def update(self, dt: float) -> None:
        self.rect.y += int(round(self.speed_y * dt))
        if self.rect.bottom < self.top_limit:
            self.kill()
