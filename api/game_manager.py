"""
Game Manager - Floor Is Lava (Grid)
Manages running Play instances and game state for the 16×26 LED floor game.
Headless: no tkinter GUI. Input via API websocket, output via LED state.
"""
import uuid
import threading
import time
import asyncio
import os
import sys
import math
import shelve as _shelve
from typing import Dict, Optional
from loguru import logger
from .config import GAME_TIMEOUT_SECONDS, MAX_CONCURRENT_GAMES, GAMES_ROOT

USE_SERIAL_HD = os.environ.get("USE_SERIAL_HD", "0") == "1"
if USE_SERIAL_HD:
    _games_dir = str(GAMES_ROOT)
    if _games_dir not in sys.path:
        sys.path.insert(0, _games_dir)

# Mock hardware/network dependencies before importing game_play
# These are not needed for headless game logic:
# - tkinter: GUI (game_running.py imports tkinter.messagebox)
# - encryption: hardware dongle check (yanqian.py checks connected pedrive at module level)
# - led.led_control: hardware LED driver
# - net: network communication
from unittest.mock import MagicMock

# Mock ALL external dependencies (hardware, GUI, media, etc)
# Standard approach: mock before any imports to prevent ModuleNotFoundError
mocks = {
    # GUI/Display
    'tkinter': MagicMock(),
    'tkinter.messagebox': MagicMock(),
    'tkinter.font': MagicMock(),
    'gui': MagicMock(),
    'gui.app_gui': MagicMock(),
    'gui.gui_debugging': MagicMock(),
    'gui.gui_setting': MagicMock(),
    'gui.language': MagicMock(),
    'gui2': MagicMock(),
    'gui2.gui_led_table_editor': MagicMock(),
    'gui2.gui_led_canvas2': MagicMock(),
    'gui2.gui_table_editor': MagicMock(),
    'gui2.ui_player_setting': MagicMock(),
    'gui2.ui_table': MagicMock(),
    'gui2.gui_util': MagicMock(),
    'ui_design': MagicMock(),
    # Hardware
    **({} if USE_SERIAL_HD else {
        'serial': MagicMock(),
        'serial.tools': MagicMock(),
        'serial.tools.list_ports': MagicMock(),
        'led': MagicMock(),
        'led.led_control': MagicMock(),
        'led.communication': MagicMock(),
        'led.position_convert': MagicMock(),
        'led.led_serial_thread': MagicMock(),
        'led.led_control_c': MagicMock(),
    }),
    'net': MagicMock(),
    'socket': MagicMock(),
    # Audio/Video
    'pygame': MagicMock(),
    'pygame.mixer': MagicMock(),
    'audio_play': MagicMock(),
    'audio_play.audio': MagicMock(),
    'moviepy': MagicMock(),
    'moviepy.editor': MagicMock(),
    'cv2': MagicMock(),
    # Input
    'pynput': MagicMock(),
    'pynput.keyboard': MagicMock(),
    'pynput.mouse': MagicMock(),
    # Encryption
    'encryption': MagicMock(),
    'encryption.yanqian': MagicMock(),
    'rsa': MagicMock(),
    'Crypto': MagicMock(),
    'Crypto.Hash': MagicMock(),
    'Crypto.Cipher': MagicMock(),
    'Crypto.PublicKey': MagicMock(),
    'Crypto.Signature': MagicMock(),
    # Database
    'mysql': MagicMock(),
    'mysql.connector': MagicMock(),
    # Image processing
    'numpy': MagicMock(),
    'PIL': MagicMock(),
    'PIL.Image': MagicMock(),
    'PIL.ImageTk': MagicMock(),
}

for mod_name, mock in mocks.items():
    sys.modules[mod_name] = mock

_HW_DEFAULT_ROWS = 16
_HW_DEFAULT_COLS = 26
_hw_led_control = None
_hw_layout_type = 0
# Full-floor serial write (~1.2KB × 3 ports) takes ~80–150ms at 115200 baud.
# Drawing faster than this blocks the game loop and delays input + simulator.
_HW_DRAW_INTERVAL = float(os.environ.get("HW_DRAW_INTERVAL", "0.045"))  # ~22fps: matches serial hw ceiling
_hw_serial_lock = threading.Lock()  # all COM I/O on game thread only


def _normalize_rgb(cell):
    """Ensure [R,G,B] ints. Play.clear_led_table can leave nested tuples."""
    if isinstance(cell, (list, tuple)):
        if len(cell) >= 3 and isinstance(cell[0], (int, float)):
            return [int(cell[0]), int(cell[1]), int(cell[2])]
        if len(cell) == 1:
            return _normalize_rgb(cell[0])
    return [0, 0, 0]


def _hw_read_sensors(layout_type, state_table):
    """Read floor sensors (fast ~0.2ms). Caller must hold _hw_serial_lock."""
    if _hw_led_control is None:
        return
    _hw_led_control.update_screen_state_by_com(layout_type, state_table, state_table)


def _hw_draw_floor(layout_type, led_2d):
    """Send colors to floor. Caller must hold _hw_serial_lock."""
    if _hw_led_control is None:
        return
    rows = len(led_2d)
    cols = len(led_2d[0]) if rows else 0
    safe = [[_normalize_rgb(led_2d[r][c]) for c in range(cols)] for r in range(rows)]
    _hw_led_control.draw_screen_by_com(layout_type, safe)

def _hw_init():
    global _hw_led_control, _hw_layout_type
    if _hw_led_control is not None:
        return _hw_led_control
    try:
        import shelve as _s
        from led import led_control as _lc
        db = _s.open(str(GAMES_ROOT / 'setting' / 'led_parameter'), flag='r')
        list_com_info = db.get('list_com_info', [])
        layout_type   = int(db.get('led_layout_type', 0))
        no_use        = db.get('floor_layout_coors_no_use', [])
        rows          = int(float(db.get('value_high', _HW_DEFAULT_ROWS)))
        cols          = int(float(db.get('value_width', _HW_DEFAULT_COLS)))
        db.close()
        _lc.init_layout(layout_type, rows, cols, no_use)
        errors = _lc.init_com(list_com_info)
        if errors:
            logger.warning(f"HW init COM errors (non-fatal): {errors}")
        # Headless API: never block on serial reads (shelve may have com_is_block=True).
        _lc.com_is_block = False
        for com_entry in _lc.list_com:
            try:
                port = com_entry[0].main_engine
                port.timeout = 0.02
                port.write_timeout = 0.1
            except Exception:
                pass
        logger.info(f"Hardware ready: {len(list_com_info)} port(s), {rows}×{cols}, layout={layout_type}")
        _hw_led_control = _lc
        _hw_layout_type = layout_type
    except Exception as e:
        logger.error(f"Hardware init failed: {e}")
    return _hw_led_control

# Will import after config is set
# from game_play.Play import Play

# Grid scoring colors (from model/setting.py PLUS_ARR subset used in levels).
# 1P: blue tiles score +1.  2P (---- series): P1=blue, P2=orange.
_GRID_P1_COLOR = (0, 0, 254)
_GRID_P2_COLOR = (254, 128, 0)
_GRID_SCORE_COLORS_1P = {_GRID_P1_COLOR}
_GRID_SCORE_COLORS_2P = {_GRID_P1_COLOR, _GRID_P2_COLOR}
_GRID_HAZARD_COLORS = {(254, 0, 0), (240, 0, 0)}

# Settings from Climb's own led_parameter shelve.
_LED_PARAM  = str(GAMES_ROOT / "setting" / "led_parameter")
_DEBUG_PARAM = str(GAMES_ROOT / "setting" / "debug_parameter")

