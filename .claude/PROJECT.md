# Suomalaiset NHL:ssä - Project Info

## Overview

A static web application that tracks Finnish NHL players, featuring:
- Real-time player statistics and game data
- Standings and leaderboards
- Finnish name correction for proper character display (ä, ö, å)

## Tech Stack

- **Framework**: SvelteKit with `adapter-static` (static site generation)
- **Language**: JavaScript/TypeScript
- **Styling**: Tailwind CSS
- **Data Sources**: NHL API, local pre-populated JSON files

## Key Features

### Main Page (`/`)
- Daily Finnish player game performance
- Player cards with detailed stats
- Date navigation for historical games

### Leaderboard (`/pisteporssi`)
- Top 100 Finnish players by points
- Real-time stats from NHL API
- Finnish name corrections applied

### Player List (`/pelaajat`)
- All Finnish NHL players (skaters + goalies)
- Sorted alphabetically
- Search functionality

### Standings (`/sarjataulukko`)
- Full NHL standings with Finnish headers
- Conference/division breakdown
- Advanced stats toggle

## Important Files

### Data Services
- `src/lib/services/standingsService.js` - Standings calculation
- `src/lib/services/dataService.js` - Game data fetching
- `src/lib/utils/apiHelpers.js` - Local JSON fetching

### Name Correction
- `src/lib/utils/finnishNameUtils.js` - Server-side Finnish name correction
- `scripts/data_collection/finnish/finnish_text_utils.py` - Python OpenAI-based correction

### Data Storage
- `static/data/prepopulated/games/*.json` - Daily game data with player stats
- `static/data/games_manifest.json` - Available dates manifest

## Build & Deploy

```bash
# Install dependencies
npm install

# Build for production
npm run build

# Preview production build
npm run preview

# Run dev server
npm run dev
```

## Data Collection

Python scripts in `scripts/data_collection/` fetch and process NHL data:
- `finnish/fetch.py` - Fetch Finnish player data
- `finnish/finnish_text_utils.py` - OpenAI name correction
- `season/` - Season-level data collection

## Character Encoding

The app uses UTF-8 throughout:
- HTML: `<meta charset="UTF-8" />`
- Language: `<html lang="fi">`
- JSON files: UTF-8 encoded

Finnish characters (ä, ö, å) are corrected server-side before being baked into static HTML.
