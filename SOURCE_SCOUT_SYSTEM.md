# Source Scout System

## Purpose

Source Scout is an iterative information-source discovery system. Its job is not to remember every solution pattern. Its job is to help Codex find the right places to look, use each source correctly, detect stale access methods, and improve the source map over time.

## Core Loop

1. Maintain a structured Source Map of known information sources.
2. For a concrete user problem, retrieve the most relevant sources from the Source Map first.
3. Search each selected source using its recommended access methods and query patterns.
4. If results are weak, stale, or user feedback says quality is poor, launch a heavier source-discovery pass.
5. Record what worked, what failed, and what should be changed in the relevant source card.
6. Periodically run maintenance checks for access methods, freshness, and source usefulness.

## Helper Script

Use this to get a first-pass source shortlist:

```powershell
python scripts/source_scout.py select "Google Trends data collection 429 browser extension MCP existing session" --top 6
```

The script is a routing aid, not a substitute for judgment. Read the selected source cards before searching.

Validate the Source Map after edits:

```powershell
python scripts/source_scout.py validate
```

Create a task search log:

```powershell
python scripts/source_scout.py log --task "Reddit comment data source search" --problem-type "data_collection" --sources "reddit,github,apify"
```

Generate a maintenance report:

```powershell
python scripts/source_scout.py maintain
```

Run lightweight entry-point validation and inspect latest structured status:

```powershell
python scripts/source_scout.py runtime-check --limit 10 --timeout 3
python scripts/source_scout.py validation-status
```

Export a prompt pack for another AI tool:

```powershell
python scripts/source_scout.py export-prompt --problem-type data_collection_antibot --task "<problem>" --top 22
```

Generate an active discovery plan when current sources may be incomplete:

```powershell
python scripts/source_scout.py discover-plan "<problem>"
```

## System Layers

| Layer | Role | Trigger |
|---|---|---|
| Source Map | Structured source cards: fit, access, query patterns, reliability, known failures | Always available |
| Problem-time Retrieval | Lightweight matching from problem type to 3-8 likely sources | Every concrete research task |
| Source Discovery | Active discovery of unknown channels, directories, communities, registries, and marketplaces | Weak results, new domain, or scheduled expansion |
| Active Discovery Plan | Choose discovery trails before searching, such as implementation trail, real-browser workaround trail, community failure trail, and marketplace trail | Unknown source types or poor first-pass results |
| Maintenance | Re-check access methods, stale tools, source quality, and query patterns | Scheduled or after failed searches |
| Runtime Validation | Store concrete entry-point reachability results in `validation/runtime-results.jsonl` | After `runtime-check` or suspected access drift |
| Prompt Export | Export selected sources and access surfaces for other AI tools | When ChatGPT/Claude/Gemini/etc. should follow Source Scout |
| Search Logs | Task-level trace of sources used, result quality, and user feedback | After search tasks |

## Default Decision Rule

Do not run full source discovery for every task. Start from the Source Map. Escalate only when:

- Source Map coverage is thin for the domain.
- The selected sources return weak or generic results.
- An access method fails or appears stale.
- The user explicitly says search quality is poor.
- A new class of source appears during research.

## Minimum Output For A Source Scout Search

1. Problem type and selected sources.
2. Access method used for each source.
3. Evidence found, with source links.
4. Source quality notes: high value, medium, low, stale, blocked.
5. Missing-source risk: what source types may still be absent.
6. Suggested Source Map updates if any.

## Persistence Rule

Search logs may be created whenever they help preserve useful feedback. Source cards should be updated only when a pattern is reusable across future tasks, such as a source becoming stale, a query pattern consistently working, or a new source type proving useful.
