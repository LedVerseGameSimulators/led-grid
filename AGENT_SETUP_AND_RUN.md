# AGENT_SETUP_AND_RUN.md — LED Grid (Floor Is Lava) (Windows game machine)

**Audience:** an AI coding agent on **this Windows game PC** — one-time setup
today, then daily start/stop.

## Mandatory first steps (do these before any install/clone/copy)

1. **Read this entire file** (`AGENT_SETUP_AND_RUN.md`) end to end.  
2. Also skim `WINDOWS_ONSITE_HANDOFF.md` and `OPERATOR_GUIDE.md` if present.  
3. **Ask the human** for the OLD on-machine codebase path (Phase 1) — do not guess.  
4. Clone/pull remote (Phase 2), run the audit (Phase 3), then **present the full
   audit results in chat and wait for explicit human confirmation** before
   copying, merging, committing, pushing, or installing/running.

**Hard rule:** after the audit, **STOP and ask**. Do not auto-keep venue
configs, auto-copy levels, or auto-push. Wait for the human to confirm (or
reject) each proposed action.

---

## Machine identity

| Item | Value |
|------|-------|
| Repo | `led-grid` |
| Clone URL | `https://github.com/LedVerseGameSimulators/led-grid.git` |
| Suggested NEW path | `C:\activerse\led-grid` (or `...\led-grid-git` if OLD already uses that folder) |
| API / Bridge / UI | `8003` / `8769` / `5176` |
| Start / Stop | `START_GAME.bat` / `STOP_GAME.bat` |
| First-time setup | `SETUP_FIRST_TIME.bat` |
| RFID env | `frontend\.env` → `VITE_RFID_API_URL` |

---

## Truth table

| Location | Role |
|----------|------|
| GitHub `main` | Intended going-forward **source of truth** for code + LFS levels |
| OLD game-machine install | May be outdated **or** hold fixes/levels never pushed — **audit once today** |
| Venue configs (`games\setting`, `.env`) | Candidate to keep from OLD — **only after human confirms** |

---

## One-time sync model (today only)

```
0. READ this file fully
1. ASK human for OLD_ROOT path (or NONE)
2. Clone/pull GitHub main + git lfs pull → NEW
3. AUDIT OLD vs NEW (code + LFS levels + venue config candidates)
4. PRESENT report in chat → WAIT for human confirmation
5. Only then: apply approved copies / LFS add+push / setting/.env choices
6. SETUP_FIRST_TIME → START_GAME (after human OK)
7. After today: git pull + git lfs pull only
```

---

## Phase 0 — Prerequisites (once)

Check (install only if missing, tell human what you install):

1. Git for Windows  
2. Git LFS → `git lfs install`  
3. Python 3.11 on PATH  
4. Node.js LTS on PATH  
5. USB serial drivers for this floor  

---

## Phase 1 — Ask for OLD codebase path (**deliberately**)

**Do not guess. Do not invent a path.**

Ask in chat:

> What is the full path to the **existing / old** LED Grid (Floor Is Lava) install on this PC  
> (the codebase that was running here before today’s git clone)?  
> Examples: `C:\activerse\led-grid`, `D:\led-grid`, a Desktop extract.  
> If there is **no** old install, reply `NONE`.

Rules:

1. Wait for the answer before Phase 2–3.  
2. If path given: verify with `dir`. Record `OLD_ROOT`.  
3. If `NONE`: skip OLD vs NEW diffs; still clone NEW and ask before setup/run.  
4. Wrong/empty path → ask again.  

**Do not delete `OLD_ROOT` until Phase 6 passes and human agrees.**

---

## Phase 2 — Clone / update GitHub `main` (NEW tree)

If OLD already lives at the suggested path, clone to a sibling folder
(e.g. `C:\activerse\led-grid-git`) so you do not overwrite OLD before audit.

