# Exact-SHA Read-Only Spec Audit

Use this pattern when the required output is an approval tied to one immutable commit.

## Identity and hygiene

1. Record `git rev-parse HEAD` and compare it byte-for-byte with the requested SHA.
2. Record `git status --porcelain=v1 --untracked-files=all`; any candidate-file drift means the audit is not solely of the named commit.
3. Inspect the commit parent/subject and the feature diff against the authoritative base.
4. Repeat HEAD and status checks immediately before the verdict.
5. Treat identity as a live invariant, not a one-time preflight: a long review can race another agent or branch update. If `HEAD` or the branch ref moves, record the requested and observed SHAs plus the exact ref path (for example `.git/refs/heads/<branch>:1`). Never reset, checkout, detach, or otherwise mutate the repository to recover during a strict read-only review.
6. A moving branch does not invalidate evidence already collected from the immutable requested commit, but it fails any acceptance condition requiring the current clean `HEAD` to equal that SHA before and after review. Classify this as an identity/acceptance-evidence blocker, not a source-code defect.

## Requirement evidence

For each requirement, collect:

- implementation path and line range;
- focused test path and line range;
- production-path or GUI evidence when behavior cannot be proved statically;
- CI workflow evidence showing the required check runs against the packaged artifact;
- classification: satisfied, live blocking gap, hardening-only, or acceptance-evidence blocker.

Do not infer a GUI behavior from layout constants alone. For click/hover requirements, inspect the event path and require a smoke that performs the interaction and fails on missing visual change or process death.

## Non-mutating verification

- Prefer executing existing test binaries directly when `ctest` would update `Testing/` logs.
- Before trusting an existing test binary, check build freshness non-mutatingly (for Ninja, `ninja -C <build-dir> -n <test-target>`). A passing stale binary is not evidence for the requested source. Distinguish actual object rebuilds from harmless always-run packaging steps such as asset copies or relinks; use the build plan and source/object timestamps together.
- Verification metadata may live under `.git/` rather than the tracked tree (for example `.git/hermes-verification.json`). Inspect it directly, require its `head_sha` to equal the requested SHA, and compare every recorded artifact hash to the actual package. The marker remains supporting evidence, not proof that its commands or GUI profiles were reproduced.
- Use `git diff-tree --check` for commit-local whitespace hygiene.
- Compare recorded checksums with actual packaged binaries/assets and confirm executable formats.
- Treat an exact-SHA verification manifest as supporting evidence, not a substitute for inspecting its claimed test, build, and smoke paths.
- Do not run formatters, configure/build commands, `py_compile`, or ad-hoc probes that write into the repository or user workspace during strict read-only review.
- If existing test binaries are stale, export the exact commit with `git archive HEAD` into a unique OS/container temporary directory, configure/build/test only there, execute the resulting test binaries directly, and delete the entire temporary tree before the final identity check. This yields source-bound execution evidence without touching the reviewed worktree.
- For an essential native-GUI probe, copy only the hash-verified package and checked-in smoke script to an OS temporary directory, run there, capture the exact failed assertion/report, and delete the directory before the final hygiene check.

## Concurrent-worker identity drift

Shared review containers may be advanced by another worker during a long audit. Check both `HEAD` and status after each long build, GUI run, or external interaction as well as immediately before the verdict. `HEAD` can remain unchanged while another worker edits tracked files; a newly dirty worktree is still identity drift for a strict clean-tree review.

If the observed SHA changes **or the worktree becomes dirty**:

1. Stop gathering source evidence from the moving worktree; otherwise the report mixes committed and uncommitted states.
2. Preserve already-recorded command output and artifact hashes that are demonstrably tied to the requested SHA.
3. Record requested SHA, initial SHA/status, and final observed SHA/status. For dirty drift, capture `git diff -- <path>` and cite the first concrete `path:line` changes without attributing authorship unless independently proven.
4. Classify the drift as an acceptance-evidence blocker. Do not reset, checkout, restore, stash, or otherwise mutate the shared worktree in a read-only review.
5. A stale manifest naming the requested SHA does not repair final identity; cite both the manifest line and live identity/hygiene results.

## Native GUI smoke evidence

A manifest field claiming native smoke success is only supporting evidence. To reproduce it:

1. Verify the package executable hash exactly matches the manifest before copying it.
2. Run the repository's checked-in smoke script against that package from an isolated OS temp directory.
3. Exercise each advertised sizing profile when practical, not only the auto-selected profile; constrained and full profiles can fail differently. Give each profile a **fresh, separately copied package directory** and a separate artifact directory; do not reuse one extracted runnable package across profile runs.
4. Require exact window ownership, exact resize settlement, semantic scene checks, causal click/hover checks, process liveness, and cleanup.
5. Treat a generic nonblank or pixel-variance wait as readiness only—not scene correctness. It can accept a fully rendered but wrong scene. The semantic assertion must also pass.
6. Re-run a surprising failure once to distinguish a transient capture from a reproducible blocker. If the failure shows the wrong scene after an earlier profile run, make the retry from a fresh hash-verified package copy: runtime state, delayed input, or package/process side effects can contaminate reused-profile evidence even when no new package files are obvious. A pass from the fresh isolated copy refutes contamination; repeated fresh-copy failure is the blocker. Preserve the exact check name and dimensions, then clean temporary artifacts.

## Isolated native GUI execution

When a required native GUI smoke is reproducible only on the host, export the already-built exact artifact and the committed smoke script to a unique OS temporary directory; never copy probes into the repository or general user workspace.

1. Hash the exported executable and compare it to the verification manifest before execution.
2. Copy the complete runnable package, including assets and runtime libraries, not only the executable.
3. Run the committed smoke script against that exported package and place all screenshots/reports under the same temporary directory.
4. If the smoke supports adaptive profiles, exercise every acceptance-relevant profile explicitly (for example both `full` and `constrained`), rather than relying only on `auto` selecting one profile for the current desktop.
5. Preserve command output as review evidence, then remove the entire temporary directory before the final repository identity/cleanliness check.
6. On Git Bash/MSYS hosts, prevent path rewriting around Docker copies with `MSYS_NO_PATHCONV=1` and pass native paths to Windows Python via `cygpath -w`. A failed first launch followed by a successful retry is evidence of the retry technique, not a durable claim that the tool is broken.

## Adversarial finding gate

Before reporting a blocker, try to refute it using the live production path and focused tests. A speculative edge case without a reachable trigger is not a blocker. Conversely, inability to reproduce required acceptance evidence blocks unconditional approval even when no source defect is proven.

## Verdict format

Honor the caller's exact protocol:

- `APPROVED <exact-sha>` when every required row is satisfied and evidence is reproducible.
- `NOT APPROVED` followed only by concrete blockers with `path:line` evidence and the missing/failed command when relevant.

Put the verdict on the first line and match the requested output envelope literally. If the caller says “Return APPROVED plus SHA or NOT APPROVED with blockers,” an approval response is exactly the single line `APPROVED <exact-sha>`—do not append evidence bullets. For rejection, append only the requested concrete `path:line` blockers. Avoid substituting PASS/FAIL terminology when APPROVED/NOT APPROVED was requested.
