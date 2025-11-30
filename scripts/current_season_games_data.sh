#!/bin/bash

# Script to generate data for ALL played games in the current NHL season (2025-26)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

SEASON_START="2025-10-01"  # Approximate start of 2025-26 season
TODAY=$(date +%Y-%m-%d)

echo -e "${BLUE}🏒 Fetching ALL played games data for 2025-26 NHL Season...${NC}"
echo -e "${CYAN}Season: 2025-26 | From: $SEASON_START | To: $TODAY${NC}"
echo

# Create the comprehensive season data fetcher
create_season_script() {
    echo -e "${CYAN}Creating season games data fetcher...${NC}"

    cat > scripts/data/fetch-season-games.py << 'EOF'
#!/usr/bin/env python3
"""
Complete NHL Season Data Generator

Fetches ALL games and player data for the current NHL season.
This version gets complete game data for all players across the entire season.
Usage: python fetch-season-games.py [start_date] [end_date]
Date format: YYYY-MM-DD (defaults to current season)
"""

import json
import os
import sys
import requests
import time
from datetime import datetime, timedelta
from pathlib import Path

# NHL API endpoints
NHL_API_BASE = "https://api-web.nhle.com"

def fetch_from_api(url, max_retries=3):
    """Fetch data from NHL API with retry logic"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=12)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                print(f"Error fetching {url}: {e}")
                return None
            time.sleep(3)  # Wait before retry
    return None

def get_schedule_for_date(date):
    """Get NHL schedule for a specific date"""
    url = f"{NHL_API_BASE}/v1/schedule/{date}"
    return fetch_from_api(url)

def get_game_details(game_id):
    """Get detailed game information including player stats"""
    url = f"{NHL_API_BASE}/v1/gamecenter/{game_id}/boxscore"
    return fetch_from_api(url)

def extract_all_player_data(game_data, game_id, home_team, away_team, game_date):
    """Extract all player data from game"""
    players = []

    if not game_data:
        return players

    # Process away team players
    away_players = game_data.get("awayTeam", {}).get("players", {})
    for player_id, player_data in away_players.items():
        stats = player_data.get("stats", {})
        skater_stats = stats.get("skaterStats", {})
        goalie_stats = stats.get("goalieStats", {})

        position = player_data.get("position", {}).get("code", "N/A")
        name = f"{player_data.get('firstName', {}).get('default', '')} {player_data.get('lastName', {}).get('default', '')}"

        # Calculate total points
        goals = skater_stats.get("goals", 0) or goalie_stats.get("goals", 0)
        assists = skater_stats.get("assists", 0) or goalie_stats.get("assists", 0)
        points = goals + assists

        players.append({
            "playerId": player_id,
            "name": name.strip(),
            "team": away_team,
            "position": position,
            "goals": goals,
            "assists": assists,
            "points": points,
            "shots": skater_stats.get("shots", 0) or 0,
            "plusMinus": skater_stats.get("plusMinus", 0) or 0,
            "pim": skater_stats.get("pim", 0) or 0,
            "timeOnIce": skater_stats.get("timeOnIce", "00:00") or goalie_stats.get("timeOnIce", "00:00"),
            "isGoalie": position == "G",
            "saves": goalie_stats.get("saves", 0) or 0,
            "savePct": round(goalie_stats.get("savePercentage", 0.0) or 0.0, 3),
            "gameId": game_id,
            "gameDate": game_date
        })

    # Process home team players
    home_players = game_data.get("homeTeam", {}).get("players", {})
    for player_id, player_data in home_players.items():
        stats = player_data.get("stats", {})
        skater_stats = stats.get("skaterStats", {})
        goalie_stats = stats.get("goalieStats", {})

        position = player_data.get("position", {}).get("code", "N/A")
        name = f"{player_data.get('firstName', {}).get('default', '')} {player_data.get('lastName', {}).get('default', '')}"

        # Calculate total points
        goals = skater_stats.get("goals", 0) or goalie_stats.get("goals", 0)
        assists = skater_stats.get("assists", 0) or goalie_stats.get("assists", 0)
        points = goals + assists

        players.append({
            "playerId": player_id,
            "name": name.strip(),
            "team": home_team,
            "position": position,
            "goals": goals,
            "assists": assists,
            "points": points,
            "shots": skater_stats.get("shots", 0) or 0,
            "plusMinus": skater_stats.get("plusMinus", 0) or 0,
            "pim": skater_stats.get("pim", 0) or 0,
            "timeOnIce": skater_stats.get("timeOnIce", "00:00") or goalie_stats.get("timeOnIce", "00:00"),
            "isGoalie": position == "G",
            "saves": goalie_stats.get("saves", 0) or 0,
            "savePct": round(goalie_stats.get("savePercentage", 0.0) or 0.0, 3),
            "gameId": game_id,
            "gameDate": game_date
        })

    return players

def generate_season_data(start_date, end_date):
    """Generate comprehensive data for all games in a date range"""

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    all_games = []
    all_players = []
    total_days = (end - start).days + 1
    current_day = 0

    print(f"Fetching season data from {start_date} to {end_date}")
    print(f"Total days to process: {total_days}")
    print()

    current_date = start
    while current_date <= end:
        current_day += 1
        date_str = current_date.strftime("%Y-%m-%d")

        print(f"[{current_day:3d}/{total_days}] Processing {date_str}...")

        # Get schedule for the date
        schedule = get_schedule_for_date(date_str)
        if not schedule:
            current_date += timedelta(days=1)
            continue

        games = schedule.get("games", [])
        if not games:
            print(f"   No games scheduled")
            current_date += timedelta(days=1)
            continue

        print(f"   Found {len(games)} games")

        for i, game in enumerate(games, 1):
            game_id = game.get("id")
            home_team = game.get("homeTeam", {}).get("abbrev", "UNK")
            away_team = game.get("awayTeam", {}).get("abbrev", "UNK")
            game_state = game.get("gameState", "UNKNOWN")

            # Skip games that haven't been played yet
            if game_state in ["FUT", "PRE", "OFF"]:
                print(f"   Game {i}/{len(games)}: {away_team} @ {home_team} - Not played yet")
                continue

            print(f"   Game {i}/{len(games)}: {away_team} @ {home_team} ({game_state})")

            # Get detailed game data
            game_details = get_game_details(game_id)

            if game_details:
                # Extract all player data
                players = extract_all_player_data(game_details, game_id, home_team, away_team, date_str)
                all_players.extend(players)

                # Add game summary
                home_score = game_details.get("homeTeam", {}).get("score", 0)
                away_score = game_details.get("awayTeam", {}).get("score", 0)

                all_games.append({
                    "gameId": game_id,
                    "gameDate": date_str,
                    "homeTeam": home_team,
                    "awayTeam": away_team,
                    "homeScore": home_score,
                    "awayScore": away_score,
                    "gameState": game_state,
                    "startTime": game.get("startTimeUTC", ""),
                    "players_count": len(players)
                })

                # Show top performers from this game
                scorers = sorted([p for p in players if p["points"] > 0],
                               key=lambda x: x["points"], reverse=True)[:3]
                if scorers:
                    scorer_names = [f"{p['name']} ({p['points']}pts)" for p in scorers]
                    print(f"      Top scorers: {', '.join(scorer_names)}")

            else:
                print(f"      Failed to get details for game {game_id}")
                all_games.append({
                    "gameId": game_id,
                    "gameDate": date_str,
                    "homeTeam": home_team,
                    "awayTeam": away_team,
                    "homeScore": 0,
                    "awayScore": 0,
                    "gameState": "ERROR",
                    "startTime": game.get("startTimeUTC", ""),
                    "players_count": 0,
                    "error": True
                })

            # Rate limiting between games
            time.sleep(1)

        current_date += timedelta(days=1)

        # Rate limiting between days
        time.sleep(2)

    return {
        "season": "2025-26",
        "date_range": {
            "start": start_date,
            "end": end_date
        },
        "games": all_games,
        "players": all_players,
        "total_games": len([g for g in all_games if not g.get("error")]),
        "total_players": len(all_players),
        "generated_at": datetime.now().isoformat()
    }

def main():
    # Get dates from command line or use defaults
    if len(sys.argv) >= 2:
        start_date = sys.argv[1]
    else:
        start_date = "2025-10-01"  # Approximate start of 2025-26 season

    if len(sys.argv) >= 3:
        end_date = sys.argv[2]
    else:
        end_date = datetime.now().strftime("%Y-%m-%d")

    # Validate date formats
    try:
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        print("Error: Invalid date format. Use YYYY-MM-DD")
        sys.exit(1)

    print(f"Fetching ALL NHL games data for 2025-26 season...")
    data = generate_season_data(start_date, end_date)

    # Create output directory
    output_dir = Path("data/prepopulated/season")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"season-2025-26-{timestamp}.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Generated season data:")
    print(f"   📅 Period: {data['date_range']['start']} to {data['date_range']['end']}")
    print(f"   🏒 Games: {data['total_games']}")
    print(f"   👥 Players: {data['total_players']}")
    print(f"   📁 Saved to: {output_file}")

    # Print some statistics
    if data["games"]:
        # Top scorers in season
        season_scorers = sorted(data["players"],
                              key=lambda x: x["points"], reverse=True)[:10]

        # Games by team
        team_games = {}
        for game in data["games"]:
            if not game.get("error"):
                team_games[game["homeTeam"]] = team_games.get(game["homeTeam"], 0) + 1
                team_games[game["awayTeam"]] = team_games.get(game["awayTeam"], 0) + 1

        print(f"\n🌟 Season Top 10 Scorers:")
        for i, player in enumerate(season_scorers, 1):
            print(f"   {i:2d}. {player['name']} ({player['team']}) - {player['points']} pts")

        print(f"\n📊 Games Played by Team:")
        for team, count in sorted(team_games.items()):
            print(f"   {team}: {count} games")

if __name__ == "__main__":
    main()
EOF

    chmod +x scripts/data/fetch-season-games.py
    echo -e "${GREEN}✅ Created fetch-season-games.py${NC}"
}

# Create the season directory
mkdir -p data/prepopulated/season

# Create the season script
create_season_script

echo -e "${BLUE}🚀 Starting season data generation...${NC}"
echo

# Run the season data fetcher
python3 scripts/data/fetch-season-games.py "$SEASON_START" "$TODAY"

echo
echo -e "${GREEN}✅ Season data generation complete!${NC}"
echo
echo -e "${BLUE}📁 Data saved to: data/prepopulated/season/${NC}"
echo -e "${CYAN}💡 This dataset contains ALL games and players from the 2025-26 season so far.${NC}"
echo -e "${CYAN}    Perfect for comprehensive analysis, statistics, and insights.${NC}"