#!/usr/bin/env python
"""Generate a Source Scout maintenance report."""

from __future__ import annotations

import datetime as dt
import pathlib
import subprocess
import sys
from typing import Any

import yaml


ROOT = pathlib.Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def load_yaml(path: pathlib.Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_command(args: list[str]) -> tuple[int, str]:
    proc = subprocess.run(args, cwd=ROOT.parent, text=True, capture_output=True)
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def watch_sources() -> list[dict[str, Any]]:
    index = load_yaml(ROOT / "sources" / "source-index.yaml")
    rows = []
    for item in index["sources"]:
        path = ROOT / item["file"]
        source = load_yaml(path)
        if source.get("status") in {"watch", "stale"}:
            rows.append(
                {
                    "source_id": source["source_id"],
                    "status": source.get("status"),
                    "file": item["file"],
                    "known_failures": source.get("maintenance", {}).get("known_failures", []),
                }
            )
    return rows


def main() -> int:
    now = dt.datetime.now()
    report_path = ROOT / "maintenance" / f"{now.strftime('%Y-%m-%d-%H%M%S')}-maintenance-report.md"
    validate_code, validate_output = run_command([PYTHON, str(ROOT / "scripts" / "validate_source_map.py")])
    due_code, due_output = run_command([PYTHON, str(ROOT / "scripts" / "maintenance_due.py")])

    watch_lines = []
    for source in watch_sources():
        failures = "; ".join(source["known_failures"]) if source["known_failures"] else ""
        watch_lines.append(f"| {source['source_id']} | {source['status']} | {source['file']} | {failures} |")
    watch_table = "\n".join(watch_lines) if watch_lines else "|  |  |  |  |"

    content = f"""# Maintenance Report

Date: {now.strftime('%Y-%m-%d %H:%M:%S')}
Scope: Source Map validation, due maintenance, watch/stale sources.

## Validation

Exit code: {validate_code}

```text
{validate_output}
```

## Due Sources

Exit code: {due_code}

```text
{due_output}
```

## Watch / Stale Sources

| Source | Status | File | Known failures |
|---|---|---|---|
{watch_table}

## Next Actions

- Investigate due sources first.
- For watch sources, promote to active only after repeated useful results.
- For stale sources, either repair access method or add replacement source candidates.
"""
    report_path.write_text(content, encoding="utf-8")
    print(report_path)
    return 0 if validate_code == 0 else validate_code


if __name__ == "__main__":
    sys.exit(main())

