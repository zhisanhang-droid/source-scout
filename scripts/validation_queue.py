#!/usr/bin/env python
"""Prioritize access surfaces that need validation."""

from __future__ import annotations

import argparse
import pathlib
from typing import Any

import yaml


ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_yaml(path: pathlib.Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> int:
    parser = argparse.ArgumentParser(description="List access surfaces needing validation.")
    parser.add_argument("--status", choices=["watch", "needs_validation", "stale", "blocked"], help="Filter by status.")
    parser.add_argument("--min-priority", type=int, default=3)
    parser.add_argument("--limit", type=int, default=40)
    args = parser.parse_args()

    surfaces = load_yaml(ROOT / "access" / "access-surfaces.yaml").get("access_surfaces", [])
    candidates = []
    for surface in surfaces:
        status = surface.get("status")
        priority = int(surface.get("priority", 0) or 0)
        if args.status and status != args.status:
            continue
        if not args.status and status not in {"watch", "needs_validation", "stale", "blocked"}:
            continue
        if priority < args.min_priority:
            continue
        candidates.append(surface)
    candidates.sort(key=lambda s: (s.get("status") == "needs_validation", int(s.get("priority", 0) or 0)), reverse=True)

    for surface in candidates[: args.limit]:
        validation = surface.get("validation", {})
        print(f"{surface['surface_id']} | parent={surface['parent_source']} | status={surface['status']} | priority={surface['priority']}")
        print(f"  type={surface['access_type']} | login={surface['login_required']} | automation={surface['automation_level']}")
        print(f"  validate={validation.get('method')}")
        print(f"  success={'; '.join(validation.get('success_criteria', [])[:2])}")
        print(f"  failure={'; '.join(validation.get('failure_signals', [])[:2])}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

