# Review: project-scaffold
## Verdict: FAIL

Reason: AC3 is not actually proven. Its test only checks that the `data-testid="tagline"` attribute exists, so an empty or deleted tagline would still pass (code-reviewer, medium). No high-severity findings. The suite is green (13 passed), lint and mypy are clean, and coverage is 95.6 %.

## Acceptance criteria
- AC1 — covered by `tests/test_project.py::test_manage_check_passes_with_env_example` — PASS
- AC2 — covered by `apps/core/tests/test_views.py::test_home_page_renders_base_and_home_templates` — PASS
- AC3 — `apps/core/tests/test_views.py::test_home_page_shows_title_and_tagline` passes but doesn't prove the tagline text is there — **NOT PROVEN**
- AC4 — covered by `apps/core/tests/test_views.py::test_base_layout_links_tailwind_stylesheet` — PASS
- AC5 — covered by `tests/test_settings.py::test_missing_secret_key_fails_fast` — PASS
- AC6 — covered by `tests/test_settings.py::test_settings_come_from_environment` — PASS
- AC7 — covered by `tests/test_settings.py::test_settings_defaults_when_unset` — PASS
- AC8 — covered by `tests/test_settings.py::test_tailwind_and_theme_app_installed` — PASS
- AC9 — covered by `tests/test_repo.py::test_build_artifacts_are_gitignored` (3 cases) — PASS
- AC10 — covered by `tests/test_repo.py::test_make_targets_build_tailwind_css` (2 cases); CLAUDE.md checked manually by the code-reviewer and accurate — PASS
- AC11 — `make lint`, `make typecheck`, pytest (13 passed), coverage 95.6 % — PASS

## Findings
Code review:
- [medium] apps/core/tests/test_views.py:15 — The AC3 test checks only for the tagline attribute and checks the heading as two loose substrings. — Assert `<h1>Learning Companion</h1>` (html=True) and check that the tagline element has non-empty text. → plan step 12
- [low] tests/test_project.py, tests/test_repo.py — `subprocess.run` calls have no timeout, so a hang would stall the suite and the post-write hook. — Add `timeout=`. → plan step 13
- [low] config/settings.py:23 — A mistyped explicit `DJANGO_ENV_FILE` is silently skipped, falling back to defaults; relative paths resolve against the working directory. — Raise when an explicitly set file is missing, and resolve relative paths against `BASE_DIR`. → plan step 14
- [low] apps/core/tests/test_views.py:6 — There is a leftover `django_db` mark on a test that doesn't touch the database. tests/test_repo.py — `MAKE` is defined in the middle of the file. — Tidy both. → plan step 15 (refactor)
- [low] pyproject.toml — The djlint `node_modules` exclude from plan step 10 wasn't added. It isn't needed, because djLint excludes it by default. — Record that in plan.md. → plan step 16
- [low] CLAUDE.md:21 — The Node.js minimum version isn't stated. Tailwind v4 needs Node >= 20. — State it. → plan step 16
- [low] CLAUDE.md:57 — `static/` is listed but `STATICFILES_DIRS` isn't set. — Add it when `static/` is created. → follow-up, not in this ticket

Security review (0 high, 0 medium):
- [low] config/settings.py — No production cookie/HTTPS settings (secure cookies, HSTS, SSL redirect). — Make them env-driven and run `check --deploy` before deployment. → follow-up (deployment ticket, #13/#14)
- [low] .env.example:2-3 — `DEBUG=true` and the `change-me` key would be unsafe if copied to a server. — Add a comment on how to generate a key, and/or reject the placeholder when `DEBUG` is False. → follow-up (deployment hardening). AC1 depends on this file passing `check`.
- [low] Makefile:46 — `tailwind install` runs `npm install`, not `npm ci`, so the lockfile isn't strictly enforced. — Use `npm ci` for reproducible installs. → follow-up (CI ticket #14)
- [low] config/urls.py:7 — The admin is at the default `/admin/` path with no login throttling. — Revisit before deployment. → follow-up

## Reviewed
commit d8bba8c, 2026-10-01