# Sensible fallbacks if the shelve can't be read.
_SETTINGS_DEFAULTS = {
    "game_time_sec": 300.0,    # game_time_sw (min) * 60
    "life_value": 20,          # life_value_sw  (starting HP)
    "leval_span": 0.5,         # leval_span_sw  (Floor Is Lava default)
    "blue_hide_max_time": 5.0, # blue_hide_max_time_sw
    "corner_line_start": 0,    # corner_line_start
    "tread_red_time": 0.01,    # debug: secs on red before life loss
    "life_value_count_time": 1.2,  # debug: min secs between life losses
    "grid_rows": 16,           # value_high  — 16 rows
    "grid_cols": 26,           # value_width — 26 cols (SQUARE grid)
    "scode_divide_person": False,  # game_scode_divide_person
    "scode_divide_time": False,    # game_scode_divide_time
    "player_num": 1,               # player_num_sw (overridden by 2P levels)
}

_settings_cache = None


def load_real_settings() -> dict:
    """Read game settings from the decompiled project's shelve DBs once.
    Returns a parsed dict; falls back to defaults on any error."""
    global _settings_cache
    if _settings_cache is not None:
        return _settings_cache
    s = dict(_SETTINGS_DEFAULTS)
    # led_parameter: game length, HP, speed span
    try:
        db = _shelve.open(_LED_PARAM, flag="r")
        try:
            gt = db.get("game_time_sw")
            if gt is not None:
                s["game_time_sec"] = float(gt) * 60.0   # stored in minutes
            lv = db.get("life_value_sw")
            if lv is not None:
                s["life_value"] = int(float(lv))
            ls = db.get("leval_span_sw")
            if ls is not None:
                s["leval_span"] = float(ls)
            vh = db.get("value_high")
            if vh is not None:
                s["grid_rows"] = int(float(vh))
            vw = db.get("value_width")
            if vw is not None:
                s["grid_cols"] = int(float(vw))
            dp = db.get("game_scode_divide_person")
            if dp is not None:
                s["scode_divide_person"] = bool(dp)
            dt = db.get("game_scode_divide_time")
            if dt is not None:
                s["scode_divide_time"] = bool(dt)
            pn = db.get("player_num_sw")
            if pn is not None:
                s["player_num"] = int(float(pn))
            bh = db.get("blue_hide_max_time_sw")
            if bh is not None:
                s["blue_hide_max_time"] = float(bh)
            cls = db.get("corner_line_start")
            if cls is not None:
                s["corner_line_start"] = int(float(cls))
        finally:
            db.close()
    except Exception as e:
        logger.warning(f"Could not read led_parameter: {e}; using defaults")
    # debug_parameter: red-penalty timing
    try:
        db = _shelve.open(_DEBUG_PARAM, flag="r")
        try:
            trt = db.get("tread_red_time")
            if trt is not None:
                s["tread_red_time"] = float(trt)
            lct = db.get("life_value_count_time")
            if lct is not None:
                s["life_value_count_time"] = float(lct)
        finally:
            db.close()
    except Exception as e:
        logger.warning(f"Could not read debug_parameter: {e}; using defaults")
    _settings_cache = s
    logger.info(f"Loaded real settings: {s}")
    return s


def _make_play_setting(settings: dict):
    """Mock Setting object for Play.__init__ — values from real shelve settings."""

    class _Attr:
        def __init__(self, val):
            self._val = val

        def get(self):
            return self._val

    class MockSetting:
        def __init__(self, s):
            self.leval_span = _Attr(s.get("leval_span", 0.5))
            self.blue_hide_max_time = _Attr(s.get("blue_hide_max_time", 5.0))
            self.corner_line_start = _Attr(s.get("corner_line_start", 0))

    return MockSetting(settings)


# Level-progression tiers (dirs under source/, easy->hard). Category is
# locked by the START level's file type: .led = 1-player, .ledb = 2-player.
# A 1P session marathons only the 1P tiers and never crosses into 2P.
_TIERS_1P = ["-", "--", "---"]   # easy -> medium -> hard (.led)
_TIERS_2P = ["----"]             # 2-player (.ledb)


def _build_level_sequence(start_level):
    """Ordered list of level FILE PATHS forming the marathon.

    Category is locked by the START level's file type. A start level found in
    a 1P (.led) tier yields a 1P-only chain (its tier onward through
    _TIERS_1P); a start level in a 2P (.ledb) tier yields a 2P-only chain.
    Never mixes. Exact stem match is tried before prefix match so e.g. "001"
    doesn't accidentally match "001 HARD" in the hard tier."""
    import glob as _glob
    src = str(GAMES_ROOT)
    sl = str(start_level or "001").strip()

    def _sort_key(p):
        stem = os.path.basename(p).rsplit(".", 1)[0]
        return (0, int(stem)) if stem.isdigit() else (1, stem.lower())

    def _chain(dirs, ext):
        return [(d, sorted(_glob.glob(os.path.join(src, "source", d, f"*.{ext}")),
                           key=_sort_key)) for d in dirs]

    chain_1p = _chain(_TIERS_1P, "led")
    chain_2p = _chain(_TIERS_2P, "ledb")

    def _find(chain, exact):
        for ti, (_d, files) in enumerate(chain):
            for fi, f in enumerate(files):
                stem = os.path.basename(f).rsplit(".", 1)[0]
                matched = (stem == sl) if exact else stem.startswith(sl)
                if matched:
                    return ti, fi
        return None

    # Exact match first (across both categories), then prefix fallback.
    loc = _find(chain_1p, exact=True)
    chain = chain_1p
    if loc is None:
        loc = _find(chain_2p, exact=True)
        chain = chain_2p
    if loc is None:
        loc = _find(chain_1p, exact=False)
        chain = chain_1p
    if loc is None:
        loc = _find(chain_2p, exact=False)
        chain = chain_2p
    if loc is None:                       # unknown start -> begin at 1P tier 0
        chain, loc = chain_1p, (0, 0)
        if not chain or not chain[0][1]:
            return []

    ti, fi = loc
    seq = list(chain[ti][1][fi:])         # remaining levels in the start tier
    for j in range(ti + 1, len(chain)):   # then all later SAME-category tiers
        seq.extend(chain[j][1])
    return seq


def _load_level_file(path):
    """Load one .led/.ledb: unzip, find the main gameplay shelve (the one with
    play_order=False; audio/anim dirs have play_order=True), return
    (dict_group, game_obj) as in-memory objects. (None, None) on failure."""
    import zipfile, tempfile, shelve
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(path, 'r') as z:
                z.extractall(tmpdir)
            best_go = best_dg = None
            for root, _, files in os.walk(tmpdir):
                if not any(f.startswith("game_file") for f in files):
                    continue
                gf = os.path.join(root, "game_file")
                if not os.path.exists(gf + ".dat"):
                    continue
                try:
                    db = shelve.open(gf)
                    go = db.get("para_key_game")
                    dg = db.get("dict_group")
                    db.close()
                    if go is None or dg is None:
                        continue
                    if not getattr(go, "play_order", True):
                        return dg, go          # main gameplay — done
                    elif best_go is None:
                        best_go, best_dg = go, dg
                except Exception:
                    continue
            return best_dg, best_go
    except Exception as e:
        logger.warning(f"Could not load level file {path}: {e}")
        return None, None


