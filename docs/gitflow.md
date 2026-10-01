# Gitflow

Branching and merging rules for this project. Two long-lived branches, short-lived ticket branches that are kept forever, squash merges at both levels.

```
main       ◄── squash-merged PR from develop only ("chore(release): ...")
  │  ▲
  │  └── release PR (squash)
  ▼  │
develop    ◄── squash-merged PR per ticket ("feat(<id>): <title> (#n)")
  │  ▲        ◄── merge-commit PR from main right after each release (back-sync)
  │  └── ticket PR (squash)
  ▼  │
feat/<id> | fix/<id>   every TDD commit lives here; never deleted, never force-pushed
```

## Branches

| Branch      | Purpose                               | Created from     | Receives changes via                                 | Deleted |
|-------------|---------------------------------------|------------------|------------------------------------------------------|---------|
| `main`      | Released state                        | —                | PR from `develop` only, **squash**                   | never   |
| `develop`   | Integration branch, default branch    | `main` (once)    | PR from `feat/*` / `fix/*`, **squash**; back-sync PR from `main`, **merge commit** | never   |
| `feat/<id>` | New behaviour for ticket `<id>`        | latest `develop` | direct commits (one per green TDD cycle)             | only with explicit permission |
| `fix/<id>`  | Bug fix for ticket `<id>`              | latest `develop` | direct commits (one per green TDD cycle)             | only with explicit permission |

`<id>` is the kebab-case ticket id from `work/<id>/`. Use `feat/` when the ticket adds or changes behaviour, `fix/` when it corrects a defect. The prefix matches the Conventional Commit type of the branch's commits (`feat(<id>): ...` / `fix(<id>): ...`).

## Rules

1. **No direct commits or pushes to `main` or `develop`.** They change only through merged PRs.
2. **`main` accepts PRs from `develop` only.** No ticket branch is ever merged into `main` directly, including urgent fixes. A production fix is a `fix/<id>` branch into `develop`, followed by a release.
3. **Ticket PRs into `develop` are always squash-merged.** One ticket = one commit on `develop`. The squash commit title is the PR title, so the PR title must be a Conventional Commit: `feat(<id>): <title>` or `fix(<id>): <title>`.
4. **Individual commits stay on the ticket branch.** That branch is the audit trail of the TDD cycle; `develop` and `main` only carry the squashed result.
5. **Never delete a ticket branch** — not locally (`git branch -d/-D`), not remotely (`git push --delete`, `git push origin :<branch>`), not on merge (`gh pr merge --delete-branch` / `-d`, the GitHub "Delete branch" button). Deletion needs explicit permission from the repo owner for that specific branch.
6. **Never rewrite pushed history** on any branch: no `git push --force` / `--force-with-lease`, no rebase or amend of pushed commits. To bring a ticket branch up to date with `develop`, merge `develop` into it.
7. **Never reuse a ticket branch after its PR is merged.** Its commits are not ancestors of `develop` (squash), so continuing on it replays already-merged changes. Follow-up work gets a new branch from the latest `develop`, e.g. `fix/<id>-followup`.
8. **Every release is followed by a back-sync** (`main` → `develop`, merge commit). Squashing `develop` into `main` creates a commit that `develop` doesn't contain; without the back-sync, the next release PR shows already-released changes again and conflicts on any line touched twice.

## Ticket lifecycle

```bash
# 1. Start from the latest develop
git switch develop
git pull --ff-only
git switch -c feat/<id>            # or fix/<id>

# 2. Work: one commit per green TDD cycle
git commit -m "feat(<id>): <what the step delivers>"

# 2a. (only if develop moved and you need its changes) merge, don't rebase
git fetch origin
git merge origin/develop

# 3. Publish and open the PR against develop
git push -u origin feat/<id>
gh pr create --base develop --head feat/<id> \
  --title "feat(<id>): <title>" \
  --body "<story, acceptance criteria, reference to work/<id>/review.md>"

# 4. Merge: squash, keep the branch
gh pr merge <pr-number> --squash    # never add --delete-branch / -d

# 5. Back to develop for the next ticket
git switch develop
git pull --ff-only
```

After step 4 the ticket branch stays on the remote and locally, with every individual commit visible on GitHub under the PR's "Commits" tab and on the branch itself.

## Release (develop → main)

```bash
# 1. Release PR, squash-merged
gh pr create --base main --head develop \
  --title "chore(release): <version or date>" \
  --body "<list of ticket PRs since the last release>"
gh pr merge <pr-number> --squash

# 2. Immediately back-sync main into develop — MERGE COMMIT, never squash
gh pr create --base develop --head main \
  --title "chore: sync main into develop after <version or date>" \
  --body "Back-sync after release; makes the release squash commit an ancestor of develop."
gh pr merge <pr-number> --merge

# 3. Optional: tag the release on main
git fetch origin
git tag -a v<x.y.z> origin/main -m "<version>"
git push origin v<x.y.z>
```

