#!/bin/bash
set -e

if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

if [ -z "$DATABASE_URL" ]; then
  echo "ERROR: DATABASE_URL is not set"
  exit 1
fi

SEEDS_DIR="$(dirname "$0")/../seeds"

echo "Running seeds..."
for file in "$SEEDS_DIR"/*.sql; do
  echo "  Seeding: $(basename "$file")"
  psql "$DATABASE_URL" -f "$file"
done
echo "Seeds applied."
