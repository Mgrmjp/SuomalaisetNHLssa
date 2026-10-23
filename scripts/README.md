# Scripts Directory - Usage Guide

Organized collection of scripts for NHL data collection and Finnish player tracking.

## 📁 Directory Structure

### `/data_collection/` - Data Fetchers
Main data collection scripts, organized by data type.

- **`finnish/`** - Finnish NHL players only (2-28 players per date)
  - Use for: Tracking Finnish players in NHL
  - See: [finnish/README.md](data_collection/finnish/README.md)

- **`season/`** - All NHL players (500+ players per date)
  - Use for: Comprehensive season data
  - See: [season/README.md](data_collection/season/README.md)

- **`headshots/`** - Player thumbnail utilities
  - Use for: Fetching player headshots
  - See: [headshots/README.md](data_collection/headshots/README.md)

### `/shell_wrappers/` - Bash Scripts
Convenience wrapper scripts for common operations.

- **`fetch-finnish-games.sh`** - Fetch Finnish players for date range
- **`fetch_november_games.sh`** - Fetch all November 2025 games

### `/python_utils/` - Helper Tools
Utility scripts for checking, testing, and data manipulation.

- **`check_season.py`** - Check NHL season availability
- **`expand_games.py`** - Expand existing game data
- **`test_api.py`** - Test NHL API endpoints

## 🚀 Quick Start

### Fetch Finnish Players (Most Common)
```bash
# Single date
python3 scripts/data_collection/finnish/fetch.py 2025-11-01

# Using shell wrapper for date range
bash scripts/shell_wrappers/fetch-finnish-games.sh 2025-11-01 2025-11-30

# Build/update cache (run when new Finnish players join NHL)
python3 scripts/data_collection/finnish/build_cache.py
```

### Fetch All Players
```bash
# Season data (all players)
python3 scripts/data_collection/season/fetch_season_games.py 2025-10-01 2025-11-30
```

### Test API
```bash
# Verify NHL API is working
python3 scripts/python_utils/test_api.py
```

## 📊 Data Output

### Finnish Players
- **Location:** `static/data/prepopulated/games/YYYY-MM-DD.json`
- **Count:** 2-28 players per date
- **Size:** ~2-10KB per date

### Season Data (All Players)
- **Location:** `static/data/prepopulated/season/YYYY-MM-DD.json`
- **Count:** 500+ players per date
- **Size:** ~15-30KB per date

## 🗑️ Deprecated Files

Deprecated scripts are removed from this directory; use the commands listed above.

## 📝 Requirements

- Python 3.10+
- `requests` library (`pip install requests`)

## 🎯 Choosing the Right Script

| Need | Script |
|------|--------|
| Finnish players only | `data_collection/finnish/fetch.py` |
| All NHL players | `data_collection/season/fetch_season_games.py` |
| Fetch date range | `shell_wrappers/fetch-finnish-games.sh` |
| Build player cache | `data_collection/finnish/build_cache.py` |
| Get player headshots | `data_collection/headshots/fetch_thumbnails.py` |
| Test API | `python_utils/test_api.py` |

## ⚠️ Important Notes

1. **Cache First**: Always run `build_cache.py` after NHL roster changes
2. **Rate Limiting**: Scripts include delays to respect API limits
3. **Date Format**: Use `YYYY-MM-DD` format
4. **Current Season**: The NHL prospects cache derives its season from the current date; third-party league feeds may use provider-specific season IDs.

**System:** Finnish NHL Players Tracker
