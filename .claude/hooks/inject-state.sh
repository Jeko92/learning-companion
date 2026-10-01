#!/usr/bin/env bash
# UserPromptSubmit hook: stdout is added to Claude's context on every prompt,
# so the session always knows which workflow phase it is in.
source "$(dirname "$0")/lib.sh"

phase="$(current_phase)"
ticket="$(current_ticket)"

if [ "$phase" = "idle" ]; then
  echo "[workflow] No ticket in progress (phase: idle). Feature work must start with the refine-ticket skill; source files are write-protected until the implementing phase."
else
  echo "[workflow] phase=$phase ticket=${ticket:-unknown} branch=$(current_branch). Artifacts live in work/${ticket:-unknown}/. Follow .claude/rules/workflow.md; do not skip phases."
fi
exit 0
