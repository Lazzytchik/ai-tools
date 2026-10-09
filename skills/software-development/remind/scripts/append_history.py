#!/usr/bin/env python3
"""Writer-only helper: append one terse non-normative summary atomically.

Caller must serialize with the vault writer queue; role is a procedural contract.
"""
from __future__ import annotations

import argparse
from datetime import date as iso_date, datetime, timezone
import os
from pathlib import Path
import tempfile

ROOT = Path(os.environ.get("REMIND_ROOT", Path(__file__).resolve().parents[1]))
HISTORY = ROOT / "references" / "interaction-history.md"
MARKER = "<!-- append-below -->"
MAX_SCOPE = 80
MAX_SUMMARY = 240


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def clean(value: str, name: str, limit: int) -> str:
    value = " ".join(value.split())
    if not value:
        fail(f"{name} must not be empty")
    if len(value) > limit:
        fail(f"{name} exceeds {limit} characters")
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--date", help="ISO YYYY-MM-DD; defaults to current UTC date")
    args = parser.parse_args()
    scope = clean(args.scope, "scope", MAX_SCOPE)
    summary = clean(args.summary, "summary", MAX_SUMMARY)
    date = args.date or datetime.now(timezone.utc).date().isoformat()
    try:
        if iso_date.fromisoformat(date).isoformat() != date:
            fail("date must be ISO YYYY-MM-DD")
    except ValueError:
        fail("date must be ISO YYYY-MM-DD")
    if not HISTORY.exists():
        fail(f"missing history file: {HISTORY}")
    old = HISTORY.read_text(encoding="utf-8")
    if old.count(MARKER) != 1:
        fail("history append marker missing or duplicated")
    entry = f"- {date} — {scope} — {summary}"
    new = old.replace(MARKER, f"{MARKER}\n{entry}", 1)
    fd, raw = tempfile.mkstemp(prefix=".interaction-history.", suffix=".tmp", dir=HISTORY.parent)
    tmp = Path(raw)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(new)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, HISTORY)
    finally:
        tmp.unlink(missing_ok=True)
    print(entry)


if __name__ == "__main__":
    main()
