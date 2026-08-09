# Source Scout

Source Scout is an information-source discovery and maintenance system for AI agents.

Use it when a problem likely has prior art, hidden community experience, open-source implementations, plugins, MCP tools, browser automation approaches, tool-market entries, or source-specific access methods that normal AI search may miss.

The central idea: do not store only broad source names such as GitHub or Reddit. Store concrete access surfaces: GitHub code search, GitHub Issues, Reddit native search, Reddit comment deep read, Chrome Web Store search, userscript ecosystems, MCP registries, package registries, community forums, local browser/session routes, and the validation method for each.

## What This Repo Contains

- `sources/`: broad source cards.
- `access/access-surfaces.yaml`: concrete access surfaces with entry points, query templates, retrieval depth, validation methods, failure signals, and fallbacks.
- `routing/problem-type-routing.yaml`: default source mixes by problem type.
- `playbooks/`: retrieval, discovery, maintenance, feedback, and answer quality workflows.
- `scripts/`: CLI helpers for selecting sources, listing access surfaces, validating the source map, creating logs, checking runtime access, and exporting prompts.
- `schemas/`: source card and access surface schemas.
- `templates/`: reusable report templates.
- `AI_USAGE.md`: instructions for AI tools that only have the GitHub link.
- `codex-skill/SKILL.md`: optional Codex skill file.

## Install

```bash
git clone https://github.com/zhisanhang-droid/source-scout.git
cd source-scout
python -m pip install -r requirements.txt
python scripts/source_scout.py validate
```

Expected validation output:

```text
Source Map valid: <N> indexed sources, <N> access surfaces
```

## Daily Use

Select likely sources and concrete access surfaces for a problem:

```bash
python scripts/source_scout.py select "<problem>" --top 6 --surfaces 12
```

Generate an active discovery plan when the current library may be missing source types:

```bash
python scripts/source_scout.py discover-plan "<problem>"
```

List concrete access surfaces:

```bash
python scripts/source_scout.py surfaces --source reddit
python scripts/source_scout.py surfaces --status needs_validation
python scripts/source_scout.py surfaces --query comments
```

Validate after editing source cards or access surfaces:

```bash
python scripts/source_scout.py validate
```

Check due maintenance:

```bash
python scripts/source_scout.py due
```

Run lightweight entry-point reachability checks:

```bash
python scripts/source_scout.py runtime-check --limit 10 --timeout 3
python scripts/source_scout.py validation-status
```

Export a prompt pack for another AI tool:

```bash
python scripts/source_scout.py export-prompt --problem-type data_collection_antibot --task "<problem>" --top 22
```

Record feedback after a source performs well or poorly:

```bash
python scripts/source_scout.py feedback --source reddit --task "<task>" --result-quality stale --feedback "<what failed>"
```

Create a task search log:

```bash
python scripts/source_scout.py log --task "<task>" --problem-type "<type>" --sources "github,reddit"
```

## CLI Commands

```text
source_scout.py select             choose likely sources for a problem
source_scout.py discover-plan      generate active source-discovery trails
source_scout.py surfaces           list or filter concrete access surfaces
source_scout.py validate           validate source cards, routing, and access surfaces
source_scout.py due                list sources due for maintenance
source_scout.py maintain           generate a maintenance report
source_scout.py runtime-check      check URL entry-point reachability
source_scout.py validation-status  show latest structured runtime check results
source_scout.py validation-queue   list access surfaces needing validation
source_scout.py coverage           generate source/access coverage report
source_scout.py log                create a search log
source_scout.py feedback           record source quality feedback
source_scout.py export-prompt      export a reusable prompt pack for other AI tools
```

## How Other AI Tools Should Use This

If the AI can run local commands, give it this repo and ask it to run:

```bash
python scripts/source_scout.py discover-plan "<problem>"
python scripts/source_scout.py select "<problem>" --top 6 --surfaces 12
```

If the AI cannot run commands, give it `AI_USAGE.md` plus `access/access-surfaces.yaml` and ask it to follow the same workflow manually.

For Codex, copy `codex-skill/SKILL.md` into the local Codex skills directory as a skill named `source-scout`, or ask Codex to use this repository as the Source Scout reference.

## Answer Quality Gate

A Source Scout answer should name:

1. Problem type.
2. Selected source cards.
3. Concrete access surfaces searched.
4. Evidence found, with source links.
5. Source quality labels: high value, medium, low, stale, blocked.
6. Missing-source risk.
7. Suggested Source Map updates.

Red flags:

- Only official docs and SaaS/API pages were searched for an engineering workaround.
- GitHub was searched only by repo name, with no Issues/code/PR check when reliability matters.
- Reddit was summarized from titles without reading comments when user experience matters.
- Package registries were trusted without following the repo and Issues.
- Marketplace listings were treated as proof of reliability.
- The answer gives one recommended route without fallback or failure modes.

