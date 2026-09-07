"""Production transition .led assets must stay below serial sync byte 255."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.game_manager import _load_level_file

PROD_EFFECTS_DIR = ROOT / "games" / "source" / "effects"
EFFECT_NAMES = ("countdown", "level_clear", "level_fail")


def _collect_group_rgbs(dict_group) -> set[tuple[int, int, int]]:
    colors: set[tuple[int, int, int]] = set()
    for group in dict_group.values():
        color = getattr(group, "color", None)
        if isinstance(color, (list, tuple)) and color and isinstance(color[0], (list, tuple)):
            for row in color:
                colors.add(tuple(int(channel) for channel in row[:3]))
        elif isinstance(color, (list, tuple)) and len(color) >= 3:
            colors.add(tuple(int(channel) for channel in color[:3]))
    return colors


class ProductionEffectsRgbTests(unittest.TestCase):
    def test_production_transition_assets_avoid_sync_byte(self):
        for name in EFFECT_NAMES:
            path = PROD_EFFECTS_DIR / f"{name}.led"
            self.assertTrue(path.is_file(), f"missing production effect: {path}")
            dict_group, game_obj = _load_level_file(str(path))
            self.assertIsNotNone(dict_group, f"could not decode {path}")
            self.assertIsNotNone(game_obj, f"missing game metadata in {path}")

            colors = _collect_group_rgbs(dict_group)
            self.assertTrue(colors, f"{name} has no authored colors")
            self.assertFalse(
                any(channel == 255 for rgb in colors for channel in rgb),
                f"{name} contains RGB channel 255: {sorted(colors)}",
            )

    def test_production_transition_assets_are_not_all_black(self):
        for name in EFFECT_NAMES:
            path = PROD_EFFECTS_DIR / f"{name}.led"
            dict_group, _ = _load_level_file(str(path))
            colors = _collect_group_rgbs(dict_group)
            self.assertTrue(
                any(any(channel > 0 for channel in rgb) for rgb in colors),
                f"{name} is all black",
            )


if __name__ == "__main__":
    unittest.main()
