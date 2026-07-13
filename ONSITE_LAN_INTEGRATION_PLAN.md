# Onsite LAN Integration Plan — 6 Machines, 1 Network

**Status:** Design complete, not yet executed on real hardware. This plan is copied into all 6 repos (5 games + `activerse-rfid`) so each machine's setup can proceed independently, using this as the shared source of truth for IPs/ports/roles.

**Read alongside:** each repo's own `ONSITE.md` (single-machine setup steps: extract zip, install deps, verify COM ports, start services) and `HARDWARE_VALIDATION.md` (what's actually been tested on real hardware vs implemented-but-unverified). This document covers ONLY the cross-machine network layer — how the 6 machines find and talk to each other. It does not repeat single-machine setup steps.

---

## Physical layout

6 Windows PCs on one LAN/WiFi (same router/switch, same subnet):

| # | Machine | Repo | Role |
|---|---------|------|------|
| 1 | Hoops floor | `led-hoops` | Game machine — own LED floor, own serial hardware |
| 2 | Laser floor | `led-laser` | Game machine |
| 3 | Climb floor | `led-climb` | Game machine |
| 4 | Grid floor (Floor Is Lava) | `led-grid` | Game machine |
| 5 | Hexagon floor | `led-hexagon` | Game machine |
| 6 | Reception desk | `activerse-rfid` | Central server — player registry, RFID validate, session/credit CRUD, cross-game leaderboard poller |

Each game machine is **autonomous**: it runs its own game regardless of whether Machine 6 is reachable. Machine 6 never controls start/stop on any game machine — it only (a) answers `/validate?card_id=` calls from game machines at login time, and (b) polls each game machine's `/scores` endpoint every 120s to build the cross-game leaderboard. If Machine 6 goes down mid-event, games keep running in guest mode (the "Skip — Play as Guest" fallback already built into every `LoginScreen.jsx`); only RFID-scan login and live leaderboard updates pause until it's back.

---

## Static IP scheme

Assign these as **static IPs** on each machine (not DHCP-leased, so they never drift) — set via Windows: Settings → Network & Internet → Ethernet/Wi-Fi → IP assignment → Manual.

| Machine | Static IP | Subnet mask | Gateway |
|---|---|---|---|
| Hoops | `192.168.1.101` | `255.255.255.0` | `192.168.1.1` (your router) |
| Laser | `192.168.1.102` | `255.255.255.0` | `192.168.1.1` |
| Climb | `192.168.1.103` | `255.255.255.0` | `192.168.1.1` |
| Grid | `192.168.1.104` | `255.255.255.0` | `192.168.1.1` |
| Hexagon | `192.168.1.105` | `255.255.255.0` | `192.168.1.1` |
| RFID / Reception | `192.168.1.106` | `255.255.255.0` | `192.168.1.1` |

If your router's LAN range is different (e.g. `10.0.0.x` or a different `192.168.x.x` block), substitute consistently — what matters is that all 6 are static, on the same subnet, and match the table below.

---

## Port map (per machine, unchanged from dev — only the host IP changes)

| Machine | API (backend) | WS bridge (hardware↔sim) | UI (frontend, kiosk display) |
|---|---|---|---|
| Hoops | 8000 | 8765 | 5173 |
| Laser | 8001 | 8768 | 5174 |
| Climb | 8002 | 8766 | 5175 |
| Grid | 8003 | 8769 | 5176 |
| Hexagon | 8004 | 8767 | 5177 |
| RFID | 9000 | — | 5178 |

**Only the API ports (8000-8004, 9000) need to be reachable across machines.** The WS bridge and UI ports are local to each machine (a game's own frontend talks to its own `localhost` API/WS; nobody browses another machine's UI over the LAN). Windows Firewall inbound rules only need opening for the API port on each machine — see below.

---

## What needs to change from `localhost` to a real IP

Everything in dev defaults to `localhost` because dev runs all 6 on one machine. Onsite, each machine only knows about itself as `localhost` — cross-machine calls need the real IP.

### 1. Each game's frontend → RFID server

`frontend/src/config.js` in every game already supports an override:
```js
export const RFID_API_URL = import.meta.env.VITE_RFID_API_URL || 'http://localhost:9000'
```
Create a `.env` file in each game's `frontend/` directory (Vite picks this up automatically):
```env
VITE_RFID_API_URL=http://192.168.1.106:9000
```
Without this, RFID card scans at any game machine will fail (trying to reach a nonexistent server on `localhost:9000` on that same game machine).

