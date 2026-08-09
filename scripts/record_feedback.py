#!/usr/bin/env python
"""Record Source Scout feedback, optionally appending it to a source card history."""

from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import sys
from typing import Any

import yaml


ROOT = pathlib.Path(__file__).resolve().parents[1]
FEEDBACK_LOG = ROOT / "logs" / "feedback-log.md"


def load_yaml(path: pathlib.Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def dump_yaml(path: pathlib.Path, data: Any) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True, width=120)


def source_path(source_id: str) -> pathlib.Path:
    index = load_yaml(ROOT / "sources" / "source-index.yaml")
    for item in index["sources"]:
        if item["source_id"] == source_id:
            return ROOT / item["file"]
    raise KeyError(source_id)


def append_feedback_log(args: argparse.Namespace) -> None:
    FEEDBACK_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = f"""## {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {args.task}

- Source: {args.source}
- Result quality: {args.result_quality}
- Access method: {args.access_method or ''}
- Feedback: {args.feedback}
- Proposed action: {args.proposed_action or ''}

"""
    with FEEDBACK_LOG.open("a", encoding="utf-8", newline="\n") as f:
        f.write(entry)


def append_source_history(args: argparse.Namespace) -> pathlib.Path:
    path = source_path(args.source)
    data = load_yaml(path)
    data.setdefault("history", []).append(
        {
            "date": dt.date.today().isoformat(),
            "task": args.task,
            "access_method": args.access_method or "unspecified",
            "result_quality": args.result_quality,
            "feedback": args.feedback,
        }
    )
    if args.known_failure:
        failures = data.setdefault("maintenance", {}).setdefault("known_failures", [])
        if args.known_failure not in failures:
            failures.append(args.known_failure)
    if args.status:
        data["status"] = args.status
    dump_yaml(path, data)
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Record Source Scout feedback.")
    parser.add_argument("--source", required=True, help="source_id, e.g. reddit")
    parser.add_argument("--task", required=True, help="Task or problem name.")
    parser.add_argument("--result-quality", required=True, choices=["high", "medium", "low", "stale", "blocked"])
    parser.add_argument("--feedback", required=True, help="Concrete feedback or failure detail.")
    parser.add_argument("--access-method", default="", help="Access method used.")
    parser.add_argument("--proposed-action", default="", help="Suggested follow-up action.")
    parser.add_argument("--known-failure", default="", help="Failure to add to source maintenance. Requires --update-card.")
    parser.add_argument("--status", choices=["active", "watch", "stale", "deprecated"], help="Optional new source status. Requires --update-card.")
    parser.add_argument("--update-card", action="store_true", help="Also append feedback to the source card history.")
    args = parser.parse_args()

    try:
        source_path(args.source)
    except KeyError:
        print(f"Unknown source_id: {args.source}", file=sys.stderr)
        return 2

    append_feedback_log(args)
    print(FEEDBACK_LOG)
    if args.update_card:
        path = append_source_history(args)
        print(path)
    elif args.known_failure or args.status:
        print("Note: --known-failure and --status are ignored unless --update-card is set.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

