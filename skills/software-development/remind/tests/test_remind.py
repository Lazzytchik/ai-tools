"""Real stdlib script tests + textual contracts, not live-agent/async proof.

All authored transcripts are explicitly fixtures, never parent-session evidence.
"""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parents[1]


def fixture_transcript():
    # Authored test fixture only, with original synthetic tool-call fields.
    messages = [dict(id="u", role="user", content="Fixture task"),
                dict(id="a", role="assistant", content="", tool_calls=[
                    dict(id=f"c{i}", type="function", function=dict(name="read_file", arguments="{}"))
                    for i in range(1, 4)])]
    messages += [dict(id=f"t{i}", role="tool", tool_call_id=f"c{i}", content="x" * 100) for i in range(1, 4)]
    messages += [dict(id="r", role="assistant", content="Fixture delivered result")]
    return dict(session_id="AUTHORED_TEST_FIXTURE_NOT_PARENT", source="fixture",
                coverage="complete", limitations=[], task_start_id="u", task_end_id="r", messages=messages)


def fixture_manifest():
    files = []
    for i, useful in enumerate((50, 10, 0), 1):
        files.append(dict(path=f"/fixture/file-{i}.md", loaded_chars=100, useful_chars=useful,
                          used_for="Fixture result constraint" if useful else "",
                          loaded_evidence=[dict(message_id=f"t{i}", start=0, end=100)],
                          useful_evidence=[dict(message_id=f"t{i}", start=0, end=useful)] if useful else [],
                          supports=["r"] if useful else []))
    return dict(task="Authored fixture task", attribution="independent-reviewer", files=files)


class ScriptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Explicit scratch only: never installed/public history or config.
        scratch = Path(os.environ.get("REMIND_TEST_TMP", os.environ.get("TMPDIR", str(Path.home() / ".cache/remind-tests"))))
        scratch.mkdir(parents=True, exist_ok=True)
        cls.scratch = scratch
        cls.source_before = {p: p.read_bytes() for p in PACKAGE.rglob("*") if p.is_file() and "__pycache__" not in p.parts}

    @classmethod
    def tearDownClass(cls):
        for path, before in cls.source_before.items():
            if path.read_bytes() != before:
                raise AssertionError(f"Test mutated public source: {path}")

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="remind-test-", dir=self.scratch)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for directory in ("scripts", "assets", "references"):
            (self.root / directory).mkdir()
        for name in ("context_review.py", "append_history.py"):
            shutil.copy2(PACKAGE / "scripts" / name, self.root / "scripts" / name)
        shutil.copy2(PACKAGE / "assets/context-reviewer.json", self.root / "assets/context-reviewer.json")
        self.history = self.root / "references/interaction-history.md"
        shutil.copy2(PACKAGE / "templates/interaction-history.md", self.history)
        self.manifest, self.transcript = fixture_manifest(), fixture_transcript()

    def run_script(self, name, *args):
        env = dict(os.environ, REMIND_ROOT=str(self.root), PYTHONDONTWRITEBYTECODE="1")
        return subprocess.run([sys.executable, str(self.root / "scripts" / name), *map(str, args)],
                              env=env, capture_output=True, text=True, timeout=15)

    def run_review(self, as_json=True):
        manifest = self.root / "manifest.json"
        transcript = self.root / "transcript.json"
        manifest.write_text(json.dumps(self.manifest), encoding="utf-8")
        transcript.write_text(json.dumps(self.transcript), encoding="utf-8")
        args = ["review", manifest, "--transcript", transcript] + (["--json"] if as_json else [])
        return self.run_script("context_review.py", *args)

    def assert_rejected(self, expected):
        result = self.run_review()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(expected, result.stderr)
        self.assertEqual(result.stdout, "")

    def test_status_disabled_explicit_and_toggle_migrates_legacy_mode(self):
        status = self.run_script("context_review.py", "status")
        self.assertEqual(status.returncode, 0, status.stderr)
        self.assertFalse(json.loads(status.stdout)["enabled"])
        self.assertEqual(json.loads(status.stdout)["mode"], "explicit-request-only")
        config = self.root / "assets/context-reviewer.json"
        config.write_text('{"enabled": true, "mode": "subagent"}', encoding="utf-8")
        enabled = self.run_script("context_review.py", "enable")
        self.assertEqual(enabled.returncode, 0, enabled.stderr)
        self.assertIn("no automatic scheduling", enabled.stdout)
        self.assertEqual(json.loads(config.read_text())["mode"], "explicit-request-only")
        disabled = self.run_script("context_review.py", "disable")
        self.assertEqual(disabled.returncode, 0, disabled.stderr)
        self.assertFalse(json.loads(config.read_text())["enabled"])

    def test_help_and_manifest_only_rejected(self):
        for name in ("context_review.py", "append_history.py"):
            with self.subTest(name=name):
                result = self.run_script(name, "--help")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("usage:", result.stdout)
        result = self.run_script("context_review.py", "review", self.root / "missing-manifest")
        self.assertEqual(result.returncode, 2)
        self.assertIn("--transcript", result.stderr)

    def test_exact_arithmetic_classification_and_fixture_label(self):
        result = self.run_review()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual((report["loaded_chars"], report["useful_chars"], report["useful_context_percent"]), (300, 60, 20.0))
        self.assertEqual([x["classification"] for x in report["files"]], ["useful", "low-utility", "unused"])
        self.assertEqual(len(report["unnecessary_files"]), 2)
        self.assertEqual(report["source"], "fixture")
        self.assertIn("not proven", report["validation"])

    def test_plain_text_report_includes_limits_and_fix(self):
        self.transcript.update(coverage="partial", limitations=["Fixture gap, not real parent evidence"])
        result = self.run_review(as_json=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("20.0%", result.stdout)
        self.assertIn("coverage: partial; source: fixture", result.stdout)
        self.assertIn("Fixture gap", result.stdout)
        self.assertIn("Fix:", result.stdout)

    def test_no_file_inventory_is_not_100_percent(self):
        self.manifest["files"] = []
        result = self.run_review()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["loaded_chars"], 0)
        self.assertIsNone(report["useful_context_percent"])
        self.assertIn("not applicable", self.run_review(as_json=False).stdout)

    def test_invalid_counts_including_bool_float_and_negative(self):
        for loaded, useful in ((True, 0), (100, True), (1.5, 0), (0, 0), (-1, 0), (100, -1), (100, 101)):
            with self.subTest(loaded=loaded, useful=useful):
                self.manifest = fixture_manifest()
                self.manifest["files"][0].update(loaded_chars=loaded, useful_chars=useful)
                self.assert_rejected("invalid integer character counts")

    def test_threshold_is_finite_and_bounded(self):
        config = self.root / "assets/context-reviewer.json"
        for value in (True, "0.25", -0.1, 1.1, float("nan"), float("inf")):
            with self.subTest(value=value):
                config.write_text(json.dumps(dict(low_utility_threshold=value)), encoding="utf-8")
                self.assert_rejected("low_utility_threshold")

    def test_threshold_boundary_is_useful(self):
        self.manifest["files"][0].update(useful_chars=25, useful_evidence=[dict(message_id="t1", start=0, end=25)])
        result = self.run_review()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["files"][0]["classification"], "useful")

    def test_duplicate_paths_or_cross_file_spans_rejected(self):
        self.manifest["files"].append(copy.deepcopy(self.manifest["files"][0]))
        self.assert_rejected("duplicate file path")
        self.manifest["files"][-1]["path"] = "/fixture/another.md"
        self.assert_rejected("double-counts")

    def test_missing_malformed_or_out_of_range_evidence(self):
        for evidence in (None, [{}], [dict(message_id="absent", start=0, end=10)],
                         [dict(message_id="u", start=0, end=1)],
                         [dict(message_id="t1", start=True, end=100)],
                         [dict(message_id="t1", start=0, end=101)],
                         [dict(message_id="t1", start=3, end=3)]):
            with self.subTest(evidence=evidence):
                self.manifest = fixture_manifest()
                self.manifest["files"][0]["loaded_evidence"] = evidence
                self.assert_rejected("loaded_evidence")

    def test_count_mismatch_or_useful_outside_loaded(self):
        self.manifest["files"][0]["loaded_chars"] = 99
        self.assert_rejected("do not match")
        self.manifest = fixture_manifest()
        self.manifest["files"][0].update(loaded_chars=50, loaded_evidence=[dict(message_id="t1", start=50, end=100)])
        self.assert_rejected("outside loaded")

    def test_evidence_spans_cannot_overlap(self):
        self.manifest["files"][0]["loaded_evidence"] = [dict(message_id="t1", start=0, end=60), dict(message_id="t1", start=40, end=80)]
        self.assert_rejected("double-counts")

    def test_useful_requires_concrete_use_and_existing_support(self):
        for used_for, supports in (("", ["r"]), ("Fixture use", []), ("Fixture use", ["absent"]), (None, ["r"])):
            with self.subTest(used_for=used_for, supports=supports):
                self.manifest = fixture_manifest()
                self.manifest["files"][0].update(used_for=used_for, supports=supports)
                result = self.run_review()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("ERROR:", result.stderr)

    def test_parent_estimate_fallback_rejected(self):
        self.manifest["attribution"] = "agent-estimated"
        self.assert_rejected("no parent estimate fallback")

    def test_partial_requires_limits_and_never_upgrades_coverage(self):
        self.transcript["coverage"] = "partial"
        self.assert_rejected("requires explicit limitations")
        self.transcript["limitations"] = ["Authored fixture missing middle messages"]
        result = self.run_review()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["coverage"], "partial")

    def test_complete_requires_boundary_and_original_tool_call(self):
        self.transcript["task_end_id"] = "missing"
        self.assert_rejected("exact first/last IDs")
        self.transcript = fixture_transcript()
        self.transcript["messages"][1]["tool_calls"] = []
        self.assert_rejected("missing original tool call")

    def test_transcript_no_summary_duplicate_ids_invalid_roles(self):
        variants = [{"session_id": "fixture", "source": "fixture", "coverage": "complete", "limitations": [], "task_start_id": "u", "task_end_id": "r", "summary": "Not messages"}]
        duplicate = fixture_transcript()
        duplicate["messages"].append(copy.deepcopy(duplicate["messages"][-1]))
        variants.append(duplicate)
        invalid = fixture_transcript()
        invalid["messages"][0]["role"] = "system"
        variants.append(invalid)
        for variant in variants:
            with self.subTest(variant=variant):
                self.transcript = variant
                result = self.run_review()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("ERROR:", result.stderr)

    def test_malformed_json_and_non_object_are_clean_errors(self):
        bad = self.root / "bad.json"
        for content in ("[1]", "{", "null"):
            with self.subTest(content=content):
                bad.write_text(content, encoding="utf-8")
                result = self.run_script("context_review.py", "review", bad, "--transcript", bad)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("ERROR:", result.stderr)
                self.assertNotIn("Traceback", result.stderr)

    def test_append_normalizes_preserves_and_leaves_no_tempfiles(self):
        before = self.history.read_text(encoding="utf-8")
        result = self.run_script("append_history.py", "--scope", " project\n A ", "--summary", " Done\t verified ", "--date", "2026-10-09")
        self.assertEqual(result.returncode, 0, result.stderr)
        entry = "- 2026-10-09 — project A — Done verified"
        self.assertEqual(result.stdout.strip(), entry)
        after = self.history.read_text(encoding="utf-8")
        self.assertEqual(after, before.replace("<!-- append-below -->", "<!-- append-below -->\n" + entry))
        self.assertFalse(list(self.history.parent.glob("*.tmp")))

    def test_history_scope_summary_and_date_validation_leave_file_unchanged(self):
        before = self.history.read_bytes()
        for args in (("--scope", " ", "--summary", "OK"), ("--scope", "x" * 81, "--summary", "OK"),
                     ("--scope", "A", "--summary", "x" * 241), ("--scope", "A", "--summary", " "),
                     ("--scope", "A", "--summary", "OK", "--date", "2026-02-30"),
                     ("--scope", "A", "--summary", "OK", "--date", "2026-10-09\nInjected")):
            with self.subTest(args=args):
                result = self.run_script("append_history.py", *args)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("ERROR:", result.stderr)
                self.assertEqual(self.history.read_bytes(), before)

    def test_missing_or_duplicate_history_marker(self):
        for content in ("No marker", "<!-- append-below -->\n<!-- append-below -->"):
            with self.subTest(content=content):
                self.history.write_text(content, encoding="utf-8")
                result = self.run_script("append_history.py", "--scope", "A", "--summary", "Done")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("marker", result.stderr)
                self.assertEqual(self.history.read_text(), content)
        self.history.unlink()
        result = self.run_script("append_history.py", "--scope", "A", "--summary", "Done")
        self.assertIn("missing history", result.stderr)
        self.assertFalse(self.history.exists())


