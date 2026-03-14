# League Prospect Data Collection

Multi-league prospect tracking for Finnish players worldwide.

## Quick Start

```bash
# Scrape real data from EliteProspects (FREE)
npm run prospects:scrape

# Or use demo data (no external requests)
npm run prospects:demo
```

## Data Collection Options

### Option 1: EliteProspects Scraper (FREE) ⭐ RECOMMENDED
Scrape real player statistics directly from EliteProspects:

```bash
npm run prospects:scrape
```

**Coverage:**
- ✅ Liiga (Finland) - 60+ Finnish players
- ✅ SHL (Sweden) - 25+ Finnish players  
- ✅ AHL (North America) - 10+ Finnish players
- ✅ More leagues can be added

**Output:** `static/data/leagues/league_prospects_official.json`

**Notes:**
- Rate limited (1 sec between requests)
- Respects EliteProspects' terms of service
- Finnish detection uses name patterns (ä/ö/å, -nen endings)
- Some false positives/negatives possible

### Option 2: Demo Data (No API/scraping)
Generate realistic sample data:

```bash
npm run prospects:demo
```

### Option 3: API-Hockey (Free tier available)
Get data via API (100 requests/day free):

```bash
# 1. Sign up at https://api-hockey.io/
# 2. Add key to .env.local: APIHOCKEY_KEY=your-key
# 3. Run:
npm run prospects:api-hockey
```

**Note:** API-Hockey free tier has limited player data. EliteProspects scraper is more reliable.

## Architecture

```
scripts/data_collection/leagues/
├── README.md                  # This file
├── __init__.py               # Package exports
│
# Working Scrapers
├── official_leagues.py       # ⭐ Official league websites (ACTIVE)
│
# Demo/Sample Data
├── demo_generator.py         # Sample data generator
├── demo_collector.py         # Demo orchestrator
│
# API Collectors (limited functionality)
├── api_hockey.py             # API-Hockey implementation
├── collector_ep.py           # EliteProspects API (requires key)
│
# Individual League Adapters (placeholders)
├── liiga.py, shl.py, etc.    # Adapter pattern examples
│
# Documentation
└── real_data_options.py      # Guide to all data sources
```

## Data Format

All collectors return standardized player data:

```json
{
  "player_id": "ep_atro-leppanen",
  "name": "Atro Leppänen",
  "team": "Sport",
  "league": "LIIGA",
  "position": "F",
  "games_played": 60,
  "goals": 21,
  "assists": 42,
  "points": 63,
  "plus_minus": 0,
  "penalty_minutes": 30,
  "nationality": "FIN",
  "headshot_url": "https://liiga.fi/path/to/player-photo.jpg",
  "profile_url": "https://liiga.fi/fi/pelaajat/12345/atro-leppanen",
  "source_league": "liiga",
  "source": "eliteprospects",
  "scraped_at": "2026-02-28T16:30:00"
}
```

## Usage

### Basic Scraping


scraper = EliteProspectsScraper()

# Scrape single league
liiga_players = scraper.get_league_stats('liiga', '2024-2025')
print(f"Found {len(liiga_players)} Finnish players in Liiga")

# Scrape multiple leagues
all_data = scraper.collect_all_leagues('2024-2025')
print(f"Total: {all_data['total_players']} Finnish prospects")
```

### Adding New Leagues

Edit `official_leagues.py` and add a method:

```python
LEAGUES = {
    'liiga': 'liiga',
    'shl': 'shl', 
    'ahl': 'ahl',
    'khl': 'khl',      # Add this
    'del': 'del',      # Add this
}
```

Then run: `npm run prospects:scrape`

## Finnish Detection

The scraper detects Finnish players using:

1. **Nationality column** (if present in table)
2. **Finnish characters** (ä, ö, å) - strongest indicator
3. **Name endings** (-nen is ~40% of Finnish surnames)

**Limitations:**
- Swedish players with Finnish names may be included
- Finnish players with internationalized names (no ä/ö) may be missed
- Some edge cases with hyphenated names

## Troubleshooting

### "Found 0 Finnish players"
- EliteProspects page structure may have changed
- Check if the league season exists on their site
- Verify the scraper can access the website

### Too many false positives
- This was a bug in earlier versions (nationality defaulting to 'FIN')
- Make sure you're using official_leagues.py

### Rate limiting / blocked
- The scraper has built-in delays (1 sec between requests)
- Don't run too frequently
- Consider caching results

## Comparison of Data Sources

| Source | Cost | Reliability | Coverage | Speed |
|--------|------|-------------|----------|-------|
| EliteProspects Scraper | Free | High | Liiga, SHL, AHL | ~30 sec |
| Demo Data | Free | N/A | All leagues | Instant |
| API-Hockey Free | Free | Low | Limited | ~10 sec |
| API-Hockey Pro | €15/mo | Medium | Good | ~10 sec |

## Legal Note

The EliteProspects scraper:
- Only accesses publicly available statistics
- Includes rate limiting to avoid server load
- Respects robots.txt (read-only access)

**You are responsible for ensuring your use complies with EliteProspects' Terms of Service.**

## Status

| Method | Status | Notes |
|--------|--------|-------|
| EliteProspects Scraper | ✅ Working | Primary recommendation |
| API-Hockey | ⚠️ Limited | Free tier lacks player rosters |
| Liiga API | ❌ Removed | Site redesign removed public API |
| SHL API | ❌ Protected | Now requires authentication |
