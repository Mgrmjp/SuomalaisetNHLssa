#!/usr/bin/env python3
"""
Complete NHL Season Data Generator

Fetches ALL games and player data for the current NHL season.
This version gets complete game data for all players across the entire season.
Usage: python fetch-season-games.py [start_date] [end_date]
Date format: YYYY-MM-DD (defaults to current season)
"""

import json
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# Import shared configuration and utilities
# Add parent directory to path for imports
_parent_dir = str(Path(__file__).parent.parent)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

from config import SEASON_DIR, NHL_API_BASE
from utils import fetch_from_api, rate_limit, save_json, schedule_url, game_boxscore_url

def get_schedule_for_date(date):
    """Get NHL schedule for a specific date"""
    url = schedule_url(date)
    data = fetch_from_api(url)
    if not data:
        return None

    # Extract games from the nested gameWeek structure
    game_week = data.get("gameWeek", [])
    if game_week and len(game_week) > 0:
        return {
            "games": game_week[0].get("games", []),
            "date": game_week[0].get("date", date)
        }
    return {"games": [], "date": date}

def get_game_details(game_id):
    """Get detailed game information including player stats"""
    url = game_boxscore_url(game_id)
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
                shots_against = player.get("shotsAgainst", 0)
                save_pct = player.get("savePctg", 0.0)
                goals_against = player.get("goalsAgainst", 0)

                players.append({
                    "playerId": player_id,
                    "name": name.strip(),
                    "team": away_team,
                    "position": position,
                    "goals": 0,  # Goalies don't score in this structure
                    "assists": 0,  # Goalies don't get assists in this structure
                    "points": 0,
                    "shots": 0,
                    "plusMinus": 0,
                    "pim": player.get("pim", 0),
                    "timeOnIce": player.get("toi", "00:00"),
                    "isGoalie": True,
                    "saves": saves,
                    "savePct": round(save_pct, 3) if save_pct else 0.0,
                    "shotsAgainst": shots_against,
                    "goalsAgainst": goals_against,
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
                    "hits": player.get("hits", 0),
                    "blockedShots": player.get("blockedShots", 0),
                    "takeaways": player.get("takeaways", 0),
                    "giveaways": player.get("giveaways", 0),
                    "powerPlayGoals": player.get("powerPlayGoals", 0),
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
                shots_against = player.get("shotsAgainst", 0)
                save_pct = player.get("savePctg", 0.0)
                goals_against = player.get("goalsAgainst", 0)

                players.append({
                    "playerId": player_id,
                    "name": name.strip(),
                    "team": home_team,
                    "position": position,
                    "goals": 0,  # Goalies don't score in this structure
                    "assists": 0,  # Goalies don't get assists in this structure
                    "points": 0,
                    "shots": 0,
                    "plusMinus": 0,
                    "pim": player.get("pim", 0),
                    "timeOnIce": player.get("toi", "00:00"),
                    "isGoalie": True,
                    "saves": saves,
                    "savePct": round(save_pct, 3) if save_pct else 0.0,
                    "shotsAgainst": shots_against,
                    "goalsAgainst": goals_against,
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
                    "hits": player.get("hits", 0),
                    "blockedShots": player.get("blockedShots", 0),
                    "takeaways": player.get("takeaways", 0),
                    "giveaways": player.get("giveaways", 0),
                    "powerPlayGoals": player.get("powerPlayGoals", 0),
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

            # Skip games that haven't been played yet (FUT = future, PRE = preseason)
            # OFF/FINAL = game is over and finished (this is what we want!)
            # CRIT = overtime/shootout - only accept if period > 3
            if game_state in ["FUT", "PRE"]:
                print(f"   Game {i}/{len(games)}: {away_team} @ {home_team} - Not played yet ({game_state})")
                continue

            # Skip CRIT games from schedule - need boxscore to check period
            if game_state == "CRIT":
                print(f"   Game {i}/{len(games)}: {away_team} @ {home_team} - CRIT state, checking details...")

            print(f"   Game {i}/{len(games)}: {away_team} @ {home_team} ({game_state})")

            # Get detailed game data
            game_details = get_game_details(game_id)

            if game_details:
                # Get game state from boxscore (more accurate than schedule)
                detail_state = game_details.get("gameState", game_state)

                # Normalize FINAL to OFF
                normalized_state = "OFF" if detail_state == "FINAL" else detail_state

                # Skip CRIT games with incomplete data (period <= 3)
                if normalized_state == "CRIT":
                    pd = game_details.get("periodDescriptor", {})
                    period = pd.get("number", 3)
                    if period <= 3:
                        print(f"      ⚠️ Skipping: CRIT with period={period} (incomplete scores)")
                        continue

                # Extract all player data
                players = extract_all_player_data(game_details, game_id, home_team, away_team, date_str)
                all_players.extend(players)

                # Add game summary
                home_score = game_details.get("homeTeam", {}).get("score", 0)
                away_score = game_details.get("awayTeam", {}).get("score", 0)

                # Extract overtime/shootout info
                pd = game_details.get("periodDescriptor", {})
                is_ot = pd.get("number", 0) > 3
                is_so = pd.get("periodType") == "SO"
                period = pd.get("number", 3)

                all_games.append({
                    "gameId": game_id,
                    "gameDate": date_str,
                    "homeTeam": home_team,
                    "awayTeam": away_team,
                    "homeScore": home_score,
                    "awayScore": away_score,
                    "gameState": normalized_state,
                    "gameType": game.get("gameType", 2),  # 1=preseason, 2=regular, 3=playoffs
                    "startTime": game.get("startTimeUTC", ""),
                    "isOT": is_ot,
                    "isSO": is_so,
                    "period": period,
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
                    "gameType": game.get("gameType", 2),
                    "startTime": game.get("startTimeUTC", ""),
                    "players_count": 0,
                    "error": True
                })

            # Rate limiting between games
            rate_limit(1.0)

        current_date += timedelta(days=1)

        # Rate limiting between days
        rate_limit(2.0)

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

    # Save using shared utilities
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = SEASON_DIR / f"season-2025-26-{timestamp}.json"
    save_json(data, output_file)

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
