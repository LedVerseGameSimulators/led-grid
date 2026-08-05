# Onsite takeaway merge — led-grid — 2026-08-03

**Branch:** `merge/onsite-takeaway-2026-08-03`  
**Base:** `enhancement/led-floor-level-scaling` @ `430c961`  
**Commit:** `2f9560b`  
**Onsite source:** `.onsite-analysis/led-grid/led-grid/` (extract of `led-grid-merged-takeaway-20260803.zip`)

## Summary

Confirmation merge + ops packaging. Application code was byte-identical to local tip; only operator tooling and one shelve key were applied.

## Changes applied

| Path | Action |
|------|--------|
| `OPERATOR_GUIDE.md` | **Added** from onsite |
| `START_GAME.bat` | **Added** from onsite |
| `STOP_GAME.bat` | **Added** from onsite |
| `games/setting/led_parameter.*` | **Updated** — `game_result_show_time`: 15 → **2** (onsite venue-validated) |

## Verified identical (no change)

| Path | Verification |
|------|--------------|
| `ws_bridge.py` | `diff -q` — identical |
| `api/game_manager.py` | `diff -q` — identical |
| `api/level_scaler.py` | `diff -q` — identical |
| `games/led/led_control.py` | `diff -q` — identical |
| `games/led/communication.py` | `diff -q` — identical |
| `frontend/src/App.jsx` | `diff -q` — identical |
| `frontend/src/screens/SimulatorScreen.jsx` | `diff -q` — identical |
| `games/setting/debug_parameter.*` | `diff -q` — identical |
| `games/setting/language_parameter.*` | `diff -q` — identical |
| `.gitignore`, `.gitattributes` | **Kept local** (shelve tracked + LFS) |

## Shelve notes

- **Only differing key** in `led_parameter`: `game_result_show_time` (local 15, onsite 2). Applied onsite value per plan default.
- COM/grid keys identical: COM4/3/6, 16×26 (`value_width=26`).
- `program_params.dat` differs only in runtime timestamp (`program_is_opened`) — **not copied** (ignore per plan).

## Not committed (by design)

- `frontend/.env` — deploy-only (`VITE_RFID_API_URL=http://192.168.1.106:9000` on site)
- `ledplaydb.sqlite` — runtime score DB
- `node_modules/`, logs

## LFS verification

- Ran `git lfs install`, `git lfs fetch --all`, `git lfs checkout`.
- Level files smudged correctly (e.g. `DK001.ledb` = 517 KB, not 131-byte pointer stub).
- LFS pointers retained in git index — no raw blobs committed as normal objects.

## Test results

```
python3 -m pytest tests/test_level_scaler.py \
  tests/test_game_manager_level_scaling.py \
  tests/test_scaled_gameplay.py \
  tests/test_level_catalog_validation.py
```

**103 passed** in 3.16s — all green.

## Blockers

None. No `MERGE_BLOCKERS.md` required.

## Deploy reminders (site)

1. `git pull` on venue PC
2. `git lfs install && git lfs pull`
3. Copy/create `frontend/.env` with live RFID IP
4. Use `START_GAME.bat` / `STOP_GAME.bat` for operator workflow
