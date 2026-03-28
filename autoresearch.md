# Autoresearch: Player Data Quality Validation

## Objective
Improve player data quality by catching and fixing inconsistent/bad data. Issues found:
- Wrong birthdates (e.g., Juuso Välimäki: born 2008 but drafted 2017 = age 9!)
- Wrong stats (e.g., 3 GP instead of correct 27 GP)
- Cross-league headshot assignment (Otto Salin using Otto Kivenmäki's photo)

## Metrics
- **Primary**: data_quality_score (% of players passing all validation checks, higher is better)
- **Secondary**: issue_count_birthdate, issue_count_stats, issue_count_headshot, issue_count_age_impossible

## How to Run
```bash
cd /home/miikka/dev/suomalaisetnhlssa
python scripts/data_collection/validate_prospect_data.py
```

## Validation Checks
1. **Age consistency**: birthDate must be consistent with draft year (age 17-40 at draft)
2. **Stats plausibility**: games played > 0 implies goals/assists should exist for skaters
3. **Headshot ownership**: headshot filename ID must match player's actual ID in source league
4. **League consistency**: headshot league prefix must match player's current league

## Files in Scope
- `scripts/data_collection/finnish/build_prospects_cache.py` - Data pipeline with validation
- `scripts/data_collection/validate_prospect_data.py` - Standalone validation script
- `static/data/finnish_prospects.json` - Target data file

## Off Limits
- Don't delete players without data - mark them as needing review instead
- Don't modify PlayerStats dataclass field names

## Constraints
- Validation must run in < 30 seconds
- All existing players with GOOD data must not be modified

## What's Been Tried
- Run 6: Fixed merge logic to prefer league_file sources over draft_picks/wikidata