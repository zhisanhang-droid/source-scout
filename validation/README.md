# Source Scout Validation Store

`runtime-results.jsonl` records lightweight access checks for concrete access surfaces.

Each row means: the listed entry point was reachable, blocked in a recognizable way, or failed at the time of the check. This is not enough to prove source quality; it is the first gate before deeper retrieval checks.

Useful commands:

```powershell
python source-scout\scripts\source_scout.py runtime-check --limit 20 --timeout 4
python source-scout\scripts\source_scout.py validation-status
python source-scout\scripts\source_scout.py validation-status --status reachable_limited
python source-scout\scripts\source_scout.py validation-status --source reddit
```
