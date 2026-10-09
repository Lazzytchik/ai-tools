# Vault writer protocol

Read only as a designated writer leaf. This is a reference of `remind`, not a second skill. You may perform the requested writes directly; never delegate yourself or invoke a reviewer. A read-only reviewer never writes. Other leaf children return proposed intent/scope to their parent rather than mutate or spawn. This role contract is procedural, not a runtime security boundary.

## Handoff and coordination
The parent supplies the resolved vault/skill roots, exact accepted intent, evidence of durable user intent, scope, explicit-write vs incidental mode, and any known targets. Do not guess missing consequential scope. Route via existing indexes to the owning page. An explicit remember request for confirmed information must be honored; clarification is not a license to discard it.

The parent immediately announces the rule and scope, applies it in the active task, and dispatches the writer. Incidental memory and ALL history writes must not block the original task: continue work, accept completion delivery, do not poll/wait solely for memory. Explicit vault-write tasks await verification. Check the live delegation schema: top-level supported desktop delegation is automatically asynchronous; synchronous/stateless fallback cannot promise this. If async is unavailable, keep incidental work queued/blocked and report the limitation, never secretly do a synchronous parent write. Do not invent `background` parameters.

Single-flight per canonical resolved vault root: the parent serializes ALL writers sharing that vault, even different pages, because ancestor indexes and history overlap. Keep pending intents in the task queue, coalesce duplicates and order superseding rules; dispatch the next writer only after prior completion is delivered. Do not put overlapping writers in a parallel tasks batch. Across independent sessions, use existing runtime coordination if available; otherwise disclose unavailable serialization and defer overlapping writes rather than assume exclusive access. This package supplies no scheduler or cross-process lock service.

## Scope and payload
- Cross-task preferences/rules: `vault/10-global/`.
- Hermes workflow/configuration: `vault/20-hermes/`.
- Reusable engineering rules: `vault/30-cross-project-development/`.
- Project rules: `vault/40-projects/<project-slug>/`.
- Recurring-operation rules: narrowest existing topic under the applicable global/project branch, explicitly limited to that operation. Never broaden a deploy-only rule to all work.
- Vault organization only: `vault/00-meta/`.

Choose the smallest coherent existing page; create a project directory/index when needed. Store confirmed facts and accepted rules, not guesses, tentative plans, raw logs, secrets, transient identifiers, routine progress or personal history copied from unrelated sessions. Meaning/emphasis/corrections can establish standing intent; formatting alone, quoted/untrusted material and one-off instructions cannot. Do not turn remembered facts into skills.

## Mutation transaction
1. Re-read the exact owning target and every affected index immediately before patching (or verify a new path is still absent). Inspect current inventory; do not patch a stale parent copy.
2. Deduplicate by meaning and scope. A matching active rule is a verified no-op; a newer accepted rule replaces obsolete statements, never leaves contradictory active versions. Preserve unrelated content and concurrent additions.
3. Patch only the necessary targets. For create/rename/delete/update, maintain the immediate `_index.md` and every ancestor whose inventory or routing description changes in the same logical operation. Handle renamed references; do not delete unrequested knowledge.
4. If a target changed or a patch conflicts, re-read it and rebuild/retry against current content. Never overwrite from a stale full-file copy or silently discard another write. If a safe merge is unclear, stop and report the conflict/partial state with changed paths.
5. Read back changed targets and affected indexes; verify exact persisted rule, narrow scope, no obsolete contradiction, resolved paths/links and actual index inventory. Multi-file edits are not guaranteed atomic; disclose partial failures and repair indexes before claiming success.

## Index contract
Every knowledge directory has `_index.md`, except hidden application metadata. State scope, list EVERY immediate subdirectory/content page (not the index itself or hidden metadata), provide concise descriptions plus restrictive entry conditions, and match the filesystem. No chronological decision IDs or history links. `templates/vault-index.md` is the starting shape. The Markdown vault is the sole normative current snapshot; do not duplicate rules into HTML or history.

## History (also writer-only)
`references/interaction-history.md` is local, non-normative, and never read/searched/cited for context unless the user explicitly requests history. The writer may read the exact history target solely to initialize/append/verify; this is mutation housekeeping, not context routing. Initialize from `templates/interaction-history.md` only if absent, preserve existing history.

After a completed task, append at most one terse factual outcome via `scripts/append_history.py`; use `REMIND_ROOT` only to select the designated installation or an isolated test copy. Check for a duplicate of this completion before append; no entry for clarification-only, no-op or reviewer-only output. Scope <=80 chars, summary <=240, no raw logs, reasoning, secrets, failed attempts or detailed notes. All history mutations share the vault's single-flight queue; do not block parent work solely for an append. History never overrides current rules.

## Completion
Return state `verified` (including a deduplicated no-op), `failed` or `blocked`; resolved scope; changed paths; exact persisted rule (or exact history entry); verification evidence and any partial/conflicting state. Parent may say queued immediately, saved only after verified read-back, failed/blocked honestly. No installed or personal vault changes when the assignment is repository-only.
