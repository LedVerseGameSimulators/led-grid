#!/usr/bin/env bash
# Start Climb dev stack (API 8001, ws_bridge 8766, UI 5174).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

export API_PORT=8001
export WS_BRIDGE_PORT=8766
UI_PORT=5174

kill_port() {
  local port=$1
  local pids
  pids=$(lsof -ti:"$port" 2>/dev/null || true)
  if [ -n "$pids" ]; then
    echo "Stopping port $port (pids: $pids)"
    kill $pids 2>/dev/null || true
    sleep 1
    pids=$(lsof -ti:"$port" 2>/dev/null || true)
    [ -n "$pids" ] && kill -9 $pids 2>/dev/null || true
  fi
}

echo "==> Climb dev stack from $ROOT"
kill_port "$API_PORT"
kill_port "$WS_BRIDGE_PORT"
kill_port "$UI_PORT"

echo "==> API :$API_PORT"
uvicorn api.main:app --host 0.0.0.0 --port "$API_PORT" --loop asyncio &
API_PID=$!

echo "==> ws_bridge :$WS_BRIDGE_PORT"
python3 ws_bridge.py &
WS_PID=$!

echo "==> frontend :$UI_PORT"
cd frontend && npm run dev &
UI_PID=$!

cleanup() {
  echo "Stopping Climb stack..."
  kill $API_PID $WS_PID $UI_PID 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo ""
echo "Climb ready:"
echo "  UI:        http://localhost:$UI_PORT"
echo "  API:       http://localhost:$API_PORT"
echo "  ws_bridge: http://localhost:$WS_BRIDGE_PORT"
echo "Press Ctrl+C to stop."
wait
