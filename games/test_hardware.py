"""
Grid hardware diagnostic.
Run from led-grid/games/: python test_hardware.py

Sends all-green to the floor for 3s, then reads sensors for 5s.
Expected: 16x26 floor lights up green; stepping on a tile prints a PRESS line.
"""
import sys
import os
import time
import shelve

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from led import led_control

SHELVE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'setting', 'led_parameter')
DEFAULT_ROWS, DEFAULT_COLS = 16, 26


def main():
    print("=== Grid Hardware Test ===")
    print(f"Reading shelve: {SHELVE}")
    db = shelve.open(SHELVE, flag='r')
    list_com_info = db.get('list_com_info', [])
    layout_type   = int(db.get('led_layout_type', 0))
    no_use        = db.get('floor_layout_coors_no_use', [])
    rows          = int(float(db.get('value_high', DEFAULT_ROWS)))
    cols          = int(float(db.get('value_width', DEFAULT_COLS)))
    db.close()
    print(f"  COM ports : {list_com_info}")
    print(f"  Grid      : {rows}x{cols}  layout={layout_type}")

    led_control.init_layout(layout_type, rows, cols, no_use)
    errors = led_control.init_com(list_com_info)
    if errors:
        print(f"  WARNING: failed to open port(s): {errors}")
    else:
        print("  All COM ports opened OK")

    green = [0, 254, 0]
    led_2d = [[green[:] for _ in range(cols)] for _ in range(rows)]
    print("Sending green pattern for 3s — check floor lights up...")
    t0 = time.time()
    while time.time() - t0 < 3:
        led_control.draw_screen_by_com(layout_type, led_2d)
        time.sleep(0.05)

    state_table = [[False] * cols for _ in range(rows)]
    print("Reading sensors for 5s — step on tiles to test...")
    t0 = time.time()
    pressed = set()
    while time.time() - t0 < 5:
        led_control.update_screen_state_by_com(layout_type, state_table, state_table)
        for r in range(rows):
            for c in range(cols):
                if state_table[r][c] and (r, c) not in pressed:
                    pressed.add((r, c))
                    print(f"  PRESS detected: row={r} col={c}")
        time.sleep(0.01)

    print(f"\nResult: {len(pressed)} unique tile(s) pressed: {sorted(pressed)}")

    black = [0, 0, 0]
    black_2d = [[black[:] for _ in range(cols)] for _ in range(rows)]
    led_control.draw_screen_by_com(layout_type, black_2d)
    print("Floor cleared. Done.")


if __name__ == '__main__':
    main()
