# API Reference — LED Grid (Floor Is Lava)

Lightweight reference for every FastAPI endpoint in `api/main.py`. Not a
full OpenAPI spec — just enough to understand what this backend exposes at
a glance. Field names below are read directly from `api/main.py` and
`api/models.py`.

---

## Game lifecycle

### `POST /login`
Look up a player by RFID card ID.
- **Body:** `{ card_id: str }`
- **Response:** `{ success: bool, player?: { custom_id, name, phone, time_left (sec), card_id }, error?: str }`

### `POST /start-game`
Create and start a new game instance (kiosk model — `create_game()` calls
`clear_all()` first, so starting a new game always kills any prior game on
this machine).
- **Body:** `{ card_id: str, level: int|str, difficulty: "easy"|"normal"|"hard" }` (numeric level 17-26, or named e.g. `DK01` for a `----`-tier 2P level)
- **Response:** `{ success: bool, game_id?: str, ws_url?: str, error?: str }`

### `WS /game/{game_id}`
Real-time game state stream (~60fps, `asyncio.sleep(0.016)`). Server →
client: `{ type: "game_state", data: <full state dict> }`. Client → server
input channel exists but is currently a stub (`# TODO: Feed input to
Play.py`) — actual input goes through `POST /game-input`, not this socket.
Sends one final `{ ..., game_over: true }` frame when `game.running` goes
false, then closes.

### `GET /result/{game_id}`
Get final score/leaderboard after a game ends (works even after the game
was cleaned up — falls back to an empty state dict).
- **Response:** `{ success, score, player_name, time_used, difficulty, leaderboard: [{rank, name, score, timestamp}], error? }`

### `POST /logout`
End a session: calls `game_manager.stop_game()` (which now also blanks the
physical floor — see `HARDWARE_VALIDATION.md`) and records the score to the
DB.
- **Body:** `{ card_id: str, game_id: str }`
- **Response:** `{ success: bool, error?: str }`

### `POST /game-input`
Player input from the simulator (press/release a floor tile).
- **Body:** `{ row: int, col: int, type: "press"|"release" = "press", game_id?: str }` — applies to the named game, or the first active/running game if `game_id` omitted.
- **Response:** `{ success: bool, score: int, life: int }`

### `POST /save-score`
Persist a finished game to the leaderboard/scores table.
- **Body key fields:** `card_id, card_id2, multiplayer, level (starting), end_level, score (P1 raw), score2 (P2 raw), final_score (P1 normalized), final_score2 (P2 normalized), life, lives_start, result, time_used, levels_cleared, difficulty, started_at`
- **Response:** `{ success: bool, error?: str }`

### `GET /active-game`
Resume support: returns the currently-running (non-game-over) game, if
any, so the frontend can restore the simulator after a page reload instead
of restarting login.
- **Response:** `{ success: true, game_id, card_id, level, difficulty, state }` or `{ success: false }`

### `GET /game-state/{game_id}`
State of one specific game (simulator polls its own game).
- **Response:** `{ success: bool, game_id, state }` or `{ success: false, error }`

### `GET /game-state`
State of the first active game (fallback / legacy single-game poll).
- **Response:** `{ success, game_id, state }` or `{ success: false, error: "No active games" }`

### `GET /levels`
List available Floor Is Lava levels, grouped by tier.
- **Response:** `{ success, levels: [{id, name, path, category, multiplayer, file_type}], categories: {easy: [...], medium: [...], hard: [...], "2player": [...]}, count }`
  - `easy` = `source/-/*.led` (10 levels, 1P) · `medium` = `source/--/*.led` (15 levels, 1P) · `hard` = `source/---/*.led` (14 levels, 1P) · `2player` = `source/----/*.ledb` (13 levels, real 2P)

### `GET /leaderboard/{level}?limit=10`
Top scores for one level.
- **Response:** `{ success: true, level: str, entries: [...] }` (entries per `db.get_leaderboard`)

---

## RFID / settings

### `GET /game-settings`
Load grid/timing/scoring settings from the `led_parameter` shelve (via
`load_real_settings()`).
- **Response:** `{ success, game, wall_layout, grid_dims: {rows, cols}, game_time_sec, life_value, leval_span, blue_hide_max_time, life_value_count_time, scode_divide_person, scode_divide_time }`

### `POST /settings`
Runtime overrides **pushed from the central RFID server** (default
difficulty, session length). Written to `games/setting/runtime_overrides.json`;
does not touch the original read-only shelve config.
- **Body:** `{ default_difficulty?: str, session_minutes?: int }`
- **Response:** `{ success: true, overrides: {...} }`

### `GET /settings`
Read back the current runtime overrides (empty `{}` if none set yet).

---

## Scores / diagnostics

### `GET /scores?since=<ISO timestamp>`
Scores recorded after `since` (default `2000-01-01T00:00:00`) — used by the
RFID server's cross-game leaderboard poller.
- **Response:** `{ success: bool, game: str, scores: [...] }` or `{ success: false, error }`

### `GET /health`
Basic liveness + game-manager stats.
- **Response:** `{ status: "ok", game: str, stats: {...} }`

### `GET /hw-debug`
Live hardware-loop diagnostics for onsite testing: whether `USE_SERIAL_HD`
is on, each active game's `running`/`level`/`score`/`frame_count`/
`hw_draw_count`/`lit_pixels`/pressed tiles, and any zombie threads that
failed to join during `clear_all()` (non-empty = a stale thread may still
be hitting the hardware concurrently with the current game).
- **Response:** `{ use_serial_hd: bool, active_games: int, games: [...], zombie_threads: [...] }`

---

## Notes

- All endpoints live in `api/main.py`; request/response Pydantic models are
  in `api/models.py` (note: several endpoints — `/game-input`, `/save-score`,
  `/settings`, `/hw-debug` — take/return raw `dict`, not typed models;
  `LoginRequest`/`StartGameRequest`/`LogoutRequest`/`GameResult` etc. cover
  the rest).
- CORS is wide open (`allow_origins=["*"]`) — fine for LAN kiosk use, not
  for public internet exposure.
- `POST /start-game` → `game_manager.create_game()` → `clear_all()` first:
  starting a new game always kills any prior game on this machine
  (single-game-at-a-time kiosk model).
- The blank-on-stop hardware fix (physical floor blanks on session end /
  `stop_game()` / `clear_all()`) lives in `api/game_manager.py`, not in
  `main.py` — see `HARDWARE_VALIDATION.md` for the validation checklist.
