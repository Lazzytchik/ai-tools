#!/usr/bin/env python3
"""Validate transcript evidence and quantify an explicitly requested leaf review.

No scheduler, role enforcement, provenance proof or semantic-utility classifier.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "assets" / "context-reviewer.json"


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        fail(f"{name} must be a non-empty string")
    return value


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        fail(f"cannot read {path}: {exc}")
    if not isinstance(value, dict):
        fail(f"{path} must contain a JSON object")
    return value


def save_config(config: dict) -> None:
    CONFIG.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def set_enabled(enabled: bool) -> None:
    config = load_json(CONFIG)
    config.update(enabled=enabled, mode="explicit-request-only")
    save_config(config)
    print("enabled (explicit requests only; no automatic scheduling)" if enabled else "disabled")


def status() -> None:
    print(json.dumps(load_json(CONFIG), ensure_ascii=False, indent=2))


def transcript_evidence(path: Path) -> tuple[dict, dict]:
    transcript = load_json(path)
    text(transcript.get("session_id"), "transcript.session_id")
    if transcript.get("source") not in ("parent-session-artifact", "session-search", "fixture"):
        fail("transcript.source must identify the actual artifact/search or test fixture")
    if transcript.get("coverage") not in ("complete", "partial"):
        fail("transcript.coverage must be complete or partial")
    limitations = transcript.get("limitations")
    if not isinstance(limitations, list) or any(not isinstance(x, str) or not x.strip() for x in limitations):
        fail("transcript.limitations must be a list of non-empty strings")
    if transcript["coverage"] == "partial" and not limitations:
        fail("partial coverage requires explicit limitations")
    start = text(transcript.get("task_start_id"), "transcript.task_start_id")
    end = text(transcript.get("task_end_id"), "transcript.task_end_id")
    rows = transcript.get("messages")
    if not isinstance(rows, list) or not rows:
        fail("transcript.messages must contain exact task messages")
    messages, calls = {}, set()
    for row in rows:
        if not isinstance(row, dict):
            fail("transcript message must be an object")
        key = text(row.get("id"), "message.id")
        if key in messages:
            fail(f"duplicate transcript message id: {key}")
        if row.get("role") not in ("user", "assistant", "tool") or not isinstance(row.get("content"), str):
            fail(f"invalid role/content for message {key}")
        if "tool_calls" in row:
            if row["role"] != "assistant" or not isinstance(row["tool_calls"], list):
                fail(f"invalid tool_calls for message {key}")
            for call in row["tool_calls"]:
                if not isinstance(call, dict):
                    fail(f"invalid tool call in message {key}")
                call_id = text(call.get("id"), "tool call id")
                if call_id in calls:
                    fail(f"duplicate tool call id: {call_id}")
                calls.add(call_id)
        if row["role"] == "tool":
            text(row.get("tool_call_id"), f"message {key} tool_call_id")
        messages[key] = row
    if transcript["coverage"] == "complete":
        if rows[0]["id"] != start or rows[-1]["id"] != end or limitations:
            fail("complete task coverage requires exact first/last IDs and no known gaps")
        for key, row in messages.items():
            if row["role"] == "tool" and row["tool_call_id"] not in calls:
                fail(f"missing original tool call for result {key}")
    return transcript, messages


def spans(value: object, messages: dict, name: str) -> list[tuple[str, int, int]]:
    if not isinstance(value, list):
        fail(f"{name} must be an evidence list")
    result = []
    for span in value:
        if not isinstance(span, dict):
            fail(f"{name} span must be an object")
        key, start, end = span.get("message_id"), span.get("start"), span.get("end")
        if not isinstance(key, str) or key not in messages or messages[key]["role"] != "tool":
            fail(f"{name} must reference an actual tool-result message")
        if type(start) is not int or type(end) is not int or not 0 <= start < end <= len(messages[key]["content"]):
            fail(f"{name} contains invalid character bounds")
        result.append((key, start, end))
    result.sort()
    reject_overlaps(result, name)
    return result


def reject_overlaps(rows: list, name: str) -> None:
    for left, right in zip(rows, rows[1:]):
        if left[0] == right[0] and right[1] < left[2]:
            fail(f"{name} double-counts overlapping transcript spans")


def review(path: Path, as_json: bool, transcript_path: Path) -> None:
    config, manifest = load_json(CONFIG), load_json(path)
    transcript, messages = transcript_evidence(transcript_path)
    if manifest.get("attribution") != "independent-reviewer":
        fail("manifest attribution must be independent-reviewer; no parent estimate fallback")
    task = text(manifest.get("task"), "manifest.task")
    files = manifest.get("files")
    if not isinstance(files, list):
        fail("manifest.files must be a list (empty is valid for no file reads)")
    threshold = config.get("low_utility_threshold", 0.25)
    if type(threshold) not in (int, float) or not math.isfinite(threshold) or not 0 <= threshold <= 1:
        fail("low_utility_threshold must be finite and between 0 and 1")
    total_loaded, total_useful, rows, inventory, all_loaded = 0, 0, [], set(), []
    for index, item in enumerate(files, 1):
        if not isinstance(item, dict):
            fail(f"files[{index}] must be an object")
        file_path = text(item.get("path"), f"files[{index}].path")
        if file_path in inventory:
            fail(f"duplicate file path: {file_path}; aggregate repeated reads into one row")
        inventory.add(file_path)
        loaded, useful = item.get("loaded_chars"), item.get("useful_chars")
        if type(loaded) is not int or type(useful) is not int or loaded <= 0 or not 0 <= useful <= loaded:
            fail(f"invalid integer character counts for {file_path}")
        evidence = spans(item.get("loaded_evidence"), messages, "loaded_evidence")
        selected = spans(item.get("useful_evidence"), messages, "useful_evidence")
        if sum(end - start for _, start, end in evidence) != loaded or sum(end - start for _, start, end in selected) != useful:
            fail(f"character counts do not match exact transcript spans for {file_path}")
        for key, start, end in selected:
            if not any(k == key and a <= start and end <= b for k, a, b in evidence):
                fail(f"useful evidence is outside loaded evidence for {file_path}")
        used_for, supports = item.get("used_for"), item.get("supports")
        if not isinstance(used_for, str) or not isinstance(supports, list) or any(not isinstance(k, str) or k not in messages for k in supports):
            fail(f"invalid used_for/supports for {file_path}")
        if useful and (not used_for.strip() or not supports):
            fail(f"useful context requires concrete use and supporting task message IDs for {file_path}")
        all_loaded.extend(evidence)
        ratio = useful / loaded
        classification = "unused" if not useful else "low-utility" if ratio < threshold else "useful"
        suggestion = {"unused": "Tighten the parent index gate; do not load by default.",
                      "low-utility": "Read a narrower range or split/condense the file.",
                      "useful": "Keep the current route."}[classification]
        rows.append(dict(path=file_path, loaded_chars=loaded, useful_chars=useful,
                         utility_percent=round(ratio * 100, 1), classification=classification,
                         used_for=used_for.strip(), supports=supports, suggestion=suggestion))
        total_loaded += loaded
        total_useful += useful
    reject_overlaps(sorted(all_loaded), "file inventory")
    report = dict(task=task, attribution="independent-reviewer", session_id=transcript["session_id"],
                  source=transcript["source"], coverage=transcript["coverage"],
                  task_start_id=transcript["task_start_id"], task_end_id=transcript["task_end_id"],
                  limitations=transcript["limitations"],
                  validation="transcript spans and arithmetic only; provenance/coverage/usefulness not proven",
                  loaded_chars=total_loaded, useful_chars=total_useful,
                  useful_context_percent=round(total_useful / total_loaded * 100, 1) if total_loaded else None,
                  unnecessary_files=[row for row in rows if row["classification"] != "useful"], files=rows)
    if as_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return
    percent = report["useful_context_percent"]
    print(f"Useful context: {percent}% ({total_useful}/{total_loaded} chars)" if percent is not None else "Useful context: not applicable (no file content loaded)")
    print(f"Attribution: independent-reviewer; coverage: {report['coverage']}; source: {report['source']}")
    print(f"Validation: {report['validation']}")
    for limitation in report["limitations"]:
        print(f"Limit: {limitation}")
    for row in report["unnecessary_files"]:
        print(f"- {row['path']}: {row['utility_percent']:.1f}% — {row['classification']}")
        print(f"  Used for: {row['used_for'] or 'none'}; Fix: {row['suggestion']}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("enable", help="Opt in to explicit reviews only; never schedules a review")
    sub.add_parser("disable")
    sub.add_parser("status")
    review_parser = sub.add_parser("review", help="Read-only evidence/arithmetic helper for reviewer leaf")
    review_parser.add_argument("manifest", type=Path)
    review_parser.add_argument("--transcript", type=Path, required=True)
    review_parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.command == "enable":
        set_enabled(True)
    elif args.command == "disable":
        set_enabled(False)
    elif args.command == "status":
        status()
    else:
        review(args.manifest, args.json, args.transcript)


if __name__ == "__main__":
    main()
