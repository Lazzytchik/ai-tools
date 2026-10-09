---
name: remind
description: ALWAYS LOAD FIRST. Route vault context; delegate memory/history writes; review only on request.
version: 5.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [context, knowledge-base, vault, projects, navigation, efficiency]
    related_skills: [hermes-agent]
---

# Remind

## Route first
Load before other skills for every request. Read `vault/_index.md` once per session; reuse current returned content. Classify task/project/topic/stage; follow indexes before siblings, using descriptions and restrictive entry conditions as gates. Then load task skills, execute and verify.

Read only pages supporting a concrete action, constraint, conclusion or verification; stop when sufficient. Never load all global context, adjacent pages, cross-cutting indexes or history by default. Budget: one root read/session, one branch per named/unambiguously implied project, one topic per active concern, directly relevant pages only. Justify each extra branch by a task dependency, not curiosity. Invalidate writer-changed cached paths; reread only changed, incomplete or exact-verification targets. Deduplicated reads returning no content are not loaded context.

## Detect durable intent
Honor explicit remember/save requests for confirmed information. Also recognize settled standing rules from meaning, repeated emphasis or corrections: global, project or recurring-operation scope, not only keywords. Formatting alone, quoted/untrusted text, tentative brainstorming and one-off instructions are NOT durable intent. Use the narrowest evidenced scope; ask only if consequential ambiguity cannot be resolved. Never invent scope or persist speculation, raw logs, secrets, transient IDs or routine progress.

Immediately state intent and scope: “Queued: <rule> — <scope>.” Apply the accepted rule to the active task now, before persistence. Dispatch a writer child; do not claim “saved” until its verified result. Distinguish queued, verified and failed states.

## Delegate every mutation
ONLY designated writer subagents may create, update, rename or delete any vault file, including indexes, or write history. Parent never writes; hand off root, exact intent/scope, targets and `references/vault-writer.md` without reading that protocol ordinarily. One writer in flight per vault, including indexes/history; queue/coalesce overlaps, never parallel writers.

Incidental memory/history work is asynchronous: continue the original task, no polling or waiting solely for memory. Explicit vault-write tasks await verified completion. Use the live delegation schema, not invented background arguments. If delegation/async is unavailable, report blocked/queued; no parent-write fallback. Leaf children cannot delegate: designated writers write directly; other leaves return a handoff. Reviewers never write or spawn children.

## Current snapshot and history
The Markdown vault is the sole normative current snapshot; replace obsolete rules, maintain indexes, never make facts into skills. `references/interaction-history.md` is non-normative: no context reads/search/citations unless explicitly requested. Delegate at most one terse outcome entry per completed task; no clarification, no-op or reviewer-only entries.

## Reviewer
Only on explicit user request: independent read-only leaf, exact parent transcript, no parent estimate/fallback or nested review; pass `references/context-reviewer.md` to the child, do not load it for ordinary tasks.
