#!/usr/bin/env python
"""List Source Scout access surfaces."""

from __future__ import annotations

import argparse
import collections
import pathlib
import sys
from typing import Any

import yaml


ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_yaml(path: pathlib.Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_surfaces() -> list[dict[str, Any]]:
    data = load_yaml(ROOT / "access" / "access-surfaces.yaml")
    return data.get("access_surfaces", [])


def matches(surface: dict[str, Any], args: argparse.Namespace) -> bool:
    if args.source and surface.get("parent_source") != args.source:
        return False
    if args.status and surface.get("status") != args.status:
        return False
    if args.access_type and surface.get("access_type") != args.access_type:
        return False
    if args.query:
        text = " ".join(
            [
                surface.get("surface_id", ""),
                surface.get("name", ""),
                surface.get("parent_source", ""),
                " ".join(surface.get("best_for", [])),
                " ".join(surface.get("query_templates", [])),
            ]
        ).lower()
        if args.query.lower() not in text:
            return False
    return True


def print_summary(surfaces: list[dict[str, Any]]) -> None:
    by_source = collections.Counter(s["parent_source"] for s in surfaces)
    by_status = collections.Counter(s["status"] for s in surfaces)
    by_type = collections.Counter(s["access_type"] for s in surfaces)
    print(f"total_surfaces={len(surfaces)}")
    print("by_source=" + ", ".join(f"{k}:{v}" for k, v in sorted(by_source.items())))
    print("by_status=" + ", ".join(f"{k}:{v}" for k, v in sorted(by_status.items())))
    print("by_access_type=" + ", ".join(f"{k}:{v}" for k, v in sorted(by_type.items())))


def main() -> int:
    parser = argparse.ArgumentParser(description="List access surfaces.")
    parser.add_argument("--source", help="Filter by parent source_id.")
    parser.add_argument("--status", help="Filter by status.")
    parser.add_argument("--access-type", help="Filter by access_type.")
    parser.add_argument("--query", help="Free-text filter.")
    parser.add_argument("--summary", action="store_true", help="Print only summary counts.")
    parser.add_argument("--limit", type=int, default=200, help="Max rows to show.")
    args = parser.parse_args()

    surfaces = [s for s in load_surfaces() if matches(s, args)]
    if args.summary:
        print_summary(surfaces)
        return 0

    print_summary(surfaces)
    print()
    for surface in surfaces[: args.limit]:
        print(f"{surface['surface_id']} | parent={surface['parent_source']} | type={surface['access_type']} | status={surface['status']} | priority={surface['priority']}")
        print(f"  name: {surface['name']}")
        print(f"  best_for: {'; '.join(surface.get('best_for', [])[:3])}")
        print(f"  entry: {'; '.join(surface.get('entry_points', [])[:2])}")
        for template in surface.get("query_templates", [])[:3]:
            print(f"  query: {template}")
        validation = surface.get("validation", {})
        print(f"  validate: {validation.get('method')}")
        print(f"  failure: {'; '.join(validation.get('failure_signals', [])[:2])}")
        print(f"  fallback: {', '.join(surface.get('fallback_surfaces', []))}")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())

