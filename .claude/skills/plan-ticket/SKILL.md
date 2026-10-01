---
name: plan-ticket
description: Produce a TDD implementation plan from a refined ticket. Second phase of the development workflow. Use after refine-ticket, when work/<id>/ticket.md exists and is approved.
---

# Plan the implementation

## Preconditions

Read `.claude/state/workflow.json`. The phase must be `refined` and `work/<id>/ticket.md` must exist. If not, stop and point the user to `refine-ticket`.

## Steps

1. **Research fan-out.** Spawn parallel read-only sub-agents (`Explore`), one per concern, instead of reading the codebase in the main context:
   - existing patterns and conventions in the modules the ticket touches,
   - the test setup: framework, file naming, how existing tests arrange/act/assert, how to run a single test file,
   - data layer / API surface the feature must integrate with.

   Each sub-agent returns a summary; the main session works from the summaries only. This is the pipeline pattern: research produces an artifact, implementation later starts from that artifact with a clean context.
2. Write `work/<id>/plan.md`:

   ```markdown
   # Plan: <id>
   ## Research summary
   Patterns, conventions, test setup — condensed from the sub-agent reports.
   ## Design decisions
   The few choices that matter, each with a one-line rationale.
   ## Steps
   - [ ] 1. <behaviour> — test: `<test file>` — impl: `<files>` — covers: AC1
   - [ ] 2. ...
   ```

   Rules for steps:
   - Each step is one red–green–refactor cycle: one new failing test, minimal code to pass it.
   - Steps are ordered so the suite is green after every step (no step depends on a later one).
   - Every acceptance criterion from `ticket.md` is covered by at least one step; add a coverage line mapping ACs to steps.
3. Present the plan to the user and iterate until they approve it. The plan is the contract for the implementation phase — ambiguity here becomes improvisation later.
4. On approval:

   ```bash
   bash .claude/hooks/set-state.sh phase planned
   git add work/<id>/plan.md && git commit -m "docs(<id>): implementation plan"
   ```

   Tell the user the next step is `tdd-implement`.

## Hard limits

- Do not write or modify source code in this phase (a hook blocks it anyway).
- Do not include code in the plan beyond signatures and file paths; the tests define the behaviour.
