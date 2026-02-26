from __future__ import annotations

import random

import pygame

from scenes_arch.entities import Bounds, Mob, Player, Projectile
from scenes_arch.palette import Palette
from scenes_arch.scene import Scene, SceneManager


class TitleScene:
    name = "title"

    def __init__(self, game: Game) -> None:
        self.game = game

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_SPACE:
            self.game.scenes.switch_to(PlayScene(self.game))

    def update(self, dt: float) -> None:
        return

    def draw(self) -> None:
        screen = self.game.screen
        pal = self.game.palette
        screen.fill(pal.bg)

        title = self.game.font(56).render("Week 7: Scenes + Architecture", True, pal.text)
        hint = self.game.font(28).render("Press Space to start", True, pal.subtle)

        screen.blit(title, title.get_rect(center=(self.game.SCREEN_W // 2, 190)))
        screen.blit(hint, hint.get_rect(center=(self.game.SCREEN_W // 2, 270)))


class GameOverScene:
    name = "gameover"

    def __init__(self, game: Game, *, score: int) -> None:
        self.game = game
        self.score = score

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_SPACE:
            self.game.scenes.switch_to(PlayScene(self.game))

    def update(self, dt: float) -> None:
        return

    def draw(self) -> None:
        screen = self.game.screen
        pal = self.game.palette
        screen.fill(pal.bg)

        title = self.game.font(72).render("GAME OVER", True, pal.text)
        score = self.game.font(32).render(f"Score: {self.score}", True, pal.subtle)
        hint = self.game.font(28).render("Press Space to restart", True, pal.subtle)

        screen.blit(title, title.get_rect(center=(self.game.SCREEN_W // 2, 190)))
        screen.blit(score, score.get_rect(center=(self.game.SCREEN_W // 2, 275)))
        screen.blit(hint, hint.get_rect(center=(self.game.SCREEN_W // 2, 340)))


class PlayScene:
    name = "play"

    MOB_COUNT = 10

    def __init__(self, game: Game) -> None:
        self.game = game
        self.score = 0

        self.all_sprites: pygame.sprite.Group[pygame.sprite.Sprite] = pygame.sprite.Group()
        self.mobs: pygame.sprite.Group[Mob] = pygame.sprite.Group()
        self.projectiles: pygame.sprite.Group[Projectile] = pygame.sprite.Group()

        bounds = Bounds(self.game.playfield.copy())
        self.player = Player(self.game.playfield.midbottom, color=self.game.palette.player, bounds=bounds)
        self.player.rect.y -= 20
        self.player.pos.xy = self.player.rect.center

        self.all_sprites.add(self.player)

        for _ in range(self.MOB_COUNT):
            mob = Mob(color=self.game.palette.mob, playfield=self.game.playfield, rng=self.game.rng)
            self.mobs.add(mob)
            self.all_sprites.add(mob)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_SPACE and self.player.can_fire():
            self.player.mark_fired()
            projectile = Projectile(
                self.player.rect.centerx,
                self.player.rect.top,
                color=self.game.palette.projectile,
                top_limit=self.game.playfield.top - 40,
            )
            self.projectiles.add(projectile)
            self.all_sprites.add(projectile)

    def update(self, dt: float) -> None:
        self.player.update(dt)
        self.mobs.update(dt)
        self.projectiles.update(dt)

        hits = pygame.sprite.groupcollide(self.projectiles, self.mobs, dokilla=True, dokillb=False)
        if hits:
            for mobs in hits.values():
                for mob in mobs:
                    mob.respawn()
                    self.score += 1

        if not self.player.is_invincible:
            bump = pygame.sprite.spritecollide(self.player, self.mobs, dokill=False)
            if bump:
                self.player.take_hit(1)
                for mob in bump:
                    mob.respawn()

        if self.player.hp <= 0:
            self.game.scenes.switch_to(GameOverScene(self.game, score=self.score))

    def draw(self) -> None:
        screen = self.game.screen
        pal = self.game.palette

        screen.fill(pal.bg)

        pygame.draw.rect(screen, pal.panel, self.game.hud_rect)
        pygame.draw.rect(screen, pal.panel, self.game.playfield, border_radius=12)

        self.all_sprites.draw(screen)

        self._draw_hud()

    def _draw_hud(self) -> None:
        screen = self.game.screen
        pal = self.game.palette

        left = self.game.hud_rect.left + 14
        cy = self.game.hud_rect.centery

        score = self.game.font(28).render(f"Score: {self.score}", True, pal.text)
        screen.blit(score, score.get_rect(midleft=(left, cy)))

        scene = self.game.font(22).render(f"Scene: {self.name}", True, pal.subtle)
        screen.blit(scene, scene.get_rect(midleft=(left + 180, cy)))

        bar_w = 180
        bar_h = 18
        bar_x = self.game.hud_rect.right - 14 - bar_w
        bar_y = cy - bar_h // 2

        pygame.draw.rect(screen, pal.bg, pygame.Rect(bar_x, bar_y, bar_w, bar_h), border_radius=6)
        pct = 0.0 if self.player.max_hp <= 0 else self.player.hp / self.player.max_hp
        fill_w = max(0, int(round(bar_w * pct)))
        fill_col = pal.hp_ok if pct >= 0.4 else pal.hp_bad
        pygame.draw.rect(screen, fill_col, pygame.Rect(bar_x, bar_y, fill_w, bar_h), border_radius=6)

        hp = self.game.font(22).render(f"HP: {self.player.hp}", True, pal.text)
        screen.blit(hp, hp.get_rect(midright=(bar_x - 10, cy)))

        if self.player.is_invincible:
            inv = self.game.font(20).render("invincible", True, pal.subtle)
            screen.blit(inv, inv.get_rect(midright=(self.game.hud_rect.right - 14, cy + 22)))


class Game:
    fps = 60

    SCREEN_W, SCREEN_H = 960, 540
    HUD_H = 64
    PADDING = 14

    def __init__(self) -> None:
        self.palette = Palette()

        self.screen = pygame.display.set_mode((self.SCREEN_W, self.SCREEN_H))
        self._fonts: dict[int, pygame.font.Font] = {}

        self.hud_rect = pygame.Rect(0, 0, self.SCREEN_W, self.HUD_H)
        self.playfield = pygame.Rect(
            self.PADDING,
            self.HUD_H + self.PADDING,
            self.SCREEN_W - 2 * self.PADDING,
            self.SCREEN_H - self.HUD_H - 2 * self.PADDING,
        )

        self.rng = random.Random(7)

        start: Scene = TitleScene(self)
        self.scenes = SceneManager(current=start)

    def font(self, size: int) -> pygame.font.Font:
        size = int(size)
        f = self._fonts.get(size)
        if f is None:
            f = pygame.font.SysFont(None, size)
            self._fonts[size] = f
        return f

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.event.post(pygame.event.Event(pygame.QUIT))
            return

        self.scenes.current.handle_event(event)

    def update(self, dt: float) -> None:
        self.scenes.current.update(dt)

    def draw(self) -> None:
        self.scenes.current.draw()
