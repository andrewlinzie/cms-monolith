#!/usr/bin/env bash
set -e

CONTAINER_NAME="${CONTAINER_NAME:-cms-monolith}"

echo "Restarting container: ${CONTAINER_NAME}"

docker restart "${CONTAINER_NAME}"

echo "Running post-restart health check..."
./scripts/health_check.sh

echo "Restart completed successfully."