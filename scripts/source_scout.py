#!/usr/bin/env python
"""Unified Source Scout command wrapper."""

from __future__ import annotations

import pathlib
import subprocess
import sys


HERE = pathlib.Path(__file__).resolve().parent
PYTHON = sys.executable

COMMANDS = {
    "select": "select_sources.py",
    "validate": "validate_source_map.py",
    "due": "maintenance_due.py",
    "maintain": "run_maintenance_check.py",
    "surfaces": "list_surfaces.py",
    "runtime-check": "check_access_runtime.py",
    "validation-status": "validation_status.py",
    "validation-queue": "validation_queue.py",
    "coverage": "coverage_report.py",
    "log": "new_search_log.py",
    "feedback": "record_feedback.py",
    "export-prompt": "export_prompt_pack.py",
    "discover-plan": "discover_plan.py",
}


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] in {"-h", "--help", "help"}:
        print("Usage: source_scout.py <select|surfaces|validate|due|maintain|runtime-check|validation-status|validation-queue|coverage|log|feedback|export-prompt|discover-plan> [args...]")
        return 0
    command = sys.argv[1]
    script = COMMANDS.get(command)
    if not script:
        print(f"Unknown command: {command}", file=sys.stderr)
        return 2
    return subprocess.call([PYTHON, str(HERE / script), *sys.argv[2:]])


if __name__ == "__main__":
    sys.exit(main())
