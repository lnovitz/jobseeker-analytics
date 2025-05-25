#!/bin/bash
set -e

# Run Alembic migrations
alembic upgrade head

# Start the FastAPI app
exec uvicorn main:app --reload --host 0.0.0.0 --port 8000