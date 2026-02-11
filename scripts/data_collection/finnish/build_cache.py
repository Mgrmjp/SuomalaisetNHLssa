#!/usr/bin/env python3
"""
Build comprehensive Finnish players cache by scanning multiple game dates.

This script fetches player data from multiple recent games to build a complete
cache of all Finnish players currently in the NHL.

Usage: python build-finnish-cache-from-games.py
"""

import json
import requests
import time
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import FINNISH_CACHE_FILE
from utils import save_json, load_json

# Import Finnish text correction utilities
from finnish_text_utils import normalize_finnish_player_data

# NHL API endpoints
NHL_API_BASE = "https://api-web.nhle.com"

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
            time.sleep(2)
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


def get_boxscore(game_id):
    """Get detailed game information including player stats"""
    url = f"{NHL_API_BASE}/v1/gamecenter/{game_id}/boxscore"
    return fetch_from_api(url)

def get_team_roster(team_abbrev):
     """Get roster for a specific team"""
     url = f"{NHL_API_BASE}/v1/roster/{team_abbrev}/current"
     return fetch_from_api(url)

def get_player_info(player_id):
    """Get player information"""
    url = f"{NHL_API_BASE}/v1/player/{player_id}/landing"
    return fetch_from_api(url)


def get_master_finnish_player_ids():
    """
    Fetch all Finnish player IDs (skaters and goalies) from NHL Stats API.
    This uses nationalityCode="FIN" which correctly identifies all Finnish players
    regardless of birth country.
    """
    ids = set()
    skaters_ok = False
    goalies_ok = False
    
    # Endpoints
    skater_url = "https://api.nhle.com/stats/rest/en/skater/bios"
    goalie_url = "https://api.nhle.com/stats/rest/en/goalie/bios"
    
    params = {
        "limit": -1,
        "cayenneExp": 'nationalityCode="FIN"'
    }
    
    print("Fetching master list of Finnish players from Stats API...")
    
    # Skaters
    try:
        r = requests.get(skater_url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        count = 0
        for player in data.get("data", []):
            ids.add(player.get("playerId"))
            count += 1
        print(f"   Found {count} skaters")
        skaters_ok = True
    except Exception as e:
        print(f"   ❌ Error fetching skaters: {e}")

    # Goalies
    try:
        r = requests.get(goalie_url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        count = 0
        for player in data.get("data", []):
            ids.add(player.get("playerId"))
            count += 1
        print(f"   Found {count} goalies")
        goalies_ok = True
    except Exception as e:
        print(f"   ❌ Error fetching goalies: {e}")
        
    print(f"   Total unique Finnish players: {len(ids)}\n")
    return ids, (skaters_ok and goalies_ok and len(ids) > 0)

def load_existing_cache():
    """Load existing cache if available"""
    if FINNISH_CACHE_FILE.exists():
        try:
            return load_json(FINNISH_CACHE_FILE) or {}
        except:
            return {}
    return {}


def prune_cache_with_master_ids(existing_cache, master_finnish_ids):
    """
    Keep only players present in authoritative NHL Stats Finnish player IDs.
    """
    pruned_cache = {}
    for player_id, player_data in existing_cache.items():
        try:
            normalized_id = int(player_id)
        except (TypeError, ValueError):
            continue
        if normalized_id in master_finnish_ids:
            pruned_cache[player_id] = player_data
    return pruned_cache

def main():
    print("Building comprehensive Finnish players cache (Roster Scan Mode)...")
    print("=" * 60)
    print()

    # Load existing cache first to preserve manual edits/inactive players
    finnish_players = load_existing_cache()
    print(f"Loaded {len(finnish_players)} existing players from cache.")

    # Get all teams
    print("Fetching active NHL teams...")
    teams = get_all_teams()
    print(f"Found {len(teams)} teams.")
    print()

    player_count = 0
    new_players_count = 0

    # Get master list of Finnish players for robust identification
    master_finnish_ids, master_ids_reliable = get_master_finnish_player_ids()

    # Prune stale/incorrect players only when master IDs are fully reliable.
    # This prevents accidental data loss during partial API outages.
    if master_ids_reliable:
        before_prune = len(finnish_players)
        finnish_players = prune_cache_with_master_ids(finnish_players, master_finnish_ids)
        removed_count = before_prune - len(finnish_players)
        if removed_count > 0:
            print(f"🧹 Pruned {removed_count} non-Finnish stale entries from existing cache.\n")
    else:
        print("⚠️ Master Finnish IDs not fully reliable; skipping stale entry pruning.\n")

    # Scan each team's roster
    for i, team in enumerate(teams, 1):
        print(f"[{i}/{len(teams)}] Scanning {team} roster...", end=" ")
        
        roster = get_team_roster(team)
        if not roster:
            print("Failed to fetch roster")
            continue

        team_finnish_count = 0
        
        # Roster is grouped by position categories
        for category in ["forwards", "defensemen", "goalies"]:
            for player in roster.get(category, []):
                player_id = player.get("id")
                
                # Check if player is in our master list of Finnish players
                # Fallback to birthCountry check just in case stats API failed
                is_finnish = (player_id in master_finnish_ids) or (player.get("birthCountry") == "FIN")
                
                if is_finnish:
                    
                    # If already in cache, just update the team/active status to be safe, 
                    # but we should re-fetch to ensure data freshness occasionally.
                    # For now, let's always re-fetch if discovered on roster to keep data fresh.
                    
                    # Fetch full player details for cache consistency
                    # The roster has some info, but landing page has everything we need for the cache format
                    player_landing = get_player_info(player_id)
                    
                    if player_landing:
                         # Apply Finnish text corrections
                        player_info = normalize_finnish_player_data(player_landing)

                        player_data = {
                            "playerId": player_id,
                            "name": f"{player_info.get('firstName', {}).get('default', '')} {player_info.get('lastName', {}).get('default', '')}".strip(),
                            "firstName": player_info.get("firstName", {}),
                            "lastName": player_info.get("lastName", {}),
                            "position": player_info.get("position", "N/A"),
                            "sweaterNumber": player_info.get("sweaterNumber", 0),
                            "birthDate": player_info.get("birthDate", ""),
                            "birthCity": player_info.get("birthCity", {}),
                            "birthCountry": player_info.get("birthCountry", ""),
                            "birthplace": f"{player_info.get('birthCity', {}).get('default', '')}, {player_info.get('birthCountry', '')}",
                            "heightInches": player_info.get("heightInInches", 0),
                            "weightLbs": player_info.get("weightInPounds", 0),
                            "shootsCatches": player_info.get("shootsCatches", ""),
                            "headshot": player_info.get("headshot", ""),
                            "isActive": player_info.get("isActive", True),
                            "currentTeam": team  # Add current team info
                        }
                        
                        if player_id not in finnish_players:
                            new_players_count += 1
                            
                        finnish_players[player_id] = player_data
                        team_finnish_count += 1
                        player_count += 1
            
        print(f"Found {team_finnish_count} Finnish/Exception players")
        
        # Rate limiting
        time.sleep(0.5)

    print()
    print("=" * 60)
    print(f"✅ Built comprehensive cache with {len(finnish_players)} players")
    print(f"🆕 Added/Updated {new_players_count} newly discovered players")
    print()

    # Save cache
    save_json(finnish_players, FINNISH_CACHE_FILE)

    print(f"📁 Saved to: {FINNISH_CACHE_FILE}")
    print()

    # Sync to static roster location for frontend
    print("🔄 Syncing to static roster...")
    from sync_roster import sync_roster
    sync_roster()

    # Print summary by position
    positions = {}
    for player_id, player in finnish_players.items():
        pos = player["position"]
        positions[pos] = positions.get(pos, 0) + 1

    print("📊 Finnish players by position:")
    for pos, count in sorted(positions.items()):
        print(f"   {pos}: {count} players")
    print()

    # Print all players
    print("🌟 All Finnish players:")
    for player_id, player in sorted(finnish_players.items(), key=lambda x: x[1]["name"]):
        print(f"   {player['name']} (ID: {player_id}) - {player['position']}")

if __name__ == "__main__":
    main()
