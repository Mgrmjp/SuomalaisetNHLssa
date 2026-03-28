# Autoresearch: Headshot Coverage Optimization

## Objective
Improve headshot coverage for Finnish prospects across all leagues from ~70% to 95%+. Current issues:
- DEL, ICEHL, USHL have 0% headshot coverage (no extraction in adapters)
- Liiga missing 81/444 (18%), SHL missing 12/114 (10%)
- Schema inconsistency: Puppeteer uses `image`, Python uses `headshot_url`

## Metrics
- **Primary**: headshot_coverage_rate (% of players with headshot_url populated, higher is better)
- **Secondary**: league_coverage_DEL, league_coverage_ICEHL, league_coverage_Liiga, league_coverage_SHL

## How to Run
```bash
cd /home/miikka/dev/suomalaisetnhlssa
python -c "
import json
data = json.load(open('static/data/leagues/league_prospects_official.json'))
total = len(data['players'])
with_headshot = sum(1 for p in data['players'] if p.get('headshot_url'))
print(f'headshot_coverage_rate={with_headshot/total*100:.2f}')
"
```

## Files in Scope
- `scripts/data_collection/leagues/del_.py` - DEL adapter (no headshot extraction)
- `scripts/data_collection/leagues/icehl.py` - ICEHL adapter (no headshot in JSON)
- `scripts/data_collection/leagues/scraper_liiga.py` - Liiga scraper
- `scripts/data_collection/official_leagues.py` - Main orchestrator
- `scripts/data_collection/leagues/base.py` - Base adapter with headshot extraction helpers
- `scripts/data_collection/headshots/sync_prospect_headshots.py` - Headshot downloader

## Off Limits
- Don't modify PlayerStats dataclass field names (breaks serialization)
- Don't remove league adapters entirely

## Constraints
- Must maintain >90% success rate for existing working leagues
- Headshot URLs must be valid (reachable, not placeholder)

## What's Been Tried
- Run 1: Added player page validation to Mestis scraper (preventing wrong images)