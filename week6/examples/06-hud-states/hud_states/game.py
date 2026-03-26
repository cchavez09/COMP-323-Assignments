from __future__ import annotations

from dataclasses import dataclass, field
import random

import pygame


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


@dataclass(frozen=True)
class Palette:
    bg: pygame.Color = field(default_factory=lambda: pygame.Color("#1e222a"))
    panel: pygame.Color = field(default_factory=lambda: pygame.Color("#2a303c"))
    text: pygame.Color = field(default_factory=lambda: pygame.Color("#e5e9f0"))
    subtle: pygame.Color = field(default_factory=lambda: pygame.Color("#a3adbf"))

    player: pygame.Color = field(default_factory=lambda: pygame.Color("#88c0d0"))
    coin: pygame.Color = field(default_factory=lambda: pygame.Color("#ebcb8b"))
    hazard: pygame.Color = field(default_factory=lambda: pygame.Color("#bf616a"))
    wall: pygame.Color = field(default_factory=lambda: pygame.Color("#4c566a"))

    # Darker fills so the HP label can stay white
    hp_ok: pygame.Color = field(default_factory=lambda: pygame.Color("#1f6f3a"))
    hp_warn: pygame.Color = field(default_factory=lambda: pygame.Color("#7a5a1c"))
    hp_bad: pygame.Color = field(default_factory=lambda: pygame.Color("#7a1f2a"))


class Player(pygame.sprite.Sprite):
    def __init__(self, center: tuple[int, int], *, color: pygame.Color) -> None:
        super().__init__()

        self.image = pygame.Surface((34, 34), pygame.SRCALPHA)
        pygame.draw.rect(self.image, color, self.image.get_rect(), border_radius=8)
        self.rect = self.image.get_rect(center=center)

        self.pos = pygame.Vector2(self.rect.center)
        self.vel = pygame.Vector2(0, 0)
        self.speed = 320.0

        self.max_hp = 100
        self.hp = 100
        self.invincible_for = 0.0

    @property
    def is_invincible(self) -> bool:
        return self.invincible_for > 0

    def update(self, dt: float) -> None:
        if self.invincible_for > 0:
            self.invincible_for = max(0.0, self.invincible_for - dt)


class Coin(pygame.sprite.Sprite):
    def __init__(self, center: tuple[int, int], *, color: pygame.Color) -> None:
        super().__init__()
        self.image = pygame.Surface((22, 22), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (11, 11), 10)
        self.rect = self.image.get_rect(center=center)


class Hazard(pygame.sprite.Sprite):
    def __init__(self, center: tuple[int, int], *, color: pygame.Color) -> None:
        super().__init__()
        self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.polygon(
            self.image,
            color,
            [(16, 2), (30, 16), (16, 30), (2, 16)],
        )
        self.rect = self.image.get_rect(center=center)


class Wall(pygame.sprite.Sprite):
    def __init__(self, rect: pygame.Rect, color: pygame.Color) -> None:
        super().__init__()
        self.rect = rect.copy()
        self.color = color


