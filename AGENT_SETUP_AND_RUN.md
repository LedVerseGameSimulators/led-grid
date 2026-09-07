# AGENT_SETUP_AND_RUN.md — LED Grid (Floor Is Lava) (Windows game machine)

**Audience:** an AI coding agent on **this Windows game PC** — one-time setup
today, then daily start/stop.

**Repos:**

| Location | Role |
|----------|------|
| GitHub `main` | Going-forward **source of truth** for code (already matches the developer PC) |
| This game PC’s **old** install (if any) | May be outdated **or** may hold a fix that never got pushed — **audit once today** |
| Venue configs on this PC | Shelve / COM / `.env` — keep these |

Also read: `WINDOWS_ONSITE_HANDOFF.md`, `OPERATOR_GUIDE.md`.

---

## Machine identity

| Item | Value |
|------|-------|
| Repo | `led-grid` |
| Clone URL | `https://github.com/LedVerseGameSimulators/led-grid.git` |
| Suggested path | `C:\activerse\led-grid` |
| API / Bridge / UI | `8003` / `8769` / `5176` |
| Start / Stop | `START_GAME.bat` / `STOP_GAME.bat` |
| First-time setup | `SETUP_FIRST_TIME.bat` |
| RFID env | `frontend\.env` → `VITE_RFID_API_URL` |

---

## One-time sync model (today only)

```
1. Pull GitHub main into a NEW (or updated) folder + git lfs pull
2. Find OLD game-machine copy (if any)
3. AUDIT code AND LFS levels: anything in OLD not on remote?
      → report + add/push (incl. git lfs for .led/.ledb)
4. Keep venue settings from OLD
5. After today: always git pull + git lfs pull; never copy old tree over new
```

**Important:** Do **not** blindly delete OLD without the audit. Remote is the
intended truth, but today’s job is to catch fixes **and levels** that exist
**only on this game machine** and never reached GitHub / Git LFS.

---

## Phase 0 — Prerequisites (once)

1. Git for Windows  
2. Git LFS → `git lfs install`  
3. Python 3.11 on PATH  
4. Node.js LTS on PATH  
5. USB serial drivers for this floor  

---

## Phase 1 — Get the OLD game-machine codebase path from the human (**ask deliberately**)

**Do not guess. Do not skip this. Do not invent a path.**

Before cloning or diffing, **ask the human (operator / tech on site) in chat**:

> What is the full path to the **existing / old** LED Grid (Floor Is Lava) install on this PC  
> (the codebase that was running here before today’s git clone)?  
> Examples: `C:\activerse\led-grid`, `D:\led-grid`, a Desktop extract folder.  
> If there is **no** old install on this machine, reply `NONE`.

Rules:

1. Wait for their answer before Phase 2–3.  
2. If they give a path: verify it exists (`dir <path>`). Record it as `OLD_ROOT`.  
3. If they say `NONE` / no old copy: set `OLD_ROOT=` empty, skip code/LFS diffs vs OLD, still do fresh clone + setup.  
4. If the path is wrong or empty: ask again — do not proceed with a guessed location.  
5. Optional hint only after they ask for help: common folders to look in are  
   `C:\activerse\`, `C:\`, `D:\`, Desktop, Downloads — but **they** confirm the path.

**Do not delete `OLD_ROOT` until Phase 6 passes.**

---

## Phase 2 — Clone / update GitHub `main` (NEW tree)

Prefer a **new** folder if OLD already occupies `C:\activerse\led-grid`, e.g.
`C:\activerse\led-grid-git`, then swap after audit. Or rename OLD aside first.

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

A file under `games\source\*.led` / `*.ledb` must be many KB/MB — **not** ~130
bytes of `version https://git-lfs.github.com/spec/v1`.  
On fail: fix LFS, `git lfs pull`, stop.

---

## Phase 3 — ONE-TIME audit: OLD game machine vs NEW (remote + LFS)

Audit **code** and **level assets** (Git LFS). Both must be reconciled today.

### 3.1 What to compare

**Code** (not `node_modules`, `__pycache__`, `ledplaydb.sqlite`, logs):

| Path | Why |
|------|-----|
| `api\` | Backend / marathon / effects |
| `frontend\src\` | UI / countdown sync |
| `games\led\` | Serial / hardware |
| `ws_bridge.py` | Bridge |
| `START_GAME.bat` / `STOP_GAME.bat` | Launchers |
| `hardware_config.py` (if present) | COM / grid |

**Levels / LFS assets** (must match; these live in Git LFS on remote):

| Path | Why |
|------|-----|
| `games\source\**\*.led` / `*.ledb` | Normal + marathon levels |
| `games\source_group\**\*.led` / `*.ledb` | Group / corporate playlists |
| `games\source\effects\*.led` | Countdown / clear / fail panels |
| `tests\fixtures\**\*.led` (if present) | Test fixtures |

Also compare any other large media the OLD tree used for play (e.g. production
`.mp3` under `games\audio\` that are real files, not silent placeholders) —
if OLD has a real asset NEW lacks, treat it like an LFS/asset gap and push it.

### 3.2 PowerShell audit — code + LFS levels (run on the game PC)

```powershell
$NEW = "C:\activerse\led-grid"          # the git clone (after git lfs pull)
$OLD = "C:\path\to\OLD_ROOT"             # set from Phase 1
$Report = "C:\activerse\grid-reconcile-report.txt"

