# Development workflow

All feature work in this project follows a fixed pipeline. Each phase is a skill, each phase produces an artifact in `work/<ticket-id>/`, and hooks enforce the gates. The current phase lives in `.claude/state/workflow.json` and is injected into every prompt.

| Phase          | Skill          | Artifact                    | Exit condition                          |
|----------------|----------------|-----------------------------|------------------------------------------|
| `idle`         | —              | —                           | User brings a ticket                     |
| `refined`      | `refine-ticket`| `work/<id>/ticket.md`       | User approves acceptance criteria        |
| `planned`      | `plan-ticket`  | `work/<id>/plan.md`         | User approves the plan                   |
| `implementing` | `tdd-implement`| green commits, ticked plan  | All plan steps done, suite green         |
| `reviewing`    | `final-review` | `work/<id>/review.md`       | Verdict PASS                             |
| `done`         | —              | pushed branch, PR           | —                                        |

Rules that always apply:

- Never skip a phase and never set the phase yourself outside of the skill that owns the transition. Phases are changed only via `bash .claude/hooks/set-state.sh`, exactly where a skill says so.
- Source code is write-protected outside the `implementing` phase (enforced by a hook). If a write is blocked, do not work around it — you are in the wrong phase.
- Each phase works from the previous phase's artifact, not from the conversation. If `plan.md` is missing context, fix `plan.md`, don't improvise.
- Review findings are not fixed during review. They become new steps in `plan.md` and go back through `tdd-implement`.
- If the user asks for a quick change outside the workflow (typo, config tweak, docs), say so explicitly and ask whether to bypass the workflow for it; markdown and config files are not write-protected.
