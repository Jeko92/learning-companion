# Plan: project-scaffold

## Research summary
- **Repo state:** no Django code yet. `pyproject.toml` has `django>=5.2,<5.3` and `django-environ>=0.12`, plus dev dependencies ruff, djlint, django-stubs (mypy), pytest, pytest-django and pytest-cov. Locking: `make lock` runs pip-compile with `--generate-hashes` into `requirements/{base,dev}.txt`; `make sync` installs them. `.env.example` has `DEBUG`, `SECRET_KEY`, `ALLOWED_HOSTS`, `DATABASE_URL` and `OPENAI_API_KEY`.
- **Tests:** pytest with `DJANGO_SETTINGS_MODULE=config.settings`, `filterwarnings=error`, `--strict-config`, no testpaths. ruff relaxes S101/PLR2004 only under `**/tests/**`. mypy is strict; tests are allowed untyped defs. Coverage measures `apps` and `config`, omits migrations, tests, asgi/wsgi and manage.py, and must reach 90 %.
- **Hooks:**
  - The post-write hook runs `pytest -q` only once `manage.py` exists, and any non-zero exit counts as red. Pytest's exit 5 ("no tests collected") is red too.
  - Commits in the implementing phase need a green suite once `manage.py` exists.
  - Pre-commit runs:
    - ruff and ruff-format
    - djlint
    - django-upgrade
    - mypy
    - `makemigrations --check`
    - JSON/YAML checks and whitespace/end-of-file fixers
    - a 500 KB file-size limit
- **django-tailwind:**
  - Latest is 4.5.0, which needs Python 3.11 or newer. The last release that supports 3.10 is **4.2.0** (Django 4.2–5.2). Both default to Tailwind v4 and use npm.
  - `tailwind init` uses cookiecutter, which it pip-installs on the fly. It also can't generate into `apps/theme` because it only accepts plain app names.
  - `{% tailwind_css %}` renders `<link … href="{% static 'css/dist/styles.css' %}">` and doesn't check that the file exists. There's no `?v=` suffix when `DEBUG` is False.
  - The package has no type hints. Commands: `tailwind install` (npm install + build), `build`, `start` (watch).
  - The built CSS goes to `<theme>/static/css/dist/styles.css`.
- **Environment:** Node v24 and npm are on the dev machine (installed through fnm).

## Design decisions
- **Pin `django-tailwind>=4.2,<4.3`.** It's the newest line that still runs on Python 3.10, which CLAUDE.md requires. Without the pin, the lock file would get 4.5.0.
- **Hand-write the theme app in `apps/theme`.** It copies django-tailwind 4.2.0's v4 app template: `apps.py`, `static_src/package.json`, `postcss.config.js` and `src/styles.css`. We don't run `tailwind init`, which would mean a cookiecutter dependency, an on-the-fly pip install and a rename step.
- **Commit `package-lock.json`** for reproducible npm installs. Built CSS and `node_modules/` are gitignored (AC9).
- **Settings with `django-environ`.**
  - `SECRET_KEY` is `env("SECRET_KEY")` with no default, so a missing key fails at startup.
  - `DEBUG` defaults to False and `ALLOWED_HOSTS` to an empty list.
  - `DATABASE_URL` defaults to `sqlite:///<BASE_DIR>/db.sqlite3`.
- **`.env` path can be overridden through `DJANGO_ENV_FILE`.** The default is `<BASE_DIR>/.env`, an empty value means "read no file", and a missing file is skipped. This lets tests run without a developer's local `.env` leaking in.
- **`pytest-env` (new dev dependency)** sets `SECRET_KEY` and `DJANGO_ENV_FILE=` for the test run, before pytest-django loads settings. That way the suite also works on a checkout with no `.env`, such as CI later.
- **Settings tests reload `config.settings`** with `importlib.reload` under `monkeypatch`, check the module's attributes, and reload again at teardown. This keeps the tests in-process and counted by coverage.
- **AC1 runs in a subprocess:** `manage.py check` with `DJANGO_ENV_FILE=.env.example`. That's the only way to load real settings from that file.
- **Home page:** a `TemplateView` in `apps/core` (created with `startapp`), using `core/home.html`, which extends the project-level `templates/base.html`.
- **Make targets:** `make css` runs `manage.py tailwind install` (npm install and build). `make css-watch` runs `manage.py tailwind start`. djlint excludes `node_modules`.