The back-sync changes no files (the release commit's tree already equals `develop`), it only joins the histories. Do it before the next ticket PR lands in `develop`.

## Deleting a branch (exception)

Only after the repo owner has explicitly approved deleting that specific branch:

```bash
git branch -D feat/<id>                  # local
git push origin --delete feat/<id>       # remote (needs ruleset bypass, see below)
```

Note the approval (who, when, why) in the PR conversation of that branch.

## Server-side enforcement (GitHub)

Local discipline is not enough; GitHub enforces the rules via repository settings, three rulesets and one required check.

| Setting                         | Value                                                      |
|---------------------------------|------------------------------------------------------------|
| Default branch                  | `develop` (PRs target it unless told otherwise)            |
| Allowed merge methods (repo)    | squash, merge commit; rebase off                           |
| Automatically delete head branches | **off**                                                 |
| Squash commit message           | PR title + PR body                                         |

| Ruleset    | Targets                     | Rules                                                                                     | Bypass        |
|------------|-----------------------------|-------------------------------------------------------------------------------------------|---------------|
| `main`     | `main`                      | block deletion, block force-push, require PR (squash only), require check `source-branch` | none          |
| `develop`  | `develop`                   | block deletion, block force-push, require PR (squash + merge), require check `source-branch` | none       |
| `tickets`  | `feat/**`, `fix/**`         | block deletion, block force-push                                                          | repo admins (for approved deletions) |

The `source-branch` check (GitHub Action `.github/workflows/pr-source-branch.yml`) fails a PR whose head is not allowed for its base:

| Base      | Allowed heads                 |
|-----------|-------------------------------|
| `main`    | `develop`                     |
| `develop` | `feat/*`, `fix/*`, `main` (back-sync) |

GitHub can't restrict the merge method per source branch, so `develop` allows both squash and merge commit. The convention is strict: **ticket PRs squash, the back-sync PR merges**.

Rulesets on **private** repositories require GitHub Pro/Team; on the free plan they only work on public repositories. `required_approving_review_count` is `0` for a solo project — raise it when the team grows.

## One-time setup script

The repo has no commits and no remote yet. Review the script below, save it to a temporary file (e.g. `/tmp/setup-gitflow.sh`), and run it **yourself in a normal terminal** from the project root:

```bash
bash /tmp/setup-gitflow.sh <owner>/<repo> [private|public]
```

It is not meant to be run by Claude: the workflow hooks block commits and pushes in phase `idle`, and the initial commit on `main` deliberately skips pre-commit's `no-commit-to-branch` once. Before running, stage exactly what the initial commit should contain (`git status`); the script adds only the files it creates.

```bash
#!/usr/bin/env bash
# One-time gitflow bootstrap: initial commit, develop branch, GitHub repo,
# repo settings, rulesets, and the source-branch check. See docs/gitflow.md.
set -euo pipefail

REPO="${1:?usage: setup-gitflow.sh <owner>/<repo> [private|public]}"
VISIBILITY="${2:-private}"

[ "$(git symbolic-ref --short HEAD)" = "main" ] || { echo "✗ run this on main"; exit 1; }
git rev-parse --verify --quiet HEAD >/dev/null && { echo "✗ main already has commits; do the remaining steps by hand"; exit 1; }

# --- 1. Required check: PR head must be allowed for its base ----------------
mkdir -p .github/workflows
cat > .github/workflows/pr-source-branch.yml <<'YAML'
# Enforces docs/gitflow.md: main only from develop; develop only from
# feat/*, fix/* and the main back-sync. Required check on both branches.
name: pr-source-branch
on:
  pull_request:
    types: [opened, edited, reopened, synchronize]
    branches: [main, develop]
jobs:
  source-branch:
    name: source-branch
    runs-on: ubuntu-latest
    steps:
      - name: Check head branch is allowed for this base
        env:
          BASE: ${{ github.base_ref }}
          HEAD: ${{ github.head_ref }}
        run: |
          case "$BASE:$HEAD" in
            main:develop) ;;
            develop:feat/*|develop:fix/*|develop:main) ;;
            *) echo "::error::PRs into '$BASE' may not come from '$HEAD'. See docs/gitflow.md."; exit 1 ;;
          esac
YAML

# --- 2. Initial commit on main, then develop --------------------------------
git add .github/workflows/pr-source-branch.yml docs/gitflow.md
SKIP=no-commit-to-branch git commit -m "chore: initial project setup"
git branch develop

# --- 3. GitHub repo, push both long-lived branches ---------------------------
gh repo create "$REPO" "--$VISIBILITY" --source=. --remote=origin
git push -u origin main develop

# --- 4. Repo settings --------------------------------------------------------
gh api -X PATCH "repos/$REPO" \
  -F allow_squash_merge=true -F allow_merge_commit=true -F allow_rebase_merge=false \
  -F delete_branch_on_merge=false \
  -f squash_merge_commit_title=PR_TITLE -f squash_merge_commit_message=PR_BODY \
  -f merge_commit_title=PR_TITLE -f merge_commit_message=PR_BODY \
  -f default_branch=develop >/dev/null

# --- 5. Rulesets -------------------------------------------------------------
ruleset() { gh api -X POST "repos/$REPO/rulesets" --input - >/dev/null; }

ruleset <<'JSON'
{
  "name": "main",
  "target": "branch",
  "enforcement": "active",
  "conditions": { "ref_name": { "include": ["refs/heads/main"], "exclude": [] } },
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    { "type": "pull_request", "parameters": {
        "required_approving_review_count": 0,
        "dismiss_stale_reviews_on_push": false,
        "require_code_owner_review": false,
        "require_last_push_approval": false,
        "required_review_thread_resolution": false,
        "allowed_merge_methods": ["squash"] } },
    { "type": "required_status_checks", "parameters": {
        "strict_required_status_checks_policy": false,
        "required_status_checks": [{ "context": "source-branch" }] } }
  ]
}
JSON

ruleset <<'JSON'
{
  "name": "develop",
  "target": "branch",
  "enforcement": "active",
  "conditions": { "ref_name": { "include": ["refs/heads/develop"], "exclude": [] } },
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    { "type": "pull_request", "parameters": {
        "required_approving_review_count": 0,
        "dismiss_stale_reviews_on_push": false,
        "require_code_owner_review": false,
        "require_last_push_approval": false,
        "required_review_thread_resolution": false,
        "allowed_merge_methods": ["squash", "merge"] } },
    { "type": "required_status_checks", "parameters": {
        "strict_required_status_checks_policy": false,
        "required_status_checks": [{ "context": "source-branch" }] } }
  ]
}
JSON

# Repository role 5 = admin: the only actor allowed to delete a ticket branch.
ruleset <<'JSON'
{
  "name": "tickets",
  "target": "branch",
  "enforcement": "active",
  "conditions": { "ref_name": { "include": ["refs/heads/feat/**", "refs/heads/fix/**"], "exclude": [] } },
  "bypass_actors": [{ "actor_id": 5, "actor_type": "RepositoryRole", "bypass_mode": "always" }],
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" }
  ]
}
JSON

git switch develop
echo "✓ gitflow set up: default branch develop, rulesets main/develop/tickets active"
```

## Not yet aligned with the Claude workflow

The `.claude/` pipeline still assumes `main` as the integration branch. Until it is updated, these parts contradict this document:

| File                                   | Currently                                                 | Needs to become                                              |
|----------------------------------------|-----------------------------------------------------------|--------------------------------------------------------------|
| `.claude/rules/git.md`                 | feature branches `feat/<id>` targeting `main`             | this document's rules                                        |
| `.claude/hooks/config.sh`              | `PROTECTED_BRANCHES="main\|master"`                       | add `develop`                                                |
| `.claude/hooks/guard-bash.sh`          | blocks force-push only to protected branches; no deletion guard | block force-push everywhere; block `git branch -d/-D`, `git push --delete`, `git push origin :<b>`, `gh pr merge -d/--delete-branch`; block `gh pr create --base main` unless head is `develop` |
| `.claude/skills/refine-ticket`         | `git switch -c feat/<id>` from the current branch         | `git switch develop && git pull --ff-only`, then `feat/<id>` or `fix/<id>` |
| `.claude/skills/tdd-implement`         | precondition: branch is `feat/<id>`                       | `feat/<id>` or `fix/<id>`                                    |
| `.claude/skills/final-review`          | `git diff main...HEAD`, `gh pr create --base main`        | `develop...HEAD`, `--base develop`, PR title as Conventional Commit |
| `.claude/skills/factory-manager`       | close-out switches to `main`                              | switch to `develop` and `git pull --ff-only`                 |
| `.pre-commit-config.yaml`              | `no-commit-to-branch --branch main`                       | also `--branch develop`                                      |
| `docs/ai-factory-workflow.md`          | describes the `main`-based flow                           | reference this document                                      |

Unrelated but found on the way: `config.sh` sets `TEST_CMD="npm test --silent"`, and every test gate is skipped when there's no `package.json`. In this Python/Django project the "commit only on green" gates therefore never run; `TEST_CMD` should be `make test` (or `.venv/bin/python -m pytest -q`) with the `package.json` checks removed.
