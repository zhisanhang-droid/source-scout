# Source Maintenance Playbook

Use this for scheduled checks or after failed searches.

## Maintenance Checks

1. Access method still works.
2. Query patterns still produce relevant results.
3. Source is still active and searchable.
4. Known tools, APIs, or local bridges still return complete data.
5. The source's `best_for` and `not_good_for` fields still match reality.
6. Recent search logs show high or low value.

## Update Rules

- Mark `status: stale` when the source is temporarily unreliable.
- Mark `status: deprecated` only when replacement sources are identified or the source no longer provides useful access.
- Add `known_failures` for concrete failures, such as missing Reddit comments or broken registry search.
- Update `history` after meaningful user feedback.

## Suggested Cadence

- High-priority, fast-moving sources: monthly.
- Marketplaces and package registries: quarterly.
- Domain-specific new sources: after each serious research project.