```bat
git lfs install
mkdir C:\activerse 2>nul
cd C:\activerse
git clone https://github.com/LedVerseGameSimulators/led-grid.git
cd led-grid
git checkout main
git pull
git lfs pull
```

### LFS check (mandatory)

A `games\source\*.led` / `*.ledb` must be many KB/MB — **not** ~130 bytes starting
with `version https://git-lfs.github.com/spec/v1`. Fix LFS before auditing.

---

## Phase 3 — ONE-TIME audit (read-only until confirmation)

Audit **code**, **LFS levels**, and **venue config candidates**.  
**Do not copy, commit, or push in this phase.**

### 3.1 Paths

**Code:** `api\`, `frontend\src\`, `games\led\`, `ws_bridge.py`, bats, `hardware_config.py`  

**LFS / levels:** `games\source\**\*.led|*.ledb`, `games\source_group\**\`, `games\source\effects\`, `tests\fixtures\`  

**Venue candidates (report only):** `games\setting\*`, `frontend\.env`  

Ignore: `node_modules`, `__pycache__`, `ledplaydb.sqlite`, logs.

### 3.2 PowerShell audit (read-only)

```powershell
$NEW = "C:\activerse\led-grid"          # adjust to actual NEW path
$OLD = "C:\path\to\OLD_ROOT"
$Report = "C:\activerse\grid-reconcile-report.txt"

$lines = @()
$lines += "NEW tip: $(git -C $NEW rev-parse --short HEAD)"
$lines += "NEW status: $(git -C $NEW status -sb)"
$lines += "NEW lfs count: $((git -C $NEW lfs ls-files | Measure-Object -Line).Lines)"

