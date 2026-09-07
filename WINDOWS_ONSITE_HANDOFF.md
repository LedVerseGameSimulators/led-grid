# Windows onsite handoff — 6 machines

**Audience:** tech who clones once + operator who only double-clicks Start/Stop.

Operators should **not** run git, pip, or npm by hand. Tech runs setup once per PC; after that operators only use the Start/Stop bats.

---

## 1. Clone URLs (branch: `main`)

| PC | Folder suggestion | URL |
|----|-------------------|-----|
| Hoops | `C:\activerse\led-hoops` | `https://github.com/LedVerseGameSimulators/led-hoops.git` |
| Laser | `C:\activerse\led-laser` | `https://github.com/LedVerseGameSimulators/led-laser.git` |
| Climb | `C:\activerse\led-climb` | `https://github.com/LedVerseGameSimulators/led-climb.git` |
| Grid | `C:\activerse\led-grid` | `https://github.com/LedVerseGameSimulators/led-grid.git` |
| Hexagon | `C:\activerse\led-hexagon` | `https://github.com/LedVerseGameSimulators/led-hexagon.git` |
| RFID / Reception | `C:\activerse\activerse-rfid` | `https://github.com/LedVerseGameSimulators\activerse-rfid.git` |

Use a GitHub account that can read the `LedVerseGameSimulators` org.

---

## 2. Static IPs (recommended)

| Machine | IP |
|---------|-----|
| Hoops | `192.168.1.101` |
| Laser | `192.168.1.102` |
| Climb | `192.168.1.103` |
| Grid | `192.168.1.104` |
| Hexagon | `192.168.1.105` |
| RFID | `192.168.1.106` |

---

## 3. Ports

| Machine | API | Bridge | UI |
|---------|-----|--------|-----|
| Hoops | 8000 | 8765 | 5173 |
| Laser | 8001 | 8768 | 5174 |
| Climb | 8002 | 8766 | 5175 |
| Grid | 8003 | 8769 | 5176 |
| Hexagon | 8004 | 8767 | 5177 |
| RFID | 9000 | — | **5180** |

---

## 4. Tech — first time on each Windows PC

### Install once (all PCs)

1. **Git for Windows**
2. **Git LFS** (`git lfs install` after install — required for **all 5 games**; levels are LFS)
3. **Python 3.11** (tick “Add to PATH”)
4. **Node.js LTS**
5. USB serial drivers for that floor’s controllers

### Clone + setup (each game PC)

In **Git Bash** or PowerShell:

```bat
git lfs install
cd C:\activerse
git clone https://github.com/LedVerseGameSimulators/led-hoops.git
cd led-hoops
git lfs pull
```

Repeat for laser / climb / grid / hexagon with the matching URL.

Then double-click **`SETUP_FIRST_TIME.bat`** in that folder (installs pip + npm, pulls LFS again, creates `frontend\.env`).

Confirm `frontend\.env` contains:

```env
VITE_RFID_API_URL=http://192.168.1.106:9000
```

(Use the real RFID PC IP if different.)

### RFID PC

```bat
cd C:\activerse
git clone https://github.com/LedVerseGameSimulators/activerse-rfid.git
cd activerse-rfid
```

Double-click **`SETUP_FIRST_TIME.bat`**, then edit **`.env`** (from `.env.example`): set `ADMIN_PASSWORD` and the five `*_API=` URLs to the game PC IPs.

### Daily operator use (after setup)

| PC | Start | Stop |
|----|-------|------|
| Any game | `START_GAME.bat` | `STOP_GAME.bat` |
| RFID | `START_SERVER.bat` | `STOP_SERVER.bat` |

That is all the operator needs.

---

## 5. Git LFS (important)

All **five game repos** store `.led` / `.ledb` level files in **Git LFS**.

Without LFS, levels are tiny text pointers and games break.

After every fresh clone or pull on a game PC:

```bat
git lfs pull
```

`SETUP_FIRST_TIME.bat` already runs this.

**Quick check:** a level file under `games\source\` should be many KB/MB, not ~130 bytes of text saying `version https://git-lfs.github.com/...`.

---

## 6. Update later (pull new code)

On each PC, in the repo folder:

```bat
git pull
git lfs pull
```

Then operators keep using Start/Stop as usual. If Python/frontend deps changed, re-run `SETUP_FIRST_TIME.bat` once.

---

## 7. What operators never do

- Edit `games\setting`
- Close the minimized black service windows during play
- Run pip / npm / git (unless tech asks)
- Unplug USB serial mid-game

---

## 8. If something fails

1. Run Stop bat
2. Wait 5 seconds
3. Run Start bat again
4. If still broken: open the minimized API window, screenshot the error, call tech

Full per-game notes: each repo’s `OPERATOR_GUIDE.md`.
