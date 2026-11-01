# Project configuration

[Documentation index](README.md)

The dashboard reads generated static JSON. It needs no environment variables to run against the existing snapshots.

Ordinary defaults belong in tracked code. Keep `.env.local` for API keys and deliberate local overrides; do not copy defaults into it.

## Local credentials

Copy `.env.example` to `.env.local`, preserving any keys already present. Fill only what you use:

| Variable | Purpose |
| --- | --- |
| `TAVILY_API_KEY` | News discovery in `scripts/generate_daily_news.py` |
| `OPENAI_API_KEY` | Optional news translations and player-name correction |
| `APIHOCKEY_KEY` | Optional API-Hockey league collector |
| `ELITEPROSPECTS_API_KEY` | Optional Elite Prospects input for prospect collection |
| `THE_SPORTS_DB_KEY` | Optional TheSportsDB prospect/league input |

`.env.local` is ignored by Git; `.env.example` contains blank placeholders and is tracked. A separate `.env` file is unnecessary for the normal local setup.

Vite and the Node prebuild scripts load local env files. Python scripts do not generally load `.env.local`: export their required variables in the shell before invoking them. The API-Hockey helper has its own local-file loader. GitHub Actions receive keys through repository secrets.

## Tracked defaults

| Configuration | Location |
| --- | --- |
| NHL collector API URL, timeout, retries and rate limits | `scripts/data_collection/config.py` |
| Player positions and date constants | `src/lib/constants/gameConstants.js` |
| Player-stats prebuild retry and cache-fallback defaults | `scripts/prebuild/fetch-player-stats.cjs` |
| News publication-age and refresh windows | `scripts/generate_daily_news.py`, `src/lib/utils/dailyNews.js`, `src/lib/services/dailyNewsService.js` |
| Public section availability | `src/lib/config/features.js` |

The old `NHL_API_BASE_URL`, generic `API_*`, cache/performance settings and fixed season-date variables came from a removed configuration service. Current code does not read those env entries. Do not reintroduce them as active settings. Python's `API_MAX_RETRIES` is a tracked constant, despite sharing a name with one old env entry.

Supported prebuild overrides remain available when intentionally needed: `NHL_SEASON_ID`, `NHL_API_MAX_RETRIES`, `NHL_API_RETRY_DELAY_MS`, `NHL_API_MAX_RETRY_DELAY_MS`, and `NHL_API_CACHE_FALLBACK`. Their defaults already live in the prebuild script; leave them out of `.env.local` unless changing behavior locally.
