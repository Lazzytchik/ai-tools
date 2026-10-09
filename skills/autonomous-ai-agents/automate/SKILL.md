---
name: automate
description: "Use for autonomous software delivery after spec approval."
---

# Automate

Turn an end goal into an approved specification and a working, empirically verified result. Not for tiny edits, Q&A, or plan-only requests. Load `orchestrate`; inherit its delegation, model-routing, writer-isolation, and evidence rules rather than duplicating them.

## 1. Discover
Delegate scoped investigation of the repository, product behavior, architecture, constraints, risks, and feasibility. Maintain a short `todo` plan. Resolve material unknowns from evidence; ask the user only for consequential choices that cannot be inferred safely. Workers return questions with recommended defaults to the orchestrator, never block directly on the user.

## 2. Specify and obtain approval
Synthesize a compact, executable spec: goal/non-goals, resolved decisions and assumptions, target behavior/contracts, implementation blocks, acceptance criteria, empirical validation, and safety/rollback where relevant. No TBDs or deferred user decisions.

Present the spec and wait for explicit approval **before implementation**. Incorporate corrections and repeat; investigate new unknowns before re-presenting. After approval, resolve routine details from the spec/evidence; escalate only genuinely new consequential decisions or unapproved side effects.

## 3. Execute and challenge
Delegate implementation in bounded blocks with non-overlapping writers. Require changed files, commands/results, risks, and next steps. Adapt the plan from feedback.

After every block:
1. Independent skeptics attack spec compliance, runtime behavior, regressions, and relevant edge/security cases.
2. Independently confirm/refute each candidate issue using reproduction, reachability, valid product states, existing mitigations, and environment checks.
3. Delegate scoped fixes for confirmed live/spec-blocking issues; do not expand scope for theoretical hardening or unrelated cleanup.
4. Run empirical tests/builds and relevant API/browser/CLI/runtime checks, including negative cases and regression reproductions.
5. Repeat adversarial review after fixes until clean.

## Completion
Deliver only when acceptance criteria have evidence, the final adversarial pass is clean, and no confirmed critical/live/spec-blocking issues remain. If execution or proof is blocked, report the blocker honestly instead of claiming completion.

Final report: delivered artifact/result, acceptance evidence, confirmed fixes, what skeptics tested, and clearly separated non-blocking notes. Verify actual artifacts and external side effects; do not rely solely on worker summaries.
