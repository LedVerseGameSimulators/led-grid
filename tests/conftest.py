"""Headless pytest setup for loading the original LED level archives."""

from __future__ import annotations

import os
import shelve
import sys
import tempfile
import zipfile
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
GAMES_ROOT = REPO_ROOT / "games"

# Pickles in the archives refer to top-level modules such as ``model.group``.
for path in (REPO_ROOT, GAMES_ROOT):
    path_string = str(path)
    if path_string not in sys.path:
        sys.path.insert(0, path_string)

# Never inherit hardware/display settings from the developer's shell.
os.environ["USE_SERIAL_HD"] = "0"
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ.setdefault("DISABLE_AUDIO", "1")


@pytest.fixture(scope="session")
def load_level_archive():
    """Load the main gameplay shelf without importing side-effectful API code."""
    def load(relative_path: str):
        path = REPO_ROOT / relative_path
        assert path.is_file(), f"Expected repository level archive: {path}"
        fallback = None
        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(path, "r") as archive:
                archive.extractall(tmpdir)
            for root, directories, files in os.walk(tmpdir):
                directories.sort()
                files.sort()
                # Archives contain unrelated files beside dbm shelves. Only an
                # exact game_file.dat marks a shelf candidate for this format.
                if "game_file.dat" not in files:
                    continue
                shelf_path = os.path.join(root, "game_file")
                try:
                    with shelve.open(shelf_path, flag="r") as database:
                        game = database.get("para_key_game")
                        groups = database.get("dict_group")
                except Exception as exc:
                    raise RuntimeError(
                        f"Failed to read candidate level shelf {shelf_path} "
                        f"from archive {path}"
                    ) from exc
                # A readable auxiliary shelf may not contain gameplay keys.
                if game is None or groups is None:
                    continue
                if not getattr(game, "play_order", True):
                    return groups, game
                if fallback is None:
                    fallback = (groups, game)

        assert fallback is not None, f"Could not load a gameplay shelf from {path}"
        return fallback

    return load
