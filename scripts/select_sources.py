#!/usr/bin/env python
"""Select likely Source Scout sources for a problem statement."""

from __future__ import annotations

import argparse
import pathlib
import re
import sys
from typing import Any

import yaml


ROOT = pathlib.Path(__file__).resolve().parents[1]


DOMAIN_KEYWORDS = {
    "ecommerce": [
        "amazon",
        "1688",
        "alibaba",
        "keepa",
        "sorftime",
        "importyeti",
        "supplier",
        "price",
        "cost",
        "asin",
        "listing",
        "sourcing",
        "product",
        "factory",
        "quote",
    ],
    "engineering": [
        "github",
        "code",
        "open source",
        "implementation",
        "bug",
        "api",
        "mcp",
        "plugin",
        "extension",
        "playwright",
        "tampermonkey",
        "userscript",
    ],
    "consumer_feedback": [
        "review",
        "complaint",
        "reddit",
        "feedback",
        "user",
        "community",
        "experience",
        "worth it",
    ],
    "data_collection": [
        "scrape",
        "scraper",
        "crawl",
        "data",
        "trend",
        "captcha",
        "429",
        "rate limit",
        "browser",
        "session",
        "export",
        "dataset",
    ],
    "ai_tools": [
        "ai",
        "agent",
        "mcp",
        "llm",
        "codex",
        "claude",
        "gpt",
        "tool",
        "automation",
        "research agent",
    ],
}

SOURCE_HINTS = {
    "local_workspace": ["local", "already built", "previous", "tested", "1688", "google trends", "reddit pool"],
    "ecommerce_data_sources": ["amazon", "1688", "alibaba", "keepa", "sorftime", "asin", "supplier", "quote", "cost", "factory", "reviews"],
    "github": ["github", "open source", "repo", "code", "issues", "implementation"],
    "reddit": ["reddit", "user feedback", "complaint", "community", "comments"],
    "google_search": ["discover", "unknown source", "web", "search"],
    "chrome_web_store": ["chrome", "edge", "extension", "browser plugin", "content script"],
    "apify": ["apify", "actor", "scraping marketplace"],
    "package_registries": ["npm", "pypi", "package", "library", "sdk", "wrapper"],
    "community_forums": ["v2ex", "stackoverflow", "hacker news", "zhihu", "juejin", "csdn", "forum"],
    "mcp_registries": ["mcp", "model context protocol", "tool server"],
    "osint_directories": ["osint", "source discovery", "search operators", "triangulation"],
    "ai_research_agents": ["deep research", "research agent", "planner", "citation", "query expansion"],
    "userscript_ecosystem": ["userscript", "tampermonkey", "greasyfork", "油猴"],
    "video_tutorials": ["youtube", "bilibili", "video", "tutorial", "walkthrough"],
    "newsletters_tool_radars": ["newsletter", "tool radar", "weekly", "curated"],
    "rapidapi_marketplaces": ["rapidapi", "api marketplace", "third party api", "endpoint"],
    "tool_directories": ["alternativeto", "product hunt", "tool directory", "alternatives"],
    "independent_blogs": ["blog", "writeup", "postmortem", "case study", "architecture"],
    "official_docs": ["official", "docs", "changelog", "rate limit", "policy", "developer portal"],
}


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def load_sources() -> list[dict[str, Any]]:
    index_path = ROOT / "sources" / "source-index.yaml"
    index = yaml.safe_load(index_path.read_text(encoding="utf-8"))
    sources = []
    for item in index["sources"]:
        path = ROOT / item["file"]
        source = yaml.safe_load(path.read_text(encoding="utf-8"))
        source["_path"] = str(path.relative_to(ROOT))
        sources.append(source)
    return sources


def load_access_surfaces() -> list[dict[str, Any]]:
    path = ROOT / "access" / "access-surfaces.yaml"
    if not path.exists():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data.get("access_surfaces", [])


