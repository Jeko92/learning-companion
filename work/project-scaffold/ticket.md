# Project scaffolding: runnable Django project

Source: GitHub issue #1 (board "Learning Companion").

## Story
As a developer, I want a runnable, tested Django skeleton with a Tailwind-styled base layout, so that every later feature has a green suite and a fixed layout to build on.

## Acceptance criteria
- [x] AC1 `python manage.py check` passes with a `.env` copied unchanged from `.env.example` (test runs the `check` command with those values and gets no errors).
- [x] AC2 GET `/` returns 200 and renders `base.html` plus the home template of the `apps/core` app.
- [x] AC3 The home page shows the heading "Learning Companion" and a one-line tagline.
- [x] AC4 `base.html` loads the Tailwind stylesheet through django-tailwind (`{% tailwind_css %}`); the rendered home page contains the link to the built stylesheet.
- [x] AC5 With `SECRET_KEY` unset, loading settings raises `ImproperlyConfigured`.
- [x] AC6 Settings come from the environment: setting `DEBUG`, `ALLOWED_HOSTS` (comma-separated) and `DATABASE_URL` changes the matching Django setting.
- [x] AC7 Defaults when the variable is unset: `DEBUG` is `False`, `ALLOWED_HOSTS` is empty, and `DATABASE_URL` falls back to SQLite.
- [x] AC8 `tailwind` and the Tailwind theme app are in `INSTALLED_APPS`, and `TAILWIND_APP_NAME` points at the theme app.
- [x] AC9 `.gitignore` excludes the built Tailwind CSS and `node_modules/`, so neither is committed.
- [x] AC10 The Makefile has a target that builds the Tailwind CSS (via `manage.py tailwind`), and CLAUDE.md documents it, the Node.js requirement, and the actual layout (no longer "planned").
- [x] AC11 `make check` is green and `make coverage` passes (>= 90 %).

## Out of scope
- Authentication and any nav links that depend on it (next ticket).
- Any domain models.
- Docker / CI, including building CSS in CI.
- Tailwind design system / component styling beyond the base layout.
- Adding Node to `make doctor` checks.

## Notes
- Styling: Tailwind through **django-tailwind** (npm-backed), chosen by the user over a Python-only option. This adds Node.js/npm as a developer requirement. The theme app should live under `apps/` so it stays inside `SOURCE_DIRS`.
- Built CSS is **gitignored** and built on demand. Every checkout, and later Docker/CI, must build it. Tests must not depend on the built file existing.
- Settings strictness: fail fast on a missing `SECRET_KEY`; everything else has a safe default (see AC7).
- The home view lives in a new `apps/core` app for site-wide pages. Content: title, tagline, and an empty nav slot in `base.html`.
- Existing config to respect: pytest `filterwarnings = error`, mypy strict with django-stubs, coverage source `apps` + `config` (`fail_under = 90`), ruff py310.
- Python packages go into `pyproject.toml`, followed by `make lock && make sync`. Never use a bare `pip install`.
