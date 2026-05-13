#!/bin/bash
set -e

case "$1" in
  up)
    bash /app/scripts/migrate-up.sh
    ;;
  down)
    bash /app/scripts/migrate-down.sh
    ;;
  seed)
    bash /app/scripts/seed-dev.sh
    ;;
  reset)
    bash /app/scripts/reset-db.sh
    ;;
  *)
    echo "Usage: $0 {up|down|seed|reset}"
    exit 1
    ;;
esac
