"""Measure how fast game state (led_display) updates during active play."""
import hashlib
import json
import statistics
import time
import urllib.request

API = "http://localhost:8003"


def get_active():
    with urllib.request.urlopen(f"{API}/active-game", timeout=5) as r:
        return json.loads(r.read())


def start_game():
    body = json.dumps({"card_id": "bench", "level": "007", "difficulty": "normal"}).encode()
    req = urllib.request.Request(
        f"{API}/start-game",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())


def main():
    active = get_active()
    if not active.get("success"):
        start_game()
        time.sleep(1)
        active = get_active()
    if not active.get("success"):
        print("ERROR: no active game")
        return

    game_id = active["game_id"]
    print(f"=== TEST D: State update rate (game {game_id}, level 007) ===")

    intervals = []
    last_hash = None
    last_t = None
    changes = 0
    polls = 0
    t_end = time.perf_counter() + 5.0

    while time.perf_counter() < t_end:
        polls += 1
        now = time.perf_counter()
        data = get_active()
        st = data.get("state", {})
        led = st.get("led_display", [])
        h = hashlib.md5(json.dumps(led).encode()).hexdigest()
        if last_hash is not None and h != last_hash:
            changes += 1
            if last_t is not None:
                intervals.append((now - last_t) * 1000)
            last_t = now
        last_hash = h
        time.sleep(0.005)

    if intervals:
        print(f"  Polls in 5s: {polls}")
        print(f"  led_display changes: {changes} ({changes/5:.1f}/s)")
        print(f"  Interval between changes (ms): min={min(intervals):.1f} "
              f"p50={statistics.median(intervals):.1f} "
              f"p95={sorted(intervals)[int(len(intervals)*0.95)]:.1f} "
              f"max={max(intervals):.1f}")
    else:
        print("  No led_display changes detected in 5s")


if __name__ == "__main__":
    main()
