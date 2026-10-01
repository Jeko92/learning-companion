# TDD discipline

During the `implementing` phase, every behaviour change follows red–green–refactor:

- Write exactly one failing test before touching production code. Run the suite and confirm it is red for the expected reason (assertion failure, not a syntax or import error).
- Write the minimum production code to make that test pass. Do not implement ahead of the plan step.
- Refactor only on green, and keep the suite green while refactoring.
- Never weaken, skip (`.skip`, `xit`), or delete a test to get to green. If a test turns out to be wrong, say so and fix the test deliberately, as its own step.
- One plan step = one red–green–refactor cycle = one commit.

The post-write hook records the suite result as `last_test: red|green` in the state file after every source write. Use that record: after writing the test you should see red; after implementing you must see green before committing. The Stop hook will not let the session end on red.
