# CLAUDE.md

Learning Companion: a Django 5.2 LTS app (goals, learning sessions, resources, AI
summaries). Brief: `docs/challenge.md`. The development workflow (refine → plan →
TDD → review) is defined in `.claude/rules/` and enforced by `.claude/hooks/`.

## Environment

- Dev Python is pinned to **3.13** (`.python-version`). Code must remain
  compatible with **Python 3.10+**: ruff targets `py310`, mypy checks against 3.10.
  Don't use 3.11+ only syntax or stdlib (e.g. `tomllib`, `typing.Self`, `ExceptionGroup`)
  without a fallback.
- **Node.js >= 20 + npm** are required for the Tailwind CSS build (django-tailwind,
  npm-backed). The built CSS is gitignored: run `make css` after cloning.
- Always use the project venv: `.venv/bin/python`, `.venv/bin/...`. Never install
  packages with bare `pip install`. Edit `pyproject.toml`, then `make lock && make sync`.

## Commands

```
make install     # venv + locked deps + git hooks
make sync        # venv == requirements/dev.txt
make lock        # re-lock after editing pyproject.toml
make format      # ruff fix + ruff format + djlint reformat
make lint        # all pre-commit hooks on all files
make typecheck   # mypy (strict, django-stubs)
make test        # pytest
make coverage    # pytest --cov, fail_under = 90
make check       # lint + typecheck + test
make doctor      # verify env matches team setup
make css         # npm install + build Tailwind CSS (apps/theme)
make css-watch   # rebuild Tailwind CSS on template changes
```

Dev server (first time: `cp .env.example .env`, then `make css`):

```
.venv/bin/python manage.py migrate
make css-watch                          # terminal 1
.venv/bin/python manage.py runserver    # terminal 2 -> http://127.0.0.1:8000/
```

Single test: `.venv/bin/python -m pytest apps/<app>/tests/test_x.py::test_name`.

## Layout

```
config/              Django project package (settings, urls, asgi/wsgi)
apps/<app>/          Django apps (`apps.<app>`); tests live in apps/<app>/tests/
apps/core/           site-wide pages (home)
apps/theme/          Tailwind: static_src/ (npm project), static/css/dist/ (built, gitignored)
templates/           project-level templates (base.html)
static/              project-level static files (not created yet)
tests/               cross-app / integration tests (settings, repo setup)
manage.py
```

These directories are what `.claude/hooks/config.sh` (`SOURCE_DIRS`) treats as
source code (write-protected outside the `implementing` phase). Update it if the
layout changes. `DJANGO_SETTINGS_MODULE` is `config.settings` (pyproject.toml).

Settings come from the environment via `django-environ`. `.env` is read unless
`DJANGO_ENV_FILE` points elsewhere (empty = no file; the test run uses this).
`SECRET_KEY` is required; `DEBUG` defaults to False.

## Conventions

- Style is enforced by tools, not by taste: ruff (lint + format, line length 88),
  djLint (templates, 2-space indent), mypy strict. Run `make format` before
  committing. Don't add `# noqa` / `# type: ignore` without a reason comment.
- Secrets come from `.env` via `django-environ`. Never hardcode keys; add new
  variables to `.env.example`.
- Tests use pytest + pytest-django (`pytest.mark.django_db`), not `unittest.TestCase`
  style. Warnings are errors (`filterwarnings = error`).
- Commits: Conventional Commits (`feat(<ticket-id>): ...`), enforced by a commit-msg hook.