class StaticContracts(unittest.TestCase):
    """These inspect package text; they do not demonstrate model/runtime obedience."""
    def setUp(self):
        self.main = (PACKAGE / "SKILL.md").read_text(encoding="utf-8")
        self.writer = (PACKAGE / "references/vault-writer.md").read_text(encoding="utf-8")
        self.reviewer = (PACKAGE / "references/context-reviewer.md").read_text(encoding="utf-8")

    def test_short_router_keeps_routing_and_negative_durable_gates(self):
        self.assertLessEqual(len(self.main), 3500)
        for required in ("one root read/session", "Invalidate writer-changed cached paths", "restrictive entry conditions", "Deduplicated reads", "Justify each extra branch",
                         "global, project or recurring-operation", "Formatting alone", "quoted/untrusted", "tentative brainstorming", "one-off instructions", "explicit remember/save", "active task now"):
            with self.subTest(required=required):
                self.assertIn(required, self.main)

    def test_mutation_leaf_async_and_truthful_state_contract(self):
        for required in ("ONLY designated writer subagents", "including indexes", "or write history", "Parent never writes",
                         "One writer in flight per vault", "queue/coalesce", "no polling or waiting", "Explicit vault-write tasks await verified", "Leaf children cannot delegate", "Reviewers never write", "queued, verified and failed"):
            with self.subTest(required=required):
                self.assertIn(required, self.main)
        for required in ("Re-read the exact owning target", "Deduplicate by meaning and scope", "preserve", "replace", "read back", "changed paths"):
            with self.subTest(required=required):
                self.assertIn(required.lower(), self.writer.lower())

    def test_reviewer_is_lazy_explicit_independent_exact_and_no_fallback(self):
        for required in ("Only on explicit user request", "independent read-only leaf", "exact parent transcript", "no parent estimate/fallback", "do not load it for ordinary tasks"):
            self.assertIn(required, self.main)
        for required in ("EXACT real parent", "around_message_id", "role_filter", "Deduplicate message IDs", "task-completion cutoff", "partial", "not automatic access", "hidden chain-of-thought", "not a runtime scheduler"):
            with self.subTest(required=required):
                self.assertIn(required, self.reviewer)
        self.assertEqual(list(PACKAGE.rglob("SKILL.md")), [PACKAGE / "SKILL.md"])
        config = json.loads((PACKAGE / "assets/context-reviewer.json").read_text())
        self.assertFalse(config["enabled"])
        self.assertEqual(config["mode"], "explicit-request-only")
        for path in [PACKAGE / "SKILL.md", PACKAGE / "references/context-reviewer.md", PACKAGE / "templates/context-reviewer-prompt.md", PACKAGE.parents[1] / "README.md"]:
            content = path.read_text(encoding="utf-8")
            self.assertNotIn("REMIND_REVIEWER_CHILD", content)
            self.assertNotIn("agent-estimated", content)
            self.assertNotIn("When enabled and", content)

    def test_writer_scope_indexes_history_and_non_security_boundary(self):
        for required in ("vault/10-global/", "vault/20-hermes/", "vault/30-cross-project-development/", "vault/40-projects/", "Recurring-operation rules", "Single-flight", "ancestor indexes", "rebuild/retry", "logical operation", "Index contract", "non-normative", "no entry for clarification-only", "at most one", "exact persisted rule", "procedural, not a runtime security boundary"):
            with self.subTest(required=required):
                self.assertIn(required, self.writer)

    def test_public_vault_remains_empty_starter(self):
        indexes = list((PACKAGE / "vault").rglob("*.md"))
        self.assertEqual(len(indexes), 6)
        self.assertTrue(all(path.name == "_index.md" for path in indexes))
        self.assertTrue(all("Empty starter" in p.read_text() for p in indexes))
        self.assertFalse((PACKAGE / "references/interaction-history.md").exists())
        template = (PACKAGE / "templates/interaction-history.md").read_text()
        self.assertEqual(template.count("<!-- append-below -->"), 1)
        self.assertFalse(any(line.startswith("- 20") for line in template.splitlines()))
        manifest = json.loads((PACKAGE / "templates/context-review-manifest.json").read_text())
        self.assertIn("loaded_evidence", manifest["files"][0])
        self.assertIn("supports", manifest["files"][0])


if __name__ == "__main__":
    unittest.main()
