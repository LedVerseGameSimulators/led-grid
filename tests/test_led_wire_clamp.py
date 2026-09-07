"""Serial LED wire encoding must reserve sync byte 255 for frame headers only."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from unittest import mock

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
GAMES_ROOT = REPO_ROOT / "games"
if str(GAMES_ROOT) not in sys.path:
    sys.path.insert(0, str(GAMES_ROOT))


@pytest.fixture(autouse=True)
def _real_led_modules():
    """Other suites mock led.* at import time; reload the real drivers here."""
    led_pkg = sys.modules.get("led")
    if led_pkg is None or isinstance(led_pkg, mock.MagicMock):
        for key in list(sys.modules):
            if key == "led" or key.startswith("led."):
                del sys.modules[key]
    import led.led_control as floor_module
    import led.led_control_c as wall_module

    importlib.reload(floor_module)
    importlib.reload(wall_module)
    yield floor_module, wall_module


from model.setting import Setting


class _FakeCom:
    def __init__(self):
        self.sent: list[list[int]] = []

    def Send_data(self, data):
        self.sent.append(list(data))


def _assert_wire_payload(payload: list[int]):
    assert len(payload) >= 2, payload
    assert payload[0] == 255
    assert payload[1] == 255
    for channel in payload[2:]:
        assert 0 <= channel <= 254, f"sync byte 255 leaked into RGB payload: {payload}"


@pytest.fixture()
def floor_wire(monkeypatch, _real_led_modules):
    floor_control = _real_led_modules[0]
    fake = _FakeCom()
    monkeypatch.setattr(Setting, "USE_SERIAL_HD", True)
    monkeypatch.setattr(floor_control, "list_com", [[fake, 1, 1]])
    monkeypatch.setattr(floor_control, "rect_position_arr", [(0, 0)])
    return floor_control, fake


@pytest.fixture()
def wall_wire(monkeypatch, _real_led_modules):
    fake = _FakeCom()
    monkeypatch.setattr(Setting, "USE_SERIAL_HD", True)
    controller = _real_led_modules[1].LedControl()
    controller.list_com = [[fake, 1, 1]]
    return _real_led_modules[1], controller, fake


def test_floor_draw_screen_by_com_retains_sync_header_and_clamps_payload(floor_wire):
    floor_control, fake = floor_wire
    logic = [[(255, 300, -5)]]
    floor_control.draw_screen_by_com(0, logic)
    assert len(fake.sent) == 1
    _assert_wire_payload(fake.sent[0])
    assert fake.sent[0] == [255, 255, 254, 254, 0]


def test_floor_display_led_screen_retains_sync_header_and_clamps_payload(floor_wire, monkeypatch):
    floor_control, fake = floor_wire
    monkeypatch.setattr(floor_control, "m_led_color_one_array", [(255, 0, 500)])
    floor_control.display_led_screen()
    assert len(fake.sent) == 1
    _assert_wire_payload(fake.sent[0])
    assert fake.sent[0] == [255, 255, 254, 0, 254]


def test_wall_draw_screen_by_com_retains_sync_header_and_clamps_payload(wall_wire):
    wall_module, controller, fake = wall_wire
    logic = [[(255, 128, 999)]]

    def _flatten(_layout, logic_2array, one_array):
        one_array[0] = logic_2array[0][0]

    with mock.patch("led.position_convert.position_convert_2arr_to_1arr", _flatten):
        controller.draw_screen_by_com(0, logic)

    assert len(fake.sent) == 1
    _assert_wire_payload(fake.sent[0])
    assert fake.sent[0] == [255, 255, 254, 128, 254]


def test_wall_draw_wall_light_by_com_retains_sync_header_and_clamps_payload(wall_wire):
    _wall_module, controller, fake = wall_wire
    controller.draw_wall_light_by_com([(255, 1, 260)])
    assert len(fake.sent) == 1
    _assert_wire_payload(fake.sent[0])
    assert fake.sent[0] == [255, 255, 254, 1, 254]


def test_wall_display_led_screen_retains_sync_header_and_clamps_payload(wall_wire):
    wall_module, controller, fake = wall_wire
    wall_module.m_led_color_one_array = [(0, 255, 255)]
    controller.display_led_screen()
    assert len(fake.sent) == 1
    _assert_wire_payload(fake.sent[0])
    assert fake.sent[0] == [255, 255, 0, 254, 254]


def test_gameplay_flash_white_avoids_sync_byte():
    from api.game_manager import _FLASH_ON_COLOR

    assert _FLASH_ON_COLOR == (254, 254, 254)
    assert all(0 <= channel <= 254 for channel in _FLASH_ON_COLOR)
