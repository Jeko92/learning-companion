# Learning Companion

Track learning goals and sessions, attach resources, and get AI-powered summaries
and next steps. Built with **Django 5.2 LTS**.

- Challenge brief: [docs/challenge.md](docs/challenge.md)
- AI-factory workflow (Claude Code skills, rules, hooks): [docs/ai-factory-workflow.md](docs/ai-factory-workflow.md)

## Requirements

| Tool | Version | Notes |
|---|---|---|
| Python | **3.13** for development (pinned in `.python-version`) | Code must stay compatible with **3.10+** (`requires-python`) |
| make, git, bash | any recent | macOS/Linux. On Windows use WSL. |
| gh | any recent | for PRs |

Install Python 3.13, e.g. `brew install python@3.13`, `pyenv install 3.13`
(pyenv reads `.python-version` automatically), or the python.org installer.

## Setup

```bash
git clone git@github.com:Jeko92/learning-companion.git && cd learning-companion
make install        # creates .venv with Python 3.13, installs locked deps, installs git hooks
cp .env.example .env
make doctor         # verifies your environment matches the team's
```

After every `git pull` that changes `requirements/`, run `make sync`.

## Daily commands

```
make help        list all targets
make format      auto-format Python (ruff) and templates (djlint)
make lint        run every pre-commit check on all files
make typecheck   mypy with django-stubs (strict)
make test        pytest
make coverage    pytest with coverage (fails under 90%)
make check       lint + typecheck + test (what CI runs)
```

## Dependencies

Declared in `pyproject.toml`, locked with hashes in `requirements/*.txt` (pip-tools).

- Add/change a dependency → edit `pyproject.toml` → `make lock` → `make sync` → commit both.
- Never edit `requirements/*.txt` by hand. The pre-commit hook re-locks if they drift.
- `make upgrade` bumps everything to the latest allowed versions.

When you bump **ruff** or **djlint**, bump the matching `rev:` in
`.pre-commit-config.yaml` too, so editor, CLI and hooks format identically.

## Code style (enforced, not discussed)

| Concern | Tool | Config |
|---|---|---|
| Whitespace, line endings, indentation | EditorConfig | `.editorconfig` |
| Python lint + format + import order | ruff | `pyproject.toml [tool.ruff]` |
| Django template lint + format | djLint | `pyproject.toml [tool.djlint]` |
| Types | mypy + django-stubs | `pyproject.toml [tool.mypy]` |
| Django API modernisation | django-upgrade | `.pre-commit-config.yaml` |
| Commit messages | Conventional Commits | `.pre-commit-config.yaml` |

Git hooks run on every commit (lint/format/types), on every commit message, and on
push (tests). Commits straight to `main` are rejected. Work on a branch and open a PR.

## Editor setup

**VS Code** (`.vscode/` is personal and git-ignored): install the Python, Ruff,
Mypy Type Checker, djLint and EditorConfig extensions. Then in workspace settings:

- interpreter: `.venv/bin/python`
- Python formatter: Ruff, format on save, `source.fixAll.ruff` + `source.organizeImports.ruff` on save
- `ruff.importStrategy` / `mypy-type-checker.importStrategy`: `fromEnvironment` (use the locked versions)
- `**/templates/**/*.html` → `django-html`, formatter djLint
- disable Black/isort/flake8/pylint extensions so they don't fight ruff

**PyCharm / WebStorm** (`.idea/` is personal and git-ignored):

1. *Settings → Python Interpreter*: add existing interpreter `.venv/bin/python`.
2. *Settings → Editor → Code Style*: tick **Enable EditorConfig support** (default).
3. Install the **Ruff** plugin, enable "Run ruff when the file is saved" and set
   the executable to `.venv/bin/ruff`. Disable PyCharm's own optimise-imports
   and reformat-on-save so they don't fight ruff.
4. Optional: the **Mypy** plugin pointed at `.venv/bin/mypy`.
5. *Settings → Languages → Python → Django*: enable Django support, settings
   `config/settings.py`.
6. Test runner: *Settings → Tools → Python Integrated Tools → pytest*.
