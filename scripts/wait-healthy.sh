#!/usr/bin/env bash
# Usage: ./scripts/wait-healthy.sh <service> [timeout_secs=120]
SERVICE=${1:?Usage: $0 <service> [timeout=120]}
TIMEOUT=${2:-120}
ELAPSED=0
echo "Waiting for $SERVICE to be healthy..."
until [ "$(docker compose ps --format json "$SERVICE" 2>/dev/null | python3 -c "import sys,json; d=sys.stdin.read(); print(json.loads(d).get('Health',''))" 2>/dev/null)" = "healthy" ]; do
  sleep 2
  ELAPSED=$((ELAPSED + 2))
  if [ "$ELAPSED" -ge "$TIMEOUT" ]; then
    echo "Timed out after ${TIMEOUT}s waiting for $SERVICE to be healthy"
    exit 1
  fi
  echo "  still waiting... (${ELAPSED}s)"
done
echo "$SERVICE is healthy."
