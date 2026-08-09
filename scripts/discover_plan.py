#!/usr/bin/env python
"""Generate an active discovery plan for finding new information sources."""

from __future__ import annotations

import argparse
import pathlib
import re
from typing import Any

import yaml


ROOT = pathlib.Path(__file__).resolve().parents[1]


DISCOVERY_LADDERS = [
    {
        "name": "implementation trail",
        "when": ["open source", "implementation", "code", "plugin", "mcp", "scraper", "automation"],
        "surfaces": ["github_code_search", "github_issue_global_search", "npm_package_search", "pypi_package_search", "mcp_official_registry_api"],
        "queries": [
            'site:github.com "{platform}" "{problem}"',
            '"{platform}" "content_scripts"',
            '"{platform}" "persistent context"',
            '"{platform}" "MCP server"',
        ],
    },
    {
        "name": "real browser workaround trail",
        "when": ["captcha", "429", "login", "session", "browser", "extension", "anti bot"],
        "surfaces": ["chrome_web_store_search", "userscript_greasyfork_search", "github_awesome_browser_automation", "playwright_official_docs_search", "chrome_debugging_protocol_docs"],
        "queries": [
            '"{platform}" "Chrome extension" scraper',
            '"{platform}" Tampermonkey export',
            '"{platform}" "use existing browser session"',
            '"{platform}" "headful" "Playwright"',
            '"{platform}" "Chrome DevTools Protocol"',
        ],
    },
    {
        "name": "community failure trail",
        "when": ["not working", "blocked", "alternative", "experience", "reddit", "community"],
        "surfaces": ["reddit_google_site_search", "reddit_native_global_search", "hackernews_algolia_comments_search", "stackoverflow_tag_search", "v2ex_site_search"],
        "queries": [
            'site:reddit.com "{tool}" "alternative"',
            'site:reddit.com "{platform}" "blocked"',
            '"{platform}" "429" "workaround"',
            '"{tool}" "not working" "comments"',
        ],
    },
    {
        "name": "marketplace packaged workflow trail",
        "when": ["api", "actor", "marketplace", "tool", "dataset", "export"],
        "surfaces": ["apify_actor_search", "rapidapi_search", "chrome_web_store_search", "producthunt_search", "alternativeto_search"],
        "queries": [
            '"{platform}" Apify actor',
            '"{platform}" RapidAPI',
            '"{platform}" exporter extension',
            '"{platform}" data API alternative',
        ],
    },
    {
        "name": "hidden source-type trail",
        "when": ["unknown", "new domain", "where people discuss", "source discovery"],
        "surfaces": ["osint_framework_browse", "awesome_osint_github_search", "newsletter_archive_search", "youtube_search", "bilibili_search"],
        "queries": [
            '"{domain}" "awesome list"',
            '"{domain}" community forum',
            '"{domain}" Discord',
            '"{domain}" newsletter tools',
            '"{domain}" tutorial browser automation',
        ],
    },
]


def load_yaml(path: pathlib.Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]{3,}", text.lower()))


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate active source-discovery plan.")
    parser.add_argument("problem", nargs="+")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    problem = " ".join(args.problem)
    tokens = tokenize(problem)
    surfaces = {s["surface_id"]: s for s in load_yaml(ROOT / "access" / "access-surfaces.yaml")["access_surfaces"]}

    scored = []
    for ladder in DISCOVERY_LADDERS:
        score = 1
        hits = []
        for word in ladder["when"]:
            word_tokens = tokenize(word)
            if word.lower() in problem.lower() or tokens.intersection(word_tokens):
                score += 3
                hits.append(word)
        scored.append((score, ladder, hits))
    scored.sort(key=lambda row: row[0], reverse=True)

    print("ACTIVE_DISCOVERY_PLAN")
    print(f"problem={problem}")
    print()
    for score, ladder, hits in scored[: args.limit]:
        print(f"{ladder['name']} | score={score} | triggers={', '.join(hits) if hits else 'broad fallback'}")
        print("  access_surfaces:")
        for surface_id in ladder["surfaces"]:
            surface = surfaces.get(surface_id)
            if not surface:
                continue
            print(f"    - {surface_id} | parent={surface['parent_source']} | type={surface['access_type']} | status={surface['status']}")
            print(f"      entry: {'; '.join(surface.get('entry_points', [])[:2])}")
            print(f"      validate: {surface.get('validation', {}).get('method')}")
        print("  discovery_queries:")
        for query in ladder["queries"]:
            print(f"    - {query}")
        print("  add_to_source_map_when:")
        print("    - A new source type, registry, marketplace, community, or access method repeatedly yields useful evidence.")
        print("    - The access path is concrete enough to document entry point, query template, retrieval depth, failure signals, and fallback.")
        print()

    print("QUALITY_GATE")
    print("- Do not accept a new source just because it exists; require fit, access method, retrieval depth, and failure signals.")
    print("- If all evidence comes from official/API/SaaS pages, run at least one community trail and one implementation trail.")
    print("- If native access is blocked, test a browser/session/manual route before marking the source low value.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
