#!/usr/bin/env bash
# Run a command for a pre-commit hook that needs the Django project.
# Skips (successfully) until the project is scaffolded, i.e. no manage.py yet.
# Usage: scripts/django-hook.sh <command> [args...]
set -euo pipefail

if [ ! -f manage.py ]; then
  echo "skipped: Django project not scaffolded yet (no manage.py)"
  exit 0
fi

exec "$@"
