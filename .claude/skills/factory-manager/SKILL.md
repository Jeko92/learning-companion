---
name: factory-manager
description: Inspects the GitHub project board (the ticket queue), the current workflow phase and the ticket's PRs, then takes the one next step. That is either triggering a pipeline skill (refine-ticket, plan-ticket, tdd-implement, final-review) or, after a passed review, moving the ticket through the gitflow merge gates (ticket PR → develop, release PR → main, back-sync), pausing at each one for teammates to merge. Picks the next Todo issue from the board when no ticket is in flight. Advances by exactly one step per call and reports cleanly, so it is safe to invoke repeatedly, including from a loop. Use when the user wants the AI factory to keep moving without manually tracking phase and ticket state themselves.
---

# Manage the AI factory

Orchestrates the pipeline defined in `.claude/rules/workflow.md` and the branching model in `docs/gitflow.md`. This skill never changes `phase` itself, never writes source code, never merges a PR, and never invokes more than one phase skill per call. It only reads state, decides the next step, and either triggers the phase skill that owns it (with the `Skill` tool) or opens the next gitflow PR. Every phase transition still happens inside `refine-ticket`, `plan-ticket`, `tdd-implement` and `final-review`.

## Where tickets come from

The queue is the GitHub Projects (v2) board **"Learning Companion"**, owned by the owner of the `origin` repo (currently project `5` of `Jeko92`, repo `Jeko92/ticket-shop`). The board order of the `Todo` column is the priority order. Each item is an issue whose body has `## Goal`, `## Scope`, `## Draft acceptance criteria`, `## Out of scope`, `## Depends on` (`#N` references, or `–` for none) and a footer `Suggested ticket id: \`<id>\``.

The board's `Status` field is the **shared** state across teammates' machines: `Todo` → `In Progress` (picked up by someone) → `Done` (released to `main`). Never pick up an item that isn't `Todo`; another teammate may be working on it.

`work/untracked/ledger.md` (gitignored) is this machine's **local ledger**. It maps issue numbers to ticket ids and PR numbers, and holds the `[[parked: ...]]` tags. It is not the queue, and it is never committed.

Board commands (resolve owner and number once per call with `gh project list --owner <owner>`, matching the title):

```bash
gh project item-list <num> --owner <owner> --format json --limit 200   # items in board order, with .status and .content.number
gh project field-list <num> --owner <owner> --format json              # Status field id + option ids (Todo / In Progress / Done)
gh project view <num> --owner <owner> --format json -q .id             # project node id
gh project item-edit --project-id <pid> --id <item-id> --field-id <status-field-id> --single-select-option-id <option-id>
gh issue view <N> --json number,title,body,state
```

If `gh project` fails with a missing-scope error, stop and tell the user to run `! gh auth refresh -h github.com -s project`. Do not fall back to guessing the queue.

## Preconditions

