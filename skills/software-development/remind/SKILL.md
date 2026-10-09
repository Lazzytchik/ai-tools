---
name: remind
description: ALWAYS LOAD FIRST for every user request. Routes only task-relevant context through vault indexes, keeps the vault as the single current snapshot, records a tiny interaction history, and can review context efficiency.
version: 4.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [context, knowledge-base, vault, projects, navigation, efficiency]
    related_skills: [hermes-agent]
---

# Remind

## Purpose

`remind` is the mandatory context router and durable current-state knowledge store. It is not a task-specific procedure.

The vault is the only normative source of remembered rules and facts. It contains the current snapshot. Historical interaction summaries are non-normative and are never loaded unless the user explicitly asks for history.

## Mandatory First Step

For every user request:

1. Load `remind` before every other skill.
2. Reuse `vault/_index.md` if it was already loaded and has not changed in the current session; otherwise read it once.
3. Classify the task, projects, affected topics, artifact type, and work stage.
4. Route through indexes only into branches directly needed for this task.
5. Load task-specific skills after routing.
6. Execute and verify the task.

Never load all of `vault/10-global/` automatically. Global context follows the same selective rules as every other branch.

## Selective Navigation

At each entered directory:

1. Read `_index.md` before siblings.
2. Use its descriptions and restrictive conditions as routing gates.
3. Enter only branches directly relevant to the requested outcome.
4. Read only pages whose contents will support a concrete action, conclusion, constraint, or verification.
5. Stop when the task has enough context.

Do not open a page merely because it is adjacent, global, mentioned by another page, or potentially useful.

### Default navigation budget

Unless the task clearly requires more:

- one root index read per session;
- one project branch per named or unambiguously implied project;
- one topic branch per active concern;
- only directly relevant content pages;
- no cross-cutting index or historical file.

When exceeding the budget, state an explicit task dependency that justifies each additional branch. Broad investigations may exceed the budget, but proximity and curiosity are not justifications.

## Session Cache

Within one session:

- reuse previously returned file content when it is still current;
- do not issue repeated reads merely to satisfy bootstrap wording;
- a deduplicated read that returns no content is not counted as loaded context;
- reread only after the file changed, the earlier result was incomplete, or exact verification requires it;
- preserve the original routing decision so later turns do not expand context without a new task dependency.

## Single Current Snapshot

The Markdown vault is the sole normative store. Rules are not duplicated in HTML or another chronological store, and they require no historical citation.

When information changes:

1. Update the owning current-state page in the narrowest accurate scope.
2. Remove or rewrite superseded statements in that page; do not preserve obsolete rules beside the current rule.
3. Update the immediate `_index.md` and any ancestor index whose inventory or routing description changed.
4. Verify that the snapshot has no contradictory active rules.

Scopes:

- global context -> `vault/10-global/`;
- Hermes behavior and configuration -> `vault/20-hermes/`;
- reusable cross-project engineering context -> `vault/30-cross-project-development/`;
- project context -> `vault/40-projects/<project-slug>/`.

Do not create a new skill merely to remember facts or rules. Skills are reusable execution procedures; current context belongs in the vault.

## Recording Explicit Memory

When the user explicitly asks to remember, save, retain, record, or index information:

1. Treat it as a required vault write.
2. Use the narrowest existing topic page, or create the smallest coherent page.
3. Create a project directory and `_index.md` when a newly identified project has no entry.
4. Preserve confirmed facts and accepted rules; label uncertainty and do not persist guesses as fact.
5. Update all affected indexes in the same operation.
6. Verify content, inventory, paths, and routing descriptions.

Do not store raw tool output, routine progress, temporary state, or soon-stale identifiers as current context.

## Interaction History

`references/interaction-history.md` is a short, non-normative history of completed interactions. It is not a context source.

Rules:

- Never read, search, cite, or route into history unless the user explicitly asks for interaction history.
- After a completed user task, append at most one terse bullet summarizing the outcome, using `scripts/append_history.py`.
- Keep the summary factual, outcome-focused, and no longer than the script limit.
- Do not record raw logs, reasoning, secrets, failed intermediate attempts, or detailed implementation notes.
- Do not append for clarification-only turns, reviewer-only output, or no-op responses.
- History never overrides the current vault snapshot.

## Optional Context-Efficiency Reviewer

Configuration lives in `assets/context-reviewer.json`. Manage it with:

```bash
python3 scripts/context_review.py enable
python3 scripts/context_review.py disable
python3 scripts/context_review.py status
```

When enabled and `REMIND_REVIEWER_CHILD` is not set:

1. After the primary task is ready, prepare a manifest using `templates/context-review-manifest.json`.
2. Include every file whose contents were actually returned for task context. Exclude deduplicated reads with no returned content.
3. For each file record loaded characters, useful characters, and the concrete use in the task.
4. Prefer an independent leaf subagent/reviewer to challenge the usefulness labels. Pass only the task, result summary, manifest, and necessary file paths; set `REMIND_REVIEWER_CHILD=1` for separate Hermes processes to prevent recursion.
5. Run `scripts/context_review.py review <manifest>` for the quantitative report.
6. Report:
   - useful-context percentage = total useful characters / total loaded characters;
   - files with zero or low utility;
   - why each was unnecessary;
   - one specific routing, index, or document-structure fix.

The reviewer is advisory and must not delay or modify the primary result. Never spawn a nested reviewer from a reviewer run. If independent review is unavailable, run the deterministic report and label the usefulness attribution as agent-estimated.

## Index Contract

Every knowledge directory in the vault must contain `_index.md`, except hidden application metadata directories.

Each index must:

- state the directory scope;
- list every immediate subdirectory and content page;
- give a concise description and restrictive entry condition;
- reflect the actual filesystem;
- avoid historical chronology and obsolete decision IDs.

## Verification Checklist

Before task execution:

- [ ] `remind` was loaded first.
- [ ] Root index content was read once or reused from the current session.
- [ ] Global and project branches were selected by direct task relevance.
- [ ] The default navigation budget was respected or each expansion was justified.
- [ ] Historical interaction data was not loaded without an explicit request.

After a vault change:

- [ ] The vault remains the single current snapshot.
- [ ] Superseded rules and broken historical citations are absent.
- [ ] Immediate and affected ancestor indexes match the filesystem.
- [ ] The result was verified.
- [ ] One terse interaction-history entry was appended after completion.
