#!/usr/bin/env bash
set -e

IMAGE_REPO="${IMAGE_REPO:-cms-monolith}"
IMAGE_TAG="${IMAGE_TAG:-dev}"
FULL_IMAGE="${IMAGE_REPO}:${IMAGE_TAG}"

CONTAINER_NAME="${CONTAINER_NAME:-cms-monolith}"
HOST_PORT="${HOST_PORT:-8002}"
CONTAINER_PORT="${CONTAINER_PORT:-8002}"

APP_ENV="${APP_ENV:-dev}"
LOG_LEVEL="${LOG_LEVEL:-INFO}"

echo "Deploying image: ${FULL_IMAGE}"
echo "Target container: ${CONTAINER_NAME}"

echo "Pulling latest image..."
docker pull "${FULL_IMAGE}"

echo "Stopping existing container if it exists..."
docker stop "${CONTAINER_NAME}" || true

echo "Removing existing container if it exists..."
docker rm "${CONTAINER_NAME}" || true

echo "Starting new container..."
docker run -d \
  --name "${CONTAINER_NAME}" \
  -p "${HOST_PORT}:${CONTAINER_PORT}" \
  -e APP_ENV="${APP_ENV}" \
  -e LOG_LEVEL="${LOG_LEVEL}" \
  "${FULL_IMAGE}"

echo "Running post-deploy health check..."
HOST="127.0.0.1" PORT="${HOST_PORT}" ./scripts/health_check.sh

echo "Deployment completed successfully."