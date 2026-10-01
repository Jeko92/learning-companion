---
name: tdd-implement
description: Execute the approved plan step by step with strict red-green-refactor TDD, committing after each green cycle. Third phase of the development workflow. Use after plan-ticket, when work/<id>/plan.md is approved.
---

# Implement with TDD

## Preconditions

Read `.claude/state/workflow.json`. The phase must be `planned` (fresh start) or `implementing` (resuming, e.g. after review findings). `work/<id>/plan.md` must exist, and the current branch must be `feat/<id>`. If any of these fail, stop and say which one.

On fresh start:

```bash
bash .claude/hooks/set-state.sh phase implementing
```

## The cycle — for each unchecked step in plan.md, in order

1. Record the step: `bash .claude/hooks/set-state.sh current_step "<n>: <summary>"`.
2. **Red.** Write the test for this step's behaviour — nothing else. Run the suite. Confirm it fails on the step's assertion, not on a syntax or import error. The post-write hook records `last_test: red`; that record is expected here.
3. **Green.** Write the minimum production code to pass the test. Run the suite; everything must pass.
4. **Refactor.** Improve names, remove duplication — only while staying green. Skip if there is nothing to improve; do not invent refactorings.
5. **Commit.** `git commit` with message `feat(<id>): <what the step delivers>`. The commit gate re-runs the suite; if it blocks, the suite is not actually green — fix that, never bypass.
6. Tick the step's checkbox in `plan.md` (include it in the commit).

If reality contradicts the plan (a step is impossible or based on a wrong assumption), stop the cycle, explain the conflict to the user, and update `plan.md` first. Do not improvise beyond the plan.

## After the last step

1. Run the full suite and lint one final time.
2. Verify each acceptance criterion in `work/<id>/ticket.md` has a passing test; tick the criteria checkboxes.
3. ```bash
   bash .claude/hooks/set-state.sh phase reviewing current_step ""
   ```
4. Tell the user implementation is complete and the next step is `final-review`.

## Hard limits

- Never write production code without a failing test for it (see `.claude/rules/tdd.md`).
- Never mark a step done with a red suite; the Stop hook will hold the session open on red.
- Do not push; pushing is gated on the review.
