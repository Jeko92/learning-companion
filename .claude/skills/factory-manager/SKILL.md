---
name: factory-manager
description: Inspects the ticket backlog and the current workflow phase, then triggers the one pipeline skill (refine-ticket, plan-ticket, tdd-implement, or final-review) that owns the next step. Picks the next queued ticket when idle or done. Advances the pipeline by exactly one step per call and reports cleanly, so it is safe to invoke repeatedly, including from a loop. Use when the user wants the AI factory to keep moving without manually tracking phase and ticket state themselves.
---

# Manage the AI factory

Orchestrates the pipeline defined in `.claude/rules/workflow.md`. This skill never changes `phase` itself, never writes source code, and never invokes more than one phase skill per call — it only reads state, decides which phase skill owns the next step, and triggers it with the `Skill` tool. All actual work and every phase transition still happens inside `refine-ticket`, `plan-ticket`, `tdd-implement`, and `final-review`.

## Preconditions

1. Read `.claude/state/workflow.json`. It may not exist yet — treat a missing file or a missing `phase` key as phase `idle`, exactly like `lib.sh:current_phase` does. Note `ticket` the same way (missing = none).
2. Read `work/backlog.md`. If it doesn't exist, create it with just this header, then stop this call and report that the backlog is empty and needs entries:

   ```markdown
   # Ticket backlog

   Queue for `factory-manager`. One idea per line, top to bottom = priority order.
   `factory-manager` owns the status marker, the ticket id, and the `[[parked: ...]]`
   annotation on each line — add new ideas as plain `- [ ] <description>` lines and
   leave the rest alone.
   ```

## Steps

Do exactly one of the following, then stop and report (step 5). Never chain two phase skills in one call — one call is one observable pipeline step.

1. **Idempotence check.** If `ticket` is set, find its line in `work/backlog.md`. If that line carries `[[parked: <skill> @ <phase>]]` and `<phase>` equals the *current* phase, the last call already triggered `<skill>` at this phase and it stopped to ask a human something, and nothing has moved since. Do not re-invoke it — go straight to step 5 and report that it is still waiting. Otherwise (no tag, or the tag's phase no longer matches — meaning progress happened since) continue normally and discard any stale tag when you next touch that line.

2. **Dispatch on phase:**

   | phase | action |
   |---|---|
   | `idle` or `done` | Close-out + selection, below. |
   | `refined` | Invoke `plan-ticket`. |
   | `planned` | Invoke `tdd-implement`. |
   | `implementing` | Invoke `tdd-implement` (it resumes from the plan itself). |
   | `reviewing` | Invoke `final-review`. |

3. **`idle`/`done` — close-out.** Only when `phase` is `done` and `ticket` is set: mark that ticket's backlog line `[x]` and append a reference to `work/<ticket>/review.md`. Then, before touching branches: run `git status`; if the tree isn't clean, stop and report it (final-review should have left it clean — don't paper over that). Then `git switch main` (fall back to `git switch master` if `main` doesn't exist) — `refine-ticket` will otherwise branch the next ticket off the just-finished one. `phase` starting as `idle` needs no close-out.

4. **`idle`/`done` — selection.** Read the backlog top to bottom and pick the first `[ ]` line, skipping any whose description names a dependency that's still open (e.g. "after X ships") — log a skip like that rather than guessing an order, and ask the user only if two candidates are genuinely ambiguous in priority. If no eligible `[ ]` line exists, report **"Backlog is empty — nothing to do"** and stop; that's the signal for a wrapping loop to stop too.

   Invoke `refine-ticket` with the picked line's description text as its argument. Afterwards, re-read `.claude/state/workflow.json` for the derived ticket id:
   - If `phase` is now `refined`, rewrite the line from `- [ ] <description>` to `- [~] <id>: <description>`.
   - If `phase` is still `idle`/unchanged, `refine-ticket` stopped mid-interview (or asked for ticket-id confirmation) — leave the line as `- [ ]` but add `[[parked: refine-ticket @ idle]]` so the next call doesn't restart the interview from scratch.

5. **Report.** One short summary: phase before → phase after, the ticket id, and the artifact that changed (or the backlog line, for a close-out/selection). If the invoked skill stopped to ask the user something — ticket interview, ticket-id confirmation, plan approval — say exactly that instead of answering on its behalf; a human needs to be present for that turn, and this skill does not fabricate approval to keep a loop moving.

## Hard limits

- Never call `.claude/hooks/set-state.sh`; only the phase skill that owns a transition may change `phase` or `ticket`.
- Never invoke more than one phase skill per call.
- Never fabricate or infer the user's approval of a ticket or plan.
- Never write source code from this skill (the write-protection hook would block it outside `implementing` anyway); it only ever delegates.
- Never reorder or delete backlog lines beyond updating a line's own status marker, ticket id, and `[[parked: ...]]` tag.
- Don't try to commit backlog edits made while `phase` is `idle` — `guard-bash.sh` blocks commits in that phase; leave the edit uncommitted, the next phase skill's own commit will pick it up.
