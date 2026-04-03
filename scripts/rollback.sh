#!/usr/bin/env bash
set -e

IMAGE_REPO="${IMAGE_REPO:-cms-monolith}"
ROLLBACK_TAG="${ROLLBACK_TAG:-previous}"
FULL_IMAGE="${IMAGE_REPO}:${ROLLBACK_TAG}"

CONTAINER_NAME="${CONTAINER_NAME:-cms-monolith}"
HOST_PORT="${HOST_PORT:-8002}"
CONTAINER_PORT="${CONTAINER_PORT:-8002}"

APP_ENV="${APP_ENV:-dev}"
LOG_LEVEL="${LOG_LEVEL:-INFO}"

echo "Rolling back to image: ${FULL_IMAGE}"

docker pull "${FULL_IMAGE}"

echo "Stopping current container if it exists..."
docker stop "${CONTAINER_NAME}" || true

echo "Removing current container if it exists..."
docker rm "${CONTAINER_NAME}" || true

echo "Starting rollback container..."
docker run -d \
  --name "${CONTAINER_NAME}" \
  -p "${HOST_PORT}:${CONTAINER_PORT}" \
  -e APP_ENV="${APP_ENV}" \
  -e LOG_LEVEL="${LOG_LEVEL}" \
  "${FULL_IMAGE}"

echo "Running post-rollback health check..."
HOST="127.0.0.1" PORT="${HOST_PORT}" ./scripts/health_check.sh

echo "Rollback completed successfully."