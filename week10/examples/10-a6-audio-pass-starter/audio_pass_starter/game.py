from __future__ import annotations

from dataclasses import dataclass
import random

import pygame

from audio_pass_starter.audio import AudioBank


BG = pygame.Color("#11161d")
PANEL = pygame.Color("#18222d")
PLAYFIELD = pygame.Color("#101a24")
TEXT = pygame.Color("#ecf4ff")
SUBTLE = pygame.Color("#9cb4c9")
ACCENT = pygame.Color("#f5c96a")
PLAYER = pygame.Color("#7dd3fc")
NODE = pygame.Color("#6ee7b7")
HAZARD = pygame.Color("#fb7185")
GOOD = pygame.Color("#4ade80")
BAD = pygame.Color("#ef4444")


@dataclass
class Player:
    pos: pygame.Vector2
    radius: int = 18
    speed: float = 280.0
    hp: int = 4
    invincible_for: float = 0.0
    scan_cooldown: float = 0.0
    scan_flash: float = 0.0

    def update(self, dt: float, playfield: pygame.Rect) -> None:
        if self.invincible_for > 0.0:
            self.invincible_for = max(0.0, self.invincible_for - dt)
        if self.scan_cooldown > 0.0:
            self.scan_cooldown = max(0.0, self.scan_cooldown - dt)
        if self.scan_flash > 0.0:
            self.scan_flash = max(0.0, self.scan_flash - dt)

        keys = pygame.key.get_pressed()
        axis = pygame.Vector2(0, 0)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            axis.x -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            axis.x += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            axis.y -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            axis.y += 1

        if axis.length_squared() > 0:
            axis = axis.normalize()

        self.pos += axis * self.speed * dt
        self.pos.x = max(playfield.left + self.radius, min(playfield.right - self.radius, self.pos.x))
        self.pos.y = max(playfield.top + self.radius, min(playfield.bottom - self.radius, self.pos.y))


@dataclass
class Node:
    pos: pygame.Vector2
    radius: int = 12


@dataclass
class Hazard:
    pos: pygame.Vector2
    velocity: pygame.Vector2
    radius: int = 16

    def update(self, dt: float, playfield: pygame.Rect) -> None:
        self.pos += self.velocity * dt

        if self.pos.x - self.radius <= playfield.left or self.pos.x + self.radius >= playfield.right:
            self.velocity.x *= -1
            self.pos.x = max(playfield.left + self.radius, min(playfield.right - self.radius, self.pos.x))

        if self.pos.y - self.radius <= playfield.top or self.pos.y + self.radius >= playfield.bottom:
            self.velocity.y *= -1
            self.pos.y = max(playfield.top + self.radius, min(playfield.bottom - self.radius, self.pos.y))