class HeadlessLedTable:
    """In-memory LED table — replaces tkinter LedTable for headless API operation.
    Same interface as gui2/gui_led_table_editor.LedTable but zero GUI deps.
    Ported from LED-Hex SimulatorLedTable.
    """

    def __init__(self, wall_light_arr_len: int, led_row: int, led_col: int):
        self.led_row = led_row
        self.led_col = led_col
        self.row = led_row
        self.col = led_col
        # Floor LED colors: led_table[row][col] = [R, G, B]
        self.led_table = [[[0, 0, 0] for _ in range(led_col)] for _ in range(led_row)]
        # Tile press state: True = being stepped on
        self._state_table = [[False] * led_col for _ in range(led_row)]
        self.table_state = self._state_table   # shared ref
        self.state_table = self._state_table   # alias (game_manager callback uses this)
        self.state_2array = [[5] * led_col for _ in range(led_row)]
        self.g_wall_has_been_tread_arr2 = [[False] * led_col for _ in range(led_row)]
        # Wall arrays
        self._wall_light_arr = [[0, 0, 0] for _ in range(wall_light_arr_len)]
        self._wall_light_state_array = [False] * wall_light_arr_len
        self._wall_screen_arr = [0] * wall_light_arr_len
        # Per-tile scoring state
        self.red_table = [[False] * led_col for _ in range(led_row)]
        self.green_table = [[False] * led_col for _ in range(led_row)]
        self.safe_table = [[False] * led_col for _ in range(led_row)]
        self.deduct_table = [[False] * led_col for _ in range(led_row)]
        self.plus_table = [[None] * led_col for _ in range(led_row)]
        self.other_color_table = [[False] * led_col for _ in range(led_row)]
        self.blue_table = [[False] * led_col for _ in range(led_row)]
        self.tread_short_stay = [[None] * led_col for _ in range(led_row)]
        self.goal_color = None
        self.goal_color2 = None
        self.safe_color = None
        self.canvas = None
        self.led_coors_click = [[0, 0], False]
        self.led_coors_click_wall = [[0, 0], False]

    # ── State table ────────────────────────────────────────────────────
    def get_state_table(self):
        return self._state_table

    def get_state_2array(self):
        return self.state_2array

    def get_g_wall_has_been_tread_arr2(self):
        return self.g_wall_has_been_tread_arr2

    # ── Wall accessors ─────────────────────────────────────────────────
    def get_wall_light_arr(self):
        return self._wall_light_arr

    def get_wall_light_state_array(self):
        return self._wall_light_state_array

    def get_wall_screen_arr(self):
        return self._wall_screen_arr

    # ── Color output ───────────────────────────────────────────────────
    def set_color_table_by_set_cell(self, start_member, color) -> None:
        c = list(color) if isinstance(color, (tuple, list)) else [0, 0, 0]
        for cell in (start_member or []):
            try:
                r_idx, c_idx = int(round(cell[0])), int(round(cell[1]))
                if 0 <= r_idx < self.led_row and 0 <= c_idx < self.led_col:
                    self.led_table[r_idx][c_idx] = c[:]
            except (IndexError, TypeError, ValueError):
                pass

    def set_table_color(self, table, color=None):
        c = list(color) if isinstance(color, (tuple, list)) else [0, 0, 0]
        for row in table:
            for i in range(len(row)):
                row[i] = c[:]

    def redraw_led_table_default(self, line=0, draw_canvas=True):
        pass  # no-op: game_manager reads led_table directly

    def draw_led_color(self):
        pass

    def clear_led_table(self):
        for r in range(self.led_row):
            for c in range(self.led_col):
                self.led_table[r][c] = [0, 0, 0]
        for i in range(len(self._wall_light_arr)):
            self._wall_light_arr[i] = [0, 0, 0]
        self._wall_screen_arr = [0] * wall_light_arr_len

    def screen_mouse_click_state_get(self):
        pass

    # ── Input (press/release from simulator) ──────────────────────────
    def press_cell(self, row: int, col: int):
        if 0 <= row < self.led_row and 0 <= col < self.led_col:
            self._state_table[row][col] = True

    def release_cell(self, row: int, col: int):
        if 0 <= row < self.led_row and 0 <= col < self.led_col:
            self._state_table[row][col] = False

    # ── tkinter-compat stubs ───────────────────────────────────────────
    def pack(self, **kw): pass
    def grid(self, **kw): pass
    def update(self): pass
    def update_idletasks(self): pass
    def configure(self, **kw): pass
    def config(self, **kw): pass
    def destroy(self): pass
    def bind(self, *a, **kw): pass
    def unbind(self, *a, **kw): pass
    def after(self, ms, func=None, *args):
        import threading
        if func:
            t = threading.Timer(ms / 1000.0, func, args)
            t.daemon = True
            t.start()
    def after_cancel(self, *a): pass
    def winfo_width(self): return self.led_col * 44
    def winfo_height(self): return self.led_row * 38
    def get_canvas_table_size(self): return (self.led_row, self.led_col)


def _normalize_rings(cell):
    """Normalize a led_table cell to 3 ring colors [[r,g,b],[r,g,b],[r,g,b]]
    (outer, mid, inner). Cell is normally a 3-ring list, but tolerate a flat
    (r,g,b) (broadcast to all rings)."""
    try:
        if isinstance(cell, (list, tuple)) and len(cell) > 0:
            if isinstance(cell[0], (list, tuple)):
                rings = [[int(c[0]), int(c[1]), int(c[2])] for c in cell[:3]]
                while len(rings) < 3:
                    rings.append(rings[-1])
                return rings
            # flat (r,g,b) -> all rings same
            rgb = [int(cell[0]), int(cell[1]), int(cell[2])]
            return [rgb, rgb, rgb]
    except Exception:
        pass
    return [[0, 0, 0], [0, 0, 0], [0, 0, 0]]


def _cell_is_lit(cell):
    """True if any ring of the cell has a non-zero channel."""
    for ring in _normalize_rings(cell):
        if ring[0] or ring[1] or ring[2]:
            return True
    return False


def _cell_is_red(cell):
    """True if any ring is RED-dominant ((254,0,0)-like). Red = penalty tile."""
    for r, g, b in _normalize_rings(cell):
        if r >= 200 and g < 80 and b < 80:
            return True
    return False


def _group_main_color(color):
    """A group's representative color = its middle ring (ring[1]); ring[0] is a
    constant green marker. Returns an (r,g,b) tuple."""
    rings = _normalize_rings(color)
    return tuple(rings[1])


def _rgb_is_deduct(rgb):
    """DEDUCT_COLOR (254,0,48): consume + penalty (distinct from plain red)."""
    return rgb[0] >= 200 and rgb[1] < 80 and 30 <= rgb[2] <= 90


def _rgb_is_red(rgb):
    """Plain RED (254,0,0): hazard, stays, repeats. Excludes DEDUCT (b~48)."""
    return rgb[0] >= 200 and rgb[1] < 80 and rgb[2] < 30


class HeadlessGameGUI:
    """Mock GUI parent for Play.running_new() - provides LED update callback"""

    def __init__(self, led_table):
        self.led_table = led_table

    def update_draw_led_table_idle_game(self, dict_group, total_pass=0, time_pass=0):
        """Called by Play.running_new() to update LED display"""
        try:
            if dict_group:
                for key, value in dict_group.items():
                    group = value
                    set_cell = group.start_member
                    start_time = group.start_time_sec
                    end_time = group.end_time_sec
                    if set_cell is not None and total_pass > start_time and total_pass < end_time:
                        color = getattr(group, 'color', (0, 255, 0))
                        if hasattr(self.led_table, 'set_color_table_by_set_cell'):
                            self.led_table.set_color_table_by_set_cell(set_cell, color)
        except Exception as e:
            logger.debug(f"LED update error: {e}")

    def clear_last_wall_display(self):
        """Clear display for next frame"""
        pass


