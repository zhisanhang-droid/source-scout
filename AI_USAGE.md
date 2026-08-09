# AI Usage Guide

Source Scout is an information-source discovery system. Use it when a user asks for existing solutions, prior art, open-source implementations, plugins, MCP servers, browser automation paths, community experience, data-collection workarounds, or hidden engineering routes.

## Core Rule

Do not stop at official APIs, SaaS vendors, or generic search results. First choose the right information sources, then search their concrete access surfaces.

## Fast Start For Any AI

1. Read `README.md`.
2. Read `SOURCE_SCOUT_SYSTEM.md`.
3. Run or conceptually follow:

```bash
python scripts/source_scout.py discover-plan "<problem>"
python scripts/source_scout.py select "<problem>" --top 6 --surfaces 12
```

4. Search the selected access surfaces, not only the broad source names.
5. Report what worked, what was weak, what was blocked, and what source types may still be missing.

## Mandatory Output Shape

For a Source Scout search, answer with:

- Problem type.
- Selected source cards.
- Concrete access surfaces searched.
- Evidence summary with links.
- Source quality labels: high value, medium, low, stale, blocked.
- Missing-source risk.
- Suggested Source Map updates.

## Quality Gate

A good answer must include multiple source types. For engineering workaround or data-collection tasks, include at least some of:

- GitHub repository search.
- GitHub code search.
- GitHub Issues/PRs/Discussions.
- Reddit search plus comment reading.
- Hacker News or Stack Overflow discussion search.
- Chrome/Edge extension marketplaces.
- Userscript ecosystems such as GreasyFork/OpenUserJS/ScriptCat.
- MCP registries.
- Package registries such as npm/PyPI.
- Apify/RapidAPI/tool marketplaces.
- Chinese communities when the domain is likely China-heavy.
- Local browser/session/extension/agent routes when anti-bot, login, captcha, or 429 appears.

## Reusable Prompt For Non-CLI AI

```text
Use Source Scout. Do not stop at official APIs, SaaS vendors, or generic web results.

First classify the problem type. Then select concrete access surfaces from the Source Map:
GitHub repo/code/issues/PRs/discussions, Reddit search/comments, HN/StackOverflow, Chrome/Edge extensions, userscripts, MCP registries, npm/PyPI, Apify/RapidAPI/tool marketplaces, Chinese communities, official docs, local/browser/session routes, and adjacent source-discovery directories.

For each selected surface, state:
1. why it fits,
2. exact query templates used,
3. what retrieval depth it can provide,
4. validation method,
5. failure signals,
6. fallback surfaces.

After searching, separate official facts, implementation evidence, community experience, and inference. Also state what source types may still be missing and propose updates to the Source Map.
```

