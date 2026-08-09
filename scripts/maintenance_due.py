#!/usr/bin/env python
"""List Source Scout sources whose maintenance check is due."""

from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import sys
from typing import Any

import yaml


ROOT = pathlib.Path(__file__).resolve().parents[1]
CADENCE_DAYS = {
    "weekly": 7,
    "monthly": 30,
    "quarterly": 90,
    "ad_hoc": None,
}


def load_yaml(path: pathlib.Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def parse_date(value: str) -> dt.date | None:
    try:
        return dt.date.fromisoformat(str(value))
    except ValueError:
        return None


def load_sources() -> list[tuple[pathlib.Path, dict[str, Any]]]:
    index = load_yaml(ROOT / "sources" / "source-index.yaml")
    loaded = []
    for item in index["sources"]:
        path = ROOT / item["file"]
        loaded.append((path, load_yaml(path)))
    return loaded


def main() -> int:
    parser = argparse.ArgumentParser(description="List maintenance-due Source Scout sources.")
    parser.add_argument("--today", default=dt.date.today().isoformat(), help="Override today's date YYYY-MM-DD.")
    parser.add_argument("--all", action="store_true", help="Show all sources with due status.")
    args = parser.parse_args()

    today = parse_date(args.today)
    if today is None:
        print(f"Invalid --today date: {args.today}", file=sys.stderr)
        return 2

    due_rows = []
    all_rows = []
    for path, source in load_sources():
        maintenance = source.get("maintenance", {})
        cadence = maintenance.get("check_frequency")
        last_checked = parse_date(str(maintenance.get("last_checked", "")))
        days = CADENCE_DAYS.get(cadence)
        status = source.get("status", "unknown")

        if days is None or last_checked is None:
            due = status in {"stale", "watch"}
            age = "unknown"
        else:
            age_days = (today - last_checked).days
            due = age_days >= days or status == "stale"
            age = f"{age_days}d"

        row = (due, source["source_id"], status, cadence, maintenance.get("last_checked"), age, path)
        all_rows.append(row)
        if due:
            due_rows.append(row)

    rows = all_rows if args.all else due_rows
    if not rows:
        print("No sources are due for maintenance.")
        return 0

    for due, source_id, status, cadence, last_checked, age, path in rows:
        marker = "DUE" if due else "OK"
        print(f"{marker} | {source_id} | status={status} | cadence={cadence} | last_checked={last_checked} | age={age} | {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

