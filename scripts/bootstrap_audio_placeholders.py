#!/usr/bin/env python3
"""Create minimal silent WAV placeholders for Grid audio assets."""

from __future__ import annotations

import struct
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIO = ROOT / "games" / "audio"
EFFECTS = AUDIO / "effects"


def _silent_wav(path: Path, *, seconds: float = 0.15) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rate = 22050
    frames = int(rate * seconds)
    with wave.open(str(path), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(struct.pack("<h", 0) * frames)


def main() -> int:
    _silent_wav(AUDIO / "transition_stinger.wav", seconds=0.5)
    _silent_wav(EFFECTS / "bgm_bye_bye_bye.wav", seconds=1.0)
    _silent_wav(EFFECTS / "sfx_positive.wav", seconds=0.1)
    _silent_wav(EFFECTS / "sfx_negative.wav", seconds=0.1)
    _silent_wav(EFFECTS / "sfx_countdown_tick.wav", seconds=0.08)
    print(f"Wrote silent WAV placeholders under {AUDIO}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
