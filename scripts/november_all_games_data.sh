#!/bin/bash

# Script to generate comprehensive data for ALL NHL games (not just Finnish players) for November 2025

TOTAL_DAYS=30
CURRENT_DAY=0
COMPLETED_DATES=()

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}🏒 Starting ALL NHL games data generation for November 2025...${NC}"
echo -e "${CYAN}Note: This will fetch data for ALL players in every game (comprehensive dataset)${NC}"
echo

# Function to draw progress bar
draw_progress_bar() {
    local progress=$1
    local total=$2
    local width=50
    local percentage=$((progress * 100 / total))
    local filled=$((progress * width / total))
    local empty=$((width - filled))

    printf "\r${GREEN}[${NC}"
    printf "%*s" $filled | tr ' ' '='
    printf "${RED}%*s${NC}" $empty | tr ' ' '-'
    printf "${GREEN}]${NC} %d%% (%d/%d)" $percentage $progress $total
}

# Function to process a single date with all games data
process_all_games_date() {
    local date_str=$1

    echo -e "\n${BLUE}🏒 Processing ALL games for $date_str...${NC}"

    # Check if the comprehensive all-games data script exists
    if [ ! -f "scripts/data/fetch-all-nhl-games.py" ]; then
        echo -e "${RED}❌ Need to create fetch-all-nhl-games.py script first${NC}"
        return 1
    fi

    # Run the all-games script and capture output
    local output=$(python3 scripts/data/fetch-all-nhl-games.py "$date_str" 2>&1)
    local exit_code=$?

    if [ $exit_code -eq 0 ]; then
        # Extract game count from output
        local games=$(echo "$output" | grep -o "Found [0-9]* games" | grep -o "[0-9]*" || echo "0")
        local players=$(echo "$output" | grep -o "Generated data for [0-9]* players" | grep -o "[0-9]*" || echo "0")

        echo -e "${GREEN}✅${NC} $date_str: $games games, $players total players"

        # Show some game details
        echo "$output" | grep "Games found:" -A 10 | tail -n +2 2>/dev/null || true

        COMPLETED_DATES+=("$date_str ($games games)")
    else
        echo -e "${RED}❌${NC} $date_str: Error occurred"
        echo "$output" | head -3
        COMPLETED_DATES+=("$date_str (ERROR)")
    fi

    # Rate limiting: wait between dates
    sleep 3
}

# Create the comprehensive all-games data fetcher
create_all_games_script() {
    echo -e "${CYAN}Creating comprehensive all-games data fetcher...${NC}"

    cat > scripts/data/fetch-all-nhl-games.py << 'EOF'
#!/usr/bin/env python3
"""
Comprehensive NHL Games Data Generator

Fetches ALL players data from NHL API for specific game dates.
This version gets complete game data for all players, not just Finnish ones.
Usage: python fetch-all-nhl-games.py [date]
Date format: YYYY-MM-DD (default: today)
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

def fetch_from_api(url, max_retries=2):
    """Fetch data from NHL API with retry logic"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                print(f"Error fetching {url}: {e}")
                return None
            time.sleep(2)  # Wait before retry
    return None

def get_schedule_for_date(date):
    """Get NHL schedule for a specific date"""
    url = f"{NHL_API_BASE}/v1/schedule/{date}"
    return fetch_from_api(url)

def get_game_details(game_id):
    """Get detailed game information including player stats"""
    url = f"{NHL_API_BASE}/v1/gamecenter/{game_id}/boxscore"
    return fetch_from_api(url)

def extract_all_player_data(game_data, game_id, home_team, away_team):
    """Extract all player data from game"""
    players = []

    if not game_data:
        return players

    # Process away team players
    away_players = game_data.get("awayTeam", {}).get("players", [])
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
            "savePct": goalie_stats.get("savePercentage", 0.0) or 0.0
        })

    # Process home team players
    home_players = game_data.get("homeTeam", {}).get("players", [])
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
            "savePct": goalie_stats.get("savePercentage", 0.0) or 0.0
        })

    return players

