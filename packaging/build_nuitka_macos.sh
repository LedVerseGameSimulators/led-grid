#!/usr/bin/env bash
# Build the Grid operator package with Nuitka (macOS): ONE executable with roles
# (supervisor / api / bridge / --selftest / --stop), staged next to data, zipped.
# Windows twin: packaging/build_nuitka_windows.ps1 (CI: .github/workflows/package.yml)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

EXE_NAME="${EXE_NAME:-LED-Grid}"
VENV="${ROOT}/packaging/.venv"
PYTHON="${VENV}/bin/python"

if [[ ! -x "${PYTHON}" ]]; then
  echo "==> Creating packaging/.venv"
  python3 -m venv "${VENV}"
fi

echo "==> Installing Nuitka + deps"
"${PYTHON}" -m pip install -q -U pip wheel
"${PYTHON}" -m pip install -q nuitka ordered-set zstandard
"${PYTHON}" -m pip install -q -r api/requirements.txt

echo "==> Building UI"
(cd frontend && npm ci --silent && npm run build)

OUT="${ROOT}/dist/nuitka"
rm -rf "${OUT}"
mkdir -p "${OUT}"

# games/ holds the engine packages (game_play, led, ...) that api.game_manager imports.
export PYTHONPATH="${ROOT}:${ROOT}/games${PYTHONPATH:+:$PYTHONPATH}"

# api.game_manager replaces these with MagicMock in sys.modules at import time
# (GUI, dongle check `encryption`, mysql, numpy/PIL/cv2, ...). They must NOT be bundled.
NOFOLLOW=(tkinter numpy PIL cv2 moviepy pynput rsa Crypto mysql encryption gui gui2 ui_design net)
NOFOLLOW_ARGS=()
for m in "${NOFOLLOW[@]}"; do NOFOLLOW_ARGS+=("--nofollow-import-to=${m}"); done

echo "==> Nuitka ${EXE_NAME} (this can take a long time)"
"${PYTHON}" -m nuitka \
  --standalone \
  --static-libpython=no \
  --assume-yes-for-downloads \
  --output-dir="${OUT}" \
  --output-filename="${EXE_NAME}" \
  --include-package=api \
  --include-package=floor_launcher \
  --include-module=ws_bridge \
  --include-package=fastapi \
  --include-package=starlette \
  --include-package=uvicorn \
  --include-package=pydantic \
  --include-package=pydantic_core \
  --include-package=websockets \
  --include-package=httpx \
  --include-package=httpcore \
  --include-package=anyio \
  --include-package=h11 \
  --include-package=loguru \
  --include-package=dotenv \
  --include-package=serial \
  --include-package=pygame \
  --include-package=game_play \
  --include-package=led \
  --include-package=model \
  --include-package=model_in \
  --include-package=audio_play \
  --include-package=database \
  --include-package=util \
  --include-module=shelve \
  --include-module=dbm.dumb \
  --nofollow-import-to=pygame.tests \
  "${NOFOLLOW_ARGS[@]}" \
  floor_launcher/entry.py

DIST="${OUT}/entry.dist"
[[ -d "${DIST}" ]] || { echo "ERROR: missing ${DIST}"; exit 1; }

echo "==> Staging allowlist"
bash packaging/stage_release.sh "${TAG:-}"
STAGE="$(cat dist/release/.last_stage_macos)"
cp -R "${DIST}/." "${STAGE}/"

PY_HITS="$(find "${STAGE}" \( -name '*.py' -o -name '*.pyc' \) -print 2>/dev/null || true)"
if [[ -n "${PY_HITS}" ]]; then
  echo "ERROR: Python source/bytecode found in operator package:"
  echo "${PY_HITS}" | head -20
  exit 1
fi

ZIP_NAME="$(basename "${STAGE}")-nuitka.zip"
( cd "${ROOT}/dist/release" && rm -f "${ZIP_NAME}" && zip -qy -r "${ZIP_NAME}" "$(basename "${STAGE}")" )
echo "==> Wrote dist/release/${ZIP_NAME}"
