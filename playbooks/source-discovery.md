# Source Discovery Playbook

Use this only when the existing Source Map is insufficient, stale, or the domain is new.

## Discovery Questions

1. Which people or roles are most likely to have solved this problem?
2. Where do those people publish, complain, share code, sell tools, or ask for help?
3. Which marketplaces, registries, plugin ecosystems, package indexes, forums, newsletters, or private communities may contain traces?
4. Which names, slang, errors, and adjacent categories might they use instead of the user's words?
5. Which access surface is correct: web search, site search, API, CLI, RSS, code search, issue search, comments, or marketplace search?

## Search Patterns

```text
{domain} tools directory
{domain} marketplace
{domain} forum
{domain} subreddit
{domain} discord
{domain} telegram
{domain} newsletter
awesome {domain}
{domain} github topic
{platform} chrome extension
{platform} userscript
{platform} apify actor
{platform} MCP server
{platform} npm
{platform} pypi
{problem} workaround
{problem} alternative
```

## Add A Source Candidate When

- It repeatedly appears from independent paths.
- It has a distinct audience or access surface.
- It returns evidence unavailable from current sources.
- It offers a better way to search an existing source.

## Do Not Add When

- It is only a duplicate mirror.
- It has no clear access method.
- It is a one-off article with no reusable source value.

