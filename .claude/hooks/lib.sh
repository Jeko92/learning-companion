# Shared helpers for all workflow hooks. Sourced, not executed.

HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$HOOK_DIR/config.sh"

STATE_FILE=".claude/state/workflow.json"

get_state() {
  jq -r --arg k "$1" '.[$k] // empty' "$STATE_FILE" 2>/dev/null
}

current_phase() {
  local p
  p="$(get_state phase)"
  echo "${p:-idle}"
}

current_ticket() {
  get_state ticket
}

current_branch() {
  git branch --show-current 2>/dev/null
}

has_test_suite() {
  [ -f "$PROJECT_MARKER" ]
}
