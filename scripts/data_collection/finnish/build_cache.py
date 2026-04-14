#!/usr/bin/env python3
"""
Build comprehensive Finnish players cache using NHL Stats API as primary source.

This script fetches the authoritative list of ALL Finnish players (nationalityCode="FIN")
from the NHL Stats API, then fetches full player data for each one. This ensures
players on AHL/minor league teams are tracked BEFORE they get called up to the NHL.

The roster scan is used as a secondary source to enrich data with current team info
for players on active NHL rosters.

Usage: python build_cache.py [--dry-run]
"""

import json
import requests
import time
import sys
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import FINNISH_CACHE_FILE
from utils import save_json, load_json, fetch_from_api, player_landing_url

# Import Finnish text correction utilities
from finnish_text_utils import normalize_finnish_player_data

# NHL API endpoints
NHL_API_BASE = "https://api-web.nhle.com"
NHL_STATS_API = "https://api.nhle.com/stats/rest/en"


def get_master_finnish_players():
    """
    Fetch ALL Finnish players (skaters and goalies) from NHL Stats API.
    
    This uses nationalityCode="FIN" which correctly identifies all Finnish players
    regardless of birth country or current team assignment.
    
    Returns:
        Tuple of (player_ids_dict, is_reliable)
        - player_ids_dict: {player_id: {firstName, lastName, position, teamAbbrev}}
        - is_reliable: True if both skater and goalie endpoints succeeded
    """
    players = {}
    skaters_ok = False
    goalies_ok = False

    print("Fetching master list of Finnish players from NHL Stats API...")

    # Fetch skaters
    skater_url = f"{NHL_STATS_API}/skater/bios"
    params = {
        "limit": -1,
        "cayenneExp": 'nationalityCode="FIN"'
    }

    try:
        r = requests.get(skater_url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        count = 0
        for player in data.get("data", []):
            player_id = player.get("playerId")
            if player_id:
                players[player_id] = {
                    "firstName": player.get("firstName", ""),
                    "lastName": player.get("lastName", ""),
                    "position": player.get("positionCode", "N/A"),
                    "teamAbbrev": player.get("teamAbbrev", ""),
                    "birthCountry": player.get("birthCountry", ""),
                    "nationalityCode": player.get("nationalityCode", ""),
                }
                count += 1
        print(f"   Found {count} skaters")
        skaters_ok = True
    except Exception as e:
        print(f"   ❌ Error fetching skaters: {e}")

    # Fetch goalies
    goalie_url = f"{NHL_STATS_API}/goalie/bios"
    try:
        r = requests.get(goalie_url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        count = 0
        for player in data.get("data", []):
            player_id = player.get("playerId")
            if player_id:
                players[player_id] = {
                    "firstName": player.get("firstName", ""),
                    "lastName": player.get("lastName", ""),
                    "position": "G",
                    "teamAbbrev": player.get("teamAbbrev", ""),
                    "birthCountry": player.get("birthCountry", ""),
                    "nationalityCode": player.get("nationalityCode", ""),
                }
                count += 1
        print(f"   Found {count} goalies")
        goalies_ok = True
    except Exception as e:
        print(f"   ❌ Error fetching goalies: {e}")

    is_reliable = skaters_ok and goalies_ok and len(players) > 0
    print(f"   Total unique Finnish players: {len(players)}\n")
    return players, is_reliable


def get_current_nhl_rosters():
    """
    Get current rosters for all NHL teams to enrich player data with team info.
    
    Returns:
        Dict mapping player_id -> team_abbrev for players on NHL rosters
    """
    print("Fetching current NHL team rosters for team enrichment...")
    
    # Get all teams
    url = f"{NHL_API_BASE}/v1/standings/now"
    standings_data = fetch_from_api(url)
    teams = []
    if standings_data and "standings" in standings_data:
        for record in standings_data["standings"]:
            abbrev = record.get("teamAbbrev", {}).get("default")
            if abbrev:
                teams.append(abbrev)
    
    print(f"   Found {len(teams)} teams")
    
    player_teams = {}
    for team in teams:
        roster_url = f"{NHL_API_BASE}/v1/roster/{team}/current"
        roster = fetch_from_api(roster_url)
        if roster:
            for category in ["forwards", "defensemen", "goalies"]:
                for player in roster.get(category, []):
                    player_id = player.get("id")
                    if player_id:
                        player_teams[player_id] = team
        time.sleep(0.3)
    
    print(f"   Found {len(player_teams)} players on NHL rosters\n")
    return player_teams


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


def fetch_player_landing(player_id):
    """Fetch full player data from NHL API landing page"""
    return fetch_from_api(player_landing_url(player_id))


def build_player_cache_entry(player_landing, team_abbrev=None):
    """
    Build a standardized cache entry from player landing data.
    
    Args:
        player_landing: Full player data from NHL API
        team_abbrev: Current team abbreviation (from roster scan or stats API)
    
    Returns:
        Standardized player data dict
    """
    if not player_landing:
        return None
    
    # Apply Finnish text corrections
    player_info = normalize_finnish_player_data(player_landing)
    
    # Use provided team or fall back to player's currentTeam
    team = team_abbrev or player_info.get("currentTeamAbbrev", "")
    
    return {
        "playerId": player_info.get("playerId"),
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
        "currentTeam": team
    }


def main():
    parser = argparse.ArgumentParser(description='Build Finnish players cache')
    parser.add_argument('--dry-run', action='store_true', help='Only show what would be done without fetching player data')
    args = parser.parse_args()

    print("Building comprehensive Finnish players cache (Master List Mode)...")
    print("=" * 60)
    print()

    # Load existing cache first to preserve manual edits/inactive players
    finnish_players = load_existing_cache()
    print(f"Loaded {len(finnish_players)} existing players from cache.")
    print()

    # Step 1: Get master list of ALL Finnish players from Stats API
    master_finnish_players, master_ids_reliable = get_master_finnish_players()
    master_finnish_ids = set(master_finnish_players.keys())

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

    # Step 2: Get current NHL rosters for team enrichment
    player_teams = get_current_nhl_rosters()

    # Step 3: Fetch full player data for ALL Finnish players from master list
    missing_from_cache = []
    for player_id, player_meta in master_finnish_players.items():
        player_id_str = str(player_id)
        if player_id_str not in finnish_players:
            missing_from_cache.append((player_id, player_meta))

    print(f"Found {len(missing_from_cache)} Finnish players missing from cache")
    print()

    if args.dry_run:
        print("🔍 DRY RUN - would add these players:")
        print("-" * 60)
        for player_id, player_meta in sorted(missing_from_cache)[:20]:
            name = f"{player_meta.get('firstName', '')} {player_meta.get('lastName', '')}"
            position = player_meta.get('position', 'N/A')
            team = player_meta.get('teamAbbrev', 'N/A')
            print(f"   ID: {player_id:<10} | {name:<30} | {position} | {team}")
        if len(missing_from_cache) > 20:
            print(f"   ... and {len(missing_from_cache) - 20} more")
        print()
        print("Run without --dry-run to actually fetch and add these players")
        return

    if not missing_from_cache:
        print("✅ All Finnish players from NHL Stats API are already in cache!")
        print()
        # Still update team info for existing players
        updated_players_count = 0
        for player_id_str, existing in finnish_players.items():
            try:
                player_id = int(player_id_str)
            except (ValueError, TypeError):
                continue
            if player_id in player_teams:
                old_team = existing.get("currentTeam", "")
                new_team = player_teams[player_id]
                if old_team != new_team:
                    existing["currentTeam"] = new_team
                    updated_players_count += 1

        if updated_players_count > 0:
            print(f"🔄 Updated team info for {updated_players_count} existing players")
            save_json(finnish_players, FINNISH_CACHE_FILE)
            from sync_roster import sync_roster
            sync_roster()
        return

    # Fetch missing players using concurrent requests with rate limiting
    print("Fetching full player data for missing Finnish players...")
    print("(using concurrent requests with rate limiting)")
    print()

    new_players_count = 0
    failed_fetches = []
    max_workers = 5  # Concurrent workers (conservative to avoid rate limiting)
    batch_size = 20  # Process in batches to show progress
    processed = 0

    def fetch_single_player(player_id, player_meta):
        """Fetch data for a single player"""
        player_landing = fetch_player_landing(player_id)
        if player_landing:
            team = player_teams.get(player_id, player_meta.get("teamAbbrev", ""))
            player_data = build_player_cache_entry(player_landing, team)
            if player_data:
                return player_id, player_data
        return player_id, None

    # Process in batches to show progress and manage rate limiting
    for batch_start in range(0, len(missing_from_cache), batch_size):
        batch = missing_from_cache[batch_start:batch_start + batch_size]
        batch_results = {}

        # Use thread pool for concurrent fetching
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(fetch_single_player, pid, pmeta): (pid, pmeta)
                for pid, pmeta in batch
            }

            for future in as_completed(futures):
                player_id, player_data = future.result()
                if player_data:
                    finnish_players[str(player_id)] = player_data
                    new_players_count += 1
                else:
                    player_meta = futures[future][1]
                    failed_fetches.append(player_id)

        processed += len(batch)
        print(f"   Progress: {processed}/{len(missing_from_cache)} players processed ({new_players_count} added)")

        # Rate limit between batches
        if batch_start + batch_size < len(missing_from_cache):
            time.sleep(1)

    print()
    print("=" * 60)
    print(f"✅ Built comprehensive cache with {len(finnish_players)} players")
    print(f"🆕 Added {new_players_count} newly discovered players")
    if failed_fetches:
        print(f"❌ Failed to fetch {len(failed_fetches)} players: {failed_fetches[:10]}{'...' if len(failed_fetches) > 10 else ''}")
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
        team = player.get('currentTeam', 'N/A')
        print(f"   {player['name']} (ID: {player_id}) - {player['position']} - {team}")

if __name__ == "__main__":
    main()
