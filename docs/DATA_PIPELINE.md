# Data pipeline

[Documentation index](README.md)

Run commands from the repository root with Python dependencies installed as described in [Development](DEVELOPMENT.md). Collection contacts external services and can update tracked JSON. Record which dates were collected and inspect the resulting diff.

## Refresh daily results

```bash
# One NHL schedule date; replace the example date as needed.
.venv/bin/python3 scripts/data_collection/finnish/fetch.py 2026-10-31

# Inclusive date range.
.venv/bin/python3 scripts/data_collection/finnish/fetch.py 2026-10-31 2026-11-01

# Rebuild the browser's index of available snapshot dates.
.venv/bin/python3 scripts/data_collection/generate_manifest.py
```

The equivalent npm entry point is `npm run data:fetch:date -- 2026-10-31`. Without date arguments, `npm run data:fetch` fetches today through seven days ahead. `bash scripts/daily_update.sh` has a different default window: yesterday through seven days ahead, with roster-cache and news work as well. Neither command alone performs every enrichment step in the daily GitHub workflow.

The Finnish fetcher loads the ID-keyed player cache, requests the exact schedule day and boxscores, and saves one validated snapshot per date. Failure on a date must preserve that date's previous good file. A multi-date run can save earlier successful dates before a later date fails. Regenerate the manifest after a manual collection run.

Do not label a scheduled 0–0 game as a completed result. See [Player data](PLAYER_DATA.md) for state and participant rules.

## Roster and season statistics

```bash
.venv/bin/python3 scripts/data_collection/finnish/build_cache.py
.venv/bin/python3 scripts/data_collection/finnish/sync_roster.py
npm run prebuild
```

For a stale local points leaderboard or player-season table, run `npm run data:stats` and reload the page. `npm run dev` and `npm run build:quick` use the existing snapshots; they do not refresh season statistics. The update time in `static/data/player-stats/metadata.json` records collection time.

The cache builder owns the internal Finnish-player cache. The sync step publishes the master roster, preserving inactive-player `lastTeam` and `gamesPlayed`. The Node prebuild scripts enrich season stats and inactive-player history. They are also invoked by `npm run build`.

Player totals and team membership change over time; inspect the generated files rather than assuming a fixed roster size. See [Name correction](NAME_CORRECTION.md) before changing normalization.

## Supporting datasets

| Dataset | Refresh command or guide |
| --- | --- |
| Future games with roster-based Finnish names | `.venv/bin/python3 scripts/data_collection/finnish/fetch_upcoming_games.py` |
| Official standings | `npm run data:standings`; [Standings](STANDINGS.md) |
| Recent Finnish-player news | `npm run data:news:daily`; [News rules](DAILY_NEWS.md) |
| Prospect rankings and application cache | `bash scripts/update_prospects.sh` |
| Official league prospect inputs | `npm run prospects:leagues:update` |
| Headshot processing | [Headshot tools](../scripts/data_collection/headshots/README.md) |

Upcoming games use current roster membership as a preview; lineup participation is not confirmed. The collector excludes already-started games. The UI must not substitute past games when no future data qualifies.

Prospect input collection and application-cache building are separate steps. `update_prospects.sh` refreshes rankings and builds from available inputs; it does not run every league scraper. The prospect builder preserves previous data when required inputs fail validation, including empty, wrong-season or over-age inputs. Disabled public prospect routes do not stop scheduled prospect collection.

## Ownership and outputs

| Output | Producer |
| --- | --- |
| `scripts/data_collection/finnish/cache/finnish-players.json` | Finnish cache builder |
| `static/data/players/finnish-roster.json` | Roster sync; inactive-player enrichment during prebuild |
| `static/data/prepopulated/games/` | Finnish daily fetcher |
| `static/data/games_manifest.json` | Manifest generator |
| `static/data/player-stats/` | Node stats prebuild collectors |
| `static/data/upcoming-finnish-games.json` | Upcoming Finnish-game collector |
| `static/data/standings.json` | Standings collector |
| `static/data/daily-news.json` | Verified news collector |

The [shared Python writer](../scripts/data_collection/utils.py) uses atomic replacement for its callers. Other collectors have their own write behavior; do not assume every legacy script has the same guarantees. Static data is copied into `build/` during the production build.

Use [Deployment](DEPLOYMENT.md) to publish a collected snapshot. Local JSON changes alone do not change the live site.
