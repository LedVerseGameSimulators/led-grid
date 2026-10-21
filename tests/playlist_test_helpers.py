"""Patch playlist validation/sequence for HTTP session tests using fixture levels."""

from __future__ import annotations

from typing import Callable, Optional, Sequence


def patch_playlist_session(
    monkeypatch,
    sequence: Sequence[str | object],
    *,
    start_level: str = "003",
) -> str:
    """Force a fixed level path list through /start-game (playlist-aware engine).

    Patches ``validate_playlist_start`` on both ``api.game_manager`` and
    ``api.main`` (import binding) and replaces ``_build_playlist_sequence``.
    """
    import api.game_manager as gm
    import api.main as main_mod

    seq = [str(p) for p in sequence]

    def _fake_playlist_sequence(_mode_key: str, _start_id: str) -> list[str]:
        return seq

    def _noop_validate(_level, mode: Optional[str] = None) -> None:
        del _level, mode

    monkeypatch.setattr(gm, "_build_playlist_sequence", _fake_playlist_sequence)
    monkeypatch.setattr(gm, "validate_playlist_start", _noop_validate)
    monkeypatch.setattr(main_mod, "validate_playlist_start", _noop_validate)
    return start_level


def patch_playlist_session_callable(
    monkeypatch,
    build_sequence: Callable[[str, str], list[str]],
    *,
    start_level: str = "003",
) -> str:
    """Like ``patch_playlist_session`` but sequence depends on mode/start args."""
    import api.game_manager as gm
    import api.main as main_mod

    def _noop_validate(_level, mode: Optional[str] = None) -> None:
        del _level, mode

    monkeypatch.setattr(gm, "_build_playlist_sequence", build_sequence)
    monkeypatch.setattr(gm, "validate_playlist_start", _noop_validate)
    monkeypatch.setattr(main_mod, "validate_playlist_start", _noop_validate)
    return start_level
