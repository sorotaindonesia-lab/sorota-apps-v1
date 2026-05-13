#!/bin/bash
set -e

SCRIPT_DIR="$(dirname "$0")"

echo "Resetting database..."
bash "$SCRIPT_DIR/migrate-down.sh"
bash "$SCRIPT_DIR/migrate-up.sh"
echo "Database reset complete."
