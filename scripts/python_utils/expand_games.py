#!/usr/bin/env python3
"""
Expand existing Finnish player data to include ALL players from the same games
This uses the game IDs we already discovered to get comprehensive data
"""

import json
import os
import requests
import time
from datetime import datetime
from pathlib import Path

NHL_API_BASE = "https://api-web.nhle.com"

def fetch_from_api(url, max_retries=2):
    """Fetch data from NHL API with retry logic"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=8)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                print(f"Error fetching {url}: {e}")
                return None
            time.sleep(2)  # Wait before retry
    return None

def get_game_details(game_id):
    """Get detailed game information including player stats"""
    url = f"{NHL_API_BASE}/v1/gamecenter/{game_id}/boxscore"
    return fetch_from_api(url)

def extract_all_player_data(game_data, game_id, home_team, away_team, game_date):
    """Extract all player data from game"""
    players = []

    if not game_data:
        return players

    # Get player stats from the correct API structure
    player_stats = game_data.get("playerByGameStats", {})
    if not player_stats:
        return players

    # Process away team players (forwards, defense, goalies)
    away_stats = player_stats.get("awayTeam", {})
    for player_category in ["forwards", "defense", "goalies"]:
        for player in away_stats.get(player_category, []):
            player_id = player.get("playerId")
            name = player.get("name", {}).get("default", "")
            position = player.get("position", "N/A")

            # Extract stats based on position
            if position == "G":
                # Goalie stats
                saves = player.get("saves", 0)
                save_pct = player.get("savePctg", 0.0)

                players.append({
                    "playerId": player_id,
                    "name": name.strip(),
                    "team": away_team,
                    "position": position,
                    "goals": 0,
                    "assists": 0,
                    "points": 0,
                    "shots": 0,
                    "plusMinus": 0,
                    "pim": player.get("pim", 0),
                    "timeOnIce": player.get("toi", "00:00"),
                    "isGoalie": True,
                    "saves": saves,
                    "savePct": round(save_pct, 3) if save_pct else 0.0,
                    "gameId": game_id,
                    "gameDate": game_date
                })
            else:
                # Skater stats (forwards and defense)
                players.append({
                    "playerId": player_id,
                    "name": name.strip(),
                    "team": away_team,
                    "position": position,
                    "goals": player.get("goals", 0),
                    "assists": player.get("assists", 0),
                    "points": player.get("points", 0),
                    "shots": player.get("sog", 0),
                    "plusMinus": player.get("plusMinus", 0),
                    "pim": player.get("pim", 0),
                    "timeOnIce": player.get("toi", "00:00"),
                    "isGoalie": False,
                    "saves": 0,
                    "savePct": 0.0,
                    "gameId": game_id,
                    "gameDate": game_date
                })

    # Process home team players (forwards, defense, goalies)
    home_stats = player_stats.get("homeTeam", {})
    for player_category in ["forwards", "defense", "goalies"]:
        for player in home_stats.get(player_category, []):
            player_id = player.get("playerId")
            name = player.get("name", {}).get("default", "")
            position = player.get("position", "N/A")

            # Extract stats based on position
            if position == "G":
                # Goalie stats
                saves = player.get("saves", 0)
                save_pct = player.get("savePctg", 0.0)

                players.append({
                    "playerId": player_id,
                    "name": name.strip(),
                    "team": home_team,
                    "position": position,
                    "goals": 0,
                    "assists": 0,
                    "points": 0,
                    "shots": 0,
                    "plusMinus": 0,
                    "pim": player.get("pim", 0),
                    "timeOnIce": player.get("toi", "00:00"),
                    "isGoalie": True,
                    "saves": saves,
                    "savePct": round(save_pct, 3) if save_pct else 0.0,
                    "gameId": game_id,
                    "gameDate": game_date
                })
            else:
                # Skater stats (forwards and defense)
                players.append({
                    "playerId": player_id,
                    "name": name.strip(),
                    "team": home_team,
                    "position": position,
                    "goals": player.get("goals", 0),
                    "assists": player.get("assists", 0),
                    "points": player.get("points", 0),
                    "shots": player.get("sog", 0),
                    "plusMinus": player.get("plusMinus", 0),
                    "pim": player.get("pim", 0),
                    "timeOnIce": player.get("toi", "00:00"),
                    "isGoalie": False,
                    "saves": 0,
                    "savePct": 0.0,
                    "gameId": game_id,
                    "gameDate": game_date
                })

    return players

def main():
    print("🏒 Expanding existing Finnish player data to include ALL players...")
    print("=" * 60)

    # Find existing Finnish player data files
    data_dir = Path("static/data/prepopulated/games")
    existing_files = list(data_dir.glob("2025-11-*.json"))
    existing_files.sort()

    if not existing_files:
        print("❌ No existing Finnish player data files found")
        return

    print(f"📁 Found {len(existing_files)} existing files")

    # Create output directory
    output_dir = Path("static/data/prepopulated/all-players")
    output_dir.mkdir(parents=True, exist_ok=True)

    all_players = []
    all_games = []
    processed_count = 0

    for file_path in existing_files:
        date_str = file_path.stem  # Extract date from filename

        print(f"\n📅 Processing {date_str}...")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                finnish_data = json.load(f)
        except Exception as e:
            print(f"   ❌ Error reading {file_path}: {e}")
            continue

        # Extract unique game IDs from Finnish player data
        finnish_players = finnish_data.get("players", [])
        game_ids = set()
        games_map = {}

        for player in finnish_players:
            game_id = player.get("game_id")
            if game_id:
                game_ids.add(game_id)
                # Store game info if available
                if "opponent" in player:
                    games_map[game_id] = {
                        "opponent": player["opponent"],
                        "game_score": player.get("game_score", ""),
                        "game_result": player.get("game_result", ""),
                        "team": player.get("team", "")
                    }

        print(f"   🎯 Found {len(game_ids)} unique games with Finnish players")

        if not game_ids:
            print(f"   ⚠️  No game IDs found in {date_str}")
            continue

        date_players = []

        for i, game_id in enumerate(game_ids, 1):
            print(f"   🏒 Game {i}/{len(game_ids)}: ID {game_id}")

            # Get detailed game data
            game_details = get_game_details(game_id)

            if game_details:
                # Extract all player data
                players = extract_all_player_data(
                    game_details,
                    game_id,
                    game_details.get("homeTeam", {}).get("abbrev", "UNK"),
                    game_details.get("awayTeam", {}).get("abbrev", "UNK"),
                    date_str
                )
                date_players.extend(players)

                # Add game summary
                home_team = game_details.get("homeTeam", {}).get("abbrev", "UNK")
                away_team = game_details.get("awayTeam", {}).get("abbrev", "UNK")
                home_score = game_details.get("homeTeam", {}).get("score", 0)
                away_score = game_details.get("awayTeam", {}).get("score", 0)

                all_games.append({
                    "gameId": game_id,
                    "gameDate": date_str,
                    "homeTeam": home_team,
                    "awayTeam": away_team,
                    "homeScore": home_score,
                    "awayScore": away_score,
                    "players_count": len(players)
                })

                print(f"      ✅ Extracted {len(players)} players ({away_team} {away_score} @ {home_team} {home_score})")

            else:
                print(f"      ❌ Failed to get details for game {game_id}")

            # Rate limiting
            time.sleep(3)

        all_players.extend(date_players)
        processed_count += 1

        # Save daily data
        daily_data = {
            "date": date_str,
            "games": [g for g in all_games if g["gameDate"] == date_str],
            "players": date_players,
            "total_players": len(date_players),
            "total_games": len(game_ids),
            "generated_at": datetime.now().isoformat()
        }

        output_file = output_dir / f"{date_str}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(daily_data, f, indent=2, ensure_ascii=False)

        print(f"   💾 Saved {len(date_players)} players from {len(game_ids)} games")

    # Create combined season file
    season_data = {
        "season": "2025-26",
        "period": "November 2025 (Expanded)",
        "games": all_games,
        "players": all_players,
        "total_games": len(all_games),
        "total_players": len(all_players),
        "processed_dates": processed_count,
        "generated_at": datetime.now().isoformat()
    }

    season_file = output_dir / "season-2025-26-november-expanded.json"
    with open(season_file, 'w', encoding='utf-8') as f:
        json.dump(season_data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Expansion complete!")
    print(f"   📅 Processed {processed_count} dates")
    print(f"   🏒 Total games: {len(all_games)}")
    print(f"   👥 Total players: {len(all_players)}")
    print(f"   📁 Daily files: {output_dir}")
    print(f"   📄 Season file: {season_file}")

    # Show some statistics
    if all_players:
        # Top scorers
        scorers = sorted(all_players, key=lambda x: x["points"], reverse=True)[:10]
        print(f"\n🌟 Top 10 Scorers:")
        for i, player in enumerate(scorers, 1):
            print(f"   {i:2d}. {player['name']} ({player['team']}) - {player['points']} pts")

        # Team player counts
        team_counts = {}
        for player in all_players:
            team = player["team"]
            team_counts[team] = team_counts.get(team, 0) + 1

        print(f"\n📊 Players by Team:")
        for team, count in sorted(team_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   {team}: {count} players")

if __name__ == "__main__":
    main()