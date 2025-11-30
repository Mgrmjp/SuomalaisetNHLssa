# Utilities

Helper scripts for testing, checking, and data manipulation.

## 📁 Files

### `test_api.py`
Tests NHL API endpoints and connectivity.

**Usage:**
```bash
# Test API
python3 scripts/python_utils/test_api.py

# Tests multiple dates
# Shows which games are available
# Verifies API is working
```

**Output:**
```
🏒 Testing NHL API with various dates...
==================================================

📅 Testing 2025-11-04:
   ✅ Found 10 games
   1. UTA @ BUF (OFF) - ID: 2025020203

📅 Testing 2025-11-08:
   ✅ Found 13 games
   1. PIT @ NJD (OFF) - ID: 2025020231
```

**Use For:**
- ✅ Verify API is working
- ✅ Check game availability
- ✅ Debug API issues
- ✅ Confirm data is available

---

### `check_season.py`
Checks what NHL season data is available for dates.

**Usage:**
```bash
# Check specific date
python3 scripts/python_utils/check_season.py 2025-11-01

# Check current season
python3 scripts/python_utils/check_season.py
```

**Output:**
```
Checking NHL season data for 2025-11-01...
Found 13 games
✅ Season is active

Games:
- CAR @ BOS (OFF)
- PIT @ WPG (OFF)
...
```

**Use For:**
- ✅ Verify dates have games
- ✅ Check season status
- ✅ Plan data collection
- ✅ Debug missing dates

---

### `expand_games.py`
Expands existing Finnish player data to include ALL players from the same games.

**Usage:**
```bash
# Expand all existing game data
python3 scripts/python_utils/expand_games.py

# Takes game IDs from Finnish data
# Fetches all players from those games
# Creates comprehensive dataset
```

**Process:**
1. Reads existing Finnish game data
2. Extracts game IDs
3. Fetches ALL players from each game
4. Creates expanded dataset

**Use For:**
- ✅ Converting Finnish → All players
- ✅ Complete game analysis
- ✅ Cross-referencing data
- ⚠️ Slow (fetches 500+ players per game)

**Output:**
- Expanded game data with all players
- Larger files than Finnish-only system

---

## 🔧 Common Tasks

### Verify API Working
```bash
python3 scripts/python_utils/test_api.py
```
Look for ✅ marks indicating success

### Check If Data Available
```bash
python3 scripts/python_utils/check_season.py 2025-12-25
```
Look for "Season is active" message

### Expand Finnish to All Players
```bash
python3 scripts/python_utils/expand_games.py
```
Takes 5-10 minutes, creates large dataset

## ⚠️ Important Notes

### `expand_games.py` Performance
- **Slow:** 5-10 minutes to run
- **Large output:** 10x bigger than Finnish data
- **Use sparingly:** Only when you need ALL players
- **Alternative:** Use `../data_collection/season/fetch_season_games.py` directly

### API Testing
- `test_api.py` is fastest (no player data)
- `check_season.py` is medium speed (just schedule)
- Full fetchers are slowest (include player stats)

## 📊 When to Use Each

| Need | Script |
|------|--------|
| Quick API check | `test_api.py` |
| Check date has games | `check_season.py` |
| Convert Finnish → All | `expand_games.py` |

## 🚨 Troubleshooting

### API errors
→ Run `test_api.py` first to verify connectivity

### No games found
→ Run `check_season.py` to verify date has data

### "expand_games.py" too slow
→ Use `../data_collection/season/fetch_season_games.py` instead

---

**Status:** ✅ All working (2025-11-22)
**API:** NHL API v1 (https://api-web.nhle.com)
**Tested:** 2025-11-01 through 2025-11-30
