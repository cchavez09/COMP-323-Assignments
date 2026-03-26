from __future__ import annotations

from array import array
import math

import pygame


class AudioBank:
    def __init__(self) -> None:
        self.enabled = False
        self.muted = False

        self.music_volume = 0.2
        self.sfx_volume = 0.3

        self._sounds: dict[str, pygame.mixer.Sound] = {}
        self._loop_channel: pygame.mixer.Channel | None = None

        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init(frequency=22050, size=-16, channels=2)

            pygame.mixer.set_num_channels(8)
            self._loop_channel = pygame.mixer.Channel(0)
            self.enabled = True
            self._build_sounds()
            self._apply_volumes()
        except pygame.error:
            self.enabled = False

    def _build_sounds(self) -> None:
        self._sounds = {
            "start": self._make_tone(523.25, 120, 0.85, wave="sine"),
            "scan": self._make_tone(740.0, 80, 0.60, wave="triangle"),
            # Altered title_loop to preset music for ambience within title menu
            "title_loop": pygame.mixer.Sound("audio_pass_starter/Assets/title_loop.mp3"),
            "play_loop": self._make_tone(261.63, 520, 0.12, wave="triangle"),
            # Added more sound effects/loop scenes
            "damage": self._make_tone(85.0, 65, 0.85, wave="square"),
            "pickup": self._make_tone(4125.0, 65, 0.25, wave="sine"),
            "win_loop": pygame.mixer.Sound("audio_pass_starter/Assets/win_scene.mp3"),
            "lose_loop": pygame.mixer.Sound("audio_pass_starter/Assets/lose_scene.mp3"),
        }

    def _make_tone(self, frequency: float, duration_ms: int, volume: float, *, wave: str) -> pygame.mixer.Sound:
        init = pygame.mixer.get_init()
        if init is None:
            raise pygame.error("Mixer not initialized")

        sample_rate, _fmt, channels = init
        sample_count = max(1, int(sample_rate * duration_ms / 1000))
        fade_len = max(1, min(sample_count // 8, int(sample_rate * 0.02)))
        max_amp = int(32767 * max(0.0, min(1.0, volume)))

        buf = array("h")
        for index in range(sample_count):
            phase = (index / sample_rate) * frequency
            frac = phase - math.floor(phase)

            if wave == "triangle":
                sample = 4.0 * abs(frac - 0.5) - 1.0
            elif wave == "square":
                sample = 1.0 if frac < 0.5 else -1.0
            elif wave == "saw":
                sample = 2.0 * frac - 1.0
            else:
                sample = math.sin(2.0 * math.pi * phase)

            envelope = 1.0
            if index < fade_len:
                envelope *= index / fade_len
            if index >= sample_count - fade_len:
                envelope *= (sample_count - index - 1) / fade_len

            amp = int(sample * envelope * max_amp)
            if channels == 2:
                buf.append(amp)
                buf.append(amp)
            else:
                buf.append(amp)

        return pygame.mixer.Sound(buffer=buf.tobytes())

    def _apply_volumes(self) -> None:
        if not self.enabled:
            return

        if self._loop_channel is not None:
            self._loop_channel.set_volume(0.0 if self.muted else self.music_volume)

        for name, sound in self._sounds.items():
            base = self.music_volume if name.endswith("_loop") else self.sfx_volume
            sound.set_volume(0.0 if self.muted else base)

    def toggle_mute(self) -> None:
        self.muted = not self.muted
        self._apply_volumes()

    # Added option to increase or decrease music volume and sfx volume
    def _adjust_volumes(self, adjust) -> None:
        if not self.enabled:
            return
        
        if self._loop_channel is not None and adjust:
            self.music_volume = min(1.0, self.music_volume + 0.05)
            self._loop_channel.set_volume(self.music_volume)
            
        
        if self._loop_channel is not None and not adjust:
            self.music_volume = max(0.0, self.music_volume - 0.05)
            self._loop_channel.set_volume(self.music_volume)
            

    def play(self, name: str) -> None:
        if not self.enabled or self.muted:
            return

        sound = self._sounds.get(name)
        if sound is not None:
            sound.play()

    def play_loop(self, name: str) -> None:
        if not self.enabled or self._loop_channel is None:
            return

        sound = self._sounds.get(name)
        if sound is None:
            return

        if self._loop_channel.get_sound() is sound:
            return

        self._loop_channel.stop()
        self._loop_channel.play(sound, loops=-1)
        self._apply_volumes()

    def stop_loop(self) -> None:
        if self._loop_channel is not None:
            self._loop_channel.stop()

    def shutdown(self) -> None:
        if self.enabled:
            self.stop_loop()