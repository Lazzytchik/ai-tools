#!/usr/bin/env python3
"""Toggle and quantify the optional Remind context-efficiency review."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "assets" / "context-reviewer.json"


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"ERROR: cannot read {path}: {exc}") from exc


def save_config(config: dict) -> None:
    CONFIG.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def set_enabled(enabled: bool) -> None:
    config = load_json(CONFIG)
    config["enabled"] = enabled
    save_config(config)
    print("enabled" if enabled else "disabled")


def status() -> None:
    print(json.dumps(load_json(CONFIG), ensure_ascii=False, indent=2))


def review(path: Path, as_json: bool) -> None:
    config = load_json(CONFIG)
    manifest = load_json(path)
    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        raise SystemExit("ERROR: manifest.files must be a non-empty list")

    total_loaded = 0
    total_useful = 0
    rows = []
    threshold = float(config.get("low_utility_threshold", 0.25))

    for index, item in enumerate(files, 1):
        if not isinstance(item, dict):
            raise SystemExit(f"ERROR: files[{index}] must be an object")
        file_path = str(item.get("path", "")).strip()
        loaded = item.get("loaded_chars")
        useful = item.get("useful_chars")
        if not file_path or not isinstance(loaded, int) or not isinstance(useful, int):
            raise SystemExit(f"ERROR: files[{index}] requires path and integer loaded_chars/useful_chars")
        if loaded <= 0 or useful < 0 or useful > loaded:
            raise SystemExit(f"ERROR: invalid character counts for {file_path}")
        ratio = useful / loaded
        total_loaded += loaded
        total_useful += useful
        if useful == 0:
            classification = "unused"
            suggestion = "Do not load this file by default; tighten its parent index gate."
        elif ratio < threshold:
            classification = "low-utility"
            suggestion = "Load a narrower range or split/condense the file around the used information."
        else:
            classification = "useful"
            suggestion = "Keep the current route."
        rows.append({
            "path": file_path,
            "loaded_chars": loaded,
            "useful_chars": useful,
            "utility_percent": round(ratio * 100, 1),
            "classification": classification,
            "used_for": str(item.get("used_for", "")).strip(),
            "suggestion": suggestion,
        })

    report = {
        "task": manifest.get("task", ""),
        "attribution": manifest.get("attribution", "agent-estimated"),
        "loaded_chars": total_loaded,
        "useful_chars": total_useful,
        "useful_context_percent": round(total_useful / total_loaded * 100, 1),
        "unnecessary_files": [row for row in rows if row["classification"] != "useful"],
        "files": rows,
    }

    if as_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return

    print(f"Useful context: {report['useful_context_percent']:.1f}% ({total_useful}/{total_loaded} chars)")
    print(f"Attribution: {report['attribution']}")
    if not report["unnecessary_files"]:
        print("No unused or low-utility files found.")
        return
    print("Unused or low-utility files:")
    for row in report["unnecessary_files"]:
        print(f"- {row['path']}: {row['utility_percent']:.1f}% — {row['classification']}")
        if row["used_for"]:
            print(f"  Used for: {row['used_for']}")
        print(f"  Fix: {row['suggestion']}")


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("enable")
    sub.add_parser("disable")
    sub.add_parser("status")
    review_parser = sub.add_parser("review")
    review_parser.add_argument("manifest", type=Path)
    review_parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.command == "enable":
        set_enabled(True)
    elif args.command == "disable":
        set_enabled(False)
    elif args.command == "status":
        status()
    else:
        review(args.manifest, args.json)


if __name__ == "__main__":
    main()
