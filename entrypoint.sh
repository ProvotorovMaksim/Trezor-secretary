#!/bin/bash
set -e

echo "Waiting for PostgreSQL to be ready..."
# Ждем, пока PostgreSQL станет доступен (максимум 30 секунд)
for i in {1..5}; do
  if python -c "import asyncpg; import asyncio; asyncio.run(asyncpg.connect('$DATABASE_URL'))" 2>/dev/null; then
    echo "PostgreSQL is ready!"
    break
  fi
  echo "PostgreSQL is unavailable - sleeping ($i/30)"
  sleep 1
done

echo "Running database migrations..."
# Применяем все миграции до последней версии
alembic upgrade head

echo "Starting FastAPI application..."
# Запускаем приложение

exec uvicorn main:app --host 0.0.0.0 --port 8003