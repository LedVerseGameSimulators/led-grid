# On-Site Hardware Integration Guide — LED Grid (Floor Is Lava)

> **For Cursor agent:** Follow every step in order. Do not skip verification steps. Do not touch the RFID server, SQL server, or any service already running on this PC.

> **Important:** LED Grid lives inside the parent `activerse_final_changes` repo, NOT a standalone repo. The zip for this game contains the full parent repo. The game code is at `led-grid\` inside it.

---

## Game Config

| Key | Value |
|-----|-------|
| Game | LED Grid / Floor Is Lava |
| Grid | 16 rows × 26 cols |
| COM ports | 3 (read from shelve — see Step 4) |
| Layout type | 6 (read from shelve to confirm) |
| Display var | `led_display` |
| Zip extract dir | `C:\activerse\activerse_final_changes` |
| Game dir | `C:\activerse\activerse_final_changes\led-grid` |
| Python version | 3.10 or 3.11 |
| Server port | 8003 (adjust if already assigned differently) |

---

## Step 1 — Extract the zip

Extract so the structure is:
```
C:\activerse\activerse_final_changes\
  led-grid\
    api\
    games\
    requirements.txt
  led-hoops\    (ignore)
  led-laser\    (ignore)
  ...
```

Open **Command Prompt as Administrator**. Use for all remaining steps.

---

## Step 2 — Check Python

```cmd
python --version
pip --version
```

**If missing:** install Python 3.11 (winget or python.org, add to PATH). See HOOPS_ONSITE.md Step 2.

---

## Step 3 — Install dependencies

```cmd
cd C:\activerse\activerse_final_changes\led-grid
pip install -r requirements.txt
```

---

## Step 4 — Verify shelve

```cmd
cd C:\activerse\activerse_final_changes\led-grid\games
python -c "import shelve; db=shelve.open('setting/led_parameter',flag='r'); [print(k,'=',db[k]) for k in db.keys()]; db.close()"
```

**Expected:**
- `list_com_info` — 3 COM port entries
- `led_layout_type` — 6
- `value_high` — 16
- `value_width` — 26

---

## Step 5 — Verify COM ports

```cmd
python -c "import serial.tools.list_ports; [print(p) for p in serial.tools.list_ports.comports()]"
```

All 3 COM ports from shelve must appear.

---

## Step 6 — Run hardware diagnostic

```cmd
cd C:\activerse\activerse_final_changes\led-grid\games
python test_hardware.py
```

**Expected:**
1. `All COM ports opened OK` (3 ports)
2. Full 16×26 floor lights **green** for 3s
3. Step on tiles → `PRESS detected: row=X col=Y`
4. `Floor cleared. Done.`

16×26 is the largest floor (416 tiles). All sections should light.

---

## Step 7 — Start game server

```cmd
cd C:\activerse\activerse_final_changes\led-grid
set USE_SERIAL_HD=1
python -m uvicorn api.main:app --host 0.0.0.0 --port 8003
```

**Expected log:**
```
Hardware ready: 3 port(s), 16×26, layout=6
```

**PowerShell:**
```powershell
$env:USE_SERIAL_HD="1"
python -m uvicorn api.main:app --host 0.0.0.0 --port 8003
```

---

## Step 8 — Verify sim + hardware

1. Browser → `http://localhost:8003`
2. Start a Grid game
3. Lava tiles update on physical floor
4. Stepping on a safe tile scores; stepping on lava deducts life

---

## What NOT to touch

- RFID server / SQL server — leave untouched
- `games/setting/led_parameter` shelve — do not modify
- Other game folders (`led-hoops`, `led-laser`, etc.) — not relevant to this PC

---

## Troubleshooting

**16×26 is large — partial lighting:** each of 3 COM ports covers ~138 tiles. Identify which third is dark and trace its cable.

**Port 8003 in use:** `netstat -ano | findstr :8003` → `taskkill /PID <pid> /F`
