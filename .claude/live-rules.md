# Live rules — CV
# Injected automatically by the live-rules plugin. Global rules fire every prompt;
# scoped rules fire when their files/keywords match. Keep each body tight — all rules
# matching one event share a ~10k-char budget. Anything above the first `---` fence is ignored.
# Edit freely; changes take effect on the next prompt. Commit this file so the team shares it.

---
description: Atomic commits & two hats
priority: 95
---
- One logical, self-contained change per commit; never bundle unrelated changes (a feature, a
  refactor, and a doc fix are three commits). Split by dependency order.
- Two hats: a commit either *adds behavior* (ships with its test) or *refactors*
  (behavior-preserving) — never both in one commit.
- Stage deliberately, per path or per hunk; never blind-add everything at once.
- Commit at each finished, green step. Commit only when asked; don't push unless asked. On the
  default branch, create a working branch first. Never amend published commits, never skip hooks.

---
description: Simple design & small reversible steps (Beck / Fowler)
priority: 90
---
Wear one hat at a time; small reversible steps, re-check between moves. Separate a behavior change
(pin with a test) from a refactor (behavior-preserving) — never fold tidy-up into a behavior change.
Beck's order: 1) passes tests, 2) reveals intention, 3) no duplication, 4) fewest elements (YAGNI).
Ties break toward clarity. Leave each file cleaner than you found it — as its own step.

---
description: Surgical, simple, honest
priority: 90
---
- Think before coding: state assumptions, surface ambiguity, push back on overcomplication. A wrong
  guess costs more than a question — ask instead of silently picking a reading.
- Simplicity first: the minimum code that solves it. No speculative abstractions, no "flexibility"
  nobody asked for, no error handling for impossible states.
- Surgical: every changed line traces to the request. Don't "improve" adjacent code or refactor what
  isn't broken; match the existing style. Remove only the dead code your change created.
- Define "done" and verify it before calling a change finished.

---
description: Verify behavior deterministically
priority: 85
---
- Prove changes by exercising them — a script that asserts, a test, a real run whose output you show —
  not by eyeballing that it "looks right". Round-trip harnesses, diffs, exact-equality checks, counts.
- A change isn't "done" until a deterministic check passes and its output is shown.

---
description: House code conventions
priority: 80
---
- No inline comments unless they capture a real hidden constraint (a *why* the code can't express).
  Lean on naming and structure, not narration. Delete commented-out code.
- Replace magic numbers with named constants. Match the surrounding code's idiom, naming, and
  comment density.

---
description: Commit messages state only what you verified
priority: 87
---
- Every technical claim in a commit message must be something you actually observed or reproduced,
  not a plausible guess. An honest "cause not yet confirmed" beats an invented root cause.
- Describe what changed and why; don't narrate a fix you didn't verify.

---
description: Refactoring discipline (Fowler)
prompt: ["refactor", "refactoring", "clean up", "cleanup", "tidy", "restructure"]
priority: 45
---
Refactoring changes structure, never behavior — and only starts from green (add a characterization
test first if needed). Name the smell, then apply the matching small named move (extract function,
rename, parameter object…), running tests after each. No behavior changes or features folded in —
separate commits. Many tiny safe moves beat one big rewrite.

---
description: Responsibility-driven Python & API design (Metz / Wirfs-Brock / Bloch)
globs: ["**/*.py"]
priority: 50
---
- One clear responsibility per function/class, named for its role (not its data).
- Tell, don't ask; talk to friends, not strangers (Demeter). Guard clauses over deep nesting.
- Metz targets, justify any break: methods ~5 lines, classes ~100, ≤4 params.
- Isolate external deps (the network, the clock, RNG, heavy libs) behind small seams so core logic
  stays pure and testable. Validate at boundaries; prefer immutable value objects.
- Public API is a contract (Bloch): start private, widen only when needed. Log via a real logger,
  never `print()`.

---
description: Python testing discipline
globs: ["**/tests/**", "**/test_*.py", "**/*_test.py", "**/conftest.py"]
priority: 55
---
- Red → Green → Refactor. One behavior per test; Arrange-Act-Assert; name `test_<situation>_<expected>`.
- Add a characterization test before changing untested logic. Tests mirror the source tree.

---
description: Verify framework behavior against docs, not memory
prompt: ["api", "version", "does astro", "does uv", "does pyyaml", "how does", "the docs"]
priority: 70
---
- For a library/framework/CLI whose behavior you're about to assert, verify against context7 (or the
  project's docs) before claiming an API works a certain way — training data lags releases.
- Record durable, verified facts in the codebase map so the next session doesn't re-check.

---
description: Self-improvement — turn friction into a fix that sticks
priority: 40
---
After finishing a chunk of work, take a beat: did you hit friction? Signs — you fumbled the stack or
its tooling, re-derived something that should've been written down, tripped over a missing or unclear
convention, guessed wrong about where code lives, or repeated a workaround. If so, don't just move on:
make that friction cheaper or impossible next time by improving the workspace itself.
- Wrong/missing convention → add or refine a **live rule** (scope it tightly).
- Stale or missing project knowledge → update the **codebase map** (`.claude/.codebase-info/`).
- A repeatable multi-step task you did by hand → propose a **skill** (via skill-creator).
- A durable project fact or decision → into **CLAUDE.md** or a map doc.
Keep it small and incremental — one improvement, not a rewrite. Do it as its own step/commit. If
nothing was off, skip it silently; don't manufacture busywork. For a deeper periodic pass, run `retro`.