def score_source(source: dict[str, Any], problem: str) -> tuple[int, list[str]]:
    score = int(source.get("priority", 1))
    reasons = [f"priority={score}"]
    text = normalize(problem)

    for domain, words in DOMAIN_KEYWORDS.items():
        if any(word in text for word in words):
            fit = int(source.get("domain_fit", {}).get(domain, 0) or 0)
            if fit:
                score += fit
                reasons.append(f"{domain}_fit={fit}")

    for word in SOURCE_HINTS.get(source["source_id"], []):
        if word in text:
            score += 4
            reasons.append(f"hint={word}")

    searchable = " ".join(
        [
            " ".join(source.get("best_for", [])),
            " ".join(source.get("query_patterns", [])),
            " ".join(source.get("source_discovery_patterns", [])),
        ]
    ).lower()
    keyword_hits = 0
    for token in set(re.findall(r"[a-z0-9]{3,}", text)):
        if token in searchable:
            keyword_hits += 1
    if keyword_hits:
        score += min(keyword_hits, 5)
        reasons.append(f"keyword_hits={keyword_hits}")

    return score, reasons


def score_surface(surface: dict[str, Any], problem: str, selected_source_ids: set[str]) -> tuple[int, list[str]]:
    score = int(surface.get("priority", 1))
    reasons = [f"priority={score}"]
    text = normalize(problem)

    if surface.get("parent_source") in selected_source_ids:
        score += 4
        reasons.append("selected_parent")

    searchable = " ".join(
        [
            surface.get("name", ""),
            " ".join(surface.get("best_for", [])),
            " ".join(surface.get("query_templates", [])),
            surface.get("access_type", ""),
        ]
    ).lower()

    keyword_hits = 0
    for token in set(re.findall(r"[a-z0-9]{3,}", text)):
        if token in searchable:
            keyword_hits += 1
    if keyword_hits:
        score += min(keyword_hits, 6)
        reasons.append(f"keyword_hits={keyword_hits}")

    if surface.get("status") == "active":
        score += 2
        reasons.append("active")
    elif surface.get("status") in {"stale", "blocked", "deprecated"}:
        score -= 5
        reasons.append(f"status={surface.get('status')}")
    elif surface.get("status") == "needs_validation":
        score -= 1
        reasons.append("needs_validation")

    return score, reasons


def main() -> int:
    parser = argparse.ArgumentParser(description="Select Source Scout sources for a problem.")
    parser.add_argument("problem", nargs="+", help="Problem statement to match against the Source Map.")
    parser.add_argument("--top", type=int, default=6, help="Number of sources to show.")
    parser.add_argument("--surfaces", type=int, default=10, help="Number of access surfaces to show.")
    args = parser.parse_args()

    problem = " ".join(args.problem)
    scored = []
    for source in load_sources():
        score, reasons = score_source(source, problem)
        scored.append((score, source, reasons))
    scored.sort(key=lambda row: row[0], reverse=True)

    selected_sources = scored[: args.top]
    selected_source_ids = {source["source_id"] for _, source, _ in selected_sources}

    print("SOURCES")
    for score, source, reasons in selected_sources:
        print(f"{source['source_id']} | score={score} | {source['_path']}")
        print(f"  why: {', '.join(reasons)}")
        methods = source.get("access_methods", [])
        if methods:
            method = methods[0]
            print(f"  first_access: {method['method_id']} - {method['description']}")
        patterns = source.get("query_patterns", [])[:3]
        for pattern in patterns:
            print(f"  query: {pattern}")
        print()

    surfaces = []
    for surface in load_access_surfaces():
        score, reasons = score_surface(surface, problem, selected_source_ids)
        surfaces.append((score, surface, reasons))
    surfaces.sort(key=lambda row: row[0], reverse=True)

    if surfaces:
        print("ACCESS_SURFACES")
        for score, surface, reasons in surfaces[: args.surfaces]:
            print(f"{surface['surface_id']} | score={score} | parent={surface['parent_source']} | status={surface['status']}")
            print(f"  why: {', '.join(reasons)}")
            print(f"  access_type: {surface['access_type']} | automation: {surface['automation_level']} | login: {surface['login_required']}")
            for template in surface.get("query_templates", [])[:3]:
                print(f"  query: {template}")
            validation = surface.get("validation", {})
            failures = "; ".join(validation.get("failure_signals", [])[:2])
            print(f"  validation: {validation.get('method')} | failure_signals: {failures}")
            print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
