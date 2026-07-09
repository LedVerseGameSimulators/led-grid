# LED Hex Headless Game Stack — Deployment & API Reference

> **Outdated paths below** — this doc references `kavida_claude` and old clone paths.  
> **Use instead:** [`CLIMB_DEVELOPMENT_PLAYBOOK.md`](./CLIMB_DEVELOPMENT_PLAYBOOK.md) (Climb) or [`../led-hexagon/docs/LED_HEX_DEVELOPMENT_PLAYBOOK.md`](../led-hexagon/docs/LED_HEX_DEVELOPMENT_PLAYBOOK.md) (Hex) for current ports and `./scripts/start-dev.sh`.

## Quick Start

Start all three services in separate terminals in this order:

```bash
# Terminal 1 — API (FastAPI)
cd /Users/apple/Desktop/kavida_claude && python -m api.main

# Terminal 2 — WS Bridge
cd /Users/apple/Desktop/kavida_claude && python ws_bridge.py

# Terminal 3 — React Frontend
cd /Users/apple/Desktop/kavida_claude/frontend && npm run dev
```

Then open [http://localhost:5173](http://localhost:5173) in a browser.

**Prerequisites:** Python 3.11, Node 18+, all dependencies installed. No `.env` file needed — paths are hardcoded for local dev.

---

## Services

### 1. API (FastAPI, Python)

| Property | Value |
|----------|-------|
| Location | `/Users/apple/Desktop/kavida_claude/` |
| Start command | `cd /Users/apple/Desktop/kavida_claude && python -m api.main` |
| Port | `8000` |
| Base URL | `http://localhost:8000` |
| Depends on | `/Users/apple/parallel-work/ledhexagon_clone/` (game logic + `.led` files) |

The API is the central service. It manages game sessions, loads `.led`/`.ledb` level files, runs game logic, persists scores to SQLite, and serves state to the WS Bridge and frontend.

---

### 2. WS Bridge

| Property | Value |
|----------|-------|
| Location | `/Users/apple/Desktop/kavida_claude/ws_bridge.py` |
| Start command | `python ws_bridge.py` |
| Port | `8765` |

The WS Bridge acts as a relay layer between the API and the simulator canvas:

- Polls `GET /game-state/{game_id}` from the API at regular intervals
- Broadcasts LED frame data (416 cells × 3 rings × RGB) to the simulator over WebSocket
- Forwards button press/release events from the simulator canvas to `POST /game-input`

---

### 3. React Frontend

| Property | Value |
|----------|-------|
| Location | `/Users/apple/Desktop/kavida_claude/frontend/` |
| Start command | `cd frontend && npm run dev` |
| Port | `5173` |
| URL | `http://localhost:5173` |

**Screen flow:**

```
Select Game
    → Game Settings (players / category / level / difficulty)
    → Login (1P or 2P card IDs)
    → Countdown (3 → 2 → 1)
    → Simulator (live score / life / time, LED canvas)
    → Result (leaderboard)
```

---

## API Reference

Base URL: `http://localhost:8000`

---

### GET `/levels`

Returns all available levels.

**Response:** Array of level objects.

```json
[
  {
    "id": "extra_17",
    "name": "Level 17",
    "category": "extra",
    "multiplayer": false,
    "file_type": "led"
  }
]
```

**Categories:** `extra` | `basic` | `advanced` | `pro`  
**Total levels:** 67

---

### POST `/start-game`

Starts a new game session.

**Request body:**
```json
{
  "card_id": "ABC123",
  "level": "extra_17",
  "difficulty": "normal"
}
```

**Response:**
```json
{
  "game_id": "uuid-...",
  "ws_url": "ws://localhost:8765"
}
```

---

### POST `/game-input`

Sends a button press or release event to the running game.

**Request body:**
```json
{
  "game_id": "uuid-...",
  "row": 3,
  "col": 7,
  "type": "press"
}
```

`type` is `"press"` or `"release"`.

**Response:**
```json
{
  "success": true,
  "score": 420
}
```

---

### GET `/game-state/{game_id}`

Returns the full current state of a game session. Polled by the WS Bridge.

**Path parameter:** `game_id`

**Response:**
```json
{
  "score": 420,
  "score2": 0,
  "life": 3,
  "max_life": 5,
  "time_left": 47.2,
  "multiplayer": false,
  "led_display": [[[r, g, b], ...], ...],
  "game_over": false,
  "result": null
}
```

`led_display` is a 416-element array. Each element contains 3 rings, each ring is an `[R, G, B]` tuple (0–255).

`result` is `null` during play, then `"win"` | `"lose"` | `"timeout"` when the game ends.

---

### GET `/active-game`

Returns the currently running game session, if any. Used by the frontend to resume state after a page reload.

**Response:** Same shape as `/game-state/{game_id}`, or `null` if no active game.

---

### POST `/save-score`

Persists a completed game's score to the database.

**Request body:**
```json
{
  "card_id": "ABC123",
  "level": "extra_17",
  "score": 1850,
  "score2": 0,
  "life": 2,
  "lives_start": 5,
  "result": "win",
  "time_used": 52.8
}
```

---

### GET `/leaderboard/{level}`

Returns the top scores for a level.

**Path parameter:** `level` (e.g. `extra_17`)  
**Query parameter:** `limit` (default `10`)

**Response:** Array of score records sorted by score descending.

---

### POST `/logout`

Ends a session and cleans up the active game for the given card.

**Request body:**
```json
{
  "card_id": "ABC123",
  "game_id": "uuid-..."
}
```

---

## File Paths

### Level Files

| Category | Players | Path | File type | Notes |
|----------|---------|------|-----------|-------|
| Extra | 1P | `/Users/apple/parallel-work/ledhexagon_clone/Extra/*.led` | `.led` | Levels 17–26 |
| Advanced | 1P | `/Users/apple/parallel-work/ledhexagon_clone/source/--/*.led` | `.led` | YC series |
| Pro | 1P | `/Users/apple/parallel-work/ledhexagon_clone/source/-/*.led` | `.led` | Levels 00–16 |
| Multiplayer | 2P | `/Users/apple/parallel-work/ledhexagon_clone/source/---/*.ledb` | `.ledb` | DK/YCDK series |

### Game Logic

```
/Users/apple/parallel-work/ledhexagon_clone/
```

The API imports game logic directly from this directory. It must exist and be intact for the API to start.

---

## Database

**File:** `/Users/apple/parallel-work/ledhexagon_clone/setting/ledplaydb.sqlite`

**Table:** `hex_scores`

| Column | Type | Description |
|--------|------|-------------|
| `card_id` | TEXT | Player card identifier |
| `level` | TEXT | Level ID |
| `score` | INTEGER | Player 1 score |
| `score2` | INTEGER | Player 2 score (0 for 1P games) |
| `life` | INTEGER | Lives remaining at end |
| `lives_start` | INTEGER | Lives at game start |
| `result` | TEXT | `win` / `lose` / `timeout` |
| `time_used` | REAL | Seconds elapsed |
| `ts` | TEXT / DATETIME | Timestamp of the record |

The database file is read/written by the API. No migrations needed — the table is created automatically if it does not exist.
