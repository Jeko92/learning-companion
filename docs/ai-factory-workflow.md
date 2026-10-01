# Claude Code development workflow template

A drop-in `.claude` setup that turns Claude Code into a process-controlled development pipeline: refine a ticket, plan against the codebase, implement with strict TDD, and pass an independent review before anything gets pushed. It applies the [ai-factory](../ai-factory.md) patterns to a single feature: pipeline stages with named artifacts, research fan-out with sub-agents, and a verification gate before the work leaves the machine.

## Division of labour

Three mechanisms, three responsibilities:

- **Skills** own the phases. Each phase is a skill (`refine-ticket`, `plan-ticket`, `tdd-implement`, `final-review`) that consumes the previous phase's artifact, produces its own, and performs the state transition. Skills are the only place the workflow state changes.
- **Rules** own the discipline. `.claude/rules` states what always applies — phase order, red–green–refactor, git conventions — so the model behaves correctly even between skill invocations.
- **Hooks** own enforcement. Rules and skills are instructions; a model can drift from instructions. Hooks are shell scripts, so the gates hold deterministically: no source edits outside the implementing phase, no commits on red or on `main`, no push before the review passed, no ending the session mid-cycle on a red suite.

Sub-agents appear in two places, mirroring the factory patterns: `plan-ticket` fans research out across parallel `Explore` agents (pipeline stage 1), and `final-review` runs two read-only reviewer agents with different lenses (verification gate).

## The pipeline

```
idle ──refine-ticket──► refined ──plan-ticket──► planned ──tdd-implement──► implementing
                        ticket.md                plan.md                    green commits
                                                                                 │ all steps done
        done ◄──PASS── reviewing ◄───────────────────────────────────────────────┘
        push + PR      review.md ──FAIL──► implementing (findings become plan steps)
```

The current phase lives in `../.claude/state/workflow.json`. A `UserPromptSubmit` hook injects it into every prompt, so the session always knows where it is — even a fresh session resumes the workflow correctly, because each phase starts from a file, not from conversation history.

## What each hook does

| Event | Script | Gate |
|---|---|---|
| `UserPromptSubmit` | `inject-state.sh` | Injects phase/ticket/branch into context every turn |
| `PreToolUse` on Write/Edit | `guard-write.sh` | Blocks source-code writes unless phase is `implementing`; `work/`, `.claude`, and markdown stay writable |
| `PreToolUse` on Bash | `guard-bash.sh` | Blocks commits on protected branches, on red tests, with `--no-verify`, and in phase `idle`; blocks push unless phase is `done`; blocks force-push to protected branches |
| `PostToolUse` on Write/Edit | `post-write.sh` | Logs every write to `work/<id>/activity.log`; during `implementing` runs the suite and records `last_test: red|green` — the evidence for each TDD cycle |
| `Stop` | `on-stop.sh` | Refuses to end the turn while `implementing` with a red suite |

Blocked calls exit with code 2; the stderr message tells Claude which phase it is in and which skill to run instead, so a blocked action self-corrects instead of dead-ending.

## Install

1. Copy `.claude` into the root of your project (merge with an existing `.claude` if you have one).
2. Adjust `.claude/hooks/config.sh`: test command, lint command, source directories, protected branches. If your suite is slow, set `RUN_TESTS_ON_WRITE="false"` — tests are then enforced at commit time only.
3. Requirements: `bash`, `jq`, `git`, and `gh` for the PR step.
4. Start a session and check the setup with any prompt — you should see the `[workflow] ... phase: idle` context line.

## A run in practice

```
> use refine-ticket: users should be able to comment on posts
  → interview, work/comments-endpoint/ticket.md, branch feat/comments-endpoint, phase refined
> use plan-ticket
  → 3 Explore agents research patterns/tests/data layer in parallel
  → work/comments-endpoint/plan.md with one TDD step per acceptance criterion, phase planned
> use tdd-implement
  → per step: failing test (hook records red) → minimal code (green) → refactor → commit
  → phase reviewing when the last step is ticked
> use final-review
  → code-reviewer + security-reviewer agents in parallel, AC check, review.md
  → PASS: phase done, push, gh pr create   |   FAIL: findings become plan steps, back to tdd-implement
```

Try to misbehave and the hooks answer: editing `src/` in phase `refined` is blocked, `git commit` with a failing test is blocked, `git push` before the review is blocked.

## Running several tickets unattended: `factory-manager`

The four phase skills above are meant to be driven by hand, one at a time. `factory-manager` is a meta-skill that sits on top of them: it reads the current phase and a ticket backlog, then triggers whichever phase skill owns the next step. It never sets `phase` itself and never touches source code — it only decides and delegates.

### The backlog

Ticket ideas live in `work/backlog.md`, one per line, top to bottom in priority order:

```markdown
- [ ] <one-line ticket idea>
- [~] <id>: <one-line ticket idea>      <!-- in progress -->
- [x] <id>: <one-line ticket idea>      <!-- done, see work/<id>/review.md -->
```

`factory-manager` creates this file on first use if it doesn't exist. Add new ideas as plain `- [ ] <description>` lines; it owns the status marker, the ticket id, and any `[[parked: ...]]` annotation, so leave those alone.

### What one call does

Each invocation advances the pipeline by exactly one step and then stops:

| phase | action |
|---|---|
| `idle` / `done` | close out the finished ticket (if any), switch back to `main`, pick the next `[ ]` backlog line, trigger `refine-ticket` |
| `refined` | trigger `plan-ticket` |
| `planned` | trigger `tdd-implement` |
| `implementing` | trigger `tdd-implement` (resumes) |
| `reviewing` | trigger `final-review` |

### Running it in a loop

Because each call is one bounded, observable step, `factory-manager` is safe to run repeatedly — e.g. with `/loop factory-manager`. Two things it deliberately will not do for you:

- **It will not approve anything on your behalf.** If `refine-ticket` or `plan-ticket` stops to ask a question (interview answers, acceptance-criteria or plan approval), `factory-manager` reports that and stops too, tagging the backlog line `[[parked: <skill> @ <phase>]]` so the next call doesn't blindly re-run the interview or rewrite the plan. A human still has to answer before the loop can move that ticket forward.
- **It treats an empty backlog as "done."** Once there's no `[ ]` line left to pick, it reports that and stops — the cue to end the loop rather than spin.

## Extension ideas

- Tighten the TDD gate: block production-code writes when the last recorded suite run was already green and no test file changed since (true test-first enforcement, not just test-before-commit).
- Add a `PostToolUse` hook on `Bash` matching `gh pr create` that posts the review verdict as a PR comment.
- Swap the state file for your ticket system via an MCP server, so `refine-ticket` pulls the ticket and `final-review` closes it.
