#!/bin/sh
set -e

echo "▶ Initializing internal database..."
uv run python -m docker_script.internal_database_init

echo "▶ Initializing external database..."
uv run python -m docker_script.external_database_factory

echo "▶ Starting API server..."
exec uv run uvicorn api.main:app \
  --host 0.0.0.0 \
  --port "${AGENT_API_PORT}" \
  --reload \
  --reload-dir "${WORKDIR_PATH}" \
  --reload-delay 0.5
