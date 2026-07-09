"""Benchmark floor serial read/draw times (no game server)."""
import os
import sys
import time
import shelve

GAMES = os.path.join(os.path.dirname(__file__), "..", "games")
sys.path.insert(0, GAMES)

from led import led_control  # noqa: E402


def bench(label: str, n: int = 20):
    db = shelve.open(os.path.join(GAMES, "setting", "led_parameter"), "r")
    com = db["list_com_info"]
    lt = int(db["led_layout_type"])
    rows = int(float(db["value_high"]))
    cols = int(float(db["value_width"]))
    db.close()

    led_control.init_layout(lt, rows, cols, [])
    led_control.init_com(com)
    led_control.com_is_block = False
    for e in led_control.list_com:
        try:
            e[0].main_engine.timeout = 0.02
            e[0].main_engine.write_timeout = 0.1
        except Exception:
            pass

    green = [[0, 254, 0] for _ in range(cols) for _ in range(rows)]
    green = [green[i * cols : (i + 1) * cols] for i in range(rows)]
    black = [[0, 0, 0] for _ in range(cols) for _ in range(rows)]
    black = [black[i * cols : (i + 1) * cols] for i in range(rows)]
    state = [[False] * cols for _ in range(rows)]

    led_control.draw_screen_by_com(lt, green)

    t0 = time.perf_counter()
    for _ in range(n):
        led_control.draw_screen_by_com(lt, green)
    draw_ms = (time.perf_counter() - t0) / n * 1000

    t0 = time.perf_counter()
    for _ in range(n):
        led_control.update_screen_state_by_com(lt, state, state)
    read_ms = (time.perf_counter() - t0) / n * 1000

    t0 = time.perf_counter()
    for _ in range(n):
        led_control.update_screen_state_by_com(lt, state, state)
        led_control.draw_screen_by_com(lt, green)
    both_ms = (time.perf_counter() - t0) / n * 1000

    led_control.draw_screen_by_com(lt, black)
    print(f"=== {label} ===")
    print(f"  Grid: {rows}x{cols}, ports: {len(led_control.list_com)}")
    print(f"  Avg DRAW only: {draw_ms:.1f} ms")
    print(f"  Avg READ only: {read_ms:.1f} ms")
    print(f"  Avg READ+DRAW: {both_ms:.1f} ms")
    print(f"  Max FPS if serial-bound (read+draw): {1000 / both_ms:.1f}")
    return draw_ms, read_ms, both_ms


if __name__ == "__main__":
    bench("TEST A: Serial I/O")
