#!/usr/bin/env bash
# Update the workflow state file. Called by the skills, not by hooks.
# Usage: set-state.sh <key> <value> [<key> <value> ...]
# Example: set-state.sh phase implementing ticket user-avatar
set -euo pipefail

STATE_FILE=".claude/state/workflow.json"
mkdir -p .claude/state
[ -f "$STATE_FILE" ] || echo '{}' > "$STATE_FILE"

while [ $# -ge 2 ]; do
  tmp="$(mktemp)"
  jq --arg k "$1" --arg v "$2" '.[$k] = $v' "$STATE_FILE" > "$tmp"
  mv "$tmp" "$STATE_FILE"
  shift 2
done

cat "$STATE_FILE"
