# Suomalaiset NHL:ssä — Finnish NHL Player Tracker

[![Svelte](https://img.shields.io/badge/Svelte-5-orange)](https://svelte.dev/)
[![SvelteKit](https://img.shields.io/badge/SvelteKit-2-blue)](https://kit.svelte.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-4-blue)](https://tailwindcss.com/)

A comprehensive web app for tracking Finnish NHL players — daily stats, standings, prospects, scouting reports, weekly recaps, and more. Automatically updated via GitHub Actions and deployed to GitHub Pages.

**Live:** [suomalaisetnhlssa.fi](https://suomalaisetnhlssa.fi)

## Features

- **Dashboard** — daily Finnish player stats, live game tracking, scoring summaries
- **Player profiles** — detailed season stats, career history, headshots, transfer history
- **Standings** — NHL conference/division standings with playoff indicators
- **Points leaderboard** (Pistepörssi) — season scoring leaders among Finnish players
- **Teams** (Joukkueet) — Finnish players grouped by NHL team
- **Prospects** (Lupaukset) — draft rankings, prospect stats, scouting reports
- **Scouting reports** — in-depth analysis of top Finnish prospects
- **Weekly recaps** (Viikkokatsaus) — editorial weekly summaries with featured players
- **Draft history** — Finnish NHL draft picks through the years
- **Championships** (Mestaruudet) — Stanley Cup winners with Finnish players
- **Realtime updates** — live polling during games, every 10 minutes via GitHub Actions
- **Calendar** — browse past games and stats by date
- **Ad system** — sponsor banners with adblock-friendly fallback messaging

## Tech Stack

- **Svelte 5** + **SvelteKit 2** (static adapter)
- **Tailwind CSS 4** via PostCSS
- **TypeScript** (with `@ts-nocheck` in most components)
- **lucide-svelte** for icons
- **Swiper** for player card carousels
- **marked** for markdown rendering (weekly recaps, scouting reports)
- **Python** — data collection, scraping, roster management
- **Biome** — linting and formatting
- **Vitest** — testing
- **Husky** + lint-staged — pre-commit hooks
- **GitHub Actions** — daily data updates, realtime polling, deployment

## Local Development

```bash
git clone https://github.com/Mgrmjp/SuomalaisetNHLssa.git
cd SuomalaisetNHLssa
npm install
npm run dev
```

Available at `http://localhost:5173`.

## Commands

```bash
# Development
npm run dev              # Dev server
npm run build            # Production build (runs prebuild first)
npm run build:quick      # Production build without prebuild
npm run preview          # Preview production build

# Validation
npm run validate         # Lint + type check + tests
npm run lint             # Biome lint
npm run format           # Biome format
npm run check            # Svelte type checking
npm run test             # Vitest tests

# Data pipeline
npm run data:fetch       # Fetch Finnish players for today
npm run data:fetch:date  # Fetch for specific date
npm run data:news:daily  # Generate daily news summary
npm run data:realtime    # Poll for live game updates
npm run goalies:collect  # Collect goalie stats

# Player management
npm run players:update   # Update player cache
npm run players:validate # Validate player data
npm run players:stats    # Show player stats
npm run players:changes  # Show recent changes
npm run players:backup   # Backup player data
npm run players:restore  # Restore from backup

# Prospects
npm run prospects:leagues:update  # Full prospects data refresh
npm run prospects:scrape          # Scrape official league stats
npm run prospects:na              # College/NCAA stats
npm run prospects:mestis          # Mestis league stats
```

## Data Pipeline

The site runs on a multi-layer data pipeline:

1. **Daily update** (06:00 UTC) — fetches game results, updates roster, generates news, rebuilds and deploys
2. **Realtime polling** (every 10 min) — checks for live games during NHL game windows
3. **Prospects update** (07:00 UTC) — scrapes league stats for Finnish prospects
4. **Prebuild** — fetches season stats and inactive player data before each build

Data is stored as static JSON files in `static/data/` and committed to the repo. The site is fully static — no server-side rendering at runtime.

## Project Structure

```
src/
  routes/           # SvelteKit pages (one per route)
  lib/
    components/     # Shared UI components
      game/         # Game-related (DateControls, PlayerList, etc.)
      ui/           # Generic UI (NavTabs, AdContainer, etc.)
      standings/    # Standings components
    stores/         # Svelte stores (gameData, ads, etc.)
    server/         # Server-side load functions
    utils/          # Helpers (dates, headshots, team mapping)
    tests/          # Component tests
  app.css           # Global styles + design tokens
static/
  data/             # Static JSON data (roster, games, stats)
  nhl-logos/        # Team logos
scripts/
  data_collection/  # Python data pipeline
  prebuild/         # Node.js prebuild scripts
  node_utils/       # CLI tools for player management
```

## Deployment

The site is deployed to GitHub Pages via the `Daily Data Update and Deploy` workflow. Every push to `main` and every scheduled run triggers a full build and deploy.

## License

Personal project. Feel free to browse or fork.
