# Problem-time Retrieval Playbook

Use this for normal user questions. This is intentionally lighter than full source discovery.

## Steps

1. Classify the problem:
   - engineering workaround
   - data collection or anti-bot
   - API/tool alternative
   - consumer feedback
   - ecommerce sourcing or price discovery
   - AI/MCP/browser automation
2. Open `source-scout/sources/source-index.yaml`.
3. Select 3-8 source cards based on `best_for`, `domain_fit`, and `priority`.
4. Use the selected cards' `access_methods` and `query_patterns`.
5. Search enough sources to satisfy the user's requested depth and local web research rules.
6. Report source quality, stale access methods, and missing-source risk.
7. If selected sources are weak, escalate to `source-discovery.md`.

## Escalation Criteria

- Fewer than two useful independent source types.
- Results are mostly official docs, SaaS pages, SEO posts, or generic summaries.
- User says the result quality is poor.
- A listed access method fails.
- The problem belongs to a domain not covered by current source cards.

