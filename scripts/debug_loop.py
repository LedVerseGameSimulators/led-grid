"""Live debug loop — polls API every 500ms during active game.

Usage: python scripts/debug_loop.py
"""
import json
import time
import urllib.request

API = "http://localhost:8003"


def get(path):
    with urllib.request.urlopen(f"{API}{path}", timeout=3) as r:
        return json.loads(r.read())


def post_input(game_id, row, col, typ):
    body = json.dumps({"row": row, "col": col, "type": typ, "game_id": game_id}).encode()
    req = urllib.request.Request(
        f"{API}/game-input", data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=3) as r:
        return json.loads(r.read())


def main():
    print("=== Debug Loop (Ctrl+C to stop) ===\n")
    last_fc = last_draw = -1
    last_t = None
    while True:
        try:
            d = get("/hw-debug")
        except Exception as e:
            print(f"API error: {e}")
            time.sleep(1)
            continue
        zombies = d.get("zombie_threads", [])
        if zombies:
            print(f"\n!!! ZOMBIE THREAD DETECTED: {zombies} — a stale game thread "
                  f"outlived its stop signal and may be hitting the hardware "
                  f"concurrently with the current game !!!")
        if d["active_games"] == 0:
            print("Waiting for game... start Level 007 at http://localhost:5176")
            time.sleep(1)
            continue
        if d["active_games"] > 1:
            print(f"\n!!! {d['active_games']} ACTIVE GAMES AT ONCE — this should "
                  f"never happen (kiosk = one game at a time) !!!")
        g = d["games"][0]
        gid = g["game_id"]
        fc = g["frame_count"]
        dc = g.get("hw_draw_count", 0)
        now_t = time.time()
        dt = (now_t - last_t) if last_t is not None else 0.0
        fps = ((fc - last_fc) / dt) if (last_fc >= 0 and dt > 0) else 0.0
        dps = ((dc - last_draw) / dt) if (last_draw >= 0 and dt > 0) else 0.0
        last_fc, last_draw = fc, dc
        last_t = now_t
        line = (
            f"game={gid} L={g['level']} score={g['score']} "
            f"frames={fc} (~{fps:.1f}/s) hw_draws={dc} (~{dps:.1f}/s) "
            f"lit={g.get('lit_pixels', '?')} pressed={g['pressed_count']}"
        )
        print(f"\r{line}   ", end="", flush=True)
        if g["pressed"]:
            print()
            for p in g["pressed"][:5]:
                src = p.get("src", "?")
                print(f"  PRESS row={p['row']} col={p['col']} ({src})")
        time.sleep(0.5)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDone.")
