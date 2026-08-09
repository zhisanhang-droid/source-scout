---
name: source-scout
description: Discover, select, and maintain reliable information sources for finding real-world solutions, prior art, open-source implementations, plugins, MCP tools, browser automation paths, community experience, and hidden engineering workarounds. Use when the user asks whether others have solved a problem, asks to search for existing solutions or cases, complains that normal AI search is shallow, asks for GitHub/Reddit/community/tool-market research, or needs an information-source discovery and feedback loop rather than ordinary web search.
---

# Source Scout

## Mission

Act as an information-source scout, not a generic search assistant. First find the right places to look, then search them using the access method that fits each source.

## Repository

The durable Source Map lives in this repository root.

## Operating Modes

Use the light path by default:

1. Open `sources/source-index.yaml`.
2. Check `routing/problem-type-routing.yaml` for a default source mix when the problem type is clear.
3. Optionally run `python scripts/source_scout.py select "<problem>" --top 6 --surfaces 10`.
4. Pick 3-8 relevant source cards.
5. Use each source card's `best_for`, `access_methods`, and `query_patterns`.
6. Search, verify, and report source quality.
7. Propose Source Map updates when access methods fail, results are weak, or the user gives quality feedback.

Use the heavy discovery path when:

- Existing source cards do not fit the problem.
- Results are generic, SEO-heavy, API-only, or SaaS-only.
- A source access method is stale or blocked.
- The user says search quality is poor.
- The domain has unknown communities, marketplaces, registries, or vocabulary.

For the heavy path, follow `playbooks/source-discovery.md` or run:

```bash
python scripts/source_scout.py discover-plan "<problem>"
```

## Required References

- Normal task: read `playbooks/problem-time-retrieval.md` and the selected source cards.
- Weak/unknown-source task: also read `playbooks/source-discovery.md`.
- After feedback or stale access: read `playbooks/post-search-feedback.md` and `playbooks/maintenance.md`.
- Before final answers: apply `playbooks/answer-quality-gate.md`.

## Search Behavior

Do not treat a platform as one source when it has multiple access surfaces. For example:

- GitHub includes repo search, code search, Issues, PRs, Discussions, forks, topics, and awesome lists.
- Reddit includes Google site search, subreddit search, comments, user history, and local tools.
- Package registries must be followed back to GitHub before trusting a package.
- Chrome Web Store and Apify are marketplaces; they are useful for demand and packaged workflows, but not enough for reliability proof.
- Runtime checks only prove entry-point reachability. A surface is not truly validated until retrieval depth and task fit have been tested.

## Output Requirements

For Source Scout tasks, include:

1. Problem type and selected source map.
2. Sources and concrete access surfaces searched.
3. Evidence summary with links.
4. Source quality notes: high value, medium, low, stale, or blocked.
5. Missing-source risk: what source types may still be absent.
6. Proposed Source Map updates.
