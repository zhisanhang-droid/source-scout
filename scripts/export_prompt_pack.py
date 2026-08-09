#!/usr/bin/env python
"""Export a compact Source Scout prompt pack for other AI tools."""

from __future__ import annotations

import argparse
import datetime as dt
import pathlib
from typing import Any

import yaml


ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_yaml(path: pathlib.Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def pick_sources(problem_type: str) -> tuple[list[str], list[str]]:
    routing = load_yaml(ROOT / "routing" / "problem-type-routing.yaml").get("problem_types", {})
    route = routing.get(problem_type)
    if not route:
        choices = ", ".join(sorted(routing))
        raise SystemExit(f"Unknown problem_type: {problem_type}. Choose one of: {choices}")
    return route.get("default_sources", []), route.get("escalation_sources", [])


def main() -> int:
    parser = argparse.ArgumentParser(description="Export a reusable Source Scout prompt pack.")
    parser.add_argument("--problem-type", default="data_collection_antibot")
    parser.add_argument("--task", default="{describe the concrete problem}")
    parser.add_argument("--top", type=int, default=18, help="Maximum access surfaces to include.")
    parser.add_argument("--output", help="Optional output Markdown path.")
    args = parser.parse_args()

    default_sources, escalation_sources = pick_sources(args.problem_type)
    source_index = {s["source_id"]: s for s in load_yaml(ROOT / "sources" / "source-index.yaml")["sources"]}
    surfaces = load_yaml(ROOT / "access" / "access-surfaces.yaml")["access_surfaces"]
    selected_sources = default_sources + [s for s in escalation_sources if s not in default_sources]
    selected = [s for s in surfaces if s["parent_source"] in selected_sources]
    selected.sort(key=lambda s: (s["parent_source"] not in default_sources, -int(s.get("priority", 0) or 0), s["surface_id"]))
    selected = selected[: args.top]

    lines = [
        "# Source Scout Prompt Pack",
        "",
        f"Generated: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Problem type: `{args.problem_type}`",
        "",
        "## Task",
        "",
        args.task,
        "",
        "## Instructions For The AI",
        "",
        "You are not allowed to stop at official APIs, SaaS vendors, or generic web results. First choose the right information sources, then search their concrete access surfaces. Report what was searched, what was blocked, what was low value, and what source types may still be missing.",
        "",
        "Use at least 5 independent channels and at least 10 substantive sources when web research is required. For engineering workaround problems, include GitHub code/issues, community comments, package registries, browser/session automation routes, and marketplace/directories when relevant.",
        "",
        "## Source Mix",
        "",
        "Default sources:",
        "",
        ", ".join(default_sources),
        "",
        "Escalate to these if results are generic, blocked, stale, or too official/API-only:",
        "",
        ", ".join(escalation_sources),
        "",
        "## Concrete Access Surfaces",
        "",
    ]

    for surface in selected:
        source = source_index.get(surface["parent_source"], {})
        lines.extend(
            [
                f"### {surface['surface_id']}",
                "",
                f"- Parent source: `{surface['parent_source']}` ({source.get('name', surface['parent_source'])})",
                f"- Access type: `{surface['access_type']}`; status: `{surface['status']}`; priority: `{surface['priority']}`",
                f"- Best for: {'; '.join(surface.get('best_for', [])[:4])}",
                f"- Entry points: {'; '.join(surface.get('entry_points', [])[:3])}",
                f"- Query templates: {'; '.join(surface.get('query_templates', [])[:4])}",
                f"- Validation: {surface.get('validation', {}).get('method')}",
                f"- Failure signals: {'; '.join(surface.get('validation', {}).get('failure_signals', [])[:3])}",
                f"- Fallback surfaces: {', '.join(surface.get('fallback_surfaces', []))}",
                "",
            ]
        )

    lines.extend(
        [
            "## Required Output",
            "",
            "1. Selected source map: source cards plus concrete access surfaces.",
            "2. Evidence summary with links and source quality labels.",
            "3. Separate official facts, implementation evidence, community experience, and inference.",
            "4. Low-value, stale, blocked, or skipped sources.",
            "5. Missing-source risk: what types of sources may still be absent.",
            "6. Suggested updates to the source library: new source, better access method, failed access, or improved query pattern.",
            "",
        ]
    )

    text = "\n".join(lines)
    if args.output:
        path = pathlib.Path(args.output)
    else:
        out_dir = ROOT / "exports"
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f"{dt.datetime.now().strftime('%Y-%m-%d-%H%M%S')}-{args.problem_type}-prompt-pack.md"
    path.write_text(text + "\n", encoding="utf-8")
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