class Game:
    fps = 60

    SCREEN_W, SCREEN_H = 960, 540
    HUD_H = 64
    PADDING = 12

    def __init__(self) -> None:
        self.palette = Palette()

        self.screen = pygame.display.set_mode((self.SCREEN_W, self.SCREEN_H))
        self._fonts: dict[int, pygame.font.Font] = {}

        self.screen_rect = pygame.Rect(0, 0, self.SCREEN_W, self.SCREEN_H)
        self.hud_rect = pygame.Rect(0, 0, self.SCREEN_W, self.HUD_H)
        self.playfield = pygame.Rect(
            self.PADDING,
            self.HUD_H + self.PADDING,
            self.SCREEN_W - 2 * self.PADDING,
            self.SCREEN_H - self.HUD_H - 2 * self.PADDING,
        )

        self.rng = random.Random(6)

        self.debug = False
        self.state = "title"  # title | play | pause | gameover

        self.score = 0

        self.all_sprites: pygame.sprite.Group[pygame.sprite.Sprite] = pygame.sprite.Group()
        self.walls: pygame.sprite.Group[Wall] = pygame.sprite.Group()
        self.coins: pygame.sprite.Group[Coin] = pygame.sprite.Group()
        self.hazards: pygame.sprite.Group[Hazard] = pygame.sprite.Group()

        self.player = Player(self.playfield.center, color=self.palette.player)
        self.all_sprites.add(self.player)

        self._reset_level(keep_state=True)

    def _font(self, size: int) -> pygame.font.Font:
        size = int(size)
        f = self._fonts.get(size)
        if f is None:
            f = pygame.font.SysFont(None, size)
            self._fonts[size] = f
        return f

    def _reset_level(self, *, keep_state: bool = False) -> None:
        self.all_sprites.empty()
        self.walls.empty()
        self.coins.empty()
        self.hazards.empty()

        self.score = 0
        self.player = Player(self.playfield.center, color=self.palette.player)
        self.all_sprites.add(self.player)

        def add_wall(r: pygame.Rect) -> None:
            wall = Wall(r, self.palette.wall)
            self.walls.add(wall)
            self.all_sprites.add(wall)

        t = 16
        add_wall(pygame.Rect(self.playfield.left, self.playfield.top, self.playfield.width, t))
        add_wall(pygame.Rect(self.playfield.left, self.playfield.bottom - t, self.playfield.width, t))
        add_wall(pygame.Rect(self.playfield.left, self.playfield.top, t, self.playfield.height))
        add_wall(pygame.Rect(self.playfield.right - t, self.playfield.top, t, self.playfield.height))

        add_wall(pygame.Rect(self.playfield.left + 260, self.playfield.top + 80, 18, 220))
        add_wall(pygame.Rect(self.playfield.left + 520, self.playfield.top + 200, 260, 18))

        for _ in range(7):
            self._spawn_coin()

        for _ in range(2):
            self._spawn_hazard()

        if not keep_state:
            self.state = "play"

    def _spawn_coin(self) -> None:
        for _ in range(200):
            x = self.rng.randint(self.playfield.left + 40, self.playfield.right - 40)
            y = self.rng.randint(self.playfield.top + 40, self.playfield.bottom - 40)
            coin = Coin((x, y), color=self.palette.coin)

            if pygame.sprite.spritecollideany(coin, self.walls):
                continue
            if pygame.sprite.spritecollideany(coin, self.coins):
                continue
            if coin.rect.colliderect(self.player.rect):
                continue

            self.coins.add(coin)
            self.all_sprites.add(coin)
            return

    def _spawn_hazard(self) -> None:
        for _ in range(200):
            x = self.rng.randint(self.playfield.left + 60, self.playfield.right - 60)
            y = self.rng.randint(self.playfield.top + 60, self.playfield.bottom - 60)
            hz = Hazard((x, y), color=self.palette.hazard)

            if pygame.sprite.spritecollideany(hz, self.walls):
                continue
            if hz.rect.colliderect(self.player.rect):
                continue

            self.hazards.add(hz)
            self.all_sprites.add(hz)
            return

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_ESCAPE:
            pygame.event.post(pygame.event.Event(pygame.QUIT))
            return

        if event.key == pygame.K_F1:
            self.debug = not self.debug
            return

        if event.key == pygame.K_r:
            self._reset_level(keep_state=True)
            return

        if self.state == "play" and event.key == pygame.K_p:
            self.state = "pause"
            return

        if self.state == "pause" and event.key == pygame.K_p:
            self.state = "play"
            return

        if self.state in {"title", "gameover"} and event.key == pygame.K_SPACE:
            self._reset_level(keep_state=True)
            self.state = "play"

    def _read_move(self) -> pygame.Vector2:
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
        return v

    def _move_player_axis(self, axis: str, amount: float) -> None:
        if axis == "x":
            self.player.pos.x += amount
            self.player.rect.centerx = int(round(self.player.pos.x))
        else:
            self.player.pos.y += amount
            self.player.rect.centery = int(round(self.player.pos.y))

        hits = pygame.sprite.spritecollide(self.player, self.walls, dokill=False)
        if not hits:
            return

        for wall in hits:
            if axis == "x":
                if amount > 0:
                    self.player.rect.right = wall.rect.left
                elif amount < 0:
                    self.player.rect.left = wall.rect.right
                self.player.pos.x = self.player.rect.centerx
            else:
                if amount > 0:
                    self.player.rect.bottom = wall.rect.top
                elif amount < 0:
                    self.player.rect.top = wall.rect.bottom
                self.player.pos.y = self.player.rect.centery

    def _apply_damage(self, source_rect: pygame.Rect) -> None:
        if self.player.is_invincible:
            return

        self.player.hp = max(0, self.player.hp - 20)
        self.player.invincible_for = 0.65

        if self.player.hp <= 0:
            self.state = "gameover"

    def update(self, dt: float) -> None:
        if self.state != "play":
            return

        move = self._read_move()
        self.player.vel = move * self.player.speed

        self._move_player_axis("x", self.player.vel.x * dt)
        self._move_player_axis("y", self.player.vel.y * dt)

        self.player.update(dt)

        got = pygame.sprite.spritecollide(self.player, self.coins, dokill=True)
        if got:
            self.score += 10 * len(got)
            for _ in got:
                self._spawn_coin()

        hit = pygame.sprite.spritecollide(self.player, self.hazards, dokill=False)
        if hit:
            self._apply_damage(hit[0].rect)

    def _draw_text(
        self,
        surface: pygame.Surface,
        text: str,
        *,
        size: int,
        color: pygame.Color,
        topleft: tuple[int, int] | None = None,
        topright: tuple[int, int] | None = None,
        center: tuple[int, int] | None = None,
        stroke: int = 0,
        stroke_color: pygame.Color | None = None,
    ) -> pygame.Rect:
        font = self._font(size)
        surf = font.render(text, True, color)
        rect = surf.get_rect()
        if topleft is not None:
            rect.topleft = topleft
        if topright is not None:
            rect.topright = topright
        if center is not None:
            rect.center = center

        if stroke > 0:
            outline_color = stroke_color or pygame.Color("#000000")
            outline_surf = font.render(text, True, outline_color)
            for dx in range(-stroke, stroke + 1):
                for dy in range(-stroke, stroke + 1):
                    if dx == 0 and dy == 0:
                        continue
                    surface.blit(outline_surf, rect.move(dx, dy))

        surface.blit(surf, rect)
        return rect

    def _draw_bar(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        pct: float,
        *,
        fill: pygame.Color,
        outline: pygame.Color,
        back: pygame.Color,
        inset: int = 0,
    ) -> None:
        pct = _clamp(pct, 0.0, 1.0)
        pygame.draw.rect(surface, back, rect)
        inner = rect.inflate(-2 * inset, -2 * inset) if inset > 0 else rect
        if inner.width > 0 and inner.height > 0:
            fill_w = int(inner.width * pct)
            if fill_w > 0:
                pygame.draw.rect(
                    surface,
                    fill,
                    pygame.Rect(inner.x, inner.y, fill_w, inner.height),
                )
        pygame.draw.rect(surface, outline, rect, 2)

    def _hp_color(self) -> pygame.Color:
        pct = self.player.hp / float(self.player.max_hp)
        if pct <= 0.30:
            return self.palette.hp_bad
        if pct <= 0.60:
            return self.palette.hp_warn
        return self.palette.hp_ok

    def draw(self) -> None:
        self.screen.fill(self.palette.bg)

        # Playfield background
        pygame.draw.rect(self.screen, pygame.Color("#171a20"), self.playfield)

        # Walls
        for wall in self.walls:
            pygame.draw.rect(self.screen, wall.color, wall.rect)

        # Sprites (non-wall)
        for spr in self.all_sprites:
            if isinstance(spr, Wall):
                continue
            self.screen.blit(spr.image, spr.rect)

        if self.debug:
            pygame.draw.rect(self.screen, pygame.Color("#5e81ac"), self.playfield, 2)
            pygame.draw.rect(self.screen, pygame.Color("#88c0d0"), self.player.rect, 2)
            for coin in self.coins:
                pygame.draw.rect(self.screen, pygame.Color("#ebcb8b"), coin.rect, 1)
            for hz in self.hazards:
                pygame.draw.rect(self.screen, pygame.Color("#bf616a"), hz.rect, 1)

        self._draw_hud()

        if self.state == "title":
            self._draw_overlay_title()
        elif self.state == "pause":
            self._draw_overlay_pause()
        elif self.state == "gameover":
            self._draw_overlay_gameover()

    def _draw_hud(self) -> None:
        pygame.draw.rect(self.screen, self.palette.panel, self.hud_rect)

        self._draw_text(
            self.screen,
            f"Score: {self.score}",
            size=24,
            color=self.palette.text,
            topleft=(self.PADDING, self.PADDING),
        )

        hp_pct = self.player.hp / float(self.player.max_hp)
        bar_w = 220
        bar_h = 22
        bar_x = (self.SCREEN_W - bar_w) // 2
        bar_rect = pygame.Rect(bar_x, 18, bar_w, bar_h)
        self._draw_bar(
            self.screen,
            bar_rect,
            hp_pct,
            fill=self._hp_color(),
            outline=self.palette.text,
            back=pygame.Color("#05070a"),
            inset=2,
        )
        self._draw_text(
            self.screen,
            f"HP {self.player.hp}/{self.player.max_hp}",
            size=18,
            color=self.palette.text,
            center=bar_rect.center,
        )

        self._draw_text(
            self.screen,
            f"State: {self.state}",
            size=18,
            color=self.palette.subtle,
            topright=(self.SCREEN_W - self.PADDING, 40),
        )

        self._draw_text(
            self.screen,
            "F1 debug  |  P pause  |  R reset  |  Esc quit",
            size=18,
            color=self.palette.subtle,
            topleft=(self.PADDING, 40),
        )

    def _draw_overlay_panel(self) -> pygame.Surface:
        overlay = pygame.Surface((self.SCREEN_W, self.SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        return overlay

    def _draw_overlay_title(self) -> None:
        self.screen.blit(self._draw_overlay_panel(), (0, 0))
        self._draw_text(
            self.screen,
            "WEEK 6 — HUD + STATES",
            size=54,
            color=self.palette.text,
            center=(self.SCREEN_W // 2, self.SCREEN_H // 2 - 70),
        )
        self._draw_text(
            self.screen,
            "Collect coins. Avoid hazards.",
            size=28,
            color=self.palette.text,
            center=(self.SCREEN_W // 2, self.SCREEN_H // 2 - 10),
        )
        self._draw_text(
            self.screen,
            "Press Space to start",
            size=32,
            color=self.palette.coin,
            center=(self.SCREEN_W // 2, self.SCREEN_H // 2 + 60),
        )

    def _draw_overlay_pause(self) -> None:
        self.screen.blit(self._draw_overlay_panel(), (0, 0))
        self._draw_text(
            self.screen,
            "PAUSED",
            size=72,
            color=self.palette.text,
            center=(self.SCREEN_W // 2, self.SCREEN_H // 2 - 40),
        )
        self._draw_text(
            self.screen,
            "Press P to resume",
            size=32,
            color=self.palette.subtle,
            center=(self.SCREEN_W // 2, self.SCREEN_H // 2 + 40),
        )

    def _draw_overlay_gameover(self) -> None:
        self.screen.blit(self._draw_overlay_panel(), (0, 0))
        self._draw_text(
            self.screen,
            "GAME OVER",
            size=72,
            color=self.palette.hazard,
            center=(self.SCREEN_W // 2, self.SCREEN_H // 2 - 60),
        )
        self._draw_text(
            self.screen,
            f"Final score: {self.score}",
            size=34,
            color=self.palette.text,
            center=(self.SCREEN_W // 2, self.SCREEN_H // 2 + 0),
        )
        self._draw_text(
            self.screen,
            "Press Space to restart",
            size=32,
            color=self.palette.coin,
            center=(self.SCREEN_W // 2, self.SCREEN_H // 2 + 70),
        )
