# Worklog: Headshot Coverage Optimization

## Session Summary
- **Goal**: Improve headshot coverage from ~82% to 95%+
- **Metric**: headshot_coverage_rate (% of players with headshot_url populated)
- **Baseline**: 82.54% (638/773 players)

## Problem Analysis
- DEL, ICEHL, USHL, OHL, Extraliga: 0% coverage (no extraction in adapters)
- Liiga: 81.76% (81/444 missing)
- SHL: 89.47% (12/114 missing)

## Experiments

### Run 1: Baseline
- **Timestamp**: 2026-03-28
- **What changed**: Established baseline metrics
- **Result**: headshot_coverage_rate=82.54%
- **Insight**: Main gaps are leagues with 0% coverage - DEL, ICEHL, USHL
- **Next**: Add headshot extraction to DEL adapter (HTML-based, should have images)

### Run 2: DEL Headshot Extraction
- **Timestamp**: 2026-03-28 17:10
- **What changed**: Added _fetch_del_headshot method to DELAdapter - extracts profile_url from player table, then fetches headshot from alc-player-info-banner__img div
- **Result**: headshot_coverage_rate=84.78% (+2.24%), DEL=100% (was 0%)
- **Insight**: DEL website stores headshots at /fileadmin/_processed_/* which doesn't match generic heuristics. Needed DEL-specific extraction.
- **Next**: Fix ICEHL adapter (also 0%)

### Run 3: USHL Headshot Extraction
- **Timestamp**: 2026-03-28 17:16
- **What changed**: Added _build_hockeytech_headshot_url() call to USHL player extraction
- **Result**: headshot_coverage_rate=85.55% (+0.77%), USHL=100% (was 0%)
- **Insight**: USHL HockeyTech API doesn't include headshot URLs in response, but standard assets.leaguestat.com URL pattern works.
- **Next**: ICEHL has no accessible headshot source - skip. Focus on Liiga (81.76%) and SHL (89.47%)

### Run 4: Fix Wrong Headshot Assignment (CRITICAL BUG FIX)
- **Timestamp**: 2026-03-28 17:30
- **What changed**: 
  1. Cleaned finnish_prospects.json - cleared 50 mismatched headshots
  2. Added _is_headshot_url_consistent() validation in build_prospects_cache.py
  3. Modified ingest_league_prospects_files() to skip headshots when league mismatch detected
- **Result**: 0 mismatches (was 50!), but coverage may drop temporarily as wrong headshots were cleared
- **Insight**: Root cause was name-based matching could incorrectly match players (especially similar first names like 'Otto') and assign wrong headshots. Otto Salin (AHL) had Otto Kivenmäki's Liiga headshot!
- **Next**: Need to re-fetch correct headshots for affected players or accept showing no photo for now

### Run 5: Robust Headshot Validation System
- **Timestamp**: 2026-03-28 17:45
- **What changed**: Added comprehensive validation to PREVENT wrong assignments:
  1. _build_league_player_lookups() - Maps player IDs to names for each league
  2. _extract_league_id_from_headshot() - Extracts ID from headshot URL filename
  3. _names_are_compatible() - Validates first AND last name match
  4. _validate_headshot_assignment() - Pre-assignment validation
- **Result**: Validation correctly catches Otto Salin trying to use Otto Kivenmäki's headshot (Invalid!)
- **Insight**: Now when pipeline runs, wrong headshots will be rejected BEFORE assignment, not after
- **Next**: Rebuild finnish_prospects.json with the fixed pipeline to re-fetch correct headshots

### Run 6: Fix Player Data Merge (Juuso Välimäki wrong age)
- **Timestamp**: 2026-03-28 17:55
- **What changed**: 
  1. Added _has_league_file_source() - checks if source includes league_file:
  2. Added _validate_player_data_consistency() - detects impossible ages (draft 2017 but born 2008 = age 9!)
  3. Modified dedupe_final_players() to prefer league_file sources over other sources for stats/birthDate
- **Result**: Validation correctly detects "impossible_age: draft_year=2017, birth_year=2008, age=9"
- **Insight**: Root cause was that draft_picks/wikidata sources were overriding correct league-direct data. League sources should always take priority for stats since they come directly from the league.
- **Next**: Rebuild finnish_prospects.json with the fixed pipeline