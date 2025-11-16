#!/usr/bin/env python3
"""
Comprehensive Finnish NHL Players Data Generator

Fetches ALL Finnish NHL players data from NHL API for specific game dates.
This version is optimized to find all Finnish players without timeouts.
Usage: python fetch-all-finnish.py [date]
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
            response = requests.get(url, timeout=8)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                print(f"Error fetching {url}: {e}")
                return None
            time.sleep(1)  # Wait before retry
    return None

def get_schedule_for_date(date):
    """Get NHL schedule for a specific date"""
    url = f"{NHL_API_BASE}/v1/schedule/{date}"
    return fetch_from_api(url)

def get_game_details(game_id):
    """Get detailed game information including player stats"""
    url = f"{NHL_API_BASE}/v1/gamecenter/{game_id}/boxscore"
    return fetch_from_api(url)

def get_player_info(player_id):
    """Get player information including nationality"""
    url = f"{NHL_API_BASE}/v1/player/{player_id}/landing"
    return fetch_from_api(url)

def is_finnish_player(player_info):
    """Check if player is Finnish based on nationality or birth place"""
    if not player_info:
        return False

    # Check birth country first (most reliable)
    birth_country = player_info.get("birthCountry", "")
    if isinstance(birth_country, str) and birth_country.upper() in ["FIN", "FINLAND"]:
        return True

    # Check birth city (backup)
    birth_city = player_info.get("birthCity", "")
    if isinstance(birth_city, str):
        finnish_cities = [
            "helsinki", "turku", "tampere", "oulu", "espoo", "vantaa",
            "pori", "rauma", "kouvola", "jyväskylä", "lahti", "kuopio",
            "joensuu", "rovaniemi", "nokia", "nousiainen", "espoo", "forssa",
            "turku", "helsinki", "rauma", "vihti", "piikkio", "kiiminki",
            "siilinjärvi", "haapavesi", "noormarkku", "kangasala", "vaasa",
            "kokkola", "seinäjoki", "lappeenranta"
        ]
        if birth_city.lower() in finnish_cities:
            return True

    return False

def calculate_age(birth_date, game_date):
    """Calculate player age"""
    if not birth_date:
        return 0
    birth = datetime.strptime(birth_date, "%Y-%m-%d")
    game = datetime.strptime(game_date, "%Y-%m-%d")
    age = game.year - birth.year - ((game.month, game.day) < (birth.month, birth.day))
    return age

def process_player(player_stats, game_details, team_info, opponent_info, game_date):
    """Process a single player from game details"""
    player_id = player_stats.get("playerId")
    if not player_id:
        return None

    # Get detailed player info
    player_info = get_player_info(player_id)
    if not player_info or not is_finnish_player(player_info):
        return None

    # Extract player details
    first_name = player_info.get("firstName", {}).get("default", "")
    last_name = player_info.get("lastName", {}).get("default", "")
    full_name = f"{first_name} {last_name}"
    position = player_stats.get("position", "N/A")

    # Get game result for player's team
    home_score = game_details.get("homeTeam", {}).get("score", 0)
    away_score = game_details.get("awayTeam", {}).get("score", 0)
    home_team_abbrev = game_details.get("homeTeam", {}).get("abbrev", "")
    away_team_abbrev = game_details.get("awayTeam", {}).get("abbrev", "")

    # Venue info
    def extract_venue(info):
        venue = info.get("venue", {})
        venue_name = ""
        venue_city = ""

        if isinstance(venue, dict):
            venue_name = venue.get("default") or venue.get("name") or venue.get("shortName") or ""
        else:
            venue_name = str(venue) if venue else ""

        venue_location = info.get("venueLocation") or venue.get("location") if isinstance(venue, dict) else None
        if isinstance(venue_location, dict):
            venue_city = venue_location.get("default") or venue_location.get("city") or venue_location.get("name") or ""
        elif isinstance(venue_location, str):
            venue_city = venue_location

        # Additional fallbacks from team info (home team city)
        if not venue_city:
            home_city = info.get("homeTeam", {}).get("city", {})
            if isinstance(home_city, dict):
                venue_city = home_city.get("default") or home_city.get("name") or ""
            elif home_city:
                venue_city = home_city

        return venue_name, venue_city

    venue_name, venue_city = extract_venue(game_details)

    if team_info["abbrev"] == home_team_abbrev:
        game_result = "W" if home_score > away_score else "L" if home_score < away_score else "OT"
        game_score = f"{home_score}-{away_score}"
    else:
        game_result = "W" if away_score > home_score else "L" if away_score < home_score else "OT"
        game_score = f"{away_score}-{home_score}"

    # Calculate age
    birth_date = player_info.get("birthDate", "")
    age = calculate_age(birth_date, game_date)

    # Get birthplace - handle different API response formats
    birth_city = player_info.get("birthCity", "")
    birth_country = player_info.get("birthCountry", "")

    # Handle nested dict format
    if isinstance(birth_city, dict):
        birth_city = birth_city.get("default", "")
    if isinstance(birth_country, dict):
        birth_country = birth_country.get("default", birth_country)

    birthplace = f"{birth_city}, {birth_country}" if birth_city and birth_country else birth_city or birth_country or "Unknown"

    # Goalie-specific helpers
    def compute_goalie_numbers(stats):
        """Return enriched goalie stat dict with fallbacks."""
        saves = stats.get("saves")
        goals_against = stats.get("goalsAgainst")
        shots_against = stats.get("shotsAgainst")
        toi = stats.get("toi")

        # Fallbacks if API omits derived values
        if saves is None and shots_against is not None and goals_against is not None:
            saves = max(shots_against - goals_against, 0)
        if shots_against is None and saves is not None and goals_against is not None:
            shots_against = max(saves + goals_against, 0)
        save_pct = stats.get("savePercentage")
        if (save_pct is None or save_pct == 0) and shots_against:
            try:
                save_pct = round(saves / shots_against, 3)
            except Exception:
                save_pct = None

        return {
            "saves": saves if saves is not None else 0,
            "shots_against": shots_against if shots_against is not None else 0,
            "save_percentage": save_pct if save_pct is not None else 0.0,
            "goals_against": goals_against if goals_against is not None else 0,
            "even_strength_saves": stats.get("evenStrengthSaves", 0),
            "even_strength_shots_against": stats.get("evenStrengthShotsAgainst", 0),
            "power_play_saves": stats.get("powerPlaySaves", 0),
            "power_play_shots_against": stats.get("powerPlayShotsAgainst", 0),
            "shorthanded_saves": stats.get("shorthandedSaves", 0),
            "shorthanded_shots_against": stats.get("shorthandedShotsAgainst", 0),
            "goalie_time_on_ice": toi,
        }

    # Extract player stats
    goalie_extra_raw = compute_goalie_numbers(player_stats) if position == "G" else {}
    # If goalie did not log ice time or shots, skip them entirely
    if position == "G":
        toi_raw = goalie_extra_raw.get("goalie_time_on_ice") or player_stats.get("toi")
        shots_against_raw = goalie_extra_raw.get("shots_against", 0)
        if (not toi_raw or toi_raw in ("00:00", "0:00")) and shots_against_raw == 0:
            return None

    def build_headshot(player_info, player_id, team_abbrev):
        headshot = player_info.get("headshot") or player_info.get("headshotUrl")
        if headshot:
            return headshot
        return f"https://assets.nhle.com/mugs/nhl/latest/{team_abbrev}/{player_id}.png"

    goalie_extra = {k: v for k, v in goalie_extra_raw.items() if k != "goalie_time_on_ice"}

    stats = {
        "goals": player_stats.get("goals", 0),
        "assists": player_stats.get("assists", 0),
        "points": player_stats.get("goals", 0) + player_stats.get("assists", 0),
        "penalty_minutes": player_stats.get("pim", 0),
        "shots": player_stats.get("shots", 0),
        "plus_minus": player_stats.get("plusMinus", 0),
        "time_on_ice": player_stats.get("toi", "00:00"),
        "faceoffs_taken": player_stats.get("faceoffsTaken", 0),
        "faceoff_wins": player_stats.get("faceoffsWon", 0),
        "takeaways": player_stats.get("takeaways", 0),
        "giveaways": player_stats.get("giveaways", 0),
        "blocked_shots": player_stats.get("blockedShots", 0),
        "hits": player_stats.get("hits", 0),
        "power_play_goals": player_stats.get("powerPlayGoals", 0),
        "short_handed_goals": player_stats.get("shortHandedGoals", 0),
        "even_strength_goals": player_stats.get("evenStrengthGoals", 0),
        "power_play_assists": player_stats.get("powerPlayAssists", 0),
        "short_handed_assists": player_stats.get("shortHandedAssists", 0),
        "shifts": player_stats.get("shifts", 0),
        "average_ice_time": player_stats.get("averageToi", "00:00"),
        **goalie_extra,
    }

    return {
        "playerId": player_id,
        "name": full_name,
        "position": player_stats.get("position", "N/A"),
        "team": team_info["abbrev"],
        "team_full": team_info.get("name", {}).get("default", "") if isinstance(team_info.get("name"), dict) else team_info.get("name", team_info["abbrev"]),
        "age": age,
        "birth_date": birth_date,
        "birthplace": birthplace,
        "jersey_number": player_stats.get("sweaterNumber", 0),
        "status": "Active",
        "opponent": opponent_info["abbrev"],
        "opponent_full": opponent_info.get("name", {}).get("default", "") if isinstance(opponent_info.get("name"), dict) else opponent_info.get("name", opponent_info["abbrev"]),
        "game_score": game_score,
        "game_result": game_result,
        "game_venue": venue_name or "Unknown venue",
        "game_city": venue_city or "",
        "game_id": game_details.get("id", 0),
        "game_date": game_date,
        "game_status": "OFF",
        "created_at": datetime.now().isoformat(),
        "headshot_url": build_headshot(player_info, player_id, team_info["abbrev"]),
        **stats
    }

def fetch_finnish_players_for_date(game_date):
    """Fetch Finnish players who played on a specific date"""
    print(f"Fetching games for {game_date}...")

    # Get schedule for the date
    schedule = get_schedule_for_date(game_date)
    if not schedule or not schedule.get("gameWeek"):
        print(f"No games found for {game_date}")
        return []

    # Find games for the requested date
    games_for_date = None
    for week in schedule["gameWeek"]:
        if week.get("date") == game_date:
            games_for_date = week.get("games", [])
            break

    if not games_for_date:
        print(f"No games found for {game_date}")
        return []

    print(f"Found {len(games_for_date)} games")

    all_finnish_players = []

    # Process each game with better error handling
    for i, game in enumerate(games_for_date, 1):
        game_id = game.get("id")
        if not game_id:
            continue

        away_team = game.get("awayTeam", {}).get("abbrev", "UNK")
        home_team = game.get("homeTeam", {}).get("abbrev", "UNK")

        print(f"Processing game {i}/{len(games_for_date)}: {away_team} @ {home_team}")

        # Get detailed game information
        game_details = get_game_details(game_id)
        if not game_details:
            print(f"Failed to get details for game {game_id}")
            continue

        # Get all players from both teams using playerByGameStats
        player_stats = game_details.get("playerByGameStats", {})
        away_team_stats = player_stats.get("awayTeam", {})
        home_team_stats = player_stats.get("homeTeam", {})

        # Get team info
        away_team = game_details.get("awayTeam", {})
        home_team = game_details.get("homeTeam", {})

        # Process away team players
        away_players = []
        if away_team_stats.get("forwards"):
            away_players.extend(away_team_stats["forwards"])
        if away_team_stats.get("defense"):
            away_players.extend(away_team_stats["defense"])
        if away_team_stats.get("goalies"):
            away_players.extend(away_team_stats["goalies"])

        # Process home team players
        home_players = []
        if home_team_stats.get("forwards"):
            home_players.extend(home_team_stats["forwards"])
        if home_team_stats.get("defense"):
            home_players.extend(home_team_stats["defense"])
        if home_team_stats.get("goalies"):
            home_players.extend(home_team_stats["goalies"])

        # Check Finnish players in away team
        print(f"   Checking {len(away_players)} away team players...")
        away_finnish = 0
        for player in away_players:
            processed = process_player(player, game_details, away_team, home_team, game_date)
            if processed:
                all_finnish_players.append(processed)
                away_finnish += 1

        # Check Finnish players in home team
        print(f"   Checking {len(home_players)} home team players...")
        home_finnish = 0
        for player in home_players:
            processed = process_player(player, game_details, home_team, away_team, game_date)
            if processed:
                all_finnish_players.append(processed)
                home_finnish += 1

        print(f"   Found {away_finnish + home_finnish} Finnish players in this game")

        # Small delay between games to avoid rate limiting
        time.sleep(0.2)

    return all_finnish_players

def generate_game_data(game_date):
    """Generate game data for Finnish players on a specific date from NHL API"""
    players_data = fetch_finnish_players_for_date(game_date)

    return {
        "date": game_date,
        "total_players": len(players_data),
        "players": players_data,
        "generated_at": datetime.now().isoformat(),
        "source": "NHL API - Comprehensive"
    }

def main():
    """Main function"""
    # Check if requests is available
    try:
        import requests
    except ImportError:
        print("Error: requests library is required. Install it with: pip install requests")
        sys.exit(1)

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

    # Generate data
    print(f"Fetching ALL Finnish players data from NHL API for {game_date}...")
    data = generate_game_data(game_date)

    # Create output directory
    output_dir = Path("data/prepopulated/games")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save to file
    output_file = output_dir / f"{game_date}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Generated data for {data['total_players']} players")
    print(f"📁 Saved to: {output_file}")

    # Print summary
    if data["players"]:
        print("\n📊 Players found:")
        for player in data["players"]:
            print(f"   {player['name']} ({player['team']}) - {player['points']} pts")
    else:
        print("\n📊 No Finnish players found for this date")

if __name__ == "__main__":
    main()
