#!/bin/bash
set -e

if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

if [ -z "$DATABASE_URL" ]; then
  echo "ERROR: DATABASE_URL is not set"
  exit 1
fi

MIGRATIONS_DIR="$(dirname "$0")/../migrations"

echo "Running migrations UP..."
for file in "$MIGRATIONS_DIR"/*.up.sql; do
  echo "  Applying: $(basename "$file")"
  psql "$DATABASE_URL" -f "$file"
done
echo "All migrations applied."
