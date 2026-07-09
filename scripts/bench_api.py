"""Benchmark API poll + game-input latency (simulator path)."""
import statistics
import time
import urllib.request
import json

API = "http://localhost:8003"


def get(path):
    t0 = time.perf_counter()
    with urllib.request.urlopen(f"{API}{path}", timeout=5) as r:
        r.read()
    return (time.perf_counter() - t0) * 1000


def post_input(row, col, game_id=None):
    body = {"row": row, "col": col, "type": "press"}
    if game_id:
        body["game_id"] = game_id
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{API}/game-input",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=5) as r:
        r.read()
    return (time.perf_counter() - t0) * 1000


def main():
    samples = []
    for _ in range(50):
        samples.append(get("/active-game"))
        time.sleep(0.008)
    print("=== TEST C: API poll latency (/active-game) ===")
    print(f"  n=50, sleep=8ms between requests")
    print(f"  min={min(samples):.1f}ms  p50={statistics.median(samples):.1f}ms  "
          f"p95={sorted(samples)[int(len(samples)*0.95)]:.1f}ms  max={max(samples):.1f}ms")

    # start game if none active
    with urllib.request.urlopen(f"{API}/active-game", timeout=5) as r:
        active = json.loads(r.read())
    if not active.get("success"):
        body = json.dumps({"card_id": "bench", "level": "007", "difficulty": "normal"}).encode()
        req = urllib.request.Request(
            f"{API}/start-game",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            started = json.loads(r.read())
        game_id = started.get("game_id")
        print(f"  Started bench game: {game_id}")
    else:
        game_id = active["game_id"]
        print(f"  Using active game: {game_id}")

    time.sleep(0.5)
    inp = []
    for i in range(30):
        inp.append(post_input(5 + (i % 3), 10 + (i % 5), game_id))
        time.sleep(0.05)
    print("=== TEST C: game-input latency ===")
    print(f"  n=30")
    print(f"  min={min(inp):.1f}ms  p50={statistics.median(inp):.1f}ms  "
          f"p95={sorted(inp)[int(len(inp)*0.95)]:.1f}ms  max={max(inp):.1f}ms")


if __name__ == "__main__":
    main()