def generate_all_games_data(game_date):
    """Generate comprehensive data for all games on a specific date"""

    # Get schedule for the date
    schedule = get_schedule_for_date(game_date)
    if not schedule:
        return {"date": game_date, "games": [], "players": [], "total_players": 0}

    games = schedule.get("games", [])
    all_players = []
    game_summaries = []

    print(f"Fetching games for {game_date}...")
    print(f"Found {len(games)} games")

    for i, game in enumerate(games, 1):
        game_id = game.get("id")
        home_team = game.get("homeTeam", {}).get("abbrev", "UNK")
        away_team = game.get("awayTeam", {}).get("abbrev", "UNK")

        print(f"Processing game {i}/{len(games)}: {away_team} @ {home_team}")

        # Get detailed game data
        game_details = get_game_details(game_id)

        if game_details:
            # Extract all player data
            players = extract_all_player_data(game_details, game_id, home_team, away_team)
            all_players.extend(players)

            # Add game summary
            game_summaries.append({
                "gameId": game_id,
                "homeTeam": home_team,
                "awayTeam": away_team,
                "homeScore": game_details.get("homeTeam", {}).get("score", 0),
                "awayScore": game_details.get("awayTeam", {}).get("score", 0),
                "gameState": game.get("gameState", "UNKNOWN"),
                "startTime": game.get("startTimeUTC", "")
            })

            print(f"   Found {len(players)} players in this game")
        else:
            print(f"   Failed to get details for game {game_id}")
            game_summaries.append({
                "gameId": game_id,
                "homeTeam": home_team,
                "awayTeam": away_team,
                "homeScore": 0,
                "awayScore": 0,
                "gameState": "ERROR",
                "startTime": game.get("startTimeUTC", ""),
                "error": True
            })

        # Rate limiting between games
        time.sleep(1)

    return {
        "date": game_date,
        "games": game_summaries,
        "players": all_players,
        "total_players": len(all_players),
        "total_games": len(games),
        "generated_at": datetime.now().isoformat()
    }

def main():
    # Get date from command line or use today
    if len(sys.argv) > 1:
        game_date = sys.argv[1]
    else:
        game_date = datetime.now().strftime("%Y-%m-%d")

    # Validate date format
    try:
        datetime.strptime(game_date, "%Y-%m-%d")
    except ValueError:
        print("Error: Invalid date format. Use YYYY-MM-DD")
        sys.exit(1)

    print(f"Fetching ALL NHL players data from NHL API for {game_date}...")
    data = generate_all_games_data(game_date)

    # Create output directory
    output_dir = Path("data/prepopulated/all-games")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save to file
    output_file = output_dir / f"{game_date}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Generated data for {data['total_players']} players in {data['total_games']} games")
    print(f"📁 Saved to: {output_file}")

    # Print summary
    if data["games"]:
        print("\n📊 Games found:")
        for game in data["games"]:
            status = ""
            if game.get("error"):
                status = " (ERROR)"
            print(f"   {game['awayTeam']} @ {game['homeTeam']}: {game['awayScore']}-{game['homeScore']}{status}")

        # Show top performers
        scorers = sorted([p for p in data["players"] if p["points"] > 0],
                         key=lambda x: x["points"], reverse=True)[:5]
        if scorers:
            print("\n🌟 Top performers:")
            for player in scorers:
                print(f"   {player['name']} ({player['team']}) - {player['points']} pts")
    else:
        print("\n📊 No games found for this date")

if __name__ == "__main__":
    main()
EOF

    chmod +x scripts/data/fetch-all-nhl-games.py
    echo -e "${GREEN}✅ Created fetch-all-nhl-games.py${NC}"
}

# Create the all-games directory
mkdir -p data/prepopulated/all-games

# Create the comprehensive script if it doesn't exist
create_all_games_script

# Check which dates are already done
echo -e "${BLUE}🔍 Checking for existing all-games files...${NC}"
for day in {1..30}; do
    date_str=$(printf "2025-11-%02d" $day)
    if [ -f "data/prepopulated/all-games/$date_str.json" ]; then
        echo -e "${GREEN}✓${NC} $date_str already exists"
        COMPLETED_DATES+=("$date_str (EXISTS)")
        CURRENT_DAY=$((CURRENT_DAY + 1))
    fi
done

if [ $CURRENT_DAY -gt 0 ]; then
    echo -e "${GREEN}Found $CURRENT_DAY existing files, will process remaining dates.${NC}"
    echo
fi

# Loop through all dates in November 2025, skipping existing ones
for day in {1..30}; do
    date_str=$(printf "2025-11-%02d" $day)

    # Skip if file already exists
    if [ -f "data/prepopulated/all-games/$date_str.json" ]; then
        continue
    fi

    CURRENT_DAY=$((CURRENT_DAY + 1))

    # Update progress bar
    draw_progress_bar $((CURRENT_DAY - 1)) $TOTAL_DAYS

    # Process the date
    process_all_games_date "$date_str"
done

# Final progress bar
draw_progress_bar $TOTAL_DAYS $TOTAL_DAYS
echo
echo

echo -e "${GREEN}✅ All-games data generation complete for November 2025!${NC}"

# Show summary
echo
echo -e "${BLUE}📊 Summary:${NC}"
echo "Total files: $(ls -1 data/prepopulated/all-games/2025-11-*.json 2>/dev/null | wc -l)"
echo "Output directory: data/prepopulated/all-games/"

echo
echo -e "${BLUE}📋 Processed dates:${NC}"
for date_info in "${COMPLETED_DATES[@]}"; do
    echo "  $date_info"
done

echo
echo -e "${CYAN}💡 Note: This comprehensive dataset contains ALL players from every game.${NC}"
echo -e "${CYAN}      Use the Finnish-only files for the main app, this is for analysis.${NC}"
echo
echo -e "${GREEN}🎉 All done! Comprehensive NHL games data is ready for analysis.${NC}"