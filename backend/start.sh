#!/bin/sh

echo "Running database migrations..."
alembic upgrade head || echo "WARNING: Alembic migrations failed. Continuing to start server..."

echo "Starting Uvicorn server on port ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
