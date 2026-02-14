#!/usr/bin/env python3
"""
Build Finnish prospects cache by scanning NHL team prospect lists.

This script fetches prospect data from all NHL teams, filters for Finnish players,
and then fetches detailed info for each to determine their current league and stats.
"""

import json
import requests
import time
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import DATA_DIR
from utils import save_json, load_json

# NHL API endpoints
NHL_API_BASE = "https://api-web.nhle.com"
PROSPECTS_CACHE_FILE = DATA_DIR / "finnish_prospects.json"

def fetch_from_api(url, max_retries=3):
    """Fetch data from NHL API with retry logic"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                print(f"Error fetching {url}: {e}")
                return None
            time.sleep(1)
    return None

def get_all_teams():
    """Get list of all active NHL team abbreviations"""
    url = f"{NHL_API_BASE}/v1/standings/now"
    data = fetch_from_api(url)
    teams = []
    if data and "standings" in data:
        for record in data["standings"]:
            teams.append(record.get("teamAbbrev", {}).get("default"))
    return sorted(list(set(filter(None, teams))))

def get_team_prospects(team_abbr):
    """Get prospects for a specific team"""
    url = f"{NHL_API_BASE}/v1/prospects/{team_abbr}"
    return fetch_from_api(url)

def get_player_landing(player_id):
    """Get detailed player info including current stats"""
    url = f"{NHL_API_BASE}/v1/player/{player_id}/landing"
    return fetch_from_api(url)

def normalize_season_stats(stats_list):
    """
    Extract the most relevant recent season stats.
    Prioritize current season (20242025).
    """
    if not stats_list:
        return None
        
    current_season = "20242025"
    
    # Try to find current season in explicit leagues
    for season in stats_list:
        if str(season.get("season")) == current_season:
            return season
            
    # Fallback to the most recent one if current season not found
    return stats_list[-1] if stats_list else None

def get_draft_class(year):
    """Fetch all players drafted in a specific year"""
    # Use V1 endpoint which returns all picks for the year
    # https://api-web.nhle.com/v1/draft/picks/{year}/all
    url = f"{NHL_API_BASE}/v1/draft/picks/{year}/all"
    return fetch_from_api(url)

def search_player_id(name):
    """Search for player ID by name using NHL search API"""
    url = "https://search.d3.nhle.com/api/v1/search/player"
    params = {
        "culture": "en-us",
        "limit": 5,
        "q": name
    }
    try:
        r = requests.get(url, params=params, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if len(data) > 0:
                # Return the ID of the first match
                return data[0].get("playerId")
    except Exception as e:
        print(f"Error searching for {name}: {e}")
    return None

def main():
    print("Building Finnish prospects cache...")
    print("=" * 60)

    # ensure data dir exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    finnish_prospects = {}
    
    # 1. Scan Team Prospect Lists
    teams = get_all_teams()
    print(f"Scanning {len(teams)} teams for Finnish prospects...")
    
    for i, team in enumerate(teams, 1):
        print(f"[{i}/{len(teams)}] Checking {team}...", end=" ")
        
        prospects_data = get_team_prospects(team)
        if not prospects_data:
            print("Failed to fetch")
            continue

        team_finnish_count = 0
        
        for category in ["forwards", "defensemen", "goalies"]:
            for player in prospects_data.get(category, []):
                if player.get("birthCountry") == "FIN":
                    player_id = player.get("id")
                    
                    # Store minimal info to start, will enrich later
                    finnish_prospects[player_id] = {
                        "id": player_id,
                        "nhlRights": team, 
                        # Name/Position/etc will be solidified during enrichment
                        "name": f"{player.get('firstName', {}).get('default')} {player.get('lastName', {}).get('default')}",
                        "position": player.get("positionCode"),
                        "headshot": player.get("headshot"),
                        "height": player.get("heightInCentimeters"),
                        "weight": player.get("weightInKilograms"),
                        "birthDate": player.get("birthDate"),
                    }
                    team_finnish_count += 1

        print(f"Found {team_finnish_count}")
        time.sleep(0.1)

    # 2. Scan Recent Drafts (Robustness Check)
    # Scan last 5 drafts (2020-2024)
    # Adjust range to include 2024 (current latest)
    current_year = datetime.now().year
    draft_years = range(2020, 2025) 
    
    print(f"\nScanning Draft History ({draft_years[0]}-{draft_years[-1]}) for missing prospects...")
    
    for year in draft_years:
        print(f"Checking Draft {year}...", end=" ")
        draft_data = get_draft_class(year)
        
        year_count = 0
        if draft_data and "picks" in draft_data:
            for pick in draft_data["picks"]:
                # V1 structure: pick has 'countryCode' (e.g. "FIN")
                if pick.get("countryCode") == "FIN":
                    # Check if we already have this player via ID (if present) or Name
                    # V1 draft response usually lacks ID, so we might duplicate check by name if needed?
                    # For now, let's assume we lack ID and MUST search if we want to confirm absence.
                    # Or better: search only if we suspect they are missing.
                    # But without ID, we can't check 'if pid in finnish_prospects'.
                    # So we construct name.
                    fname = pick.get("firstName")
                    if isinstance(fname, dict): fname = fname.get("default")
                    lname = pick.get("lastName")
                    if isinstance(lname, dict): lname = lname.get("default")
                    
                    full_name = f"{fname} {lname}"
                    
                    # Check if name already exists in our list? (Optimization)
                    already_have = False
                    for existing in finnish_prospects.values():
                        if existing.get("name") == full_name:
                            already_have = True
                            break
                    
                    if not already_have:
                        # Missing! Need to find ID.
                        print(f"  Searching for missing: {full_name}...", end=" ")
                        pid = search_player_id(full_name)
                        
                        if pid:
                            # Double check ID existence (maybe name match was fuzzy?)
                            if pid in finnish_prospects:
                                print(f"Found (ID {pid} already exists)")
                                continue
                                
                            print(f"FOUND ID: {pid}")
                            finnish_prospects[pid] = {
                                "id": pid,
                                "nhlRights": pick.get("teamAbbrev"), # Drafting team
                                "name": full_name,
                                # birthDate will come from landing
                            }
                            year_count += 1
                        else:
                            print("ID Not Found")
                            
        print(f"Added {year_count} new")
        time.sleep(0.5)

    # 3. Enrich and Validate
    print(f"\nEnriching data for {len(finnish_prospects)} total players...")
    final_list = []
    
    for pid, p_data in finnish_prospects.items():
        if not pid: continue # Skip invalid IDs
        landing = get_player_landing(pid)
        if not landing:
            print(f"Skipping {pid} (No landing data)")
            continue
            
        # Extract current status
        current_stats = None
        league = "Unknown"
        current_team = "Unknown"
        stats = {}
        
        # Try featured stats first
        featured = landing.get("featuredStats", {})
        if featured and featured.get("season") == 20242025:
             current_stats = featured.get("regularSeason", {}).get("subSeason", {})
             
        # Fallback to season totals
        if not current_stats:
            season_totals = landing.get("seasonTotals", [])
            most_recent = normalize_season_stats(season_totals)
            if most_recent:
                league = most_recent.get("leagueAbbrev", "Unknown")
                current_team = most_recent.get("teamName", {}).get("default", "Unknown")
                stats = {
                    "gp": most_recent.get("gamesPlayed", 0),
                    "goals": most_recent.get("goals", 0),
                    "assists": most_recent.get("assists", 0),
                    "points": most_recent.get("points", 0),
                    "savePct": most_recent.get("savePctg", 0.0) 
                }
        else:
            # Re-do: Always prioritized finding the season entry in SeasonTotals that matches 20242025
            season_totals = landing.get("seasonTotals", [])
            # Find 20242025 or last
            target = normalize_season_stats(season_totals)
            if target:
                league = target.get("leagueAbbrev", "Unknown")
                current_team = target.get("teamName", {}).get("default", "Unknown")
                stats = {
                    "gp": target.get("gamesPlayed", 0),
                    "goals": target.get("goals", 0),
                    "assists": target.get("assists", 0),
                    "points": target.get("points", 0),
                    "savePct": current_stats.get("savePctg", 0.0) 
                }

        # Check if playing in NHL but already "established"?
        # User wants "Prospects". If GP > 100? or Age > 24?
        # Let's keep everyone for now, maybe filter in frontend or here.
        # Ideally, we filter out guys like Luukkonen (starter).
        # Heuristic: If NHL games > 50 in career? 
        # For robustness, let's keep them in the file but maybe flag them?
        # Or just keep it simple. User said "Prospects". Luukkonen is borderline 'Alumni' now.
        # Leaving as is for now.

        p_data["currentTeam"] = current_team
        p_data["league"] = league
        p_data["stats"] = stats
        # Ensure basics are populated if coming from Draft loop
        if "headshot" not in p_data or not p_data["headshot"]:
             p_data["headshot"] = landing.get("headshot")
        if "position" not in p_data:
             p_data["position"] = landing.get("position", "U") 
        if "birthDate" not in p_data or not p_data["birthDate"]:
             p_data["birthDate"] = landing.get("birthDate")

        final_list.append(p_data)
        # print(f"  Processed {p_data['name']}")
        time.sleep(0.05)

    print(f"\nFinal count: {len(final_list)}")
    save_json(final_list, PROSPECTS_CACHE_FILE)
    print(f"Saved to {PROSPECTS_CACHE_FILE}")

if __name__ == "__main__":
    main()
