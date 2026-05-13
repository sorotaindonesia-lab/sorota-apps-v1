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

echo "Running migrations DOWN (reverse order)..."
for file in $(ls "$MIGRATIONS_DIR"/*.down.sql | sort -r); do
  echo "  Reverting: $(basename "$file")"
  psql "$DATABASE_URL" -f "$file"
done
echo "All migrations reverted."
