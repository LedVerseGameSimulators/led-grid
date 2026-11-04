# Operator packaging (K2b)

Binary-only release: one Nuitka-compiled executable with roles, plus data.
No `.py`/`.pyc` ships. See `docs/PLAN_KIOSK_AND_PACKAGING.md` in the umbrella repo.

- `floor_launcher/` — the program (supervisor, api/bridge roles, `--selftest`, `--stop`)
- `build_nuitka_macos.sh` / `build_nuitka_windows.ps1` — build + stage + zip
- `stage_release.sh` / `stage_release.py` — data allowlist (tracked files only)
- `.github/workflows/package.yml` — Windows CI build, gate, frozen smoke, artifact/release

Local mac build:  `bash packaging/build_nuitka_macos.sh`
Parity contract: the exe must behave exactly like `START_GAME.bat` (hardware ON by default).
