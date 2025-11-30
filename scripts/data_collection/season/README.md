# Season Data - All NHL Players

Fetches ALL NHL players (not just Finnish) for comprehensive season data.

## 🎯 Purpose

Get complete NHL game data with all players from every game.

**When to use:**
- Need comprehensive player stats
- Building complete database
- Research requiring all nationalities
- Historical analysis across all players

**When NOT to use:**
- Only need Finnish players (use `../finnish/` instead)

## 📁 Files

### `fetch_season_games.py`

Fetches all players from all games for date range.

**Usage:**
```bash
# Single date
python3 scripts/data_collection/season/fetch_season_games.py 2025-11-01

# Date range
python3 scripts/data_collection/season/fetch_season_games.py 2025-10-01 2025-11-30

# Current season (Oct 2025 - Apr 2026)
python3 scripts/data_collection/season/fetch_season_games.py 2025-10-01
```

## 📊 Sample Output

```json
{
  "date": "2025-11-01",
  "total_players": 520,
  "total_games": 13,
  "players": [
    {
      "playerId": 8471234,
      "name": "Connor McDavid",
      "position": "C",
      "team": "EDM",
      "birthplace": "Richmond Hill, CAN",
      "points": 3,
      "goals": 1,
      "assists": 2,
      "time_on_ice": "22:45"
    }
    // ... 519 more players
  ]
}
```

## 📈 Performance

### Data Volume
- **Players per date:** 520+ (all active players)
- **Data size:** 15-30KB per date
- **API calls:** ~14 per date (1 schedule + 13 boxscores)
- **Time:** 2-3 minutes per date

### Rate Limiting
- 1 second delay between games
- 3 retry attempts on failure
- Timeout: 12 seconds per request

## ⚠️ Important Notes

### Slow Performance
Compared to Finnish-only system:
- **10-15x more data** (520 vs 28 players)
- **3-5x slower** (2-3 min vs 30-60 sec)
- **Larger files** (15-30KB vs 2-10KB)

### Use Case
**Finnish players only:** Use `../finnish/fetch.py` (fast)
**All players needed:** Use this script (slow but complete)

## 🆚 vs Finnish System

| Feature | Finnish System | Season System |
|---------|---------------|---------------|
| Players per date | 2-28 | 520+ |
| Data size | 2-10KB | 15-30KB |
| Time per date | 30-60 sec | 2-3 min |
| API calls | ~11 | ~14 |
| Cache needed | Yes (34 players) | No |
| Use case | Finnish tracking | Complete data |

## 🔧 Technical Details

**Endpoints Used:**
- Schedule: `GET /v1/schedule/{date}`
- Boxscore: `GET /v1/gamecenter/{gameId}/boxscore`
- Player info: `GET /v1/player/{id}/landing` (for all players)

**Rate Limits:**
- 1s between games
- 3s between retries
- 12s request timeout

## 📝 Example

```bash
# Fetch one week of data
python3 scripts/data_collection/season/fetch_season_games.py 2025-11-01

# Fetch month
python3 scripts/data_collection/season/fetch_season_games.py 2025-11-01 2025-11-30

# Check result
cat data/prepopulated/games/2025-11-01.json | jq '.total_players'
# Output: 520
```

## 🚨 Troubleshooting

### Slow Performance
**Cause:** Fetching 500+ players
**Solution:** Use Finnish system if you only need Finnish players

### API Errors
**Cause:** Rate limiting or network issues
**Solution:** Script retries automatically, wait and retry

### Large Files
**Cause:** All players included
**Solution:** Normal for season data, consider filtering

---

**Status:** ✅ Working (2025-11-22)
**Use Case:** Comprehensive season data
**Recommendation:** Use Finnish system unless you need all players
