---
name: orchestrate
description: "Use for large multi-step tasks. Delegate and verify."
---

# Orchestrate

The current model remains the orchestrator: frame tasks, maintain a live `todo` plan, dispatch workers, synthesize evidence, and communicate. Delegate research, analysis, implementation, tests, and review; personally perform only minimal framing and direct checks needed to verify worker claims. Skip this workflow for small edits.

## Model routing
- Choose the lightest available model **from the orchestrator's provider** that can reliably handle each subtask; consider complexity, risk, tool support, and context needs. Escalate within that provider when necessary. Never downshift the orchestrator or pin a particular worker model.
- Verify available model IDs; do not invent names. `delegate_task` has no per-task model selector: use it only when its actual inherited/configured routing fits. For explicit routing, launch `hermes chat --provider <parent-provider> --model <verified-model> -q '<self-contained task>'` via `terminal` (background with completion notification for long tasks). Do not silently switch providers or rewrite global config. If no lighter capable model is available, use the parent model.

## Workflow
1. Read necessary context; create a short plan. Resolve consequential forks through competing evidence-backed options and independent challenge, not intuition alone.
2. Delegate bounded tasks with full context, paths, constraints, acceptance criteria, and an output contract: results, evidence, risks, recommended next steps. Parallelize independent work; never overlap writers on the same files.
3. Adapt the plan from each return. Preserve successful work; narrow failed or timed-out probes instead of blindly repeating them.
4. End each substantial block with independent adversarial review; use distinct lenses for non-trivial work. Confirm/refute candidate findings before fixing, then fix and re-test until no confirmed blocking issues remain.

## Evidence gate
- Demand real commands, outputs, and reproducible behavior; verify artifacts and external side effects directly. Worker summaries are claims, not proof.
- Before reporting a defect, test reachability, reproduction, real product states, existing mitigations, and environment causes. Separate live bugs from hardening, dead/unreachable code, moot states, ops issues, and defense-in-depth.
- Map every acceptance requirement to evidence. Missing required proof blocks unconditional approval but is not automatically a code defect.
- Respect read-only scope. For exact-revision reviews, check identity/cleanliness before and after long checks; drift blocks approval. Match artifact hashes and require semantic runtime checks, not just manifest flags. See `references/exact-sha-read-only-audit.md` only when needed.

Report delivered results, verification evidence, remaining blockers/non-blocking notes, and the requested verdict format exactly. Never claim success when required evidence is missing.
