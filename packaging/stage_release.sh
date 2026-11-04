#!/usr/bin/env bash
# Stage operator allowlist into dist/release/LED-Grid-<tag>-macos/
# No *.py, no frontend/src, no game engine source — data + ui + helpers only.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

TAG="${1:-$(git describe --tags --always 2>/dev/null || echo dev)}"
TAG="${TAG#v}"
STAGE_NAME="LED-Grid-${TAG}-macos"
STAGE_ROOT="${ROOT}/dist/release/${STAGE_NAME}"

echo "==> Stage root: ${STAGE_ROOT}"
rm -rf "${STAGE_ROOT}"
mkdir -p "${STAGE_ROOT}"

# --- UI (frontend/dist) ---
if [[ ! -f "${ROOT}/frontend/dist/index.html" ]]; then
  echo "==> frontend/dist missing — building…"
  (cd frontend && npm ci && npm run build)
fi
mkdir -p "${STAGE_ROOT}/ui"
rsync -a --delete "${ROOT}/frontend/dist/" "${STAGE_ROOT}/ui/"

# --- games data only: tracked files only (never local dev DBs/scores) ---
# git ls-files => real LFS content (checked out), no untracked/ignored dev junk.
# Audio limited to what the engine plays; .py/.pyc never.
(
  cd "${ROOT}"
  git ls-files -z -- games/source games/source_group games/setting games/audio \
    | tr '\0' '\n' \
    | grep -v -E '\.(py|pyc|mp4|md|rar)$' \
    | grep -v -E '/ledplaydb\.sqlite$' \
    | rsync -a --files-from=- "${ROOT}/" "${STAGE_ROOT}/"
)

# --- api data (playlist order; JSON, no code) ---
mkdir -p "${STAGE_ROOT}/api"
cp "${ROOT}/api/mode_playlists.json" "${STAGE_ROOT}/api/mode_playlists.json"

# --- simulator static ---
mkdir -p "${STAGE_ROOT}/simulator/static"
if [[ -d "${ROOT}/simulator/static" ]]; then
  rsync -a "${ROOT}/simulator/static/" "${STAGE_ROOT}/simulator/static/"
fi

# --- STOP + README ---
cp "${ROOT}/packaging/STOP_GAME.sh" "${STAGE_ROOT}/STOP_GAME.sh"
chmod +x "${STAGE_ROOT}/STOP_GAME.sh"
# Windows operator STOP: the exe does what STOP_GAME.bat did (kiosk, children, ports).
printf '@echo off\r\n"%%~dp0LED Grid.exe" --stop\r\n' > "${STAGE_ROOT}/STOP_GAME.bat"
cp "${ROOT}/packaging/README_OPERATOR.txt" "${STAGE_ROOT}/README_OPERATOR.txt"


# --- Assert no operator-readable Python ---
PY_HITS="$(find "${STAGE_ROOT}" -name '*.py' -print 2>/dev/null || true)"
if [[ -n "${PY_HITS}" ]]; then
  echo "ERROR: staged tree contains .py files (forbidden for operators):"
  echo "${PY_HITS}"
  exit 1
fi

echo "==> Stage OK (no .py). Contents:"
du -sh "${STAGE_ROOT}"/* 2>/dev/null || ls -la "${STAGE_ROOT}"
echo "${STAGE_ROOT}" > "${ROOT}/dist/release/.last_stage_macos"
echo "Staged: ${STAGE_ROOT}"