class GameInstance:
    """Single running game instance"""

    def __init__(self, game_id: str, card_id: str, level: int, difficulty: str):
        self.game_id = game_id
        self.card_id = card_id
        self.level = level
        self.difficulty = difficulty
        self.created_at = time.time()
        self.play = None  # Play object
        self.led_table = None  # LedTable instance (for press input)
        self.dict_group = None  # level groups (for consume-on-hit)
        self.flashes = {}  # cell -> wall-clock start time (display-only hit flash)
        self.score = 0  # accumulated score from presses on lit tiles
        self.scored_active = set()  # goal cells already scored this appearance
        # Per-frame cell classification (rebuilt each frame from dict_group):
        self.goal_cells = set()    # floor cells matching P1 goal color (scoreable)
        self.goal2_cells = set()   # floor cells matching P2 goal color (2-player)
        self.red_cells = set()     # in-time red hazard cells (penalty, stays)
        self.deduct_cells = set()  # DEDUCT_COLOR cells (penalty + consume)
        self.goal_color = None     # P1 goal color (from goal_led indicator)
        self.goal2_color = None    # P2 goal color (from goal2_led indicator)
        self.score2 = 0            # P2 score (0 in single-player)
        self.scored_active2 = set()# P2 scored cells this appearance
        self.multiplayer = False   # True when level has goal2_led
        self.zone = None          # (row_from,row_to,col_from,col_to) active area
        # 2P respawn: consumed goal tiles reappear after delay (only for .ledb multiplayer)
        self.pending_respawn = []  # [[group, (i,j), reappear_wall_time], ...]
        self.respawn_delay = 8.0   # seconds; tunable
        # Same-color 2P (e.g. DK03 cyan==cyan): alternate P1→P2→P1→P2 per cell.
        # Cells in this set score P2 next; others score P1.
        self.p2_next_cells = set()
        self.input_lock = threading.Lock()  # guards state_table writes
        self._sim_pressed = set()  # simulator clicks (not wiped by HW sensor read)
        self._frame_count = 0
        self._last_frame_at = 0.0
        self.running = False

        # Real settings (game length + HP). Loaded from led_parameter.
        _s = load_real_settings()
        self.game_time_sec = _s["game_time_sec"]   # session limit (300s)
        self.board_time_sec = 1e9                   # board length (max group end); set on load
        self.result = None                          # 0 lose / 1 complete / 2 timeout
        self.max_life = _s["life_value"]           # 20 HP
        self.life = self.max_life
        # Final-score normalization (game_scode_rule): divide raw score by
        # player count and/or game-time (minutes). Applied at session end only;
        # live `score` stays raw for display.
        self._scode_divide_person = _s.get("scode_divide_person", True)
        self._scode_divide_time = _s.get("scode_divide_time", True)
        # Default 1 player; _setup_level bumps to 2 for actual 2P (DK) levels.
        # (player_num_sw is the machine's max-player config, not per-game.)
        self._player_num = 1
        self.last_life_loss_time = 0.0             # for life_value_count_time gate
        self._life_count_time = _s["life_value_count_time"]

        # ── SESSION (5-min marathon) state ──────────────────────────────
        # Score + lives persist across levels; session ends on life<=0 or
        # timer<=0. Player picks a starting level; we marathon to series end.
        self.session_start = None      # wall-clock when first level begins
        self.level_sequence = []       # ordered list of level FILE PATHS
        self.current_level_id = None   # e.g. "A005" (for frontend display)
        self.levels_cleared = 0        # how many levels finished this session
        self._session_over = False     # True -> stop the session loop
        self._level_cleared = False    # True -> advance to next level
        self._restart_level = False    # True -> replay same level (life=0, time left)

        self.current_state = {
            "score": 0,
            "time_elapsed": 0.0,
            "time_left": self.game_time_sec,
            "life": self.max_life,
            "max_life": self.max_life,
            "display_lives": 5,   # always 5 hearts at full HP, whatever max_life is
            "display_max": 5,
            "score2": 0,
            "multiplayer": False,
            "player_pos": [0, 0],
            "led_display": [],
            "game_over": False,
            "game_over_reason": "",
            "result": None,
            "current_level": None,
            "levels_cleared": 0,
            "pressed_tiles": [],
        }
        self.thread = None

    def _get_pressed_tiles(self):
        """Merge hardware sensor state + simulator mouse presses."""
        tiles = []
        if self.led_table is None:
            return tiles
        st = self.led_table.state_table
        for r, row in enumerate(st):
            for c, v in enumerate(row):
                if v or (r, c) in self._sim_pressed:
                    tiles.append({
                        "row": r,
                        "col": c,
                        "src": "sim" if (r, c) in self._sim_pressed else "hw",
                    })
        return tiles

    def _sync_live_feedback(self):
        """Push score/life/presses immediately (don't wait for serial draw)."""
        self.update_state(
            score=self.score,
            score2=self.score2,
            life=self.life,
            pressed_tiles=self._get_pressed_tiles(),
        )

    def compute_final_score(self, raw_score):
        """No score division for Floor Is Lava — raw score is final."""
        return float(raw_score)

    def reset_for_level(self):
        """Clear PER-LEVEL board state before loading the next level.
        Score, score2, life, session timer all PERSIST (not reset)."""
        self.flashes = {}
        self.scored_active = set()
        self.scored_active2 = set()
        self.pending_respawn = []
        self.p2_next_cells = set()
        self.goal_cells = set()
        self.goal2_cells = set()
        self.red_cells = set()
        self.deduct_cells = set()
        self.last_life_loss_time = 0.0
        self._level_cleared = False
        self._restart_level = False

    def _current_level_time(self) -> float:
        """Level timeline for consume/scoring (Play.total_pass)."""
        if self.play is not None:
            return float(getattr(self.play, "total_pass", 0.0))
        return 0.0

    def is_expired(self) -> bool:
        """Check if game timed out"""
        elapsed = time.time() - self.created_at
        return elapsed > GAME_TIMEOUT_SECONDS

    def get_state(self) -> dict:
        """Get current game state"""
        return self.current_state

    def update_state(self, **kwargs):
        """Update game state"""
        self.current_state.update(kwargs)

    def try_score_cell(self, i, j, total_pass=None):
        """Type-aware scoring for a press on cell (i,j):
          - red hazard cell  -> -1 point + -1 HP (HP rate-limited)
          - goal_led target  -> +1 point + consume (tile blanks) + flash
          - background decor  -> nothing (neutral)
        goal/red membership is classified per frame in the callback."""
        if total_pass is None:
            total_pass = self._current_level_time()
        # Red hazard: penalty + HP loss (gated). Not edge-limited by
        # scored_active (standing on red keeps hurting, rate-limited by time).
        if (i, j) in self.red_cells:
            now = time.time()
            if now - self.last_life_loss_time >= self._life_count_time:
                self.score -= 1
                if self.score < 0:
                    self.score = 0
                if self.multiplayer:          # red hurts both players in 2P
                    self.score2 -= 1
                    if self.score2 < 0:
                        self.score2 = 0
                self.life -= 1
                self.last_life_loss_time = now
            self._sync_live_feedback()
            return
        # DEDUCT tile: -1 SCORE only (NO life loss), then consume.
        # Faithful to original gui_editor_game.py (DEDUCT_COLOR block):
        # scode_value -= ONE_SCODE_VALUE, no life_value change.
        if (i, j) in self.deduct_cells and (i, j) not in self.scored_active:
            self.scored_active.add((i, j))
            self.score -= 1
            if self.score < 0:
                self.score = 0
            self._consume_cell(i, j, total_pass)
            self._sync_live_feedback()
            return
        in_p1 = (i, j) in self.goal_cells
        in_p2 = (i, j) in self.goal2_cells
        same_color = in_p1 and in_p2   # DK03-style: both players same color

        if same_color:
            # Alternate P1→P2→P1→P2 per cell so both players score fairly.
            if (i, j) in self.p2_next_cells:
                if (i, j) not in self.scored_active2:
                    self.scored_active2.add((i, j))
                    self.score2 += 1
                    self.p2_next_cells.discard((i, j))
                    self._consume_cell(i, j, total_pass)
            else:
                if (i, j) not in self.scored_active:
                    self.scored_active.add((i, j))
                    self.score += 1
                    self.p2_next_cells.add((i, j))  # next time → P2
                    self._consume_cell(i, j, total_pass)
            self._sync_live_feedback()
            return

        # P1 goal: score + consume
        if in_p1 and (i, j) not in self.scored_active:
            self.scored_active.add((i, j))
            self.score += 1
            self._consume_cell(i, j, total_pass)
            self._sync_live_feedback()
            return
        # P2 goal: separate score + consume
        if in_p2 and (i, j) not in self.scored_active2:
            self.scored_active2.add((i, j))
            self.score2 += 1
            self._consume_cell(i, j, total_pass)
            self._sync_live_feedback()
            return
        # else: background decor — neutral, no effect.

    def _consume_cell(self, i, j, total_pass=None):
        """Remove a stepped goal tile from the group(s) whose time window is
        CURRENTLY ACTIVE, so it blanks. No artificial respawn — consumed =
        gone (matches real game). Level completes when all scoreable tiles
        cleared. Time-staggered waves (groups with later start_times) provide
        natural progression.

        Must filter by time window: the same (row,col) coordinate can be
        reused across separate groups/waves at different times, and without
        this filter, consuming one occurrence silently wipes out every
        future occurrence sharing that coordinate too, ending the level
        early (same bug found and fixed in laser/climb's consume functions)."""
        if total_pass is None:
            total_pass = self._current_level_time()
        reappear_at = None  # respawn disabled — clear progression for 1P + 2P
        if self.dict_group:
            for g in self.dict_group.values():
                sm = getattr(g, "start_member", None)
                if not sm:
                    continue
                st = getattr(g, "start_time_sec", 0)
                et = getattr(g, "end_time_sec", 0)
                if not (st <= total_pass <= et):
                    continue
                if (i, j) in sm:
                    try:
                        if isinstance(sm, set):
                            sm.discard((i, j))
                        else:
                            sm.remove((i, j))
                        if reappear_at is not None:
                            self.pending_respawn.append([g, (i, j), reappear_at])
                    except Exception:
                        pass
        # display-only hit flash (white blink) for ~0.4s
        self.flashes[(i, j)] = time.time()

    def process_respawns(self):
        """Re-add consumed 2P goal tiles after respawn_delay. Per-frame."""
        if not self.pending_respawn:
            return
        now = time.time(); still = []
        for entry in self.pending_respawn:
            g, cell, t = entry
            if now >= t:
                sm = getattr(g, "start_member", None)
                try:
                    if isinstance(sm, set): sm.add(cell)
                    elif sm is not None and cell not in sm: sm.append(cell)
                except Exception:
                    pass
            else:
                still.append(entry)
        self.pending_respawn = still

    def apply_input(self, row: int, col: int, action: str):
        """Player input from simulator: press/release a tile.
        Press scores immediately if the tile is lit (mouse clicks are
        instantaneous, so we can't wait for the next frame)."""
        if not self.running or self.current_state.get("game_over"):
            return False
        if self.led_table is None:
            return False
        # Ignore presses outside the level's active zone (e.g. 5x9).
        z = self.zone
        if z and not (z[0] <= row < z[1] and z[2] <= col < z[3]):
            return False
        with self.input_lock:
            if action == "press":
                self._sim_pressed.add((row, col))
                self.led_table.press_cell(row, col)
                self.try_score_cell(row, col)  # score on press (instant clicks)
            elif action == "release":
                self._sim_pressed.discard((row, col))
                self.led_table.release_cell(row, col)
        self._sync_live_feedback()
        return True


