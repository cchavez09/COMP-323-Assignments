from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import pygame


class Scene(Protocol):
    name: str

    def handle_event(self, event: pygame.event.Event) -> None: ...

    def update(self, dt: float) -> None: ...

    def draw(self) -> None: ...


@dataclass
class SceneManager:
    current: Scene

    def switch_to(self, scene: Scene) -> None:
        self.current = scene
