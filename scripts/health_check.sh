#!/usr/bin/env bash
set -e

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8002}"
HEALTH_ENDPOINT="${HEALTH_ENDPOINT:-/health}"
MAX_RETRIES="${MAX_RETRIES:-10}"
SLEEP_SECONDS="${SLEEP_SECONDS:-3}"

echo "Checking health at http://${HOST}:${PORT}${HEALTH_ENDPOINT}"

for ((i=1; i<=MAX_RETRIES; i++)); do
  STATUS_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://${HOST}:${PORT}${HEALTH_ENDPOINT}" || true)

  if [ "$STATUS_CODE" = "200" ]; then
    echo "Health check passed."
    exit 0
  fi

  echo "Attempt ${i}/${MAX_RETRIES} failed. Status code: ${STATUS_CODE}"
  sleep "$SLEEP_SECONDS"
done

echo "Health check failed after ${MAX_RETRIES} attempts."
exit 1