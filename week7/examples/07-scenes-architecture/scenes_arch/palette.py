from __future__ import annotations

from dataclasses import dataclass, field

import pygame


@dataclass(frozen=True)
class Palette:
    bg: pygame.Color = field(default_factory=lambda: pygame.Color("#1e222a"))
    panel: pygame.Color = field(default_factory=lambda: pygame.Color("#2a303c"))
    text: pygame.Color = field(default_factory=lambda: pygame.Color("#e5e9f0"))
    subtle: pygame.Color = field(default_factory=lambda: pygame.Color("#a3adbf"))

    player: pygame.Color = field(default_factory=lambda: pygame.Color("#88c0d0"))
    mob: pygame.Color = field(default_factory=lambda: pygame.Color("#bf616a"))
    projectile: pygame.Color = field(default_factory=lambda: pygame.Color("#ebcb8b"))

    hp_ok: pygame.Color = field(default_factory=lambda: pygame.Color("#1f6f3a"))
    hp_bad: pygame.Color = field(default_factory=lambda: pygame.Color("#7a1f2a"))
