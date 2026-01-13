# Suomalaiset NHL:ssä — Finnish NHL Player Tracker

[![Svelte](https://img.shields.io/badge/Svelte-5.0.0-orange)](https://svelte.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-4.0-blue)](https://tailwindcss.com/)

A personal web app for tracking Finnish NHL players' scoring stats. Automatically updated daily via GitHub Actions.

## Note

This is a personal project built for my own use. Feel free to browse or fork it if you find it useful, but it's optimized for my workflow and preferences rather than being a general-purpose tool.

## What It Does

- Tracks scoring stats for Finnish NHL players (~30-35 players)
- Auto-updates daily via GitHub Actions
- Responsive design with dark/light mode
- Calendar to view past games and stats

## Tech Stack

- **Svelte 5** + SvelteKit (Static adapter)
- **Tailwind CSS 4**
- **TypeScript**
- **Python** (data collection scripts)

## Local Development

```bash
git clone https://github.com/miikka/suomalaisetnhlssa.git
cd suomalaisetnhlssa
npm install
npm run dev
```

Available at `http://localhost:5173`.

## Commands

```bash
npm run dev      # Dev server
npm run build    # Production build
npm run lint     # Lint with Biome
npm run format   # Format code
npm run test     # Run tests
```

## Data

Uses a curated list of Finnish player IDs for fast, accurate lookups. Data is cached in the repo and updated daily via GitHub Actions, with NHL API as fallback.

