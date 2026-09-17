# Grid MP Phase A + B — manual and backend QA levels

**Repo:** `led-grid`  
**Scope:** Team Battle (`.ledb` under `games/source/----/`) + 1P regression

---

## Start Team Battle (simulator)

1. From repo root: `./scripts/start-dev.sh` (or `start-dev.bat` on Windows).
2. Open the frontend (typically `http://localhost:5173`).
3. **Mode:** Team Battle (2 players).
4. **Level:** pick one of the `.ledb` IDs below (e.g. `01`).
5. **Login:** RFID or play without RFID (random guest names).
6. Poll `/game-state/{game_id}` or watch the HUD:
   - `multiplayer: true`
   - `goal_color` / `goal2_color` (blue / orange)
   - Phase A+B behavior while playing

**API shortcut (backend smoke):**

```bash
curl -s -X POST http://localhost:8000/start-game \
  -H 'Content-Type: application/json' \
  -d '{"card_id":"qa-mp","level":"01","difficulty":"normal","player_count":2}'
```

---

## Recommended `.ledb` levels (`games/source/----/`)

| Level | File | Use for |
|-------|------|---------|
| **01** | `01.ledb` | Baseline 2P smoke — goal swatches, red/DEDUCT lives-only (Phase A), simple wave flow |
| **02** | `02.ledb` | Staggered / multi-group waves — **either-player advance** (Phase B): clear P1 while P2 tiles remain → wave should jump without waiting |
| **03** | `03.ledb` | Mixed P1/P2 timing — vacuous-empty latch (P1-only wave must not false-advance) |
| **04** | `04.ledb` | Longer marathon slice — session persistence across level advance |
| **05** | `05.ledb` | Hazard density — red rate-limit vs DEDUCT one-shot (Phase A) |
| **DK002** | `DK002` | Advanced 2P pack — same-color / dense boards (Phase A scoring unchanged; Phase B discard on wave clear) |

Pick **02** or **03** first for Phase B either-player verification.

---

## 1P regression (unchanged behavior)

| Level | File | Use for |
|-------|------|---------|
| **L1** | `games/source/-/001.led` | Quick clear → level advance |
| **L3** | `games/source/-/003.led` | Masked-goal grace (moving red) — must **not** false-clear early; grace timer rescue |
| **L2** | `games/source/-/002.led` | Multi-wave 1P — still waits for **all** scoreables before jump |

Start **Quick Play** (1 player), same dev stack as above.

---

## Verify checklist

### Phase A (already shipped)

- [ ] `multiplayer: true` on `.ledb` session
- [ ] HUD / state: `goal_color` blue, `goal2_color` orange
- [ ] Plain **red** hit → life −1, **scores unchanged**
- [ ] **DEDUCT** hit → life −1, consume tile, **scores unchanged**
- [ ] Red cooldown works; DEDUCT stays one-shot
- [ ] 1P red still deducts score + life

### Phase B (either-player advance)

- [ ] On a staggered 2P wave: finish **P1** tiles while **P2** tiles remain → floor jumps to next wave **without** waiting for P2
- [ ] P2 leftovers from that wave are gone (not carried into next wave)
- [ ] P1-only wave (no P2 tiles in window): clearing P1 advances; **empty P2 must not** discard P1 or false-advance early
- [ ] Future waves (later `start_time_sec`) still spawn after jump
- [ ] 1P Quick Play: clearing one color group still waits for all scoreables (no either-player discard)

---

## Backend pytest

From `led-grid/`:

```bash
python3 -m pytest tests/test_mp_phase_b.py tests/test_mp_phase_a.py tests/test_masked_goal_grace.py -q
```

Phase B only:

```bash
python3 -m pytest tests/test_mp_phase_b.py -q
```

---

## Related docs

- Shared MP plan (parent repo): `docs/PLAN_MULTIPLAYER_SCORING_AND_HUD.md`
- Grid FE + leftovers: `docs/PLAN_UI_AND_REMAINING_WORK.md`
