"""Live hardware test — run while stepping on tiles during an active game.

Usage (with game running on Level 007):
  python scripts/hw_live_test.py

Shows pressed tiles from /hw-debug every 200ms.
"""
import json
import time
import urllib.request

API = "http://localhost:8003"


def poll():
    with urllib.request.urlopen(f"{API}/hw-debug", timeout=3) as r:
        return json.loads(r.read())


def main():
    print("=== HW Live Test (Ctrl+C to stop) ===")
    print("Start a game first, then step on tiles.\n")
    last_pressed = frozenset()
    while True:
        try:
            d = poll()
        except Exception as e:
            print(f"API error: {e}")
            time.sleep(1)
            continue
        if d["active_games"] == 0:
            print("No active game — start one at http://localhost:5176")
            time.sleep(1)
            continue
        if d["active_games"] > 1:
            print(f"WARNING: {d['active_games']} games running (should be 1)!")
        g = d["games"][0]
        pressed = frozenset((p["row"], p["col"]) for p in g["pressed"])
        new = pressed - last_pressed
        gone = last_pressed - pressed
        for r, c in sorted(new):
            print(f"  PRESS  row={r} col={c}")
        for r, c in sorted(gone):
            print(f"  RELEASE row={r} col={c}")
        last_pressed = pressed
        print(
            f"\r game={g['game_id']} score={g['score']} "
            f"frames={g['frame_count']} pressed={g['pressed_count']}   ",
            end="",
            flush=True,
        )
        time.sleep(0.2)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDone.")
