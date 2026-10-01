#!/usr/bin/env bash
# PreToolUse hook for Bash.
# Gates around git: no commits on protected branches, no commits with red
# tests, no --no-verify, no push before the review has passed, no force-push
# to protected branches.
# Exit 2 blocks the command; stderr is fed back to Claude.
source "$(dirname "$0")/lib.sh"

input="$(cat)"
cmd="$(jq -r '.tool_input.command // empty' <<<"$input")"
[ -z "$cmd" ] && exit 0

is_git() {
  echo "$cmd" | grep -qE "(^|[;&|]\s*)git\s+$1"
}

phase="$(current_phase)"
branch="$(current_branch)"

if is_git "commit"; then
  if echo "$cmd" | grep -qE -- "--no-verify|-n\b"; then
    echo "BLOCKED by workflow: 'git commit --no-verify' is not allowed. Commit hooks are part of the quality gate." >&2
    exit 2
  fi
  if echo "$branch" | grep -qE "^($PROTECTED_BRANCHES)$"; then
    echo "BLOCKED by workflow: direct commits to '$branch' are not allowed. The refine-ticket skill creates a feature branch; work there." >&2
    exit 2
  fi
  if [ "$phase" = "idle" ]; then
    echo "BLOCKED by workflow: no ticket is in progress (phase: idle). Start with the refine-ticket skill before committing." >&2
    exit 2
  fi
  if [ "$phase" = "implementing" ] || [ "$phase" = "reviewing" ]; then
    if has_test_suite; then
      if ! $TEST_CMD >/dev/null 2>&1; then
        echo "BLOCKED by workflow: the test suite is red. Commits are only allowed on green. Finish the current TDD cycle first ($TEST_CMD)." >&2
        exit 2
      fi
    fi
  fi
fi

if is_git "push"; then
  if echo "$cmd" | grep -qE -- "--force|-f\b" && echo "$cmd" | grep -qE "($PROTECTED_BRANCHES)"; then
    echo "BLOCKED by workflow: force-pushing to a protected branch is not allowed." >&2
    exit 2
  fi
  if [ "$phase" != "done" ]; then
    echo "BLOCKED by workflow: pushing requires a passed final review (current phase: $phase). Run the final-review skill; it sets the phase to 'done' on a PASS verdict." >&2
    exit 2
  fi
fi

exit 0