1. Read `.claude/state/workflow.json`. It may not exist yet (for example on a teammate's fresh clone). Treat a missing file or a missing `phase` key as phase `idle`, exactly like `lib.sh:current_phase` does. Note `ticket` the same way (missing = none).
2. Read `work/untracked/ledger.md`. If it doesn't exist, create it with just this header:

   ```markdown
   # Ticket ledger (local, gitignored)

   One line per issue this machine picked up, maintained by `factory-manager`:
   `- [~] #<issue> <ticket-id>: <title> [[pr: #n]] [[release: #n]] [[sync: #n]]` while in flight, `[x]` when released.
   ```

3. Load the board items (`gh project item-list`, see above).

## Steps

Do exactly one of the following, then stop and report (step 6). Never chain two steps in one call: one call is one observable pipeline step.

1. **Idempotence check.** Find the in-flight ledger line. That is the line for `ticket` if it is set; otherwise any `[~]` or `[ ]` line with a `[[parked: ...]]` tag. If that line carries `[[parked: <skill> @ <phase>]]` and `<phase>` equals the *current* phase, the last call already triggered `<skill>` at this phase. It stopped to ask a human something and nothing has moved since. Do not re-invoke it; go straight to step 6 and report that it is still waiting (name the issue and what it's waiting for). Otherwise (no tag, or the tag's phase no longer matches, meaning progress happened since) continue normally, and discard any stale tag when you next touch that line.

2. **Dispatch on phase:**

   | phase | action |
   |---|---|
   | `idle` | Selection (step 5). |
   | `refined` | Invoke `plan-ticket`. |
   | `planned` | Invoke `tdd-implement`. |
   | `implementing` | Invoke `tdd-implement` (it resumes from the plan itself). |
   | `reviewing` | Invoke `final-review`. |
   | `done` | If the ticket's ledger line is already `[x]`, do selection (step 5); otherwise do the release gates (step 3). |

   For any non-idle phase, if the invoked skill stops to ask the user something (e.g. plan approval) and the phase didn't move, add `[[parked: <skill> @ <phase>]]` to the ticket's ledger line.

3. **`done` — release gates.** `final-review` has pushed `feat/<ticket>` (or `fix/<ticket>`) and opened the ticket PR into `develop`. Look up the PRs with `gh pr list --state all --json number,state,mergedAt,title,baseRefName,headRefName ...` and record each PR number in the ledger line (`[[pr: #n]]`, `[[release: #n]]`, `[[sync: #n]]`). Take the **first** gate that isn't merged yet:

   | gate | PR | if missing | if open | if merged |
   |---|---|---|---|---|
   | a. ticket | `feat/<ticket>` → `develop` | Report an error and stop (`final-review` should have opened it). | **Pause:** teammates review and squash-merge it, keeping the PR title as the commit subject. | Next gate. |
   | b. release | `develop` → `main` | Open it (below), then **pause**. | **Pause:** teammates review and squash-merge it. | Next gate. |
   | c. back-sync | `main` → `develop` | Open it (below), then **pause**. | **Pause:** teammates merge it with a **merge commit**. | Close-out (step 4). |

   A PR that was closed without merging means a human stopped the flow. Report it and stop; never reopen or recreate it on your own.

   Release PR (only once the ticket PR is merged; if an open `develop` → `main` PR already exists, reuse it instead of opening a second one):

   ```bash
   gh pr create --base main --head develop \
     --title "chore: release <YYYY-MM-DD>" \
     --body "<ticket PRs since the last release, one line each: feat(<id>): <title> (#n)>

   Closes #<issue>

   Merge: **Squash and merge**, keep the PR title as the commit subject."
   ```

   `Closes #<issue>` belongs here, not on the ticket PR, because `main` is the default branch: GitHub only closes issues for PRs merged into it.

   Back-sync PR (only once the release PR is merged). The commit it produces lands on `develop`, so its subject must be a Conventional Commit per `.conventionalcommit.json`. GitHub's default merge-commit subject ("Merge pull request #n from …") is not, so the body tells the merger which subject to use:

   ```bash
   gh pr create --base develop --head main \
     --title "chore: sync main into develop after release <YYYY-MM-DD>" \
     --body "Back-sync after release #<release-pr>; makes the release squash commit an ancestor of develop. Changes no files.

   Merge: **Create a merge commit** (not squash), with the PR title as the commit subject:
   gh pr merge <n> --merge --subject \"chore: sync main into develop after release <YYYY-MM-DD>\""
   ```

   **Pause** means: report which PR is waiting and what the merger must do, then end this call with the stop signal (step 6). Teammates merge on GitHub; the next `/loop factory-manager` run picks up from the merged state.

4. **`done` — close-out** (all three gates merged):
   - Mark the ledger line `[x]` and append a reference to `work/<ticket>/review.md`.
   - Set the issue's board `Status` to `Done`. Check that the release PR closed the issue (`gh issue view <N> --json state`). If it is still open, report that rather than closing it yourself.
   - Run `git status`. If the tree isn't clean, stop and report it; don't paper over it. Then `git switch develop && git pull --ff-only`, and `git fetch origin main`.
   - **Stop the factory** (stop signal, step 6). The feature is now on `main` and `develop`. Teammates approve the released state, pull it, and pick up the next ticket on their own machines. Do not select the next ticket in this call, and tell the wrapping loop to stop. Whoever runs `factory-manager` next starts at selection.

5. **Selection** (phase `idle`, or `done` with the ticket's ledger line already `[x]`):
   - Check that the local `develop` is up to date (`git fetch origin develop`). If an earlier ticket's PRs are still open on GitHub (any open PR into `develop` from `feat/*` or `fix/*`, or an open release or back-sync PR), report that the previous release isn't finished and stop.
   - Walk the board items in board order. Pick the first one whose `Status` is `Todo` and whose issue is open. Skip any whose `## Depends on` section lists an issue that is not yet `Done` on the board (or closed), and log each skip by issue number rather than guessing another order. If nothing is eligible, report **"Backlog is empty — nothing to do"** (or, if Todo items exist but all are blocked, say which dependencies block them) and stop; that is also the stop signal for a wrapping loop.
   - Before invoking: set the picked item's board `Status` to `In Progress` and add a ledger line `- [ ] #<issue> <suggested-id>: <title>`.
   - Invoke `refine-ticket` with this argument: `GitHub issue #<issue> — <title>. Suggested ticket id: <suggested-id>.` followed by the full issue body (the draft ACs are interview input, not final). Afterwards, re-read `.claude/state/workflow.json` for the derived ticket id:
     - If `phase` is now `refined`, rewrite the line to `- [~] #<issue> <id>: <title>`, using the id `refine-ticket` actually chose.
     - If `phase` is unchanged, `refine-ticket` stopped mid-interview (or asked for ticket-id confirmation). Leave the line as `- [ ]` but add `[[parked: refine-ticket @ <phase>]]`, so the next call doesn't restart the interview from scratch.

6. **Report.** Give one short summary: the phase before → after, the issue number and ticket id, and what changed (artifact, PR opened, ledger line or board status). If the invoked skill stopped to ask the user something (ticket interview, ticket-id confirmation, plan approval), say exactly that instead of answering on its behalf. A human needs to be present for that turn, and this skill does not fabricate approval to keep a loop moving.

   **Stop signal.** For a pause at a merge gate, after close-out, or for an empty or blocked backlog, start the report with **"Factory paused — waiting for teammates"** (or **"Factory stopped"** after close-out or with an empty backlog) and name the exact human action needed. A wrapping `/loop` must stop on this signal instead of scheduling another tick.

## Hard limits

- Never call `.claude/hooks/set-state.sh`; only the phase skill that owns a transition may change `phase` or `ticket`.
- Never invoke more than one phase skill per call, and never open more than one PR per call.
- Never merge, close, reopen or approve a PR, and never push to `main` or `develop`. Teammates merge.
- Never fabricate or infer the user's approval of a ticket or plan.
- Never write source code from this skill (the write-protection hook would block it outside `implementing` anyway); it only ever delegates.
- On the board, only change the `Status` of the item being picked up or closed out. Never reorder, edit, close or create issues or board items.
- Never reorder or delete ledger lines beyond updating a line's own status marker, ticket id, PR tags and `[[parked: ...]]` tag.
