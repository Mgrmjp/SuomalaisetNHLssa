# Finnish NHL Players - Data Collection

Fetches Finnish NHL player data only (2-28 players per game date).

## 🎯 Purpose

Track performance of Finnish players in the NHL without fetching all 500+ players from every game.

**Benefits:**
- ✅ 10-15x faster than fetching all players
- ✅ Smaller data files (2-10KB vs 15-30KB)
- ✅ Focused on Finnish players only
- ✅ Complete player info (birthplace, age, stats, etc.)

## 📁 Files

### `fetch.py`
Main data fetcher for Finnish players.

**Usage:**
```bash
# Fetch single date
python3 scripts/data_collection/finnish/fetch.py 2025-11-01

# Fetch range (use shell wrapper)
bash scripts/shell_wrappers/fetch-finnish-games.sh 2025-11-01 2025-11-30
```

**Output:** `data/prepopulated/games/2025-11-01.json`

### `build_cache.py`
Builds comprehensive Finnish players cache.

**Usage:**
```bash
# Run when new Finnish players join NHL
python3 scripts/data_collection/finnish/build_cache.py

# Takes ~3 minutes, scans 30 days of games
```

**Process:**
1. Scans 30 days of NHL games (~224 games)
2. Checks 800+ unique players
3. Filters for Finnish nationality (birthCountry == "FIN")
4. Builds complete cache with ~34 players

### `cache/finnish-players.json`
Complete Finnish players cache.

**Contents:** 34 Finnish players with:
- Player ID, name, position
- Birth date, birthplace
- Jersey number, height, weight
- Team, headshot URL
- Active status

**Update Frequency:** Run `build_cache.py` when:
- New Finnish players join NHL
- Players retire
- Major roster changes

## 📊 Sample Output

```json
{
  "date": "2025-11-01",
  "total_players": 28,
  "total_games": 13,
  "players": [
    {
      "playerId": 8478427,
      "name": "Sebastian Aho",
      "position": "C",
      "team": "CAR",
      "birthplace": "Rauma, FIN",
      "game_score": "1-2",
      "game_result": "L",
      "points": 0,
      "goals": 0,
      "assists": 0,
      "time_on_ice": "19:39",
      "shots": 0,
      "hits": 3
    }
  ]
}
```

## 🏆 Current Cache (2025-11-22)

**Total Players:** 34 Finnish players

**By Position:**
- Forwards (C/L/R): 21 players
- Defense (D): 10 players
- Goalies (G): 3 players

**Star Players:**
- Sebastian Aho (CAR)
- Mikko Rantanen (DAL)
- Miro Heiskanen (DAL)
- Roope Hintz (DAL)
- Erik Haula (NSH)

**Goalies:**
- Juuse Saros (NSH)
- Joonas Korpisalo
- Kevin Lankinen
- And 3 more

## 📈 Typical Results

### November 2025 Games
- **Total Finnish players:** 28 active
- **Players per game date:** 10-20 (depending on schedule)
- **Games with Finnish players:** 8-12 per date
- **Top scorers:** 2-4 points per game

### Peak Season
- **Total active:** 30-35 Finnish players
- **Players per date:** 15-28
- **Multiple goalies active:** 3-4

## ⚙️ How It Works

1. **Load Cache:** `fetch.py` loads `cache/finnish-players.json`
2. **Get Schedule:** Fetches NHL schedule for date
3. **Get Games:** For each game, fetches boxscore data
4. **Filter Players:** Checks if players are in Finnish cache
5. **Extract Stats:** Collects game stats for Finnish players only
6. **Save Data:** Saves to `data/prepopulated/games/YYYY-MM-DD.json`

**No API calls needed** for player nationality check (uses cache)!

## 🚨 Troubleshooting

### "0 Finnish players found"
**Cause:** Cache incomplete or outdated
**Solution:** Run `build_cache.py` to update cache (scans official team rosters)

### "API timeout"
**Cause:** Too many requests
**Solution:** Wait, then retry (scripts include rate limiting)

### "Cache file not found"
**Cause:** Cache hasn't been built
**Solution:** Run `build_cache.py` first

## 📅 Example Workflow

```bash
# 1. Update cache (once per season or when roster changes)
python3 scripts/data_collection/finnish/build_cache.py

# 2. Fetch data for specific dates
python3 scripts/data_collection/finnish/fetch.py 2025-11-01
python3 scripts/data_collection/finnish/fetch.py 2025-11-02
python3 scripts/data_collection/finnish/fetch.py 2025-11-03

# 3. Fetch range using shell wrapper
bash scripts/shell_wrappers/fetch-finnish-games.sh 2025-11-01 2025-11-30

# 4. View results
cat data/prepopulated/games/2025-11-01.json | jq '.total_players'
```

## 🔄 Updating Cache

Run `build_cache.py` when:
- ✅ New Finnish player debuts
- ✅ Player changes nationality (unlikely)
- ✅ Major mid-season transfers
- ✅ Start of new season

**Time:** ~3 minutes
**Rate Limit:** 0.2s between API calls
**Coverage:** 30 days back, 800+ players

---

**Status:** ✅ Working (2025-11-22)
**Cache:** 34 players (complete)
**Performance:** 30-60 seconds per date