### 2. RFID server → each game's `/scores` and `/settings` endpoints

`activerse-rfid/.env` (already exists locally, gitignored — create fresh on Machine 6):
```env
ADMIN_PASSWORD=<set a real password before going live>
HOOPS_API=http://192.168.1.101:8000
LASER_API=http://192.168.1.102:8001
CLIMB_API=http://192.168.1.103:8002
GRID_API=http://192.168.1.104:8003
LED_HEX_API=http://192.168.1.105:8004
DEFAULT_SESSION_MINUTES=60
MIN_MINUTES_TO_START=5
POLL_INTERVAL_SECONDS=120
DB_PATH=./data/rfid.sqlite
API_HOST=0.0.0.0
API_PORT=9000
```
Without this, the poller can't reach any game machine (`/health`, `/scores`), and Settings' per-game push (`PUT /games/{key}/settings`) can't reach the target game either. Every service already binds to `0.0.0.0` (confirmed in each game's `config.py` / `API_HOST`), so no backend code changes are needed — this is purely `.env` configuration, per machine.

### 3. Windows Firewall — allow inbound on each API port

On each game machine (PowerShell, run as Administrator):
```powershell
New-NetFirewallRule -DisplayName "Activerse Game API" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
```
(substitute the correct port per machine: 8001 laser, 8002 climb, 8003 grid, 8004 hexagon)

On the RFID machine:
```powershell
New-NetFirewallRule -DisplayName "Activerse RFID API" -Direction Inbound -Protocol TCP -LocalPort 9000 -Action Allow
```
Without this, Windows' default firewall silently blocks inbound connections from other machines even though the service is running and reachable via `localhost` on its own machine — this is the single most common "it works on my machine but not over the network" cause. Test with the connectivity check below BEFORE assuming code is broken if cross-machine calls fail.

---

## Connectivity test (run after IP + firewall setup, before any gameplay testing)

From the RFID machine (192.168.1.106), verify it can reach every game:
```powershell
curl http://192.168.1.101:8000/health
curl http://192.168.1.102:8001/health
curl http://192.168.1.103:8002/health
curl http://192.168.1.104:8003/health
curl http://192.168.1.105:8004/health
```
Each should return `{"status":"ok",...}`. If any fails: (1) `ping <that IP>` to rule out a network/cabling issue first, (2) if ping works but curl doesn't, it's almost always the firewall rule on the TARGET machine, not the RFID machine.

From any game machine, verify it can reach the RFID server:
```powershell
curl http://192.168.1.106:9000/health
```

Once all 6 checks pass, do one real end-to-end test: scan a real bound card at one game machine's `LoginScreen`, confirm the player badge shows their real name (not a "could not reach RFID server" error), play a short session, then check the RFID server's Dashboard/leaderboard (or force `POST /internal/poll-now`) and confirm the score appears there within one poll cycle.

---

## Order of operations for going live

1. Assign all 6 static IPs (table above).
2. Open the one firewall port per machine (table above).
3. Run the connectivity test (above) — fix networking before touching application code or hardware.
4. On the RFID machine: create `activerse-rfid/.env` with the real IPs, restart the RFID API.
5. On each game machine: create `frontend/.env` with `VITE_RFID_API_URL` pointing at the RFID machine, rebuild/restart the frontend.
6. Follow each repo's own `ONSITE.md` for single-machine setup (Python deps, npm install, COM port verification) if not already done.
7. Follow each repo's `HARDWARE_VALIDATION.md` for that game's real-hardware test status and checklist.
8. Do the end-to-end RFID scan test (above) on at least one game machine before considering the network layer done.
9. Only after 1-8: begin actual gameplay/hardware validation per game (separate checklist, see `HARDWARE_VALIDATION.md` in each game repo).

---

## Known limitations (by design, not bugs)

- No dynamic service discovery — IPs are static and hand-configured. If a machine's IP changes, update both its own `.env` (if it's the RFID machine) and the RFID machine's `.env` (if it's a game machine), then restart the affected service(s).
- No HTTPS/TLS — this is a closed LAN, not internet-facing. Do not expose any of these ports to the open internet or a shared/public WiFi network.
- No automatic failover — if the RFID machine goes down, games degrade to guest-mode automatically (already built in), but resume RFID-linked play only once it's back up and the poller catches up via its `since=` cursor (no data is lost, just delayed).
