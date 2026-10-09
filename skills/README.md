# Hermes skills

This directory exports three selected Hermes skills. Other installed skills are not included; this repository does not install, enable or reconfigure anything automatically.

| Skill | Purpose |
| --- | --- |
| `software-development/remind` | Selective vault context routing and delegated memory writes. |
| `autonomous-ai-agents/orchestrate` | Multi-agent coordination, independent review and verified results; includes its exact-SHA audit reference. |
| `autonomous-ai-agents/automate` | Autonomous software delivery after explicit specification approval; depends on `orchestrate`. |

The two orchestration skills preserve the current local installation text and all supporting files; repository line endings are normalized to LF.

## Remind interface (v5)

- `SKILL.md` is the short parent router: recognize confirmed durable intent from meaning/emphasis/corrections as well as explicit remember requests; exclude formatting-only, quoted/untrusted, tentative and one-off instructions. Announce intent plus global/project/recurring-operation scope immediately and apply it to the active task before persistence.
- EVERY vault mutation (including indexes/create/rename/delete/update) and EVERY history write goes to a designated writer leaf. Pass `references/vault-writer.md` to that child only; parent does not load it ordinarily. Serialize/coalesce all writers per vault, including ancestor indexes and history; re-read, merge/deduplicate and verify exact persisted rules. Other leaves return handoffs; writers do not recursively spawn themselves.
- Incidental writes are asynchronous: parent continues its task, no polling/wait solely for memory. Explicit vault-write tasks await verification. Report queued, verified or failed/blocked truthfully; no parent-write fallback. Supported top-level desktop delegation is automatically async; stateless runtimes may fall back to synchronous calls, so inspect the live tool schema/capabilities and defer incidental work if necessary. Do not invent a `background` argument.
- Context review requires an explicit user request and one independent read-only leaf. Pass `references/context-reviewer.md`, the actual parent transcript artifact OR exact real session ID, and task boundaries. Isolated children do not inherit the parent's messages. Read/scroll only that exact session, deduplicate IDs and disclose gaps. No parent estimates, nested reviews or manifest-only session review.
- Within `remind`, only `SKILL.md` is a skill; the two references are lazy role-specific instructions, not separately auto-loaded skills.

These are prompt-based policies, NOT a hard runtime permission boundary, scheduler, perfect durable-rule classifier, guaranteed concurrency lock or proof of real asynchronous execution. This package does not modify Hermes runtime/plugins. Role labels and environment variables are not security controls.

## Reviewer preference and migration

`assets/context-reviewer.json` ships `enabled: false`, `mode: explicit-request-only`. Legacy `enabled: true` NEVER grants automatic review. `enable`/`disable` only change the local explicit-review preference; JSON schedules nothing. A direct user request permits a one-shot review without enabling future automatic runs. Keep an existing personal config backup; migrate its mode/default manually in the designated installation rather than overwrite a personal vault.

```sh
python3 skills/software-development/remind/scripts/context_review.py status
python3 skills/software-development/remind/scripts/context_review.py --help
python3 skills/software-development/remind/scripts/append_history.py --help
```

Only a reviewer leaf runs `context_review.py review MANIFEST --transcript EXACT_TASK_TRANSCRIPT --json` during an explicitly requested review. The manifest template references exact character spans/message IDs in a normalized actual transcript. Native exports/JSONL require lossless task-only normalization described in the reviewer reference. The helper validates evidence shape/spans/arithmetic, NOT provenance, semantic usefulness, complete inventory, user consent or leaf isolation. Fixture reports are labeled `source: fixture`; they are tests, never evidence of the parent's session. Partial coverage stays partial; empty file inventory has no utility percentage.

Official interfaces: https://hermes-agent.nousresearch.com/docs/user-guide/features/delegation/ and https://hermes-agent.nousresearch.com/docs/user-guide/sessions/ . Use live schemas; bounded session reads require pagination, not summaries.

## Privacy boundary

- Public vault: unchanged empty starter indexes only; no project knowledge or personal rules.
- Real history is not exported; `templates/interaction-history.md` is an empty starting file.
- Credentials, Hermes configuration, usage/curator metadata and caches are excluded.
- `.gitignore` excludes local history and non-starter vault files; it cannot protect edits to tracked starter indexes. Inspect staged changes before publishing.

## Installation (manual, not performed by this repository)

Copy each selected skill directory into the same relative path under `$HERMES_HOME/skills/` (default `~/.hermes/skills/`). Copy both `autonomous-ai-agents/orchestrate/` and `autonomous-ai-agents/automate/` together to satisfy the dependency; preserve the orchestrate reference directory. Back up an existing installation before replacing its files.

For `remind`, copy `software-development/remind` into `$HERMES_HOME/skills/software-development/remind/` (default `~/.hermes/skills/software-development/remind/`). Back up existing installations. Never overwrite existing vault/history with empty starters. Start a new Hermes session after installation. A designated writer initializes local `references/interaction-history.md` from its template only if absent; parent/reviewer never initialize or append it.

## Tests

Python standard library only:

```sh
python3 -m unittest discover -s skills/software-development/remind/tests -v
```

Script tests copy the package's config/scripts/templates into isolated scratch directories and label authored transcript fixtures explicitly. They never write public config/history or installed/personal vaults. Static contract checks catch textual regressions; they do NOT prove model obedience, correct inference, race-free multi-session writes or live async delegation.
