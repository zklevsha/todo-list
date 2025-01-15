#!/bin/bash
set -e

source /app/.venv/bin/activate

alembic upgrade head

exec uvicorn app:app --host 0.0.0.0 --port 8000