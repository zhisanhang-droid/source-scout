#!/usr/bin/env python
"""Show the latest structured runtime validation status for access surfaces."""

from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any

import yaml


ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_yaml(path: pathlib.Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_latest_results() -> dict[str, dict[str, Any]]:
    path = ROOT / "validation" / "runtime-results.jsonl"
    latest: dict[str, dict[str, Any]] = {}
    if not path.exists():
        return latest
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            latest[row["surface_id"]] = row
    return latest


def main() -> int:
    parser = argparse.ArgumentParser(description="Show latest runtime validation results.")
    parser.add_argument("--source", help="Filter by parent_source.")
    parser.add_argument("--status", help="Filter by latest runtime_status.")
    parser.add_argument("--limit", type=int, default=80)
    args = parser.parse_args()

    surfaces = load_yaml(ROOT / "access" / "access-surfaces.yaml").get("access_surfaces", [])
    latest = load_latest_results()
    rows = []
    for surface in surfaces:
        if args.source and surface.get("parent_source") != args.source:
            continue
        row = latest.get(surface["surface_id"])
        runtime_status = row.get("runtime_status") if row else "unchecked"
        if args.status and runtime_status != args.status:
            continue
        rows.append((surface, row, runtime_status))

    print(f"surfaces={len(rows)}")
    print("status_counts=" + ", ".join(
        f"{status}:{sum(1 for _, _, row_status in rows if row_status == status)}"
        for status in sorted({row_status for _, _, row_status in rows})
    ))
    print()
    for surface, row, runtime_status in rows[: args.limit]:
        checked_at = row.get("checked_at", "-") if row else "-"
        detail = row.get("detail", "not checked") if row else "not checked"
        print(f"{surface['surface_id']} | parent={surface['parent_source']} | declared={surface['status']} | runtime={runtime_status} | checked={checked_at}")
        print(f"  entry: {'; '.join(surface.get('entry_points', [])[:2])}")
        print(f"  detail: {detail}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
