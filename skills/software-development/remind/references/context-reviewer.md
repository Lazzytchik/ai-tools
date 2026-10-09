# Explicit context-efficiency reviewer

This adjacent reference is NOT an auto-loaded skill. Only an explicit user request authorizes a review. Parent passes its path to one independent read-only leaf; parent does not read these instructions during ordinary tasks. No nested review, delegated writers, primary-task modification or parent usefulness estimate/fallback. If the leaf or evidence is unavailable, report review blocked, not complete.

## Invocation and handoff
The parent supplies the actual task, task-completion cutoff, result, and either an artifact of the actual parent messages or the EXACT real parent `session_id`. Children have isolated fresh contexts, not automatic access to the parent's conversation. A summary/manifest alone is insufficient. Never guess a session id, browse unrelated sessions or use personal interaction history. Role/explicit-request labels are procedural, not hard isolation enforced by an environment variable.

`assets/context-reviewer.json` ships `enabled: false`, `mode: explicit-request-only`. `enable` only records an opt-in preference for explicitly requested reviews; it NEVER creates an automatic trigger. A direct user request authorizes a one-shot review without changing the preference. Legacy `enabled: true` does not authorize automatic review. JSON is configuration, not a runtime scheduler.

## Exact transcript, coverage and limits
Use the supplied real transcript artifact; otherwise read only the supplied parent session via `session_search(session_id=<exact-id>, role_filter="user,assistant,tool")`. Read mode uses `session_id` alone (plus optional role filter), not a guessed query. For bounded/head-tail results, scroll that SAME session with `around_message_id`, `window` up to 20, and the role filter. Deduplicate message IDs, retain chronological order and paginate through every gap within the task boundary. Record covered first/last IDs and task-completion cutoff. Check continuity against the returned boundaries; do not infer full coverage merely because a page lacks a truncation warning.

Review the actual user/assistant text and task tool calls/results required to verify what was loaded and what supported the delivered result. A snapshot through task completion is legitimate: exclude later reviewer traffic. Do not request hidden chain-of-thought or invent missing text. Preserve exact message content; save/export only this task's necessary transcript to a scratch artifact. If unavailable, truncated or inaccessible, state gaps precisely and label coverage partial. Never claim an entire-session review from a summary or incomplete snapshot.

## Evidence and arithmetic helper
Build the inventory from actual returned tool content, not a parent's usefulness labels. Exclude deduplicated reads returning no content. Keep all task-context reads, including zero-use ones; challenge whether each passage supported an action, conclusion, constraint or verification. Generic orientation/potential relevance is not automatically useful. Attribute utility to exact supporting passages and cite the delivered task messages. Utility attribution remains a judgment, not a measured causal fact.

Use `templates/context-review-manifest.json`. The helper takes a normalized JSON transcript with `session_id`, `source` (`parent-session-artifact`, `session-search`, or test-only `fixture`), `coverage` (`complete` or `partial`), `limitations` (list), `task_start_id`, `task_end_id`, and ordered `messages`: each has unique string `id`, `role` (`user`, `assistant`, `tool`), exact string `content`, and original `tool_calls`/`tool_call_id` where applicable. Preserve tool-call fields; normalization is not summarization. `complete` means the exact parent TASK snapshot through the cutoff, not all future conversation. Partial coverage requires explicit limitations. JSONL/native session exports must be normalized without fabricating text; retain the source artifact for audit. Use `fixture` only for authored tests, never present fixtures as the parent's session.

Each manifest row has loaded/useful counts plus `loaded_evidence` and `useful_evidence`: lists of `{message_id, start, end}` zero-based half-open character spans in exact tool-result content. Counts equal nonoverlapping spans; useful spans must be contained in loaded spans. `supports` cites actual task message IDs for a concrete `used_for` when utility >0. Count only actually returned text, including line prefixes if present, consistently. A partial/truncated file read contributes only its returned range. Do not count the same span twice. A file loaded repeatedly can have multiple evidence spans in one row. Parent manifest-only runs fail validation.

Run:

```sh
python3 scripts/context_review.py review <manifest.json> --transcript <exact-task-transcript.json> --json
```

The script validates shape, spans and arithmetic, NOT session provenance, complete inventory, actual leaf isolation, true user authorization or semantic usefulness. It cannot make authored evidence genuine. It remains a read-only stdlib helper, not a session reviewer by itself. A zero-file task is valid and has no utility percentage, not 100%.

## Return
Return task boundary/coverage, gaps/limitations, independent attribution, useful/loaded characters and percentage (or not applicable), every unused/low-utility file with reason, and one specific routing/index/document fix grounded in the transcript. Cite actual message IDs/passages; distinguish verified arithmetic from reviewer judgments. Do not read history or mutate the vault/config/history. If helper evidence validation fails, correct against the actual transcript or report failure, never substitute a manifest-only estimate.

Official interface references: https://hermes-agent.nousresearch.com/docs/user-guide/sessions/ and https://hermes-agent.nousresearch.com/docs/user-guide/features/delegation/ . Consult live schemas when running; this reference does not supply nonexistent background arguments.
