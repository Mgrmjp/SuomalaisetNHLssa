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


def main():
    print("Building comprehensive Finnish players cache (Roster Scan Mode)...")
    print("=" * 60)
    print()

    # Get all teams
    print("Fetching active NHL teams...")
    teams = get_all_teams()
    print(f"Found {len(teams)} teams.")
    print()

    finnish_players = {}
    player_count = 0

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
                # Check nationality using birthCountry
                # Note: API uses 3-letter codes like "FIN", "USA", "SWE"
                if player.get("birthCountry") == "FIN":
                    player_id = player.get("id")
                    
                    # Skip if already found (though unlikely with team rosters)
                    if player_id in finnish_players:
                        continue

                    # Fetch full player details for cache consistency
                    # The roster has some info, but landing page has everything we need for the cache format
                    player_landing = get_player_info(player_id)
                    
                    if player_landing:
                         # Apply Finnish text corrections
                        player_info = normalize_finnish_player_data(player_landing)

                        finnish_players[player_id] = {
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
                        team_finnish_count += 1
                        player_count += 1
            
        print(f"Found {team_finnish_count} Finnish players")
        
        # Rate limiting
        time.sleep(0.5)



    print()
    print("=" * 60)
    print(f"✅ Built comprehensive cache with {len(finnish_players)} Finnish players")
    print()

    # Save cache
    with open(FINNISH_CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(finnish_players, f, indent=2, ensure_ascii=False)

    print(f"📁 Saved to: {FINNISH_CACHE_FILE}")
    print()

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
