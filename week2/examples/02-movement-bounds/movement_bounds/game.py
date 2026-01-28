from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum

import pygame

class BoundaryMode(str, Enum):
    CLAMP = "clamp"
    WRAP = "wrap"
    BOUNCE = "bounce"

@dataclass
class Goal:
    pos: pygame.Vector2
    # altered radius for moments where goal is hard to see in teleporter barrier
    radius: int = 22

@dataclass
class Teleporter:
    rect: pygame.Rect

class Game:
    fps = 60

    SCREEN_W, SCREEN_H = 960, 540
    HUD_H = 54
    PLAYFIELD_PADDING = 10

    PLAYER_SIZE = 32
    PLAYER_ACCEL = 2400.0
    PLAYER_MAX_SPEED = 520.0
    PLAYER_FRICTION = 10.0

    # Platformer-style vertical movement
    GRAVITY = 2200.0
    JUMP_SPEED = 820.0

    TIMER_SECONDS = 30.0

    def __init__(self) -> None:
        self.screen = pygame.display.set_mode((self.SCREEN_W, self.SCREEN_H))
        self.font = pygame.font.SysFont(None, 22)
        self.big_font = pygame.font.SysFont(None, 48)

        self.screen_rect = pygame.Rect(0, 0, self.SCREEN_W, self.SCREEN_H)
        self.playfield = pygame.Rect(
            self.PLAYFIELD_PADDING,
            self.HUD_H + self.PLAYFIELD_PADDING,
            self.SCREEN_W - 2 * self.PLAYFIELD_PADDING,
            self.SCREEN_H - self.HUD_H - 2 * self.PLAYFIELD_PADDING,
        )

        # Set initial game boundary to Wrap instead of Clamp
        self.boundary_mode = BoundaryMode.WRAP
        self.platformer_mode = False
        self.level = 1
        self.state = "title"  # title | play | win | lose

        self.player_rect = pygame.Rect(0, 0, self.PLAYER_SIZE, self.PLAYER_SIZE)
        self.player_pos = pygame.Vector2(0, 0)
        self.player_vel = pygame.Vector2(0, 0)

        self.on_ground = True
        self.jump_requested = False

        self.time_left = self.TIMER_SECONDS

        self.goal = Goal(pos=pygame.Vector2(0, 0))
        self.teleporters = [Teleporter(rect=pygame.Rect(0, 0, 40, 40)), 
                            Teleporter(rect=pygame.Rect(0, 0, 40, 40))]

        # Created level up variable to alter time for every 5 levels
        self.level_up = 5

        self._reset_level(keep_state=True)

    def _random_point_in_playfield(self, margin: int) -> pygame.Vector2:
        x = random.randint(self.playfield.left + margin, self.playfield.right - margin)
        y = random.randint(self.playfield.top + margin, self.playfield.bottom - margin)
        return pygame.Vector2(x, y)

    def _reset_level(self, keep_state: bool = False) -> None:
        
        self.player_pos = pygame.Vector2(0, 0)
        self.player_vel = pygame.Vector2(0, 0)
        self.player_rect.center = self.player_pos
        self.on_ground = True
        self.jump_requested = False


        # Generate x & y for teleporter center and player start pos
        tp_center = self._random_point_in_playfield(margin=70)
        self_pos = self._random_point_in_playfield(margin=80)
        goal_pos = self._random_point_in_playfield(margin=80)


            
        # Player starts offset from the teleporter
        # Made teleporters 30 in width/height to make them more visible in comparison with goal
        self.player_pos = pygame.Vector2(self_pos, self_pos.y)
        self.teleporters = [Teleporter(rect=pygame.Rect(tp_center.x, self.playfield.top, 30, self.playfield.height)),
                           Teleporter(rect=pygame.Rect(self.playfield.left, tp_center.y, self.playfield.width, 30))]
        
        # Goal is randomly placed on side of teleporter opposite the player
        self.goal.pos = pygame.Vector2(goal_pos.x, goal_pos.y)

        
        
        self.time_left = self.TIMER_SECONDS

        if not keep_state:
            self.state = "play"

    def _cycle_boundary_mode(self) -> None:
        modes = list(BoundaryMode)
        idx = modes.index(self.boundary_mode)
        self.boundary_mode = modes[(idx + 1) % len(modes)]

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_ESCAPE:
            pygame.event.post(pygame.event.Event(pygame.QUIT))
            return

        if event.key == pygame.K_TAB:
            self._cycle_boundary_mode()
            return

        if event.key == pygame.K_p:
            self.platformer_mode = not self.platformer_mode
            # Reset so the player doesn't start inside walls/ground in the new mode.
            if self.state != "title":
                self._reset_level(keep_state=True)
            return

        if event.key == pygame.K_r:
            self.level = 1
            self._reset_level(keep_state=(self.state == "title"))
            if self.state != "title":
                self.state = "play"
            return

        if self.state == "title" and event.key == pygame.K_SPACE:
            self.level = 1
            self.state = "play"
            self._reset_level(keep_state=True)
            return

        if self.state in {"win", "lose"} and event.key == pygame.K_SPACE:
            self.state = "play"
            self._reset_level(keep_state=True)
            return

        if self.state == "play" and self.platformer_mode:
            if event.key in {pygame.K_UP, pygame.K_w}:
                self.jump_requested = True

    def _read_direction(self) -> pygame.Vector2:
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

        direction = pygame.Vector2(x, y)
        if direction.length_squared() > 0:
            direction = direction.normalize()
        return direction

    def _read_horizontal(self) -> float:
        keys = pygame.key.get_pressed()
        x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            x -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            x += 1
        return float(x)

    def _apply_platformer_vertical_bounds(self) -> None:
        # Treat the bottom of the playfield as "ground".
        if self.player_rect.bottom >= self.playfield.bottom:
            self.player_rect.bottom = self.playfield.bottom
            self.player_vel.y = 0
            self.on_ground = True

        # Prevent leaving the top of the playfield.
        if self.player_rect.top < self.playfield.top:
            self.player_rect.top = self.playfield.top
            if self.player_vel.y < 0:
                self.player_vel.y = 0

        self.player_pos.update(self.player_rect.center)

    def _apply_bounds_player(self) -> None:
        if self.boundary_mode == BoundaryMode.CLAMP:
            self.player_rect.clamp_ip(self.playfield)
            self.player_pos.update(self.player_rect.center)
            return

        if self.boundary_mode == BoundaryMode.WRAP:
            if self.player_rect.right < self.playfield.left:
                self.player_rect.left = self.playfield.right
            elif self.player_rect.left > self.playfield.right:
                self.player_rect.right = self.playfield.left

            if self.player_rect.bottom < self.playfield.top:
                self.player_rect.top = self.playfield.bottom
            elif self.player_rect.top > self.playfield.bottom:
                self.player_rect.bottom = self.playfield.top

            self.player_pos.update(self.player_rect.center)
            return

        # BOUNCE
        bounced = False
        if self.player_rect.left < self.playfield.left:
            self.player_rect.left = self.playfield.left
            self.player_vel.x *= -1
            bounced = True
        elif self.player_rect.right > self.playfield.right:
            self.player_rect.right = self.playfield.right
            self.player_vel.x *= -1
            bounced = True

        if self.player_rect.top < self.playfield.top:
            self.player_rect.top = self.playfield.top
            self.player_vel.y *= -1
            bounced = True
        elif self.player_rect.bottom > self.playfield.bottom:
            self.player_rect.bottom = self.playfield.bottom
            self.player_vel.y *= -1
            bounced = True

        if bounced:
            self.player_pos.update(self.player_rect.center)

    def _player_reaches_goal(self) -> bool:
        # Circle-vs-rect (approx): check rect center distance to goal.
        dx = self.player_pos.x - self.goal.pos.x
        dy = self.player_pos.y - self.goal.pos.y
        return (dx * dx + dy * dy) <= (self.goal.radius + self.PLAYER_SIZE * 0.3) ** 2

    def update(self, dt: float) -> None:
        if self.state != "play":
            return

        self.time_left -= dt
        if self.time_left <= 0:
            self.time_left = 0
            self.state = "lose"
            return

        if self.platformer_mode:
            x = self._read_horizontal()

            # Horizontal accel; no vertical input (gravity handles Y).
            self.player_vel.x += x * self.PLAYER_ACCEL * dt
            if x == 0:
                self.player_vel.x -= self.player_vel.x * min(1.0, self.PLAYER_FRICTION * dt)
            self.player_vel.x = max(-self.PLAYER_MAX_SPEED, min(self.PLAYER_MAX_SPEED, self.player_vel.x))

            # Jump is a discrete action.
            if self.jump_requested and self.on_ground:
                self.player_vel.y = -self.JUMP_SPEED
                self.on_ground = False
            self.jump_requested = False

            # Gravity.
            self.player_vel.y += self.GRAVITY * dt

            self.player_pos += self.player_vel * dt
            self.player_rect.center = (int(self.player_pos.x), int(self.player_pos.y))

            # Use the existing boundary mode for horizontal bounds.
            prev_y = self.player_rect.centery
            self._apply_bounds_player()
            self.player_rect.centery = prev_y
            self.player_pos.y = prev_y

            # Then apply platformer-specific vertical bounds.
            self._apply_platformer_vertical_bounds()
        else:
            direction = self._read_direction()

            # Accelerate toward direction.
            self.player_vel += direction * self.PLAYER_ACCEL * dt

            # Friction: nudge velocity toward zero.
            if direction.length_squared() == 0:
                self.player_vel -= self.player_vel * min(1.0, self.PLAYER_FRICTION * dt)

            if self.player_vel.length() > self.PLAYER_MAX_SPEED:
                self.player_vel.scale_to_length(self.PLAYER_MAX_SPEED)

            self.player_pos += self.player_vel * dt
            self.player_rect.center = (int(self.player_pos.x), int(self.player_pos.y))

            self._apply_bounds_player()

        # Teleporter: collision changes decision (risk/reward positional change).
        # Created for loop to iterate through teleporters since I wanted two teleporters for the game
        for tp in self.teleporters:
            if self.player_rect.colliderect(tp.rect):
                new_pos = self._random_point_in_playfield(margin=80)
                self.player_pos.update(new_pos)
                self.player_rect.center = (int(new_pos.x), int(new_pos.y))

        if self._player_reaches_goal():
            self.level += 1
            self.state = "win"

        # Decrease timer every 5 levels until timer reaches 5 seconds minimum
        if self.level >= self.level_up:
            if self.TIMER_SECONDS > 5:
                self.TIMER_SECONDS -= 5
                self.level_up += 5
            

    def _draw_hud(self) -> None:
        pygame.draw.rect(self.screen, (46, 52, 64), pygame.Rect(0, 0, self.SCREEN_W, self.HUD_H))

        control = "PLATFORMER" if self.platformer_mode else "TOPDOWN"
        left = f"Level {self.level}   Bounds: {self.boundary_mode.value.upper()}   Control: {control}"
        right = f"Time: {self.time_left:0.1f}s"

        left_surf = self.font.render(left, True, (216, 222, 233))
        right_surf = self.font.render(right, True, (216, 222, 233))

        self.screen.blit(left_surf, (14, 16))
        self.screen.blit(right_surf, (self.SCREEN_W - right_surf.get_width() - 14, 16))

    def _draw_center_message(self, title: str, subtitle: str) -> None:
        title_surf = self.big_font.render(title, True, (236, 239, 244))
        sub_surf = self.font.render(subtitle, True, (216, 222, 233))

        self.screen.blit(
            title_surf,
            (
                self.SCREEN_W // 2 - title_surf.get_width() // 2,
                self.SCREEN_H // 2 - 60,
            ),
        )
        self.screen.blit(
            sub_surf,
            (
                self.SCREEN_W // 2 - sub_surf.get_width() // 2,
                self.SCREEN_H // 2,
            ),
        )

    def draw(self) -> None:
        # Background
        self.screen.fill((20, 24, 30))

        # Playfield
        pygame.draw.rect(self.screen, (10, 12, 16), self.playfield)
        pygame.draw.rect(self.screen, (76, 86, 106), self.playfield, width=2)

        # Goal
        pygame.draw.circle(
            self.screen,
            (163, 190, 140),
            (int(self.goal.pos.x), int(self.goal.pos.y)),
            self.goal.radius,
        )

        # Teleporter
        # Drawing the teleporters in a loop to match the update method changes
        for tp in self.teleporters:
            pygame.draw.rect(self.screen, (180, 142, 173),  tp.rect, border_radius=6)

        # Player
        pygame.draw.rect(self.screen, (136, 192, 208), self.player_rect, border_radius=6)

        self._draw_hud()

        if self.state == "title":
            self._draw_center_message("Week 2", "Space: start   P: toggle control   Tab: bounds   Esc: quit")
        elif self.state == "win":
            self._draw_center_message("Level complete", "Space: next   P: toggle control   R: reset   Tab: bounds")
        elif self.state == "lose":
            self._draw_center_message("Time up", "Space: retry   R: reset   Tab: mode")
