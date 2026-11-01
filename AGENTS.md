# SuomalaisetNHLssa development guide

Start with the [documentation index](docs/README.md). Use [Development](docs/DEVELOPMENT.md) for setup, [Data pipeline](docs/DATA_PIPELINE.md) for collection, and [Testing](docs/TESTING.md) for validation.

## Commands

Run commands from the repository root using Linux Node/npm and the project `.venv`.

| Task | Command |
| --- | --- |
| Start development server | `npm run dev` |
| Production build with data collection | `npm run build` |
| Build using existing data | `npm run build:quick` |
| Refresh season statistics | `npm run data:stats` |
| Refresh season stats and inactive-player history | `npm run prebuild` |
| Fetch today through seven days ahead | `npm run data:fetch` |
| Fetch a date or inclusive date range | `npm run data:fetch:date -- YYYY-MM-DD [YYYY-MM-DD]` |
| Run Vitest tests | `npm test` |
| Watch Vitest tests | `npm run test:watch` |
| Check roster integrity | `npm run test:roster` |
| Test roster field preservation | `npm run test:sync` |
| Check JavaScript/Svelte with Biome | `npm run lint` |
| Check Python with Ruff | `npm run lint:python` |
| Format frontend files | `npm run format` |
| Check Svelte types | `npm run check` |
| Check documentation | `npm run docs:check` |
| Run docs, lint, type checks and Vitest | `npm run validate` |

`npm run dev` and `npm run build:quick` do not refresh season statistics. If a local leaderboard is stale, run `npm run data:stats` and reload. Python tooling requires `requirements-dev.txt` installed in `.venv`.

## Data files and preservation

- `static/data/players/finnish-roster.json`: master roster, keyed by player ID; includes active and inactive players.
- `scripts/data_collection/finnish/cache/finnish-players.json`: internal player cache.
- `static/data/player-stats/`: season statistics and collection metadata.
- `static/data/prepopulated/games/`: daily results; regenerate the manifest after manual collection.

Rebuild the cache with `.venv/bin/python3 scripts/data_collection/finnish/build_cache.py`, then publish it with `.venv/bin/python3 scripts/data_collection/finnish/sync_roster.py`.

Inactive-player `lastTeam` and `gamesPlayed` are collected by `scripts/prebuild/fetch-last-teams.cjs`. Both cache rebuilding and roster syncing must preserve these fields. If inactive players show missing GP or “Ei NHL:ssa” incorrectly, run `node scripts/prebuild/fetch-last-teams.cjs`.

## WSL file access

- Work inside Linux at `/home/miikka/dev/suomalaisetnhlssa`; use Linux Node/npm because dependencies contain Linux binaries.
- Windows UNC access through `\\wsl.localhost\Ubuntu-24.04\...` does not support hard links. Tools using link-based atomic writes can fail even when reads work; write through WSL using `python3`, `sed -i`, or a Linux-native editor, then inspect `git diff`.
- From PowerShell, invoke commands through `wsl.exe -d Ubuntu-24.04 --cd /home/miikka/dev/suomalaisetnhlssa -- <command>`. Use single quotes for Bash bodies to preserve quoting.
