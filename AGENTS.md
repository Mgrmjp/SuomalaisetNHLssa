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
- `npm run lint` - Biome check for frontend and JavaScript scripts
- `npm run lint:python` - Ruff check for Python scripts (install `requirements-dev.txt` in `.venv`)
- `npm run format` - Biome format
- `npm run check` - Svelte type checking
- `npm run validate` - Run JavaScript and Python lint + check + test

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

## File Writes on WSL (agent tooling)

This repo lives inside WSL at `/home/miikka/dev/suomalaisetnhlssa`, reached from
Windows through the `\\wsl.localhost\Ubuntu-24.04\...` UNC share.

That share does not support hard links: `link()` fails with
`ENOTSUP` / "The request is not supported", while `rename()` works. Tools that
write atomically via link-then-rename therefore fail, even though reads are
fine. DSH's `write` and `edit` tools are affected; `read`, `grep` and `glob` are not.

Write through WSL instead of a UNC path:

```powershell
# run project commands in the Linux environment
wsl.exe -d Ubuntu-24.04 --cd /home/miikka/dev/suomalaisetnhlssa -- npm run dev

# apply edits from a script that runs inside WSL
wsl.exe -d Ubuntu-24.04 --cd /home/miikka/dev/suomalaisetnhlssa -- python3 /tmp/apply.py
```

Practical rules:

- Use the **Linux** `node`/`npm`. Running the Windows ones against this repo fails,
  because `node_modules` contains Linux binaries.
- Make file edits with `python3`, `sed -i`, or a staged script executed inside WSL,
  then confirm with `git diff`.
- Quote bash bodies from PowerShell with **single** quotes; `wsl.exe` strips double
  quotes out of arguments.

<!-- headroom:rtk-instructions -->
# RTK (Rust Token Killer) - Token-Optimized Commands

When running shell commands, **always prefix with `rtk`**. This reduces context
usage by 60-90% with zero behavior change. If rtk has no filter for a command,
it passes through unchanged — so it is always safe to use.

## Key Commands
```bash
# Git (59-80% savings)
rtk git status          rtk git diff            rtk git log

# Files & Search (60-75% savings)
rtk ls <path>           rtk read <file>         rtk grep <pattern>
rtk find <pattern>      rtk diff <file>

# Test (90-99% savings) — shows failures only
rtk pytest tests/       rtk cargo test          rtk test <cmd>

# Build & Lint (80-90% savings) — shows errors only
rtk tsc                 rtk lint                rtk cargo build
rtk prettier --check    rtk mypy                rtk ruff check

# Analysis (70-90% savings)
rtk err <cmd>           rtk log <file>          rtk json <file>
rtk summary <cmd>       rtk deps                rtk env

# GitHub (26-87% savings)
rtk gh pr view <n>      rtk gh run list         rtk gh issue list

# Infrastructure (85% savings)
rtk docker ps           rtk kubectl get         rtk docker logs <c>

# Package managers (70-90% savings)
rtk pip list            rtk pnpm install        rtk npm run <script>
```

## Rules
- In command chains, prefix each segment: `rtk git add . && rtk git commit -m "msg"`
- For debugging, use raw command without rtk prefix
- `rtk proxy <cmd>` runs command without filtering but tracks usage
<!-- /headroom:rtk-instructions -->
