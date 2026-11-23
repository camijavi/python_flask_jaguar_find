#!/bin/sh
set -e

export DATABASE_PATH="${DATABASE_PATH:-/home/jaguarFind.db}"
mkdir -p "$(dirname "$DATABASE_PATH")"

if [ ! -f "$DATABASE_PATH" ]; then
  seed_db=""

  for candidate in \
    "/home/site/wwwroot/jaguarFind.db" \
    "/app/jaguarFind.db" \
    "$(dirname "$0")/jaguarFind.db"
  do
    if [ -f "$candidate" ]; then
      seed_db="$candidate"
      break
    fi
  done

  if [ -n "$seed_db" ]; then
    cp "$seed_db" "$DATABASE_PATH"
  fi
fi

exec gunicorn \
  --bind "0.0.0.0:${PORT:-8000}" \
  --timeout 600 \
  --workers 1 \
  app:app