$codeDirs = @("api","frontend\src","games\led")
foreach ($d in $codeDirs) {
  $oldDir = Join-Path $OLD $d
  if (-not (Test-Path $oldDir)) { $lines += "OLD missing dir: $d"; continue }
  Get-ChildItem $oldDir -Recurse -File -Include *.py,*.jsx,*.js,*.bat,*.md |
    ForEach-Object {
      $rel = $_.FullName.Substring($OLD.Length).TrimStart("\")
      $counterpart = Join-Path $NEW $rel
      if (-not (Test-Path $counterpart)) {
        $lines += "ONLY_ON_MACHINE_CODE: $rel"
      } else {
        $h1 = (Get-FileHash $_.FullName -Algorithm SHA256).Hash
        $h2 = (Get-FileHash $counterpart -Algorithm SHA256).Hash
        if ($h1 -ne $h2) { $lines += "DIFFERS_CODE: $rel" }
      }
    }
}

$levelRoots = @("games\source","games\source_group","tests\fixtures")
foreach ($d in $levelRoots) {
  $oldDir = Join-Path $OLD $d
  if (-not (Test-Path $oldDir)) { continue }
  Get-ChildItem $oldDir -Recurse -File -Include *.led,*.ledb |
    Where-Object { $_.Length -gt 500 } |
    ForEach-Object {
      $rel = $_.FullName.Substring($OLD.Length).TrimStart("\")
      $counterpart = Join-Path $NEW $rel
      if (-not (Test-Path $counterpart)) {
        $lines += "ONLY_ON_MACHINE_LFS: $rel  size=$($_.Length)"
      } elseif ((Get-Item $counterpart).Length -lt 500) {
        $lines += "NEW_IS_LFS_POINTER_OR_EMPTY: $rel"
      } else {
        $h1 = (Get-FileHash $_.FullName -Algorithm SHA256).Hash
        $h2 = (Get-FileHash $counterpart -Algorithm SHA256).Hash
        if ($h1 -ne $h2) {
          $lines += "DIFFERS_LFS: $rel  old=$($_.Length) new=$((Get-Item $counterpart).Length)"
        }
      }
    }
}

# Venue candidates — existence only (do not copy yet)
foreach ($p in @(
  "games\setting\led_parameter.dat",
  "games\setting\debug_parameter.dat",
  "frontend\.env"
)) {
  $o = Join-Path $OLD $p
  $n = Join-Path $NEW $p
  $lines += "VENUE_CANDIDATE: $p  OLD_exists=$(Test-Path $o)  NEW_exists=$(Test-Path $n)"
}

$lines | Tee-Object -FilePath $Report
Write-Host "Report written to $Report"
```

### 3.3 Present results and **WAIT for confirmation** (mandatory gate)

Paste into chat (or attach the report file) a clear summary:

1. NEW git tip + LFS file count  
2. List of `ONLY_ON_MACHINE_CODE` / `DIFFERS_CODE`  
3. List of `ONLY_ON_MACHINE_LFS` / `DIFFERS_LFS`  
4. Venue candidates (`VENUE_CANDIDATE` lines)  
5. **Proposed actions** (numbered), for example:  
   - A. Push these N levels to Git LFS  
   - B. Port these code files to NEW and push  
   - C. Copy OLD `games\setting\*` → NEW  
   - D. Copy / create `frontend\.env` with RFID IP = …  
   - E. Ignore these diffs (obsolete)  
6. Ask explicitly:

> Please confirm which proposed actions to apply (e.g. “do A, C, D; skip B”).  
> I will not copy, commit, push, or start the game until you confirm.

**Do not proceed** to Phase 3.5 / 4 / 5 until the human replies with confirmation.

| Finding | After confirmation only |
|---------|-------------------------|
| Clean | Prefer NEW; still confirm venue `.env` / settings |
| `ONLY_ON_MACHINE_CODE` / `DIFFERS_CODE` | Port + push if human approves |
| `ONLY_ON_MACHINE_LFS` / `DIFFERS_LFS` | Add via LFS + push if human approves |
| Venue candidates | Copy OLD→NEW **only if human says yes** |
| `NEW_IS_LFS_POINTER_OR_EMPTY` | Fix `git lfs pull` first, re-audit |

### 3.5 Apply approved LFS / code changes (only after confirmation)

```bat
cd C:\activerse\led-grid
git lfs track "*.led" "*.ledb"
REM copy only the human-approved files from OLD → NEW
git add <approved-paths>
git status
git lfs status
git commit -m "content: one-time reconcile from venue machine (approved)"
git push origin main
```

Levels must go through LFS (not raw blobs). Re-verify sizes after push.

### 3.6 Venue configs (only if human confirmed)

If approved, copy the agreed files:

- `games\setting\led_parameter.dat` (+ `.bak` / `.dir`) and related shelve  
- `frontend\.env` (or create from `.env.example` with the IP the human specifies)

Never bulk-copy OLD `api\` / `frontend\src\` without per-file approval.

---

## Phase 4 — Install dependencies (after audit confirmation)

Ask: “OK to run SETUP_FIRST_TIME.bat now?” then:

```bat
cd C:\activerse\led-grid
SETUP_FIRST_TIME.bat
```

---

## Phase 5 — Run (after human OK)

Ask: “OK to start the game?” then `START_GAME.bat`.  
UI: `http://localhost:5176`. Stop: `STOP_GAME.bat`.

---

## Phase 6 — Done

- [ ] This file was read first  
- [ ] OLD path asked and recorded (or NONE)  
- [ ] Audit report shown; human confirmed actions  
- [ ] Approved LFS/code pushes done (if any)  
- [ ] Approved venue configs applied (if any)  
- [ ] START / STOP verified  

Later: `git pull` + `git lfs pull` + `START_GAME.bat` only.

---

## Failure quick reference

| Symptom | Action |
|---------|--------|
| Levels ~130 bytes | Git LFS / `git lfs pull` |
| Unsure what to copy | Show report again; wait for confirmation |
| Floor dark | COM + settings (if human approved copy) + API window |
| RFID fails | Confirm `.env` IP with human |
| Port busy | `STOP_GAME.bat`, retry |
