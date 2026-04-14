#!/usr/bin/env python3
"""
Validate Finnish player cache against NHL Stats API master list.

This script compares the current Finnish player cache against the authoritative
NHL Stats API list to detect any missing Finnish players. It's designed to run
before daily updates to ensure no Finnish players are missed.

Usage: python validate_finnish_players.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import FINNISH_CACHE_FILE
from utils import load_json

import requests


def get_master_finnish_ids_from_api():
    """
    Fetch all Finnish player IDs from NHL Stats API.
    
    Returns:
        Dict mapping player_id -> {firstName, lastName, position, teamAbbrev}
    """
    players = {}
    
    print("Fetching master Finnish player list from NHL Stats API...")
    
    params = {
        "limit": -1,
        "cayenneExp": 'nationalityCode="FIN"'
    }
    
    # Fetch skaters
    try:
        url = "https://api.nhle.com/stats/rest/en/skater/bios"
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        for player in data.get("data", []):
            player_id = player.get("playerId")
            if player_id:
                players[player_id] = {
                    "firstName": player.get("firstName", ""),
                    "lastName": player.get("lastName", ""),
                    "position": player.get("positionCode", "N/A"),
                    "teamAbbrev": player.get("teamAbbrev", ""),
                }
        print(f"   Found {len(players)} skaters")
    except Exception as e:
        print(f"   ❌ Error fetching skaters: {e}")
        return None
    
    # Fetch goalies
    try:
        url = "https://api.nhle.com/stats/rest/en/goalie/bios"
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        goalie_count = 0
        for player in data.get("data", []):
            player_id = player.get("playerId")
            if player_id:
                players[player_id] = {
                    "firstName": player.get("firstName", ""),
                    "lastName": player.get("lastName", ""),
                    "position": "G",
                    "teamAbbrev": player.get("teamAbbrev", ""),
                }
                goalie_count += 1
        print(f"   Found {goalie_count} goalies")
    except Exception as e:
        print(f"   ❌ Error fetching goalies: {e}")
        return None
    
    print(f"   Total: {len(players)} Finnish players\n")
    return players


def validate_cache():
    """
    Validate Finnish player cache against NHL Stats API master list.
    
    Returns:
        Tuple of (missing_players, cache_players, master_players)
    """
    # Load current cache
    cache_data = load_json(FINNISH_CACHE_FILE) or {}
    cache_ids = set()
    for player_id in cache_data.keys():
        try:
            cache_ids.add(int(player_id))
        except (ValueError, TypeError):
            continue
    
    print(f"Current cache: {len(cache_ids)} players")
    print(f"Cache file: {FINNISH_CACHE_FILE}\n")
    
    # Fetch master list
    master_players = get_master_finnish_ids_from_api()
    if master_players is None:
        print("❌ Failed to fetch master list. Cannot validate.")
        return None, None, None
    
    master_ids = set(master_players.keys())
    
    # Find missing players
    missing_ids = master_ids - cache_ids
    missing_players = {pid: master_players[pid] for pid in missing_ids}
    
    # Find extra players (in cache but not in master list)
    extra_ids = cache_ids - master_ids
    
    print("=" * 60)
    print("VALIDATION RESULTS")
    print("=" * 60)
    print(f"✅ Master list (NHL Stats API): {len(master_ids)} players")
    print(f"✅ Cache (finnish-players.json): {len(cache_ids)} players")
    print(f"⚠️ Missing from cache: {len(missing_ids)} players")
    if extra_ids:
        print(f"ℹ️ Extra in cache (not in master list): {len(extra_ids)} players")
    print()
    
    if missing_players:
        print("🆕 MISSING FINNISH PLAYERS (should be added to cache):")
        print("-" * 60)
        for player_id, player_info in sorted(missing_players.items()):
            name = f"{player_info['firstName']} {player_info['lastName']}"
            position = player_info['position']
            team = player_info.get('teamAbbrev', 'N/A')
            print(f"   ID: {player_id:<10} | {name:<30} | {position} | {team}")
        print()
    
    if extra_ids:
        print("ℹ️ EXTRA PLAYERS IN CACHE (may be retired/inactive):")
        print("-" * 60)
        for player_id in sorted(extra_ids):
            player_data = cache_data.get(str(player_id), {})
            name = player_data.get('name', 'Unknown')
            position = player_data.get('position', 'N/A')
            team = player_data.get('currentTeam', 'N/A')
            print(f"   ID: {player_id:<10} | {name:<30} | {position} | {team}")
        print()
    
    return missing_players, cache_ids, master_ids


def main():
    print("Finnish Player Cache Validation")
    print("=" * 60)
    print()
    
    missing_players, cache_ids, master_ids = validate_cache()
    
    if missing_players is None:
        print("❌ Validation failed due to API errors")
        sys.exit(1)
    
    if missing_players:
        print(f"⚠️ Found {len(missing_players)} missing Finnish player(s)")
        print()
        print("To add these players, run:")
        print("  python scripts/data_collection/finnish/build_cache.py")
        print()
        sys.exit(2)  # Exit code 2 indicates missing players
    else:
        print("✅ All Finnish players from NHL Stats API are in cache!")
        print()
        sys.exit(0)


if __name__ == "__main__":
    main()