class GameManager:
    """Manages all running game instances"""

    def __init__(self):
        self.games: Dict[str, GameInstance] = {}
        self.lock = threading.Lock()
        self._create_lock = threading.Lock()  # serializes clear+create as one unit
        self.zombie_threads = []  # [{"game_id": ..., "detected_at": ...}] — threads that outlived their join timeout
        logger.info("GameManager initialized")

    def clear_all(self):
        """Stop and remove all existing games (kiosk = one game at a time)."""
        with self.lock:
            games = list(self.games.items())
        for gid, g in games:
            g.running = False
            t = getattr(g, "thread", None)
            if t and t.is_alive():
                t.join(timeout=3)
                if t.is_alive():
                    logger.warning(f"Game thread {gid} did not stop within 3s — "
                                   f"it may keep hitting the hardware concurrently "
                                   f"with the next game")
                    self.zombie_threads.append({"game_id": gid, "detected_at": time.time()})
        with self.lock:
            self.games.clear()
        logger.info("Cleared all existing games")

    def create_game(self, card_id: str, level: int, difficulty: str) -> str:
        """Create new game instance. Clears any prior games first (kiosk model).

        NOTE: game.running is set True HERE, synchronously, before the
        background thread even starts — not later inside _run_game() after
        the slow HW-init/import phase. That earlier version had a real race:
        if a second create_game() call (e.g. from a double-fired frontend
        mount effect) landed while the first game's thread was still mid
        setup, clear_all()'s `running = False` would get silently clobbered
        a few milliseconds later when the first thread reached its own
        `running = True` assignment — leaving an unstoppable zombie thread
        that fights the new game's thread over the same COM ports. Setting
        it here means nothing can flip it back to True after a stop signal.
        """
        with self._create_lock:
            self.clear_all()
            with self.lock:
                game_id = str(uuid.uuid4())[:8]
                game = GameInstance(game_id, card_id, level, difficulty)
                game.running = True

                # Eagerly set multiplayer from file extension BEFORE the load
                # thread starts, so _consume_cell respawns correctly even if
                # a press arrives before the shelve is fully loaded (~7s).
                _clone = str(GAMES_ROOT)
                _ledb = os.path.join(_clone, "source", "----", f"{level}.ledb")
                if os.path.exists(_ledb):
                    game.multiplayer = True
                    logger.info(f"Game created: {game_id} multiplayer=True (card={card_id}, level={level})")
                else:
                    logger.info(f"Game created: {game_id} (card={card_id}, level={level})")

                self.games[game_id] = game
                return game_id

    def get_game(self, game_id: str) -> Optional[GameInstance]:
        """Get game by ID"""
        with self.lock:
            return self.games.get(game_id)

    def get_running_game(self, game_id: str = None) -> Optional[GameInstance]:
        """Return a live game: prefer game_id, else first running non-over game."""
        with self.lock:
            games = list(self.games.items())
        if game_id:
            for gid, g in games:
                if gid == game_id and g.running and not g.current_state.get("game_over"):
                    return g
        for _gid, g in games:
            if g.running and not g.current_state.get("game_over"):
                return g
        return None

    def start_game(self, game_id: str):
        """Start game loop in background thread"""
        game = self.get_game(game_id)
        if not game:
            raise ValueError(f"Game not found: {game_id}")

        def _run_game():
            try:
                # Double-check: reinstall mocks in this thread
                if not USE_SERIAL_HD:
                    if 'serial' not in sys.modules:
                        sys.modules['serial'] = MagicMock()
                    if 'led' not in sys.modules:
                        sys.modules['led'] = MagicMock()
                    if 'led.led_control' not in sys.modules:
                        sys.modules['led.led_control'] = MagicMock()
                else:
                    _hw_init()

                logger.info(f"Starting game loop: {game_id}")

                # Import game modules (with fallback to mock loop on import error)
                Play = None
                LedTable = None
                Setting = None
                try:
                    logger.info(f"Importing game modules for {game_id}")
                    import shelve
                    import os
                    from game_play.Play import Play
                    from model.setting import Setting
                    logger.info(f"✓ Game modules imported")
                except Exception as import_err:
                    logger.warning(f"Game module import failed, using mock loop: {import_err}")
                    import traceback
                    logger.warning(f"Import traceback: {traceback.format_exc()}")
                    Play = None
                    LedTable = None
                    Setting = None
                    # If imports failed, force dict_group to None to skip to mock loop
                    dict_group = None

                # Initialize game components — always use HeadlessLedTable
                # (never the mocked gui2 LedTable — that's MagicMock, comparisons fail)
                _s = load_real_settings()
                _rows = _s.get("grid_rows", 16)
                _cols = _s.get("grid_cols", 26)
                led_table = HeadlessLedTable(wall_light_arr_len=100, led_row=_rows, led_col=_cols)
                logger.info(f"HeadlessLedTable ready: {led_table.led_row}x{led_table.led_col} (Grid square floor)")

                # Play.__init__ reads leval_span, blue_hide_max_time, corner_line_start from setting
                mock_setting = _make_play_setting(_s)

                # Create dummy callback (Play expects partial_fun_cb for UI updates)
                def dummy_callback(*args, **kwargs):
                    pass

                # game_level: numeric difficulty (1=easy, 2=normal, 3=hard), not level ID
                difficulty_map = {"easy": 1, "normal": 2, "hard": 3}
                game_level_num = difficulty_map.get(game.difficulty, 2)  # default to normal

                play = None
                try:
                    logger.debug(f"Creating Play instance for game {game_id}")
                    play = Play(led_table, mock_setting, dummy_callback, game_level=game_level_num)
                    # Mild headless sim tuning (on top of move_distance gate in Play.running).
                    difficulty_speed = {"easy": 0.25, "normal": 0.4, "hard": 0.6}
                    play.game_level_speed = difficulty_speed.get(game.difficulty, 0.4)
                    logger.info(f"Play ready: game_level={game_level_num}, "
                                f"leval_span={_s.get('leval_span')}, "
                                f"game_level_speed={play.game_level_speed}")
                except Exception as e:
                    logger.warning(f"Play creation failed, using mock loop: {e}")
                    play = None

                # ── SESSION SETUP ────────────────────────────────────────────
                # Build the level marathon sequence from the chosen start level
                # to the end of its series (A001..A025 / B01..B31 / DK01..DK10).
                game.play = play
                game.led_table = led_table          # expose for press input
                # game.running was already set True synchronously in create_game()
                # (before this thread even started) — deliberately NOT re-set here.
                # Re-setting it here caused a race: a concurrent clear_all() call's
                # `running = False` stop signal could be clobbered by this line a
                # few ms later, leaving an unstoppable zombie thread. See create_game().
                game.session_start = time.time()
                game.level_sequence = _build_level_sequence(game.level)
                logger.info(f"Session: {len(game.level_sequence)} levels from "
                            f"'{game.level}' (5-min marathon)")

                game_start_time = game.session_start  # legacy alias for mock loop

                BLACK3 = [(0, 0, 0), (0, 0, 0), (0, 0, 0)]

                def _ensure_anim(g):
                    """Pickled groups lack breath state; init it lazily so
                    group.breath() works (shimmer effect)."""
                    if not isinstance(getattr(g, "breath_color_float", None), list) \
                            or not (g.breath_color_float and isinstance(g.breath_color_float[0], (list, tuple))):
                        col = g.color if (isinstance(g.color, (list, tuple)) and g.color
                                          and isinstance(g.color[0], (list, tuple))) else BLACK3
                        g.breath_color = [list(c) for c in col]
                        g.breath_color_float = [list(c) for c in col]
                        g.breath_switch = [True, True, True]
                    if not hasattr(g, "trigger_span_tm"):
                        g.trigger_span_tm = 0

                def _setup_level(dg, go):
                    """Configure game state for a freshly-loaded level. Score,
                    score2, life, session timer all PERSIST (set elsewhere)."""
                    game.dict_group = dg
                    # Per-level board time = max group end_time.
                    try:
                        game.board_time_sec = max(
                            (getattr(g, "end_time_sec", 0) for g in dg.values()),
                            default=1e9)
                    except Exception:
                        game.board_time_sec = 1e9
                    # Play zone (guards input).
                    if go is not None:
                        try:
                            game.zone = (int(getattr(go, "zone_row_from", 0)),
                                         int(getattr(go, "zone_row_to", 16)),
                                         int(getattr(go, "zone_col_from", 0)),
                                         int(getattr(go, "zone_col_to", 26)))
                        except Exception:
                            game.zone = None
                    # Multiplayer: 2P levels have BOTH blue(P1) and orange(P2)
                    # scoreable groups. Upgrade only (never override to False).
                    _P1 = (0, 0, 254); _P2 = (254, 128, 0)
                    has_p1 = has_p2 = False
                    for g in dg.values():
                        mc = _group_main_color(g.color)
                        if mc == _P1: has_p1 = True
                        elif mc == _P2: has_p2 = True
                    if has_p1 and has_p2:
                        game.multiplayer = True
                        game._player_num = 2   # 2P: divide score by 2 players
                    # Init breath/anim state for all groups.
                    for g in dg.values():
                        try:
                            _ensure_anim(g)
                        except Exception:
                            pass

                # Per-frame callback fired by Play.update() inside Play.running().
                # By this point Play has: moved groups (deal_all_direction by
                # speed), advanced total_pass, cleared+redrawn led_table for the
                # current frame. We score presses and publish the frame.
                # Returning False makes Play.running() stop (timeout / Stop btn).
                frame_counter = {"n": 0}
                hw_draw_clock = {"t": 0.0}

                def _frame_callback(play_self, dgroup, time_pass, total_pass):
                    # total_pass is PER-LEVEL (reset each level). Session timing
                    # is wall-clock from game.session_start.
                    try:
                        session_elapsed = time.time() - game.session_start

                        # ── SESSION-END conditions (stop the whole marathon) ──
                        #   life<=0          -> result 0 (out of lives)
                        #   session timer up -> result 2 (5-min timeout)
                        if game.life <= 0:
                            time_left = game.game_time_sec - session_elapsed
                            if time_left > 10.0:
                                # Lives gone but time remains: restart same level,
                                # keep score. Session loop refills HP and replays.
                                game._restart_level = True
                                return False
                            game._session_over = True
                            game.update_state(game_over_reason="out_of_life", result=0)
                            return False
                        if (not game.running) or session_elapsed > game.game_time_sec:
                            game._session_over = True
                            game.update_state(game_over_reason="timeout", result=2)
                            return False
                        # ── LEVEL-END by TIME (advance to next level) ──
                        # board_time_sec = max group end_time. For short levels
                        # this fires; long (600s) levels advance by all-cleared.
                        if total_pass > game.board_time_sec:
                            game._level_cleared = True
                            return False

                        grid = led_table.led_table

                        # ── GRID CLASSIFICATION ──────────────────────────────
                        # Blue = scoreable (+1). Orange = P2 score (2P only).
                        # RED/DEDUCT = hazard. GREEN = safe platform (shields red).
                        goal_cells  = set()
                        goal2_cells = set()
                        red_cells   = set()
                        deduct_cells = set()
                        green_cells = set()

                        _P1_COLOR = _GRID_P1_COLOR
                        _P2_COLOR = _GRID_P2_COLOR
                        _GREEN    = (0, 254, 0)

                        # ── PRIORITY OVERLAP RESOLUTION ──────────────────────
                        # When multiple groups occupy the SAME cell, ONE wins by
                        # rank: green(3) > red/deduct(2) > blue/orange/goal(1).
                        # This gives each cell exactly ONE category + display
                        # color, so a blue tile under a moving red reads red NOW
                        # (and becomes scoreable again once red moves off it).
                        #   cell_win[(i,j)] = (rank, category, rgb)
                        cell_win = {}
                        for g in dgroup.values():
                            sm = getattr(g, "start_member", None)
                            if not sm:
                                continue
                            if getattr(g, "type", None) != Setting.FLOOR_LIGHT:
                                continue
                            if not (g.start_time_sec <= total_pass <= g.end_time_sec):
                                continue
                            mc = _group_main_color(g.color)
                            if mc == _GREEN:
                                rank, cat = 3, "green"
                            elif _rgb_is_deduct(mc):
                                rank, cat = 2, "deduct"
                            elif mc in _GRID_HAZARD_COLORS:
                                rank, cat = 2, "red"
                            elif game.multiplayer and mc == _P1_COLOR:
                                rank, cat = 1, "p1"
                            elif game.multiplayer and mc == _P2_COLOR:
                                rank, cat = 1, "p2"
                            elif (not game.multiplayer) and mc == _P1_COLOR:
                                rank, cat = 1, "goal"
                            else:
                                rank, cat = 0, "decor"
                            for cell in sm:
                                ci = round(cell[0]); cj = round(cell[1])
                                if not (0 <= ci < led_table.led_row and 0 <= cj < led_table.led_col):
                                    continue
                                prev = cell_win.get((ci, cj))
                                if prev is None or rank > prev[0]:
                                    cell_win[(ci, cj)] = (rank, cat, mc)

                        # Derive mutually-exclusive category sets from winners.
                        for (ci, cj), (rank, cat, mc) in cell_win.items():
                            if cat == "green":
                                green_cells.add((ci, cj))
                            elif cat == "deduct":
                                deduct_cells.add((ci, cj))
                            elif cat == "red":
                                red_cells.add((ci, cj))
                            elif cat == "p1" or cat == "goal":
                                goal_cells.add((ci, cj))
                            elif cat == "p2":
                                goal2_cells.add((ci, cj))

                        game.goal_cells  = goal_cells
                        game.goal2_cells = goal2_cells
                        game.red_cells   = red_cells
                        game.deduct_cells = deduct_cells

                        # ── LEVEL COMPLETION ─────────────────────────────────
                        # Count scoreable tiles remaining across ALL groups
                        # (active + future waves). When all consumed → complete.
                        # Scoreable: PLUS_ARR (1P) or blue+orange (2P). Green/red
                        # /deduct are NEVER scoreable so don't block completion.
                        _scoreable_colors = (_GRID_SCORE_COLORS_2P if game.multiplayer
                                             else _GRID_SCORE_COLORS_1P)
                        remaining_scoreable = 0
                        for g in dgroup.values():
                            if getattr(g, "type", None) != Setting.FLOOR_LIGHT:
                                continue
                            mc = _group_main_color(g.color)
                            if mc in _scoreable_colors:
                                sm = getattr(g, "start_member", None)
                                if sm:
                                    remaining_scoreable += len(sm)
                        # Grace period (>1.5s) so level has time to spawn first wave.
                        # All scoreable cleared -> LEVEL done -> ADVANCE to next
                        # level (NOT game over). Score/life persist via instance.
                        if total_pass > 1.5 and remaining_scoreable == 0:
                            logger.info(f"Level cleared (all tiles): "
                                        f"score={game.score}, score2={game.score2}, "
                                        f"life={game.life}")
                            game._level_cleared = True
                            return False

                        # AUTO-JUMP: scoreable remain but none active NOW (current
                        # wave cleared, next wave is in the future). Skip dead time
                        # by advancing total_pass to the next scoreable wave's start.
                        # Mirrors real game's running_by_blue auto-jump.
                        if total_pass > 1.5 and remaining_scoreable > 0 \
                                and not goal_cells and not goal2_cells:
                            next_start = None
                            for g in dgroup.values():
                                if getattr(g, "type", None) != Setting.FLOOR_LIGHT:
                                    continue
                                mc = _group_main_color(g.color)
                                if mc not in _scoreable_colors:
                                    continue
                                sm = getattr(g, "start_member", None)
                                if not sm:
                                    continue
                                st = g.start_time_sec
                                if st > total_pass and (next_start is None or st < next_start):
                                    next_start = st
                            if next_start is not None:
                                logger.debug(f"Auto-jump: {total_pass:.1f}s -> {next_start:.1f}s")
                                play_self.total_pass = next_start
                                game.last_life_loss_time = 0.0  # reset hazard gate

                        # DEBUG: log tile classification every 60 frames
                        if frame_counter["n"] % 60 == 0:
                            logger.debug(f"Frame {frame_counter['n']}: goal={len(goal_cells)}, "
                                         f"goal2={len(goal2_cells)}, red={len(red_cells)}, "
                                         f"deduct={len(deduct_cells)}, remaining_scoreable={remaining_scoreable}, "
                                         f"mp={game.multiplayer}")

                        # 2) SCORE pressed cells (type-aware). Drop scored marks
                        #    for goals that are no longer active so they can score
                        #    again if they reappear.
                        # Read sensors immediately before scoring (after draw).
                        if USE_SERIAL_HD and _hw_led_control is not None:
                            try:
                                with _hw_serial_lock:
                                    _hw_read_sensors(_hw_layout_type, led_table.state_table)
                            except Exception as _hw_err:
                                logger.warning(f"HW read failed: {_hw_err}")

                        with game.input_lock:
                            state = [row[:] for row in led_table.state_table]
                            if game.multiplayer:
                                game.process_respawns()
                            # Keep scored marks for ACTIVE goal/deduct cells only.
                            # Deduct cells must stay in scored_active while pressed
                            # or they fire every single frame (life drain per frame).
                            active_consumables = goal_cells | goal2_cells | deduct_cells
                            game.scored_active &= active_consumables
                            game.scored_active2 &= goal2_cells
                            for i in range(led_table.led_row):
                                for j in range(led_table.led_col):
                                    pressed = state[i][j] or (i, j) in game._sim_pressed
                                    if pressed:
                                        game.try_score_cell(i, j)

                        game._sync_live_feedback()

                        # 2) Build display buffer from the PRIORITY winner map so
                        #    overlapping cells render the WINNING color (green >
                        #    red/deduct > blue/orange), matching interaction.
                        # Single RGB per cell (16×26 square grid).
                        cols = led_table.led_col
                        rows = led_table.led_row
                        import math as _math
                        pulse = 0.60 + 0.40 * (0.5 + 0.5 * _math.sin(total_pass * _math.pi * 2))
                        led_display = [[0, 0, 0] for _ in range(rows * cols)]
                        for (ci, cj), (rank, cat, mc) in cell_win.items():
                            idx = ci * cols + cj
                            if cat in ("goal", "p1", "p2"):
                                # scoreable tiles shimmer
                                led_display[idx] = [int(ch * pulse) for ch in mc]
                            else:
                                led_display[idx] = [int(mc[0]), int(mc[1]), int(mc[2])]

                        # 2b) FLASH: stepped tiles blink white ~0.4s then vanish.
                        now = time.time()
                        for cell, t0 in list(game.flashes.items()):
                            el = now - t0
                            if el > 0.4:
                                game.flashes.pop(cell, None)
                                continue
                            fi, fj = cell
                            on = int(el / 0.1) % 2 == 0
                            led_display[fi * cols + fj] = [255, 255, 255] if on else [0, 0, 0]

                        # Hardware LED: draw after building display buffer (valid RGB).
                        if USE_SERIAL_HD and _hw_led_control is not None:
                            try:
                                now = time.time()
                                with _hw_serial_lock:
                                    if now - hw_draw_clock["t"] >= _HW_DRAW_INTERVAL:
                                        hw_draw_clock["t"] = now
                                        _ld2 = [
                                            [led_display[r * cols + c] for c in range(cols)]
                                            for r in range(rows)
                                        ]
                                        _hw_draw_floor(_hw_layout_type, _ld2)
                                        game._hw_draw_count = getattr(game, "_hw_draw_count", 0) + 1
                            except Exception as _hw_err:
                                logger.warning(f"HW draw failed: {_hw_err}")

                        game._frame_count = frame_counter["n"]
                        game._last_frame_at = time.time()

                        game.update_state(
                            score=game.score,
                            score2=game.score2,
                            multiplayer=game.multiplayer,
                            time_elapsed=session_elapsed,                       # SESSION elapsed
                            time_left=max(0, game.game_time_sec - session_elapsed),  # SESSION countdown
                            life=game.life,
                            display_lives=math.ceil(game.life * 5 / game.max_life) if game.max_life else 0,
                            display_max=5,
                            game_over=False,
                            led_display=led_display,
                            grid_rows=led_table.led_row,
                            grid_cols=led_table.led_col,
                            pressed_tiles=game._get_pressed_tiles(),
                            current_level=game.current_level_id,
                            levels_cleared=game.levels_cleared,
                        )

                        frame_counter["n"] += 1
                        if frame_counter["n"] % 120 == 0:
                            logger.debug(f"Game {game_id}: score={game.score}, "
                                         f"t={total_pass:.1f}s")
                        # Pace ~120fps cap; non-blocking serial reads keep input responsive.
                        time.sleep(0.008)
                        return True
                    except Exception as cb_err:
                        logger.error(f"Frame callback error {game_id}: {cb_err}")
                        return False

                # ── SESSION LOOP ─────────────────────────────────────────────
                # Marathon through level_sequence. Score + lives + 5-min timer
                # persist across levels. Each level runs via Play.running() until
                # the callback returns False (level cleared -> advance, or session
                # over -> stop). End on life<=0, timer<=0, or sequence exhausted.
                if play is None or not game.level_sequence:
                    logger.warning(f"No Play object or empty level sequence; "
                                   f"session cannot run: {game_id}")
                    game.update_state(game_over=True, game_over_reason="no_levels",
                                      time_left=0)
                    game.running = False
                    return

                play.callback = _frame_callback
                for lvl_path in game.level_sequence:
                    if game._session_over or not game.running:
                        break
                    session_elapsed = time.time() - game.session_start
                    if session_elapsed > game.game_time_sec:
                        game._session_over = True
                        break

                    lvl_id = os.path.basename(lvl_path).rsplit(".", 1)[0]
                    dg, go = _load_level_file(lvl_path)
                    if not dg:
                        logger.warning(f"Skipping unloadable level: {lvl_id}")
                        continue

                    # ── RESTART LOOP: replay this level whenever lives hit 0 with
                    #    >10s left (score persists, HP refills). Exits on level
                    #    clear, session timeout, or true game-over (life=0, <10s).
                    while True:
                        # Reload fresh every attempt (including the first) — dg's
                        # groups are mutated in-place as tiles are scored/consumed,
                        # so reusing the same dg across a restart would replay with
                        # already-scored tiles missing instead of a clean board.
                        dg, go = _load_level_file(lvl_path)
                        if not dg:
                            logger.warning(f"Level {lvl_id} failed to reload; aborting level")
                            break
                        game.current_level_id = lvl_id
                        game.reset_for_level()      # clear board state (keep score/life)
                        _setup_level(dg, go)        # dict_group, board_time, zone, mp, anim
                        session_elapsed = time.time() - game.session_start
                        logger.info(f"▶ Level {lvl_id}: groups={len(dg)}, "
                                    f"mp={game.multiplayer}, board_time={game.board_time_sec}s, "
                                    f"score={game.score}, life={game.life}, "
                                    f"t_left={game.game_time_sec - session_elapsed:.0f}s")

                        # Run this level. Blocks until callback returns False.
                        play.running_state = True
                        play.total_pass = 0
                        try:
                            play.running(dg)
                        except Exception as run_err:
                            import traceback
                            logger.warning(f"Level {lvl_id} run error: {run_err}\n"
                                           f"{traceback.format_exc()}")
                            game._session_over = True
                            break

                        if game._session_over:
                            break

                        if game._restart_level:
                            # life=0 with time remaining — refill HP, replay level
                            game.life = game.max_life
                            game.last_life_loss_time = 0.0
                            logger.info(f"↻ Life restart: level={lvl_id}, score={game.score}")
                            continue

                        if game._level_cleared:
                            game.levels_cleared += 1
                            logger.info(f"✓ Level {lvl_id} cleared "
                                        f"(total cleared={game.levels_cleared})")
                        break

                    if game._session_over:
                        break

                # Session finished (timer/lives/sequence end).
                game._session_over = True
                final_reason = game.get_state().get("game_over_reason") or "session_end"
                final_result = game.get_state().get("result")
                if final_result is None:
                    final_result = 1  # cleared the whole series within time
                final_score = game.compute_final_score(game.score)
                final_score2 = game.compute_final_score(game.score2)
                logger.info(f"Session over: reason={final_reason}, "
                            f"raw_score={game.score} -> final={final_score}, "
                            f"raw_score2={game.score2} -> final2={final_score2}, "
                            f"levels_cleared={game.levels_cleared}")
                game.update_state(game_over=True, time_left=0,
                                  game_over_reason=final_reason, result=final_result,
                                  levels_cleared=game.levels_cleared,
                                  final_score=final_score, final_score2=final_score2)
                game.running = False

            except Exception as e:
                import traceback
                logger.error(f"Game error {game_id}: {e}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                game.running = False
                game.update_state(
                    game_over=True,
                    game_over_reason=str(e)
                )

        game.thread = threading.Thread(target=_run_game, daemon=True)
        game.thread.start()

    def stop_game(self, game_id: str) -> dict:
        """Stop game and return final state"""
        game = self.get_game(game_id)
        if not game:
            return {"success": False, "error": f"Game not found: {game_id}"}

        game.running = False
        if game.thread:
            game.thread.join(timeout=5)

        final_state = game.get_state()

        with self.lock:
            del self.games[game_id]

        logger.info(f"Game stopped: {game_id}")
        return {"success": True, "state": final_state}

    def cleanup_expired(self):
        """Remove expired games"""
        with self.lock:
            expired = [gid for gid, game in self.games.items() if game.is_expired()]
            for gid in expired:
                del self.games[gid]
                logger.warning(f"Game expired and removed: {gid}")

    def get_stats(self) -> dict:
        """Get manager statistics"""
        with self.lock:
            return {
                "active_games": len(self.games),
                "max_games": MAX_CONCURRENT_GAMES,
                "timeout_seconds": GAME_TIMEOUT_SECONDS
            }


# Global instance
_manager = None

def get_manager() -> GameManager:
    """Get GameManager singleton"""
    global _manager
    if _manager is None:
        _manager = GameManager()
    return _manager
