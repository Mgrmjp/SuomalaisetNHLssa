# Finnish NHL news selection

[Documentation index](README.md)

The empty state shows at most two recent stories about Finnish NHL players. It hides the news section when none qualify. It does not fill empty slots with general NHL news or weekly roundups.

## Eligibility

- A current Finnish player from `static/data/players/finnish-roster.json` must appear in the publisher headline. Full names and surnames unique among active Finnish players qualify. Ambiguous surnames require a full name.
- Publication must be verified on the publisher page through `article:published_time` or the article's schema.org `datePublished`. Search dates, URL dates, modification dates and date-only values are insufficient.
- Publication must be within the previous 48 hours, with no future timestamps. Both collection and client selection enforce this window.
- Article requests and redirects stay within the existing trusted-domain list. Unreachable or unverifiable articles are omitted.
- Stories are deduplicated by canonical URL and original headline, then ordered by publication time.

Original headlines and descriptions remain the fallback. Optional OpenAI translation preserves the source text's meaning; generic dated roundup templates are removed. Translations are cached against the exact source headline and description, and only the two selected stories are translated.

## Collection and refresh

Run `.venv/bin/python3 scripts/generate_daily_news.py`. `--force` bypasses the one-hour discovery interval. Legacy date arguments from the daily pipeline remain accepted; they never establish an article's publication date.

Tavily discovery uses [news search](https://docs.tavily.com/documentation/api-reference/endpoint/search), a two-day search window and Finnish-player queries. Publisher metadata is checked independently. `TAVILY_API_KEY` is required for discovery; `OPENAI_API_KEY` is optional. Export local keys explicitly; the collector does not load env files.

The realtime GitHub workflow invokes the collector every ten minutes; the persisted `_refresh.lastAttemptAt` limits discovery to once per hour. The workflow stages both source cache and public index before rebasing, then uses the existing deployment flow. The daily workflow also runs the collector.

The client refetches the static index hourly and rechecks expiry each minute while the empty state is visible. Failed refreshes preserve verified cached stories only until their publication expiry. Historical source cache entries remain on disk but cannot appear without verified, recent publication metadata. Missing discovery credentials emit a warning and do not mark a successful attempt.

## Validation

- `.venv/bin/python3 scripts/test_generate_daily_news.py`
- `npx vitest run src/lib/tests/dailyNews.test.js src/lib/tests/dailyNewsService.test.js`