## Steps
- [x] 0. Dependencies (config only, no behaviour change). Add `django-tailwind>=4.2,<4.3` to the dependencies and `pytest-env` to the dev extras, then run `make lock && make sync`. Add a `[tool.pytest.ini_options] env` entry with `SECRET_KEY=insecure-test-key` and `DJANGO_ENV_FILE=`. — impl: `pyproject.toml`, `requirements/*.txt` — commit `chore(project-scaffold): ...`
- [x] 1. `manage.py check` passes with `.env.example` values. — test: `tests/test_project.py` (subprocess with `DJANGO_ENV_FILE=.env.example`) — impl: `django-admin startproject config .`, then the settings read the `.env` file named by `DJANGO_ENV_FILE`, plus `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` and `DATABASE_URL` through `environ.Env`. Generated code must pass ruff and mypy. — covers: AC1
- [x] 2. GET `/` returns 200 using `base.html` and `core/home.html`. — test: `apps/core/tests/test_views.py` — impl: `apps/__init__.py`, `apps/core` (startapp, `AppConfig.name = "apps.core"`), `HomeView`, `apps/core/urls.py`, include from `config/urls.py`, `templates/base.html`, `apps/core/templates/core/home.html`, `TEMPLATES.DIRS` — covers: AC2
- [ ] 3. The home page shows the heading "Learning Companion" and a tagline. — test: `apps/core/tests/test_views.py` — impl: `core/home.html`, and a nav block placeholder in `base.html` — covers: AC3
- [ ] 4. Missing `SECRET_KEY` raises `ImproperlyConfigured`. — test: `tests/test_settings.py` (reload with `SECRET_KEY` removed) — impl: `config/settings.py` if needed — covers: AC5
- [ ] 5. `DEBUG`, `ALLOWED_HOSTS` (comma-separated) and `DATABASE_URL` from the environment change the settings. — test: `tests/test_settings.py` — impl: `config/settings.py` — covers: AC6
- [ ] 6. Defaults: `DEBUG` False, `ALLOWED_HOSTS` empty, and SQLite when `DATABASE_URL` is unset. — test: `tests/test_settings.py` — impl: `config/settings.py` — covers: AC7
- [ ] 7. `tailwind` and `apps.theme` are installed, with `TAILWIND_APP_NAME == "apps.theme"`. — test: `tests/test_settings.py` — impl: `apps/theme/{__init__,apps}.py`, `apps/theme/static_src/{package.json,postcss.config.js,src/styles.css}` (copied from django-tailwind 4.2.0's v4 template, `@source` covering `templates/` and `apps/`), and the settings — covers: AC8
- [ ] 8. `base.html` loads Tailwind, so the rendered home page links to `/static/css/dist/styles.css`. — test: `apps/core/tests/test_views.py` — impl: `templates/base.html` (`{% load tailwind_tags %}{% tailwind_css %}`) — covers: AC4
- [ ] 9. Built CSS and `node_modules/` are gitignored. — test: `tests/test_repo.py` (`git check-ignore` on `apps/theme/static/css/dist/styles.css` and `apps/theme/static_src/node_modules/x`) — impl: `.gitignore` — covers: AC9
- [ ] 10. Make targets build the CSS. — test: `tests/test_repo.py` (`make -n css` shows `manage.py tailwind install`, and `make -n css-watch` shows `manage.py tailwind start`) — impl: `Makefile` (`css`, `css-watch`), djlint exclude for `node_modules`, run `make css` once and commit `package-lock.json`. Also update CLAUDE.md: the layout is now actual, plus the Node.js requirement and the CSS/dev-server commands. That doc change is reviewed, not tested. — covers: AC10
- [ ] 11. Verification, no new behaviour: `make check` and `make coverage` (≥ 90 %) pass, and anything they flag is fixed. — covers: AC11

## Coverage
| AC | Step(s) |
|----|---------|
| AC1 | 1 |
| AC2 | 2 |
| AC3 | 3 |
| AC4 | 8 |
| AC5 | 4 |
| AC6 | 5 |
| AC7 | 6 |
| AC8 | 7 |
| AC9 | 9 |
| AC10 | 10 (the CLAUDE.md part is checked in review) |
| AC11 | 11 |
