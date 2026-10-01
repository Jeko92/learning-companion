#!/usr/bin/env bash
# PostToolUse hook for Write|Edit|MultiEdit.
# Logs every file change to the ticket's activity log. During the
# implementing phase it also runs the test suite and records the red/green
# result in the state file - that record is the evidence for the TDD cycle
# (the tdd-implement skill checks it, and the Stop hook refuses to end the
# session on red).
source "$(dirname "$0")/lib.sh"

input="$(cat)"
file="$(jq -r '.tool_input.file_path // empty' <<<"$input")"
[ -z "$file" ] && exit 0

rel="${file#"$PWD"/}"
ticket="$(current_ticket)"
log_dir="work/${ticket:-untracked}"
mkdir -p "$log_dir"
echo "$(date -Iseconds) WRITE $rel" >> "$log_dir/activity.log"

phase="$(current_phase)"
if [ "$phase" = "implementing" ] && [ "$RUN_TESTS_ON_WRITE" = "true" ] \
   && has_test_suite && echo "$rel" | grep -qE "^($SOURCE_DIRS)/"; then
  if $TEST_CMD >/dev/null 2>&1; then
    status="green"
  else
    status="red"
  fi
  bash "$(dirname "$0")/set-state.sh" last_test "$status" last_test_at "$(date -Iseconds)" >/dev/null
  echo "$(date -Iseconds) TESTS $status (after $rel)" >> "$log_dir/activity.log"
  echo "[workflow] test suite is $status"
fi

exit 0
