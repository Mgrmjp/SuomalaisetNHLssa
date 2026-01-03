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
from datetime import datetime, timedelta
from pathlib import Path

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

def get_schedule_for_date(date):
    """Get NHL schedule for a specific date"""
    url = f"{NHL_API_BASE}/v1/schedule/{date}"
    data = fetch_from_api(url)
    if not data:
        return None

    game_week = data.get("gameWeek", [])
    if game_week and len(game_week) > 0:
        return game_week[0].get("games", [])
    return []

def get_game_details(game_id):
    """Get detailed game information including player stats"""
    url = f"{NHL_API_BASE}/v1/gamecenter/{game_id}/boxscore"
    return fetch_from_api(url)

def get_player_info(player_id):
    """Get player information"""
    url = f"{NHL_API_BASE}/v1/player/{player_id}/landing"
    return fetch_from_api(url)

def extract_all_players_from_game(game_data):
    """Extract all player IDs and info from a game"""
    players = {}

    if not game_data:
        return players

    player_stats = game_data.get("playerByGameStats", {})
    if not player_stats:
        return players

    # Process away team players
    away_stats = player_stats.get("awayTeam", {})
    for player_category in ["forwards", "defense", "goalies"]:
        for player in away_stats.get(player_category, []):
            player_id = player.get("playerId")
            if player_id and player_id not in players:
                players[player_id] = player

    # Process home team players
    home_stats = player_stats.get("homeTeam", {})
    for player_category in ["forwards", "defense", "goalies"]:
        for player in home_stats.get(player_category, []):
            player_id = player.get("playerId")
            if player_id and player_id not in players:
                players[player_id] = player

    return players

def main():
    print("Building comprehensive Finnish players cache...")
    print("=" * 60)
    print()

    # Scan last 30 days to find all Finnish players
    today = datetime.now()
    dates_to_scan = []

    for i in range(30):
        date = today - timedelta(days=i)
        # Skip future dates
        if date > datetime.now():
            continue
        dates_to_scan.append(date.strftime("%Y-%m-%d"))

    print(f"Scanning {len(dates_to_scan)} recent dates for Finnish players...")
    print()

    # Collect all unique player IDs
    all_player_ids = set()
    game_count = 0

    for date in dates_to_scan:
        games = get_schedule_for_date(date)

        for game in games:
            game_id = game.get("id")
            home_team = game.get("homeTeam", {}).get("abbrev", "UNK")
            away_team = game.get("awayTeam", {}).get("abbrev", "UNK")

            game_details = get_game_details(game_id)
            if game_details:
                players = extract_all_players_from_game(game_details)
                all_player_ids.update(players.keys())
                game_count += 1

        # Rate limiting
        time.sleep(0.5)

    print(f"Found {len(all_player_ids)} unique players across {game_count} games")
    print()

    # Check each player for Finnish nationality
    print("Checking nationality for all players...")
    print()

    finnish_players = {}
    checked_count = 0

    for player_id in sorted(all_player_ids):
        checked_count += 1
        print(f"[{checked_count}/{len(all_player_ids)}] Checking player {player_id}...", end=" ")

        player_info = get_player_info(player_id)

        if player_info and player_info.get("birthCountry") == "FIN":
            # Apply Finnish text corrections using Groq LLM
            player_info = normalize_finnish_player_data(player_info)

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
            }
            print(f"✓ {finnish_players[player_id]['name']} ({finnish_players[player_id]['position']})")
        else:
            print("Not Finnish")

        # Rate limiting
        time.sleep(0.2)

    print()
    print("=" * 60)
    print(f"✅ Built comprehensive cache with {len(finnish_players)} Finnish players")
    print()

    # Save cache
    cache_file = Path(__file__).parent / "finnish-players-full-cache.json"
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(finnish_players, f, indent=2, ensure_ascii=False)

    print(f"📁 Saved to: {cache_file}")
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
