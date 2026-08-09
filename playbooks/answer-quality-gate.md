# Answer Quality Gate

Use this before finalizing any Source Scout result.

## Must Pass

- The answer names the selected source cards and why they were selected.
- It reports the concrete access surfaces used for each important source, not only broad source names.
- It includes evidence from more than one source type when the task requires web research.
- It separates official facts, community experience, implementation evidence, and inference.
- It states which sources were low value, stale, blocked, or skipped.
- It includes missing-source risk when the result is uncertain.
- It proposes Source Map updates when a source fails, performs unusually well, or reveals a new source type.

## Red Flags

- Only official docs and SaaS/API pages were searched for an engineering workaround.
- GitHub was searched only by repo name, with no Issues/code/PR check when reliability matters.
- Reddit was summarized from titles without reading comments when user experience matters.
- Package registries were trusted without following the repo and Issues.
- Marketplace listings were treated as proof of reliability.
- The answer gives one recommended route without fallback or failure modes.

## Escalate To Heavy Source Discovery When

- Search results are generic.
- The selected sources are all same-type sources.
- A high-priority source access method is stale.
- The user says the answer is not useful.
- The problem likely belongs to an unknown niche community, marketplace, registry, or private/semi-private channel.
