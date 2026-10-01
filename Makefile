# Developer entry points. `make help` lists them.
# Everything runs inside .venv, built from the Python pinned in .python-version.

PY_PIN := $(shell cat .python-version)
PYTHON ?= python$(PY_PIN)
VENV   := .venv
BIN    := $(VENV)/bin
COMPILE := $(BIN)/pip-compile --quiet --strip-extras --allow-unsafe --generate-hashes

.DEFAULT_GOAL := help
.PHONY: help install sync lock upgrade doctor css css-watch lint format typecheck test coverage check clean

help: ## Show this help
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

$(BIN)/python:
	@command -v $(PYTHON) >/dev/null || { echo "✗ $(PYTHON) not found. Install Python $(PY_PIN) (e.g. brew install python@$(PY_PIN))."; exit 1; }
	$(PYTHON) -m venv $(VENV)
	$(BIN)/python -m pip install --quiet --upgrade pip

install: $(BIN)/python ## Create .venv, install locked deps, install git hooks
	@python3 scripts/check_python_version.py
	$(BIN)/python -m pip install --quiet --require-hashes -r requirements/dev.txt
	$(BIN)/pip-sync --quiet requirements/dev.txt
	$(BIN)/pre-commit install --install-hooks

sync: ## Make .venv match requirements/dev.txt exactly (after pulling)
	$(BIN)/pip-sync requirements/dev.txt

lock: ## Re-lock requirements/*.txt after editing pyproject.toml
	$(COMPILE) --output-file=requirements/base.txt pyproject.toml
	$(COMPILE) --extra=dev --output-file=requirements/dev.txt pyproject.toml

upgrade: ## Upgrade all locked deps to the newest versions allowed by pyproject.toml
	$(COMPILE) --upgrade --output-file=requirements/base.txt pyproject.toml
	$(COMPILE) --upgrade --extra=dev --output-file=requirements/dev.txt pyproject.toml

doctor: ## Verify the local environment matches the team setup
	@python3 scripts/check_python_version.py
	@$(BIN)/pip-sync --dry-run requirements/dev.txt | grep -q "Everything up-to-date" \
		&& echo "✓ .venv matches requirements/dev.txt" \
		|| { echo "✗ .venv out of sync — run: make sync"; exit 1; }
	@test -f .git/hooks/pre-commit && echo "✓ git hooks installed" || { echo "✗ git hooks missing — run: make install"; exit 1; }

css: ## Install npm deps and build Tailwind CSS (needs Node.js/npm)
	$(BIN)/python manage.py tailwind install

css-watch: ## Rebuild Tailwind CSS on template changes (run next to runserver)
	$(BIN)/python manage.py tailwind start

lint: ## Run every pre-commit check on all files
	$(BIN)/pre-commit run --all-files

format: ## Auto-format Python and templates
	$(BIN)/ruff check --fix .
	$(BIN)/ruff format .
	$(BIN)/djlint . --reformat --quiet || true

typecheck: ## Run mypy
	$(BIN)/mypy .

test: ## Run the test suite
	$(BIN)/python -m pytest

coverage: ## Run tests with coverage report (fails under threshold)
	$(BIN)/python -m pytest --cov --cov-report=term-missing

check: lint typecheck test ## Everything CI runs

clean: ## Remove caches and build artefacts
	rm -rf .mypy_cache .ruff_cache .pytest_cache htmlcov .coverage coverage.xml build dist *.egg-info
	find . -type d -name __pycache__ -not -path "./$(VENV)/*" -exec rm -rf {} +
