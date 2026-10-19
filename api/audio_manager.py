"""Non-blocking audio for Grid effects and gameplay SFX."""

from __future__ import annotations

import os
import queue
import threading
from pathlib import Path
from typing import Optional

from loguru import logger

from .config import GAMES_ROOT

_DISABLED = os.environ.get("DISABLE_AUDIO", "0") == "1"
_AUDIO_ROOT = GAMES_ROOT / "audio"
_EFFECTS_ROOT = _AUDIO_ROOT / "effects"


def _audio_file_usable(path: str) -> bool:
    if not path or not Path(path).is_file():
        return False
    try:
        with open(path, "rb") as fh:
            if fh.read(8).startswith(b"version "):
                logger.warning(
                    f"Audio file is a Git LFS pointer — run git lfs pull: {path}"
                )
                return False
    except OSError:
        return False
    return True


def _release_music(mixer) -> None:
    try:
        mixer.music.stop()
    except Exception:
        pass
    try:
        mixer.music.unload()
    except Exception:
        pass


class AudioManager:
    """Enqueue playback on a daemon thread; game thread never waits on mixer."""

    def __init__(self) -> None:
        self._ready = False
        self._mixer = None
        self._queue: queue.Queue[tuple[str, Optional[str]]] = queue.Queue()
        self._thread: Optional[threading.Thread] = None
        self._bgm_path: str | None = None

    def init(self) -> None:
        if self._ready or _DISABLED or self._thread is not None:
            return
        try:
            import pygame

            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=8, buffer=512)
            self._mixer = pygame.mixer
            self._ready = True
            self._thread = threading.Thread(
                target=self._worker, daemon=True, name="grid-audio"
            )
            self._thread.start()
            logger.info("AudioManager initialized")
        except Exception as exc:
            logger.warning(f"AudioManager init skipped: {exc}")

    def _worker(self) -> None:
        while True:
            cmd, path = self._queue.get()
            try:
                if cmd == "stop_bgm":
                    self._stop_bgm_locked()
                elif cmd == "start_bgm" and path:
                    self._start_bgm_locked(path)
                elif cmd == "play_sfx" and path:
                    self._play_sfx_locked(path)
                elif cmd == "play_transition" and path:
                    self._play_transition_locked(path)
            except Exception as exc:
                logger.debug(f"AudioManager skip {cmd}: {exc}")
            finally:
                self._queue.task_done()

    def _stop_bgm_locked(self) -> None:
        if self._mixer is None:
            return
        _release_music(self._mixer)

    def _start_bgm_locked(self, path: str) -> None:
        if self._mixer is None or not Path(path).is_file():
            return
        try:
            if self._bgm_path != path:
                self._mixer.music.load(path)
                self._bgm_path = path
            self._mixer.music.play(-1)
        except Exception as exc:
            logger.debug(f"BGM play skipped: {exc}")

    def _play_sfx_locked(self, path: str) -> None:
        if self._mixer is None or not Path(path).is_file():
            return
        try:
            ch = self._mixer.find_channel(True)
            if ch:
                ch.play(self._mixer.Sound(path))
        except Exception as exc:
            logger.debug(f"Could not play sound {path}: {exc}")

    def _play_transition_locked(self, path: str) -> None:
        self._stop_bgm_locked()
        if self._mixer is None or not _audio_file_usable(path):
            logger.warning(f"Transition stinger missing or unusable: {path}")
            return
        try:
            ch = self._mixer.find_channel(True)
            if ch:
                ch.set_volume(1.0)
                ch.play(self._mixer.Sound(path))
                logger.info("Transition stinger played (sfx)")
                return
        except Exception as exc:
            logger.warning(f"Transition stinger (sfx) failed: {exc}")
        try:
            self._mixer.music.load(path)
            self._mixer.music.play(loops=0)
            logger.info("Transition stinger played (music)")
        except Exception as exc:
            logger.warning(f"Transition stinger (music) failed: {exc}")

    def _resolve_stinger_path(self, phase: str | None = None) -> Path | None:
        if phase in ("level_clear", "level_fail"):
            for ext in ("mp3", "wav"):
                cand = _AUDIO_ROOT / f"{phase}.{ext}"
                if cand.is_file():
                    return cand
        for p in (
            _AUDIO_ROOT / "transition_stinger.mp3",
            _AUDIO_ROOT / "transition_stinger.wav",
            _EFFECTS_ROOT / "sfx_level_transition.mp3",
            _EFFECTS_ROOT / "sfx_level_transition.wav",
        ):
            if p.is_file():
                return p
        return None

    def _enqueue(self, cmd: str, path: Optional[str] = None) -> None:
        if not self._ready:
            return
        self._queue.put((cmd, path))

    def start_bgm(self, path: Path | None = None) -> None:
        self.init()
        if not self._ready:
            return
        target = path or (_EFFECTS_ROOT / "bgm_bye_bye_bye.mp3")
        if not target.is_file():
            target = _EFFECTS_ROOT / "bgm_bye_bye_bye.wav"
        if not target.is_file():
            return
        self._enqueue("start_bgm", str(target))

    play_bgm = start_bgm

    def stop_bgm(self) -> None:
        if not self._ready:
            return
        self._enqueue("stop_bgm")

    def play_sfx(self, path: Path) -> None:
        self.init()
        if not self._ready or not path.is_file():
            return
        self._enqueue("play_sfx", str(path))

    def play_stinger(self, phase: str | None = None) -> None:
        self.init()
        if not self._ready:
            return
        p = self._resolve_stinger_path(phase)
        if p is None:
            logger.warning(
                "Transition stinger missing (expected games/audio/transition_stinger "
                "or games/audio/effects/sfx_level_transition)"
            )
            return
        self._enqueue("play_transition", str(p))

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
