#!/usr/bin/env python
"""Run lightweight runtime checks for URL-based access surfaces."""

from __future__ import annotations

import argparse
import json
import datetime as dt
import pathlib
import re
import socket
import sys
import urllib.error
import urllib.request
from typing import Any

import yaml


ROOT = pathlib.Path(__file__).resolve().parents[1]
URL_RE = re.compile(r"^https?://")


def load_yaml(path: pathlib.Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def surfaces() -> list[dict[str, Any]]:
    data = load_yaml(ROOT / "access" / "access-surfaces.yaml")
    return data.get("access_surfaces", [])


def check_url(url: str, timeout: int) -> tuple[str, str]:
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": "SourceScout/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return "ok", f"HTTP {resp.status}"
    except urllib.error.HTTPError as e:
        if e.code in {401, 403, 429}:
            return "reachable_limited", f"HTTP {e.code}"
        return "http_error", f"HTTP {e.code}"
    except (urllib.error.URLError, TimeoutError, socket.timeout) as e:
        return "failed", str(e)[:160]


def main() -> int:
    parser = argparse.ArgumentParser(description="Check URL entry points for access surfaces.")
    parser.add_argument("--limit", type=int, default=12, help="Maximum URL checks.")
    parser.add_argument("--timeout", type=int, default=4, help="Per-request timeout seconds.")
    parser.add_argument("--source", help="Filter by parent_source.")
    args = parser.parse_args()

    checks = []
    seen_urls: set[str] = set()
    for surface in surfaces():
        if args.source and surface.get("parent_source") != args.source:
            continue
        for entry in surface.get("entry_points", []):
            if not isinstance(entry, str) or not URL_RE.match(entry):
                continue
            if "{" in entry or entry in seen_urls:
                continue
            seen_urls.add(entry)
            checks.append((surface, entry))
            if len(checks) >= args.limit:
                break
        if len(checks) >= args.limit:
            break

    checked_at = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows = []
    structured_rows = []
    for surface, url in checks:
        status, detail = check_url(url, args.timeout)
        rows.append((surface["surface_id"], surface["parent_source"], url, status, detail))
        structured_rows.append(
            {
                "surface_id": surface["surface_id"],
                "parent_source": surface["parent_source"],
                "url": url,
                "runtime_status": status,
                "detail": detail,
                "checked_at": checked_at,
                "scope": "entry_point_reachability",
            }
        )
        print(f"{status} | {surface['surface_id']} | {url} | {detail}")

    report_dir = ROOT / "maintenance"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"{dt.datetime.now().strftime('%Y-%m-%d-%H%M%S')}-runtime-access-check.md"
    table = "\n".join(f"| {sid} | {parent} | {url} | {status} | {detail} |" for sid, parent, url, status, detail in rows)
    report_path.write_text(
        f"""# Runtime Access Check

Date: {checked_at}
Scope: URL entry point reachability. This does not prove search quality or retrieval depth.

| Surface | Parent source | URL | Status | Detail |
|---|---|---|---|---|
{table}
""",
        encoding="utf-8",
    )
    validation_dir = ROOT / "validation"
    validation_dir.mkdir(parents=True, exist_ok=True)
    result_path = validation_dir / "runtime-results.jsonl"
    with result_path.open("a", encoding="utf-8") as f:
        for row in structured_rows:
            f.write(json.dumps(row, ensure_ascii=True) + "\n")
    print(report_path)
    print(result_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