$lines = @()
$lines += "NEW tip: $(git -C $NEW rev-parse --short HEAD)"
$lines += "NEW status: $(git -C $NEW status -sb)"
$lines += "NEW lfs count: $((git -C $NEW lfs ls-files | Measure-Object -Line).Lines)"

# --- A) Code dirs ---
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

# --- B) Level / LFS assets (.led / .ledb) ---
# Skip pointer stubs (~130 bytes). Compare real binaries by SHA256.
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
        $lines += "NEW_IS_LFS_POINTER_OR_EMPTY: $rel  (run git lfs pull)"
      } else {
        $h1 = (Get-FileHash $_.FullName -Algorithm SHA256).Hash
        $h2 = (Get-FileHash $counterpart -Algorithm SHA256).Hash
        if ($h1 -ne $h2) {
          $lines += "DIFFERS_LFS: $rel  old=$($_.Length) new=$((Get-Item $counterpart).Length)"
        }
      }
    }
}

# Levels on NEW that OLD never had are fine (remote ahead) — no action.
$lines | Tee-Object -FilePath $Report
Write-Host "Report written to $Report"
```

### 3.3 How to interpret the report

| Finding | Action |
|---------|--------|
| Clean (no `ONLY_ON_MACHINE_*` / no important `DIFFERS_*`) | Remote already complete. Prefer NEW. |
| `ONLY_ON_MACHINE_CODE` / `DIFFERS_CODE` | **Stop.** Port the fix into NEW, commit, **push to GitHub `main`**, then continue. |
| `ONLY_ON_MACHINE_LFS` | **Stop.** Level exists on the game PC but not in git/LFS. **Add + push via LFS** (section 3.5). |
| `DIFFERS_LFS` | Hashes differ. Decide which file is correct (usually the floor-proven OLD level). Replace in NEW, then **git add + push LFS** (3.5). |
| `NEW_IS_LFS_POINTER_OR_EMPTY` | `git lfs pull` not done or LFS broken — fix before comparing. |
| Diff only in `games\setting\` or `.env` | Expected. Keep venue values (3.6). |
| `node_modules` / sqlite / logs | Ignore. |

**Reconcile rule for today:** anything real on the game machine that remote lacks
(code **or** levels) must land on GitHub — including **Git LFS upload** for
`.led` / `.ledb` — before you throw OLD away.

### 3.5 Add missing / updated levels to Git LFS and push

When the report lists `ONLY_ON_MACHINE_LFS` or you chose OLD for a `DIFFERS_LFS`:

```bat
cd C:\activerse\led-grid
git lfs install
git checkout main
git pull

REM Copy the missing/updated file(s) from OLD into the same relative path under NEW
REM Example:
REM   copy /Y "OLD\games\source_group\-\001.led" "games\source_group\-\001.led"

git lfs track "*.led" "*.ledb"
git add .gitattributes
git add games\source\...path...
git add games\source_group\...path...
git status
git lfs status

git commit -m "content: add venue levels missing from LFS (one-time reconcile)"
git push origin main
```

Confirm after push:

1. `git lfs ls-files` lists the new paths  
2. On a fresh check, file size is many KB/MB (not a pointer)  
3. GitHub shows the commit on `main`  

If push fails on LFS auth, fix GitHub credentials / `git lfs` login and retry —
**do not** commit level binaries as normal git blobs; they must go through LFS
(`.gitattributes` already tracks `*.led` / `*.ledb`).

Same pattern for real production audio if OLD has full `.mp3` and NEW only has
tiny placeholders: copy into `games\audio\`, `git add`, commit, push (audio may
be normal git or LFS depending on repo — prefer matching existing tracking).

### 3.6 Venue configs (always keep from OLD when present)

Copy into NEW if missing or if OLD is the known-good floor config:

- `games\setting\led_parameter.dat` (+ `.bak` / `.dir`)
- `games\setting\debug_parameter.*`
- other `games\setting\*` shelve files
- `frontend\.env` (RFID IP) — or create from `frontend\.env.example`

Do **not** copy OLD `api\` / `frontend\src\` wholesale onto NEW.  
Do **not** skip LFS for levels — copy into NEW then `git add` so LFS clean filter runs.

---

## Phase 4 — Install dependencies

```bat
cd C:\activerse\led-grid
SETUP_FIRST_TIME.bat
```

---

## Phase 5 — Run

```bat
START_GAME.bat
```

UI: `http://localhost:5176` — leave minimized windows open.  
Stop: `STOP_GAME.bat`.

---

## Phase 6 — Done (perfect sync)

- [ ] NEW is `main` + `git lfs pull` OK (levels are real binaries)  
- [ ] One-time OLD vs NEW report reviewed — no unresolved `ONLY_ON_MACHINE_CODE` or `ONLY_ON_MACHINE_LFS`  
- [ ] Any machine-only levels were `git add`’d through LFS and **pushed**  
- [ ] Venue settings + RFID `.env` in place  
- [ ] START / STOP work on hardware  

**After today:** updates are only:

```bat
git pull origin main
git lfs pull
START_GAME.bat
```

Never copy old game-machine code or levels over the git tree again without going
through git + LFS.

---

## Failure quick reference

| Symptom | Action |
|---------|--------|
| Levels ~130 bytes | Git LFS / `git lfs pull` |
| `ONLY_ON_MACHINE_LFS` in report | Copy into NEW → `git add` → commit → push (LFS) |
| Report shows machine-only code fix | Port to NEW → commit → push before deleting OLD |
| Floor dark | COM + `led_parameter.dat` + API window |
| RFID fails | `frontend\.env` RFID IP |
| Port busy | `STOP_GAME.bat`, retry |
