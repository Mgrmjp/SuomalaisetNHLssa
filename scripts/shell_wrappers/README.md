# Shell Wrappers

Bash wrapper scripts for convenience operations.

## 📁 Files

### `fetch-finnish-games.sh`
Fetches Finnish player data for a date range.

**Usage:**
```bash
# Fetch single date
bash scripts/shell_wrappers/fetch-finnish-games.sh 2025-11-01

# Fetch date range
bash scripts/shell_wrappers/fetch-finnish-games.sh 2025-11-01 2025-11-30

# Fetch to today
bash scripts/shell_wrappers/fetch-finnish-games.sh 2025-11-01

# Fetch from date to end of month
bash scripts/shell_wrappers/fetch-finnish-games.sh 2025-11-15 2025-11-30
```

**Process:**
1. Loops through each date
2. Calls `python3 scripts/data_collection/finnish/fetch.py {date}`
3. 1 second delay between dates
4. Progress output

**Output:** `data/prepopulated/games/YYYY-MM-DD.json` for each date

---

### `fetch_november_games.sh`
Fetches all November 2025 games (prepopulated data).

**Usage:**
```bash
# Fetch all November 2025
bash scripts/shell_wrappers/fetch_november_games.sh

# Runs Oct 31, Nov 1-30
```

**Process:**
1. Loops November 1-30, 2025
2. Calls appropriate fetcher for each date
3. Includes rate limiting
4. Progress tracking

**Output:** Complete November dataset

---

## 📝 Requirements

- Python 3.9+ installed
- Finnish data scripts in `../data_collection/finnish/`
- Rate limiting (1s delay between dates)

## ⚡ Speed

### Finnish Range
- **Per date:** 30-60 seconds
- **30 dates:** 15-30 minutes
- **With delay:** Includes 1s between dates

### Example Timeline
```
11:00 - Start November (30 dates)
11:20 - Halfway (15 dates done)
11:45 - Complete (30 dates done)
```

## 🔧 Troubleshooting

### "Permission denied"
```bash
chmod +x scripts/shell_wrappers/*.sh
```

### "No such file or directory"
```bash
# Check Python path
which python3

# Check scripts exist
ls -la scripts/data_collection/finnish/fetch.py
```

### "Zero players found"
```bash
# Update cache first
python3 scripts/data_collection/finnish/build_cache.py
```

## 📊 Example Output

```bash
$ bash scripts/shell_wrappers/fetch-finnish-games.sh 2025-11-01 2025-11-03

Starting fetch for 2025-11-01 to 2025-11-03...

Processing 2025-11-01...
✅ Generated data for 28 Finnish players in 13 games
📁 Saved to: data/prepopulated/games/2025-11-01.json

Processing 2025-11-02...
✅ Generated data for 15 Finnish players in 12 games
📁 Saved to: data/prepopulated/games/2025-11-02.json

Processing 2025-11-03...
✅ Generated data for 22 Finnish players in 13 games
📁 Saved to: data/prepopulated/games/2025-11-03.json

Complete! 3 dates processed.
```

---

**Status:** ✅ Working (2025-11-22)
**Rate Limit:** 1s between dates
**Use Case:** Batch fetching
