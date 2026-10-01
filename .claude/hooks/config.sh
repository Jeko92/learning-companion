# Project-specific configuration for the workflow hooks.
# Adapt these to your project. Everything else should work unchanged.

# Django + pytest, run from the project virtualenv (see Makefile).
TEST_CMD=".venv/bin/python -m pytest -q"
LINT_CMD=".venv/bin/pre-commit run --all-files"

# File whose presence means "the project has a test suite to enforce".
# Before the Django scaffold exists there is nothing to run.
PROJECT_MARKER="manage.py"

# Run the test suite after every source/test file write (records red/green
# for the TDD cycle). Set to "false" if your suite is too slow for that;
# tests are then only enforced at commit time.
RUN_TESTS_ON_WRITE="true"

# Branches that may never receive direct commits or force-pushes.
PROTECTED_BRANCHES="main|master"

# Directories that count as production/test code (used by the write guard).
# Django layout: config/ = project package, apps/ = Django apps,
# templates/ + static/ = front end, tests/ = cross-app tests.
SOURCE_DIRS="config|apps|templates|static|tests"
