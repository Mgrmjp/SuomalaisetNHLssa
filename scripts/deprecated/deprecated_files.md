# Deprecated Files - Removed in Reorganization

Files that were removed during scripts directory reorganization (2025-11-22).

## ❌ Why Removed?

These files were removed because they were:
- **Obsolete** - Outdated versions of current scripts
- **Misleading** - Appeared to work but had bugs
- **Incomplete** - Didn't do what they claimed
- **Redundant** - Multiple versions of same script

## 📦 Removed Files (11 total)

### Misleading Cache (1 file)
❌ `scripts/data/finnish-players-cache.json`
- **Reason:** Incomplete cache (only 18 players vs 34 needed)
- **Issue:** Caused "0 Finnish players" errors
- **Replaced by:** `scripts/data_collection/finnish/cache/finnish-players.json` (34 players)

---

### Obsolete Finnish Scripts (4 files)

❌ `scripts/data/fetch-finnish-players.py`
- **Reason:** Old slow version
- **Issue:** Checked every player individually (slow)
- **Replaced by:** `scripts/data_collection/finnish/fetch.py` (uses cache)

❌ `scripts/data/fetch-finnish-players-fast.py`
- **Reason:** Alternative version
- **Issue:** Not the primary/maintained version
- **Replaced by:** `scripts/data_collection/finnish/fetch.py`

❌ `scripts/data/build-finnish-cache.py`
- **Reason:** Incomplete cache builder
- **Issue:** Hardcoded list of only 18 players (outdated)
- **Replaced by:** `scripts/data_collection/finnish/build_cache.py`

❌ `scripts/data/build-finnish-cache-comprehensive.py`
- **Reason:** Never worked
- **Issue:** Used broken `/v1/teams` API endpoint (404 error)
- **Replaced by:** `scripts/data_collection/finnish/build_cache.py`

---

### Redundant Shell Scripts (3 files)

❌ `scripts/november_prepopulation.sh`
- **Reason:** Old version
- **Issue:** Not the final/fixed version
- **Replaced by:** `scripts/shell_wrappers/fetch_november_games.sh`

❌ `scripts/november_prepopulation_rate_limited.sh`
- **Reason:** Alternative version
- **Issue:** Unclear which version to use
- **Replaced by:** `scripts/shell_wrappers/fetch_november_games.sh`

❌ `scripts/november_prepopulation_with_progress.sh`
- **Reason:** Alternative version
- **Issue:** Multiple versions causing confusion
- **Replaced by:** `scripts/shell_wrappers/fetch_november_games.sh`

---

### Misleading NHL Script (1 file)

❌ `scripts/data/fetch-nhl-data.py`
- **Reason:** Misleading name
- **Issue:** Despite name "fetch-nhl-data", was actually Finnish-focused
- **Note:** Caused confusion about data type
- **Replaced by:** `scripts/data_collection/finnish/fetch.py` (clear name)

---

## ✅ What Replaced Them

### New Structure
```
scripts/
├── data_collection/
│   ├── finnish/
│   │   ├── fetch.py              # Main Finnish fetcher
│   │   ├── build_cache.py        # Cache builder
│   │   └── cache/finnish-players.json  # Complete cache
│   └── season/
│       └── fetch_season_games.py # All players
├── shell_wrappers/
│   ├── fetch-finnish-games.sh    # Date range wrapper
│   └── fetch_november_games.sh   # November data
└── utilities/
    ├── test_api.py               # API testing
    ├── check_season.py           # Season checking
    └── expand_games.py           # Data expansion
```

## 📊 Cleanup Impact

### Before Reorganization
- 19 files scattered randomly
- 6 Finnish scripts (confusing which to use)
- Multiple versions unclear
- Incomplete/misleading caches
- No documentation

### After Reorganization
- 8 files organized by purpose
- 1 clear Finnish system
- No confusion about versions
- Complete cache (34 players)
- Comprehensive documentation

## 🎯 Benefits

1. **Clarity:** No confusion about which script to use
2. **Accuracy:** No misleading incomplete caches
3. **Performance:** Cache-based system is faster
4. **Maintainability:** Clear structure for future changes
5. **Documentation:** README files explain everything

## 🔄 Migration Guide

### Old → New Command

| Old (REMOVED) | New (WORKING) |
|---------------|---------------|
| `python3 scripts/data/fetch-finnish-players.py` | `python3 scripts/data_collection/finnish/fetch.py` |
| `python3 scripts/data/build-finnish-cache.py` | `python3 scripts/data_collection/finnish/build_cache.py` |
| `bash scripts/november_prepopulation.sh` | `bash scripts/shell_wrappers/fetch_november_games.sh` |

### File Locations

| Old (REMOVED) | New (WORKING) |
|---------------|---------------|
| `scripts/data/finnish-players-cache.json` | `scripts/data_collection/finnish/cache/finnish-players.json` |
| `scripts/data/fetch-finnish-players-final.py` | `scripts/data_collection/finnish/fetch.py` |

## ⚠️ DO NOT USE

❌ These files no longer exist:
- `scripts/data/finnish-players-cache.json`
- `scripts/data/fetch-finnish-players.py`
- `scripts/data/fetch-finnish-players-fast.py`
- `scripts/data/build-finnish-cache.py`
- `scripts/data/build-finnish-cache-comprehensive.py`
- `scripts/november_prepopulation.sh`
- `scripts/november_prepopulation_rate_limited.sh`
- `scripts/november_prepopulation_with_progress.sh`
- `scripts/data/fetch-nhl-data.py`

✅ Use the new organized structure instead!

---

**Removal Date:** 2025-11-22
**Reason:** Cleanup and reorganization
**Status:** Files deleted, no longer available
