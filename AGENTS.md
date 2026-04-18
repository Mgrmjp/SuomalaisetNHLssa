# SuomalaisetNHLssa - Development Guide

## Commands

### Development
- `npm run dev` - Start dev server
- `npm run build` - Production build (runs prebuild first)
- `npm run build:quick` - Production build without prebuild

### Testing
- `npm test` - Run all vitest tests
- `npm run test:watch` - Run vitest in watch mode
- `npm run test:roster` - Run Finnish roster data integrity tests (JS)
- `npm run test:sync` - Run sync_roster field preservation tests (Python)

### Linting & Validation
- `npm run lint` - Biome lint check
- `npm run format` - Biome format
- `npm run check` - Svelte type checking
- `npm run validate` - Run lint + check + test

### Data Pipeline
- `npm run prebuild` - Fetch player stats + inactive player lastTeam/GP
- `npm run data:fetch` - Fetch Finnish players for today
- `npm run data:fetch:date` - Fetch for specific date (pass date as arg)
- `.venv/bin/python3 scripts/data_collection/finnish/build_cache.py` - Rebuild player cache from NHL API
- `.venv/bin/python3 scripts/data_collection/finnish/sync_roster.py` - Sync cache to static roster file

## Key Data Files
- `static/data/players/finnish-roster.json` - Master roster (277 players, keyed by ID)
- `scripts/data_collection/finnish/cache/finnish-players.json` - Internal cache
- `static/data/player-stats/` - Per-season skater/goalie stats

## Inactive Player Data
Inactive players need `lastTeam` and `gamesPlayed` fields, populated by:
1. `scripts/prebuild/fetch-last-teams.cjs` - Fetches from NHL Stats API during prebuild
2. `build_cache.py` - Preserves these fields from existing roster when rebuilding
3. `sync_roster.py` - Preserves these fields from existing roster when syncing

If inactive players show "-" for GP or "Ei NHL:ssa" for team, re-run: `node scripts/prebuild/fetch-last-teams.cjs`