# Application data

This directory contains the datasets served by the static SvelteKit application.

## Primary locations

- `prepopulated/games/` — daily game and Finnish-player data keyed by date
- `players/finnish-roster.json` — master Finnish NHL roster
- `player-stats/` — season-level skater and goalie statistics
- `leagues/league_prospects_official.json` — official league prospect data
- `leagues/league_prospects_advanced.json` — supplemental prospect data
- `leagues/league_prospects_na.json` — North American prospect data
- `finnish_prospects.json` — application-ready prospect cache
- `finnish_draft_rankings.json` — merged draft rankings
- `games_manifest.json` — dates available under `prepopulated/games/`

## Data flow

1. Collectors write daily games to `prepopulated/games/` and source-specific data files.
2. Cache builders merge source data into the application-ready datasets.
3. `generate_manifest.py` updates `games_manifest.json` from the daily game files.
4. SvelteKit copies this directory into the static production build.

Timestamped season exports, backups, debugging captures, and one-off expanded datasets are generated artifacts and intentionally excluded from Git and production builds.
