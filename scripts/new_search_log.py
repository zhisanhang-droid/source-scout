#!/usr/bin/env python
"""Create a timestamped Source Scout search log from a task summary."""

from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import re
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", text)
    text = text.strip("-")
    return text[:60] or "search"


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a Source Scout search log.")
    parser.add_argument("--task", required=True, help="Task name or user problem.")
    parser.add_argument("--problem-type", default="", help="Classified problem type.")
    parser.add_argument("--sources", default="", help="Comma-separated selected sources.")
    parser.add_argument("--feedback", default="", help="Initial user or agent feedback.")
    args = parser.parse_args()

    now = dt.datetime.now().strftime("%Y-%m-%d-%H%M%S")
    path = ROOT / "logs" / f"{now}-{slugify(args.task)}.md"
    sources = [s.strip() for s in args.sources.split(",") if s.strip()]

    rows = "\n".join(f"| {source} |  | selected from Source Map |" for source in sources)
    content = f"""# Search Log

Date: {dt.date.today().isoformat()}
Task: {args.task}
Problem type: {args.problem_type}

## Selected Sources

| Source | Access method | Why selected |
|---|---|---|
{rows}

## Queries

| Source | Query | Result quality | Notes |
|---|---|---|---|

## Evidence

| Source | URL / Path | Evidence type | Reliability |
|---|---|---|---|

## Source Quality Notes

High value:
Medium value:
Low value:
Stale or blocked:

## Missing-source Risk

## Proposed Source Map Updates

## User Feedback

{args.feedback}
"""
    path.write_text(content, encoding="utf-8")
    print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())

