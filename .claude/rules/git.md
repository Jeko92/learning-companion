# Git conventions

- All work happens on a feature branch named `feat/<ticket-id>`, created by the `refine-ticket` skill. Never commit to `main` or `master` (enforced by a hook).
- Commit messages follow Conventional Commits: `feat(<ticket-id>): <what the step delivers>` for plan steps, `docs(<ticket-id>): ...` for workflow artifacts, `refactor(<ticket-id>): ...` for pure refactoring commits.
- Commit after every green TDD cycle. Small commits are the audit trail of the workflow; do not batch several steps into one commit.
- Commits require a green test suite and `--no-verify` is forbidden (both enforced by a hook).
- Pushing is only possible once the final review has passed (phase `done`, enforced by a hook). Open the PR with `gh pr create`, targeting `main`, with the ticket summary and a link-style reference to `work/<id>/review.md` in the body.
- Never rewrite history on a protected branch.
