"""A/B: measure /active-game and /game-input latency while Level 007 runs."""
import json
import statistics
import sys
import time
import urllib.error
import urllib.request

API = "http://localhost:8003"
LABEL = sys.argv[1] if len(sys.argv) > 1 else "unknown"


def req(method, path, body=None, timeout=10):
    t0 = time.perf_counter()
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(
        f"{API}{path}",
        data=data,
        headers={"Content-Type": "application/json"} if data else {},
        method=method,
    )
    with urllib.request.urlopen(r, timeout=timeout) as resp:
        resp.read()
    return (time.perf_counter() - t0) * 1000


def wait_api(retries=30):
    for _ in range(retries):
        try:
            req("GET", "/active-game", timeout=2)
            return True
        except Exception:
            time.sleep(0.5)
    return False


def main():
    if not wait_api():
        print(f"ERROR [{LABEL}]: API not up")
        return

    # ensure level 007 game running
    try:
        active = json.loads(
            urllib.request.urlopen(f"{API}/active-game", timeout=5).read()
        )
    except Exception as e:
        print(f"ERROR [{LABEL}]: {e}")
        return

    if not active.get("success"):
        body = {"card_id": f"bench-{LABEL}", "level": "007", "difficulty": "normal"}
        req("POST", "/start-game", body)
        time.sleep(1.5)

    polls = [req("GET", "/active-game") for _ in range(30)]
    time.sleep(0.3)
    inputs = [
        req("POST", "/game-input", {"row": 8, "col": 12, "type": "press"})
        for _ in range(20)
    ]

    print(f"=== TEST C/D [{LABEL}] Level 007 active ===")
    print(
        f"  /active-game (n=30): min={min(polls):.0f} p50={statistics.median(polls):.0f} "
        f"p95={sorted(polls)[int(len(polls)*0.95)]:.0f} max={max(polls):.0f} ms"
    )
    print(
        f"  /game-input  (n=20): min={min(inputs):.0f} p50={statistics.median(inputs):.0f} "
        f"p95={sorted(inputs)[int(len(inputs)*0.95)]:.0f} max={max(inputs):.0f} ms"
    )


if __name__ == "__main__":
    main()
