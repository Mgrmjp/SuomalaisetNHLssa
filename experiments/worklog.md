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