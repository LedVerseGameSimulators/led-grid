#!/usr/bin/env bash
# Decompile .pyc → .py using pycdc (Decompyle++) in Docker.
# Same toolchain used for Climb/Hoops/Laser (*_py_source trees).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
IMAGE="${PYCDC_IMAGE:-activerse-pycdc}"
DOCKERFILE="$ROOT/scripts/docker/pycdc/Dockerfile"

if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
  echo "==> Building $IMAGE (first run may take a few minutes)..."
  docker build -t "$IMAGE" -f "$DOCKERFILE" "$(dirname "$DOCKERFILE")"
fi

decompile_one() {
  local pyc="$1" py="$2"
  mkdir -p "$(dirname "$py")"
  docker run --rm -v "$(dirname "$pyc"):/in:ro" "$IMAGE" "/in/$(basename "$pyc")" > "$py" || {
    echo "[!] pycdc failed: $pyc" >&2
    return 1
  }
  if ! grep -q "def \|class " "$py" 2>/dev/null; then
    echo "[!] Output looks empty or invalid: $py" >&2
    return 1
  fi
  echo "[+] $py"
}

EXTRACT="${1:-/Users/apple/Desktop/activerse/floor_is_lava/raw/ledplayv020505/ledplay/ledplay.exe_extracted/PYZ-00.pyz_extracted}"
OUT="${2:-/Users/apple/Desktop/activerse/floor_is_lava/grid_py_source}"

PRIORITY=(
  game_play/Play.pyc
  game_play/game_running.pyc
  game_play/life_value_calculation.pyc
  game_play/game_util.pyc
  game_play/game_hw.pyc
  game_play/game_music.pyc
)

mkdir -p "$OUT"
ok=0 fail=0
for rel in "${PRIORITY[@]}"; do
  pyc="$EXTRACT/$rel"
  py="$OUT/${rel%.pyc}.py"
  if [[ ! -f "$pyc" ]]; then
    echo "[!] missing: $pyc" >&2
    ((fail++)) || true
    continue
  fi
  if decompile_one "$pyc" "$py"; then
    ((ok++)) || true
  else
    ((fail++)) || true
  fi
done

echo "[+] Decompiled: $ok  failed: $fail  → $OUT"
[[ "$fail" -eq 0 ]]
