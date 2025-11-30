# Data Collection Scripts

Main data fetching scripts, organized by data type and purpose.

## 📁 Structure

### `finnish/` - Finnish Players Only
**Purpose:** Fetch 2-28 Finnish players per date
**Speed:** Fast (30-60 seconds)
**Data Size:** Small (2-10KB)
**Cache:** Required (34 players)

**Scripts:**
- `fetch.py` - Main Finnish fetcher
- `build_cache.py` - Build/update cache
- `cache/finnish-players.json` - Player cache

**Use For:**
- ✅ Finnish player tracking
- ✅ Performance monitoring
- ✅ Daily updates
- ✅ Historical Finnish data

---

### `season/` - All NHL Players
**Purpose:** Fetch 500+ players per date
**Speed:** Slow (2-3 minutes)
**Data Size:** Large (15-30KB)
**Cache:** Not required

**Scripts:**
- `fetch_season_games.py` - All players fetcher

**Use For:**
- ✅ Complete season data
- ✅ All nationalities
- ✅ Research projects
- ❌ Not for Finnish-only tracking

---

### `headshots/` - Player Images
**Purpose:** Download player thumbnail images
**Output:** `static/headshots/thumbs/{playerId}.jpg`
**Size:** 40x40px thumbnails

**Scripts:**
- `fetch_thumbnails.py` - Download headshots

**Use For:**
- ✅ Player avatars
- ✅ UI thumbnails
- ✅ Offline image cache

---

## 🎯 Choosing System

### Need Finnish Players?
→ Use `finnish/` system

### Need All Players?
→ Use `season/` system

### Need Player Images?
→ Use `headshots/` system

## 📊 Comparison

| System | Players | Speed | Size | Cache |
|--------|---------|-------|------|-------|
| Finnish | 2-28 | Fast | Small | Yes |
| Season | 500+ | Slow | Large | No |
| Headshots | N/A | Medium | Varies | Optional |

## 🚀 Quick Start

```bash
# Finnish players (recommended for Finnish tracking)
python3 scripts/data_collection/finnish/fetch.py 2025-11-01

# All players (comprehensive but slow)
python3 scripts/data_collection/season/fetch_season_games.py 2025-11-01

# Player headshots
python3 scripts/data_collection/headshots/fetch_thumbnails.py
```

## 📝 Requirements

- Python 3.9+
- `requests` library
- Optional: `Pillow` for image resizing

## ⚠️ Important

**Don't mix systems:**
- Finnish data ≠ Season data
- Different schemas, different purposes
- Use the right system for your need

---

**Last Updated:** 2025-11-22
**Finnish Cache:** 34 players (complete)
**System Status:** ✅ All working