class TitleScene:
    name = "title"

    def __init__(self, game: Game) -> None:
        self.game = game

    def on_enter(self) -> None:
        self.game.audio.play_loop("title_loop")

    def on_exit(self) -> None:
        return

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.game.audio.play("start")
            self.game.switch_scene(PlayScene(self.game))

    def update(self, dt: float) -> None:
        return

    def draw(self) -> None:
        screen = self.game.screen
        screen.fill(BG)

        title = self.game.font(58).render("A6 Audio Pass Starter", True, TEXT)
        body = self.game.font(28).render("Collect nodes, dodge hazards, scan on cooldown.", True, SUBTLE)
        note = self.game.font(24).render("Starter only: need to add more audio events.", True, ACCENT)
        hint = self.game.font(28).render("Press Space to start", True, TEXT)
        mute = self.game.font(22).render(self.game.audio_status_text(), True, SUBTLE)

        screen.blit(title, title.get_rect(center=(self.game.SCREEN_W // 2, 180)))
        screen.blit(body, body.get_rect(center=(self.game.SCREEN_W // 2, 244)))
        screen.blit(note, note.get_rect(center=(self.game.SCREEN_W // 2, 286)))
        screen.blit(hint, hint.get_rect(center=(self.game.SCREEN_W // 2, 350)))
        screen.blit(mute, mute.get_rect(center=(self.game.SCREEN_W // 2, 392)))


class EndScene:
    name = "end"

    def __init__(self, game: Game, *, won: bool, score: int) -> None:
        self.game = game
        self.won = won
        self.score = score

    def on_enter(self) -> None:
        self.game.audio.play_loop("title_loop")

    def on_exit(self) -> None:
        return

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.game.audio.play("start")
            self.game.switch_scene(PlayScene(self.game))

    def update(self, dt: float) -> None:
        return

    def draw(self) -> None:
        screen = self.game.screen
        screen.fill(BG)

        heading = "Signal Restored" if self.won else "Signal Lost"
        detail = "TODO: add a success cue here" if self.won else "TODO: add a fail / game over cue here"
        accent = GOOD if self.won else BAD

        title = self.game.font(60).render(heading, True, TEXT)
        score = self.game.font(32).render(f"Score: {self.score}", True, accent)
        todo = self.game.font(24).render(detail, True, ACCENT)
        hint = self.game.font(28).render("Press Space to restart", True, SUBTLE)

        screen.blit(title, title.get_rect(center=(self.game.SCREEN_W // 2, 180)))
        screen.blit(score, score.get_rect(center=(self.game.SCREEN_W // 2, 246)))
        screen.blit(todo, todo.get_rect(center=(self.game.SCREEN_W // 2, 300)))
        screen.blit(hint, hint.get_rect(center=(self.game.SCREEN_W // 2, 360)))


class PlayScene:
    name = "play"
    TARGET_SCORE = 6

    def __init__(self, game: Game) -> None:
        self.game = game
        self.player = Player(pos=pygame.Vector2(self.game.playfield.center))
        self.nodes = [Node(self._random_point(40)) for _ in range(4)]
        self.hazards = [Hazard(self._random_point(70), self._random_velocity()) for _ in range(3)]

        self.score = 0
        self.banner = "Scan is on cooldown. Add more sounds as you build the pass."
        self.banner_for = 2.0
        self.scan_hint_for = 0.0

    def on_enter(self) -> None:
        self.game.audio.play_loop("play_loop")

    def on_exit(self) -> None:
        return

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_SPACE and self.player.scan_cooldown <= 0.0:
            self.player.scan_cooldown = 0.45
            self.player.scan_flash = 0.30
            self.scan_hint_for = 0.45
            self.banner = "Scan cue plays now. Add pickup, damage, and end-state cues next."
            self.banner_for = 1.0
            self.game.audio.play("scan")

    def update(self, dt: float) -> None:
        self.player.update(dt, self.game.playfield)
        if self.banner_for > 0.0:
            self.banner_for = max(0.0, self.banner_for - dt)
        if self.scan_hint_for > 0.0:
            self.scan_hint_for = max(0.0, self.scan_hint_for - dt)

        for hazard in self.hazards:
            hazard.update(dt, self.game.playfield)

        # Students can attach new sound cues in these collision branches.
        for node in self.nodes:
            if self._overlap(self.player.pos, self.player.radius, node.pos, node.radius):
                self.score += 1
                node.pos = self._random_point(40)
                self.banner = "Node collected. TODO: add a pickup sound."
                self.banner_for = 0.9

        for hazard in self.hazards:
            if self.player.invincible_for > 0.0:
                break
            if self._overlap(self.player.pos, self.player.radius, hazard.pos, hazard.radius):
                self.player.hp = max(0, self.player.hp - 1)
                self.player.invincible_for = 1.0
                self.banner = "Player hit. TODO: add a damage sound."
                self.banner_for = 0.9

        if self.score >= self.TARGET_SCORE:
            self.game.switch_scene(EndScene(self.game, won=True, score=self.score))
            return

        if self.player.hp <= 0:
            self.game.switch_scene(EndScene(self.game, won=False, score=self.score))

    def draw(self) -> None:
        screen = self.game.screen
        screen.fill(BG)

        pygame.draw.rect(screen, PANEL, self.game.hud_rect)
        pygame.draw.rect(screen, PLAYFIELD, self.game.playfield, border_radius=14)

        for node in self.nodes:
            pygame.draw.circle(screen, NODE, node.pos, node.radius)
            pygame.draw.circle(screen, TEXT, node.pos, node.radius, width=2)

        for hazard in self.hazards:
            pygame.draw.circle(screen, HAZARD, hazard.pos, hazard.radius)

        if self.scan_hint_for > 0.0:
            nearest = self._nearest_node()
            if nearest is not None:
                pygame.draw.line(screen, ACCENT, self.player.pos, nearest.pos, width=3)

        self._draw_player(screen)
        self._draw_scan_ring(screen)
        self._draw_hud(screen)

    def _draw_player(self, screen: pygame.Surface) -> None:
        visible = self.player.invincible_for <= 0.0 or int(self.player.invincible_for * 12) % 2 == 0
        if not visible:
            return
        pygame.draw.circle(screen, PLAYER, self.player.pos, self.player.radius)
        pygame.draw.circle(screen, TEXT, self.player.pos, self.player.radius, width=2)

    def _draw_scan_ring(self, screen: pygame.Surface) -> None:
        if self.player.scan_flash <= 0.0:
            return
        progress = 1.0 - (self.player.scan_flash / 0.30)
        radius = int(round(28 + progress * 120))
        width = max(1, int(round(5 - progress * 3)))
        pygame.draw.circle(screen, ACCENT, self.player.pos, radius, width=width)

    def _draw_hud(self, screen: pygame.Surface) -> None:
        cy = self.game.hud_rect.centery
        left = self.game.hud_rect.left + 16

        score = self.game.font(26).render(f"Score: {self.score}/{self.TARGET_SCORE}", True, TEXT)
        hp = self.game.font(26).render(f"HP: {self.player.hp}", True, GOOD if self.player.hp >= 2 else BAD)
        cooldown_value = max(0.0, self.player.scan_cooldown)
        cooldown = self.game.font(22).render(f"Scan cooldown: {cooldown_value:0.2f}s", True, SUBTLE)
        audio = self.game.font(22).render(self.game.audio_status_text(), True, ACCENT)

        screen.blit(score, score.get_rect(midleft=(left, cy)))
        screen.blit(hp, hp.get_rect(midleft=(left + 180, cy)))
        screen.blit(cooldown, cooldown.get_rect(midleft=(left + 280, cy)))
        screen.blit(audio, audio.get_rect(midright=(self.game.hud_rect.right - 16, cy)))

        help_text = self.game.font(20).render("Move, collect nodes, and press Space to scan.", True, SUBTLE)
        todo = self.banner if self.banner_for > 0.0 else "Starter app: extend this audio map for A6."
        todo_text = self.game.font(21).render(todo, True, ACCENT)

        screen.blit(help_text, help_text.get_rect(midtop=(self.game.playfield.centerx, self.game.playfield.top + 14)))
        screen.blit(todo_text, todo_text.get_rect(midbottom=(self.game.playfield.centerx, self.game.playfield.bottom - 16)))

    def _nearest_node(self) -> Node | None:
        if not self.nodes:
            return None
        return min(self.nodes, key=lambda node: self.player.pos.distance_squared_to(node.pos))

    def _random_point(self, margin: int) -> pygame.Vector2:
        return pygame.Vector2(
            self.game.rng.uniform(self.game.playfield.left + margin, self.game.playfield.right - margin),
            self.game.rng.uniform(self.game.playfield.top + margin, self.game.playfield.bottom - margin),
        )

    def _random_velocity(self) -> pygame.Vector2:
        choices = (-170.0, -140.0, 140.0, 170.0)
        return pygame.Vector2(self.game.rng.choice(choices), self.game.rng.choice(choices))

    @staticmethod
    def _overlap(a_pos: pygame.Vector2, a_radius: int, b_pos: pygame.Vector2, b_radius: int) -> bool:
        limit = a_radius + b_radius
        return a_pos.distance_squared_to(b_pos) <= limit * limit


class Game:
    fps = 60

    SCREEN_W = 960
    SCREEN_H = 540
    HUD_H = 66
    PADDING = 14

    def __init__(self) -> None:
        self.screen = pygame.display.set_mode((self.SCREEN_W, self.SCREEN_H))
        self._fonts: dict[int, pygame.font.Font] = {}
        self.rng = random.Random(8)

        self.hud_rect = pygame.Rect(0, 0, self.SCREEN_W, self.HUD_H)
        self.playfield = pygame.Rect(
            self.PADDING,
            self.HUD_H + self.PADDING,
            self.SCREEN_W - (2 * self.PADDING),
            self.SCREEN_H - self.HUD_H - (2 * self.PADDING),
        )

        self.audio = AudioBank()
        self.current_scene: TitleScene | PlayScene | EndScene = TitleScene(self)
        self.current_scene.on_enter()

    def font(self, size: int) -> pygame.font.Font:
        size = int(size)
        found = self._fonts.get(size)
        if found is None:
            found = pygame.font.SysFont(None, size)
            self._fonts[size] = found
        return found

    def audio_status_text(self) -> str:
        if not self.audio.enabled:
            return "Audio unavailable"
        if self.audio.muted:
            return "Audio muted (M)"
        return "Audio on (M to mute)"

    def switch_scene(self, scene: TitleScene | PlayScene | EndScene) -> None:
        self.current_scene.on_exit()
        self.current_scene = scene
        self.current_scene.on_enter()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
                return
            if event.key == pygame.K_m:
                self.audio.toggle_mute()
                return

        self.current_scene.handle_event(event)

    def update(self, dt: float) -> None:
        self.current_scene.update(dt)

    def draw(self) -> None:
        self.current_scene.draw()

    def shutdown(self) -> None:
        self.audio.shutdown()