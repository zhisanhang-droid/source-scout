#!/usr/bin/env python
"""Generate a coverage report for Source Scout."""

from __future__ import annotations

import collections
import json
import datetime as dt
import pathlib
from typing import Any

import yaml


ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_yaml(path: pathlib.Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_latest_runtime_results() -> dict[str, dict[str, Any]]:
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
    source_index = load_yaml(ROOT / "sources" / "source-index.yaml")["sources"]
    surfaces = load_yaml(ROOT / "access" / "access-surfaces.yaml")["access_surfaces"]
    runtime = load_latest_runtime_results()
    by_source = collections.defaultdict(list)
    for surface in surfaces:
        by_source[surface["parent_source"]].append(surface)

    lines = [
        "# Source Scout Coverage Report",
        "",
        f"Date: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"- Indexed sources: {len(source_index)}",
        f"- Access surfaces: {len(surfaces)}",
        "",
        "## Source Coverage",
        "",
        "| Source | Priority | Surfaces | Active | Watch | Needs validation | Runtime ok | Runtime limited/failed | Top access types |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for item in source_index:
        source_id = item["source_id"]
        rows = by_source.get(source_id, [])
        statuses = collections.Counter(s["status"] for s in rows)
        types = collections.Counter(s["access_type"] for s in rows)
        runtime_statuses = collections.Counter(runtime.get(s["surface_id"], {}).get("runtime_status", "unchecked") for s in rows)
        top_types = ", ".join(f"{k}:{v}" for k, v in types.most_common(3))
        lines.append(
            f"| {source_id} | {item['priority']} | {len(rows)} | {statuses.get('active', 0)} | {statuses.get('watch', 0)} | {statuses.get('needs_validation', 0)} | {runtime_statuses.get('ok', 0)} | {runtime_statuses.get('reachable_limited', 0) + runtime_statuses.get('failed', 0) + runtime_statuses.get('http_error', 0)} | {top_types} |"
        )

    weak = [item["source_id"] for item in source_index if len(by_source.get(item["source_id"], [])) < 2]
    needs = [s for s in surfaces if s["status"] == "needs_validation"]
    watch = [s for s in surfaces if s["status"] == "watch"]

    lines.extend(
        [
            "",
            "## Gaps",
            "",
            "Sources with fewer than 2 access surfaces:",
            "",
            ", ".join(weak) if weak else "None",
            "",
            f"Needs-validation surfaces: {len(needs)}",
            "",
            ", ".join(s["surface_id"] for s in needs[:30]) if needs else "None",
            "",
            f"Watch surfaces: {len(watch)}",
            "",
            ", ".join(s["surface_id"] for s in watch[:30]) if watch else "None",
            "",
            "## Runtime Validation Snapshot",
            "",
            ", ".join(f"{k}:{v}" for k, v in collections.Counter(row.get("runtime_status", "unknown") for row in runtime.values()).items()) if runtime else "No runtime checks recorded yet.",
        ]
    )

    report_path = ROOT / "maintenance" / f"{dt.datetime.now().strftime('%Y-%m-%d-%H%M%S')}-coverage-report.md"
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(report_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
