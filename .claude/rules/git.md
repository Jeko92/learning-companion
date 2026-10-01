# Git conventions

Branching follows `docs/gitflow.md`. `main` is the default branch and holds the released state. `develop` is the integration branch.

- All work happens on a ticket branch `feat/<ticket-id>` (or `fix/<ticket-id>` for a defect). The `refine-ticket` skill creates it from the latest `develop`. Never commit to `main`, `master` or `develop` (enforced by a hook); they change only through merged PRs.
- Commit messages follow Conventional Commits as configured in `.conventionalcommit.json`: `feat(<ticket-id>): <what the step delivers>` for plan steps, `docs(<ticket-id>): ...` for workflow artifacts, `refactor(<ticket-id>): ...` for pure refactoring commits.
- Commit after every green TDD cycle. Small commits are the audit trail of the workflow; do not batch several steps into one commit.
- Commits require a green test suite and `--no-verify` is forbidden (both enforced by a hook).
- Pushing is only possible once the final review has passed (phase `done`, enforced by a hook). Open the ticket PR with `gh pr create --base develop`. Its title is the squash commit subject, so it must be `feat(<ticket-id>): <title>`. The body holds the ticket summary and a link-style reference to `work/<id>/review.md`.
- **Claude never merges PRs.** Teammates review and merge them:
  - ticket PR into `develop`: squash
  - release PR `develop` → `main`: squash, title `chore: release <YYYY-MM-DD>`
  - back-sync PR `main` → `develop`: merge commit, with the PR title `chore: sync main into develop after release <YYYY-MM-DD>` as the commit subject

  `factory-manager` opens the release and back-sync PRs and pauses at each one.
- Never rewrite history on a protected branch. Never delete a ticket branch.
