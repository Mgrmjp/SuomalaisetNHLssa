# Data Scripts Directory - Restructured Architecture

This directory contains scripts for managing Finnish NHL player data with a clean, organized structure.

## Core Scripts

### 1. fetch-nhl-data.py
Main Python script for fetching Finnish NHL player data from the NHL API.

#### Features:
- Fetches game data for specific dates
- Identifies Finnish players using birth country/city
- Generates properly formatted JSON files
- Saves data to `data/prepopulated/games/`

#### Usage:
```bash
# Fetch data for today
python3 scripts/data/fetch-nhl-data.py

# Fetch data for specific date
python3 scripts/data/fetch-nhl-data.py 2025-11-13

# Generated data format:
# data/prepopulated/games/2025-11-13.json
```

## Directory Structure

```
scripts/
├── data/           # Data fetching and processing
│   ├── fetch-nhl-data.py      # Main NHL data fetcher
│   ├── fetch-simple-data.js   # Simple fetch utility
│   └── README.md              # This documentation
├── utils/          # Utility scripts
│   ├── player-cli.js          # Player management CLI
│   └── node-utils.js          # Node.js utilities
└── build/          # Build and deployment scripts
```

## Data Structure

Generated data is saved in a structured format:

```
data/
├── prepopulated/
│   ├── games/                 # Game data by date
│   │   ├── 2025-11-08.json   # Finnish players for that date
│   │   ├── 2025-11-09.json
│   │   └── 2025-11-13.json
│   ├── rosters/               # Static player rosters
│   └── cache/                 # Temporary cache files
```

## Integration with Frontend

The frontend automatically loads data from `data/prepopulated/games/` based on the selected date. The data fetching is done separately using the Python scripts to avoid real-time API calls in the browser.

## Environment Requirements

- Python 3.7+ for data fetching scripts
- `requests` library for API calls
- Node.js for utility scripts
- Modern browser for frontend

