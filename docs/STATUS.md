# Climb — Headless Status (summary)

> **Canonical doc:** [`CLIMB_DEVELOPMENT_PLAYBOOK.md`](./CLIMB_DEVELOPMENT_PLAYBOOK.md) — done/pending checklists, runbook, hardware path.

**Last updated:** 2026-06-07 · **Repo:** `led-climb` · **Simulator:** ✅ · **Hardware:** ⏳ pending

---

## Quick status

| Area | Status |
|------|--------|
| 6×33 square simulator + API | ✅ |
| Session marathon (A / B / DK series) | ✅ |
| Overlap priority + bounce fix | ✅ |
| 2P DK scoring + respawn | ✅ |
| Ports 8001 / 8766 / 5174 | ✅ |
| Serial floor (3 COM typical) | ⏳ code in `games/led/`, not wired |

---

## Architecture (simulator)

```
React (:5174) → FastAPI (:8001) → Play.running() → HeadlessLedTable
     iframe ↓                           ↑
Simulator (:8766) ← ws_bridge ← /game-state + /game-input
```

---

## Run

```bash
cd led-climb && ./scripts/start-dev.sh
```

---

## Note on other docs in this folder

Several files (`DEPLOYMENT.md`, `SETTINGS.md`, `LEVELS.md`, `STATUS_HARDWARE.md`) were written during the **LED Hex** migration and still mention hex paths or `kavida_claude`. Use **`CLIMB_DEVELOPMENT_PLAYBOOK.md`** for Climb-specific status; use **`HARDWARE_MODE.md`** for I/O design (applies to all floor games).
