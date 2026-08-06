"""Non-blocking audio for Grid effects and gameplay SFX."""

from __future__ import annotations

import os
from pathlib import Path

from loguru import logger

from .config import GAMES_ROOT

_DISABLED = os.environ.get("DISABLE_AUDIO", "0") == "1"
_AUDIO_ROOT = GAMES_ROOT / "audio"
_EFFECTS_ROOT = _AUDIO_ROOT / "effects"


class AudioManager:
    """Fire-and-forget mixer wrapper — never blocks the game thread."""

    def __init__(self) -> None:
        self._ready = False
        self._mixer = None
        self._bgm_path: str | None = None

    def init(self) -> None:
        if self._ready or _DISABLED:
            return
        try:
            import pygame

            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self._mixer = pygame.mixer
            self._ready = True
            logger.info("AudioManager initialized")
        except Exception as exc:
            logger.warning(f"AudioManager init skipped: {exc}")

    def _sound(self, path: Path):
        if not self._ready or not path.is_file():
            return None
        try:
            return self._mixer.Sound(str(path))
        except Exception as exc:
            logger.debug(f"Could not load sound {path}: {exc}")
            return None

    def start_bgm(self, path: Path | None = None) -> None:
        self.init()
        if not self._ready:
            return
        target = path or (_EFFECTS_ROOT / "bgm_bye_bye_bye.mp3")
        if not target.is_file():
            target = _EFFECTS_ROOT / "bgm_bye_bye_bye.wav"
        if not target.is_file():
            return
        try:
            if self._bgm_path != str(target):
                self._mixer.music.load(str(target))
                self._bgm_path = str(target)
            self._mixer.music.play(-1)
        except Exception as exc:
            logger.debug(f"BGM play skipped: {exc}")

    play_bgm = start_bgm

    def stop_bgm(self) -> None:
        if not self._ready:
            return
        try:
            self._mixer.music.stop()
        except Exception:
            pass

    def play_sfx(self, path: Path) -> None:
        self.init()
        snd = self._sound(path)
        if snd is not None:
            try:
                snd.play()
            except Exception:
                pass

    def play_stinger(self) -> None:
        p = _AUDIO_ROOT / "transition_stinger.mp3"
        if not p.is_file():
            p = _AUDIO_ROOT / "transition_stinger.wav"
        self.play_sfx(p)

    def play_countdown_tick(self) -> None:
        p = _EFFECTS_ROOT / "sfx_countdown_tick.mp3"
        if not p.is_file():
            p = _EFFECTS_ROOT / "sfx_countdown_tick.wav"
        self.play_sfx(p)

    def play_score_positive(self) -> None:
        p = _EFFECTS_ROOT / "sfx_positive.mp3"
        if not p.is_file():
            p = _EFFECTS_ROOT / "sfx_positive.wav"
        self.play_sfx(p)

    def play_score_negative(self) -> None:
        p = _EFFECTS_ROOT / "sfx_negative.mp3"
        if not p.is_file():
            p = _EFFECTS_ROOT / "sfx_negative.wav"
        self.play_sfx(p)

    @property
    def active(self) -> bool:
        return self._ready and not _DISABLED
