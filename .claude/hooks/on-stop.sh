#!/usr/bin/env bash
# Stop hook: Claude may not end its turn in the middle of a broken TDD cycle.
# If the phase is 'implementing' and the last recorded test run was red,
# block the stop and send the reason back so Claude finishes the cycle
# (or reverts to the last green commit).
source "$(dirname "$0")/lib.sh"

input="$(cat)"
# Prevent an infinite loop: if this hook already blocked once in this turn,
# let the stop through.
active="$(jq -r '.stop_hook_active // false' <<<"$input")"
[ "$active" = "true" ] && exit 0

phase="$(current_phase)"
if [ "$phase" = "implementing" ] && [ "$(get_state last_test)" = "red" ]; then
  echo "The workflow phase is 'implementing' and the test suite is red. Do not stop mid-cycle: either make the failing test pass (green) or revert to the last green commit, then report the state to the user." >&2
  exit 2
fi

exit 0
