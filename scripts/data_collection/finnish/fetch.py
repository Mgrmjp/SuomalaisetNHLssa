#!/usr/bin/env python3
"""
Enhanced Finnish NHL Players Data Fetcher with Empty Net Goal Tracking

Refactored to use shared config and utilities from parent package.
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path

# Import shared configuration and utilities
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    GAMES_DIR,
    FINNISH_CACHE_FILE,
    NOMINATIM_BASE,
    NOMINATIM_TIMEOUT,
)
from utils import (
    fetch_from_api,
    rate_limit,
    save_json,
    load_json,
    schedule_url,
    game_boxscore_url,
    play_by_play_url,
    player_landing_url,
    extract_team_name,
    get_player_name,
)
# Import Finnish text correction utilities
from finnish_text_utils import normalize_finnish_player_data

# =============================================================================
# Geocoding for venue addresses
# =============================================================================
_VENUE_ADDRESS_CACHE = {}


def geocode_venue_address(venue_name, city):
    """
    Get full address for a venue using OpenStreetMap Nominatim API.

    Args:
        venue_name: Name of the venue
        city: City where venue is located

    Returns:
        Dict with {street, state, country, full_address} or None
    """
    global _VENUE_ADDRESS_CACHE

    cache_key = f"{venue_name}|{city}"
    if cache_key in _VENUE_ADDRESS_CACHE:
        return _VENUE_ADDRESS_CACHE[cache_key]

    try:
        import requests
        headers = {'User-Agent': 'FinnishNHLPlayers/1.0'}
        query = f"{venue_name}, {city}, USA"
        url = f"{NOMINATIM_BASE}?format=json&addressdetails=1&q={requests.utils.quote(query)}&limit=1"

        response = requests.get(url, headers=headers, timeout=NOMINATIM_TIMEOUT)
        response.raise_for_status()
        results = response.json()

        if results:
            result = results[0]
            address = result.get('address', {})

            street = address.get('road', '')
            house_number = address.get('house_number', '')
            city_name = address.get('city', address.get('town', address.get('village', '')))
            state = address.get('state', '')
            country = address.get('country', '')
            postcode = address.get('postcode', '')

            full_parts = []
            if house_number and street:
                full_parts.append(f"{house_number} {street}")
            elif street:
                full_parts.append(street)

            if city_name:
                full_parts.append(city_name)
            if state:
                full_parts.append(state)
            if country:
                full_parts.append(country)

            full_address = ", ".join(full_parts)

            venue_address = {
                'street': street,
                'city': city_name,
                'state': state,
                'country': country,
                'postcode': postcode,
                'full_address': full_address
            }

            _VENUE_ADDRESS_CACHE[cache_key] = venue_address
            return venue_address
    except Exception as e:
        print(f"Warning: Geocoding failed for {venue_name}, {city}: {e}")

    return None


# =============================================================================
# Cache for teams data
# =============================================================================
_TEAMS_DATA_CACHE = None


def get_teams_data():
    """
    Fetch and cache teams data from NHL API.

    Returns:
        Dict mapping team abbrev to {venue_name, venue_city, team_name, location_name}
    """
    global _TEAMS_DATA_CACHE

    if _TEAMS_DATA_CACHE is not None:
        return _TEAMS_DATA_CACHE

    sample_game_id = 2025020376  # Use a known game ID
    game_data = fetch_from_api(game_boxscore_url(sample_game_id))

    teams_cache = {}

    if game_data:
        for team_key in ["homeTeam", "awayTeam"]:
            team = game_data.get(team_key, {})
            abbrev = team.get("abbrev", "")
            if abbrev:
                teams_cache[abbrev] = {
                    "venue_name": team.get("venue", {}).get("name", ""),
                    "venue_city": team.get("venue", {}).get("city", ""),
                    "team_name": team.get("commonName", {}).get("default", ""),
                    "location_name": team.get("placeName", {}).get("default", "")
                }

    _TEAMS_DATA_CACHE = teams_cache
    return teams_cache


def get_teams_venue_data():
    """Legacy alias for get_teams_data()"""
    teams_data = get_teams_data()
    venue_data = {}
    for abbrev, data in teams_data.items():
        venue_data[abbrev] = {
            "venue_name": data["venue_name"],
            "venue_city": data["venue_city"]
        }
    return venue_data


def load_finnish_player_cache():
    """Load cached Finnish player information with text corrections."""
    if FINNISH_CACHE_FILE.exists():
        data = load_json(FINNISH_CACHE_FILE)
        if data:
            # Apply corrections to all cached players
            corrected_cache = {}
            for player_id, player_data in data.items():
                corrected_cache[int(player_id)] = normalize_finnish_player_data(
                    player_data.copy()
                )
            return corrected_cache
    return {}


# =============================================================================
# Empty Net Goal Detection
# =============================================================================
def detect_empty_net_goals(play_by_play_data, game_id, finnish_cache, game_data=None):
    """
    Parse play-by-play data to find empty net goals.

    NHL API indicates empty net goals via:
    1. zoneCode: 'N' (Neutral zone)
    2. highlightClipSharingUrl containing 'empty-net'

    Args:
        play_by_play_data: Play-by-play data from API
        game_id: Game identifier
        finnish_cache: Finnish player cache
        game_data: Optional game data for goalie detection

    Returns:
        Tuple of (empty_net_goals_scored dict, empty_net_goals_allowed dict)
    """
    empty_net_goals_scored = {}
    empty_net_goals_allowed = {}

    if not play_by_play_data or 'plays' not in play_by_play_data:
        return empty_net_goals_scored, empty_net_goals_allowed

    # Create reverse cache mapping: playerId -> position (for goalie detection)
    finnish_positions = {}
    for pid, info in finnish_cache.items():
        if info.get('position') in ('G', 'Goalie'):
            finnish_positions[pid] = 'G'

    for play in play_by_play_data['plays']:
        if play.get('typeDescKey') == 'goal':
            details = play.get('details', {})
            zone_code = details.get('zoneCode', '')
            highlight_url = details.get('highlightClipSharingUrl', '')

            # Detect empty net goals using multiple indicators
            is_empty_net = (zone_code == 'N' or 'empty-net' in (highlight_url or '').lower())

            if is_empty_net:
                # Track scoring player
                player_id = details.get('scoringPlayerId')
                if player_id:
                    empty_net_goals_scored[player_id] = empty_net_goals_scored.get(player_id, 0) + 1

                # Track goalie who allowed it
                goalie_id = details.get('goalieInNetId')
                if goalie_id and goalie_id in finnish_positions:
                    empty_net_goals_allowed[goalie_id] = empty_net_goals_allowed.get(goalie_id, 0) + 1
                elif not goalie_id and game_data:
                    # Determine which team had the empty net
                    event_owner_team_id = details.get('eventOwnerTeamId')
                    home_team_id = game_data.get('homeTeam', {}).get('id')
                    away_team_id = game_data.get('awayTeam', {}).get('id')

                    if event_owner_team_id and home_team_id and away_team_id:
                        defending_team_id = away_team_id if event_owner_team_id == home_team_id else home_team_id

                        # Find Finnish goalies from defending team who played
                        player_stats = game_data.get('playerByGameStats', {})
                        for team_side in ['awayTeam', 'homeTeam']:
                            team_data = player_stats.get(team_side, {})
                            if game_data.get(team_side, {}).get('id') == defending_team_id:
                                for goalie in team_data.get('goalies', []):
                                    goalie_id = goalie.get('playerId')
                                    toi = goalie.get('toi', '00:00')

                                    if goalie_id in finnish_positions and toi not in ('00:00', '0'):
                                        empty_net_goals_allowed[goalie_id] = empty_net_goals_allowed.get(goalie_id, 0) + 1

    return empty_net_goals_scored, empty_net_goals_allowed


def detect_shorthanded_goals(play_by_play_data, finnish_cache):
    """
    Detect shorthanded goals from play-by-play data.

    Args:
        play_by_play_data: Play-by-play data from API
        finnish_cache: Finnish player cache

    Returns:
        Dict of player IDs to shorthanded goal counts
    """
    shorthanded_goals = {}

    if not play_by_play_data or 'plays' not in play_by_play_data:
        return shorthanded_goals

    for play in play_by_play_data['plays']:
        if play.get('typeDescKey') == 'goal':
            details = play.get('details', {})
            url = details.get('highlightClipSharingUrl', '')

            if 'shg' in (url or '').lower():
                player_id = details.get('scoringPlayerId')
                if player_id and player_id in finnish_cache:
                    shorthanded_goals[player_id] = shorthanded_goals.get(player_id, 0) + 1

    return shorthanded_goals


# =============================================================================
# NHL API Data Fetching
# =============================================================================
def get_schedule_for_date(date):
    """Get NHL schedule for a specific date."""
    data = fetch_from_api(schedule_url(date))
    if not data:
        return None

    game_week = data.get("gameWeek", [])
    if game_week and len(game_week) > 0:
        return {
            "games": game_week[0].get("games", []),
            "date": game_week[0].get("date", date),
            "week_data": game_week[0]
        }
    return {"games": [], "date": date}


def get_game_details(game_id):
    """Get detailed game information including player stats."""
    return fetch_from_api(game_boxscore_url(game_id))


def get_play_by_play_data(game_id):
    """Get play-by-play data to detect empty net goals."""
    return fetch_from_api(play_by_play_url(game_id))


def get_player_recent_games(player_id, player_team, limit=10):
    """
    Fetch recent games for a player.

    Args:
        player_id: Player ID
        player_team: Player's team abbreviation
        limit: Maximum number of recent games to fetch

    Returns:
        List of recent game results
    """
    try:
        data = fetch_from_api(player_landing_url(player_id))

        if not data or 'last5Games' not in data:
            return []

        recent_games = []
        for game in data['last5Games'][:limit]:
            game_date = game.get('gameDate', '')
            opponent_abbrev = game.get('opponentAbbrev', '')
            game_id = game.get('gameId')

            team_score = 0
            opponent_score = 0
            result = 'OT'

            if game_id:
                game_details = get_game_details(game_id)
                if game_details:
                    home_team = game_details.get("homeTeam", {})
                    away_team = game_details.get("awayTeam", {})

                    player_is_home = home_team.get("abbrev", "") == player_team

                    if player_is_home:
                        team_score = home_team.get("score", 0)
                        opponent_score = away_team.get("score", 0)
                        opponent_full = extract_team_name(away_team)
                    else:
                        team_score = away_team.get("score", 0)
                        opponent_score = home_team.get("score", 0)
                        opponent_full = extract_team_name(home_team)

                    if team_score > opponent_score:
                        result = 'W'
                    elif team_score < opponent_score:
                        result = 'L'
                else:
                    opponent_full = opponent_abbrev
                    plus_minus = game.get('plusMinus', 0)
                    if plus_minus > 0:
                        result = 'W'
                    elif plus_minus < 0:
                        result = 'L'
            else:
                opponent_full = opponent_abbrev

            recent_games.append({
                'date': game_date,
                'opponent': opponent_abbrev,
                'opponent_full': opponent_full,
                'team_score': team_score,
                'opponent_score': opponent_score,
                'result': result,
                'goals': game.get('goals', 0),
                'assists': game.get('assists', 0),
                'points': game.get('points', 0)
            })

        return recent_games
    except Exception as e:
        print(f"Warning: Failed to fetch recent games for player {player_id}: {e}")
        return []


# =============================================================================
# Finnish Player Data Extraction
# =============================================================================
def extract_finnish_player_data(game_data, game_id, date_str, schedule_data, finnish_cache):
    """
    Extract Finnish player data with empty net goal tracking.

    Args:
        game_data: Game boxscore data
        game_id: Game ID
        date_str: Game date (YYYY-MM-DD)
        schedule_data: Schedule data for venue info
        finnish_cache: Finnish player cache

    Returns:
        Tuple of (finnish_players list, game_info dict)
    """
    finnish_players = []

    if not game_data:
        return finnish_players, {}

    player_stats = game_data.get("playerByGameStats", {})
    if not player_stats:
        return finnish_players, {}

    # Get empty net and shorthanded goal data
    play_by_play_data = get_play_by_play_data(game_id)
    empty_net_goals_scored, empty_net_goals_allowed = detect_empty_net_goals(
        play_by_play_data, game_id, finnish_cache, game_data
    )
    shorthanded_goals = detect_shorthanded_goals(play_by_play_data, finnish_cache) if play_by_play_data else {}

    # Get game context
    home_team = game_data.get("homeTeam", {}).get("abbrev", "UNK")
    away_team = game_data.get("awayTeam", {}).get("abbrev", "UNK")
    home_score = game_data.get("homeTeam", {}).get("score", 0)
    away_score = game_data.get("awayTeam", {}).get("score", 0)

    # Get venue info from schedule data
    venue_info = {}

    if schedule_data and "week_data" in schedule_data:
        for game in schedule_data["week_data"].get("games", []):
            if game.get("id") == game_id:
                venue_info["venue"] = game.get("venue", {}).get("default", "")
                home_team_in_schedule = game.get("homeTeam", {})
                venue_info["city"] = home_team_in_schedule.get("placeName", {}).get("default", "")
                break

    # Fallback to game data for venue info
    if not venue_info.get("venue") and game_data:
        venue_info["venue"] = game_data.get("venue", {}).get("default", "")
        venue_info["city"] = game_data.get("venueLocation", {}).get("default", "")

    # Get full venue address via geocoding
    if venue_info.get("venue") and venue_info.get("city"):
        venue_address = geocode_venue_address(venue_info["venue"], venue_info["city"])
        if venue_address:
            venue_info["address"] = venue_address.get("full_address", "")
            venue_info["street"] = venue_address.get("street", "")
            venue_info["state"] = venue_address.get("state", "")
            venue_info["postcode"] = venue_address.get("postcode", "")

    # Get team names
    team_names = {}
    team_names[home_team] = extract_team_name(game_data.get("homeTeam", {}))
    team_names[away_team] = extract_team_name(game_data.get("awayTeam", {}))

    # Collect all player IDs
    all_players = []
    for team_side in ["awayTeam", "homeTeam"]:
        team_stats = player_stats.get(team_side, {})
        for player_category in ["forwards", "defense", "goalies"]:
            for player in team_stats.get(player_category, []):
                all_players.append((team_side, player))

    # Process only Finnish players
    finnish_player_data = {}
    for team_side, player in all_players:
        player_id = player.get("playerId")
        if player_id not in finnish_player_data and player_id in finnish_cache:
            finnish_player_data[player_id] = {
                "player_cache": finnish_cache[player_id],
                "game_stats": player,
                "team_side": team_side
            }

    # Build Finnish player records
    for player_id, data in finnish_player_data.items():
        player_cache = data["player_cache"]
        game_stats = data["game_stats"]
        team_side = data["team_side"]

        if team_side == "awayTeam":
            player_team = away_team
            opponent = home_team
            player_score = away_score
            opponent_score = home_score
            player_team_full = team_names.get(away_team, away_team)
            opponent_team_full = team_names.get(home_team, home_team)
        else:
            player_team = home_team
            opponent = away_team
            player_score = home_score
            opponent_score = away_score
            player_team_full = team_names.get(home_team, home_team)
            opponent_team_full = team_names.get(away_team, away_team)

        # Calculate age
        birth_date = player_cache.get("birthDate", "")
        age = None
        if birth_date:
            try:
                birth = datetime.strptime(birth_date, "%Y-%m-%d")
                age = (datetime.now() - birth).days // 365
            except:
                age = None

        # Count empty net goals
        position = player_cache.get("position", "")
        if position in ("G", "Goalie"):
            empty_net_count = empty_net_goals_allowed.get(player_id, 0)
        else:
            empty_net_count = empty_net_goals_scored.get(player_id, 0)

        # Build record
        record = {
            "playerId": player_id,
            "name": player_cache.get("name", ""),
            "position": position or game_stats.get("position", "N/A"),
            "team": player_team,
            "team_full": player_team_full,
            "age": age,
            "birth_date": birth_date,
            "birthplace": player_cache.get("birthplace", ""),
            "jersey_number": player_cache.get("sweaterNumber", 0),
            "status": "Active",
            "opponent": opponent,
            "opponent_full": opponent_team_full,
            "game_score": f"{player_score}-{opponent_score}",
            "game_result": "W" if player_score > opponent_score else "L" if player_score < opponent_score else "T",
            "game_venue": venue_info.get("venue", ""),
            "game_city": venue_info.get("city", ""),
            "game_address": venue_info.get("address", ""),
            "game_id": game_id,
            "game_date": date_str,
            "game_status": "OFF",
            "created_at": datetime.now().isoformat(),
            "headshot_url": player_cache.get("headshot", ""),
            # Game stats
            "goals": game_stats.get("goals", 0),
            "assists": game_stats.get("assists", 0),
            "points": game_stats.get("points", 0),
            "empty_net_goals": empty_net_count,
            "penalty_minutes": game_stats.get("pim", 0),
            "shots": game_stats.get("sog", 0),
            "plus_minus": game_stats.get("plusMinus", 0),
            "time_on_ice": game_stats.get("toi", "00:00"),
            "takeaways": game_stats.get("takeaways", 0),
            "giveaways": game_stats.get("giveaways", 0),
            "blocked_shots": game_stats.get("blockedShots", 0),
            "hits": game_stats.get("hits", 0),
            "power_play_goals": game_stats.get("powerPlayGoals", 0),
            "short_handed_goals": shorthanded_goals.get(player_id, 0),
            "even_strength_goals": 0,
            "power_play_assists": 0,
            "short_handed_assists": 0,
            "shifts": game_stats.get("shifts", 0),
            "average_ice_time": "00:00"
        }

        # Add goalie-specific stats
        if record["position"] == "G":
            record["saves"] = game_stats.get("saves", 0)
            record["shots_against"] = game_stats.get("shotsAgainst", 0)
            record["save_percentage"] = round(game_stats.get("savePctg", 0.0), 3) if game_stats.get("savePctg") else 0.0
            record["goals_against"] = game_stats.get("goalsAgainst", 0)

        # Get recent games (with delay to avoid rate limiting)
        time.sleep(0.5)
        record["recent_results"] = get_player_recent_games(player_id, player_team, limit=10)

        finnish_players.append(record)

    return finnish_players, {
        "home_team": home_team,
        "away_team": away_team,
        "home_score": home_score,
        "away_score": away_score
    }


def generate_finnish_players_data(game_date):
    """Generate data for Finnish players on a specific date."""
    finnish_cache = load_finnish_player_cache()
    print(f"Loaded {len(finnish_cache)} Finnish player records from cache\n")

    schedule = get_schedule_for_date(game_date)
    if not schedule:
        return {
            "date": game_date,
            "games": [],
            "players": [],
            "total_players": 0,
            "source": "NHL API - Enhanced"
        }

    games = schedule.get("games", [])
    all_finnish_players = []
    game_summaries = []

    print(f"Fetching Finnish players for {game_date}...")
    print(f"Found {len(games)} games\n")

    for i, game in enumerate(games, 1):
        game_id = game.get("id")
        home_team = game.get("homeTeam", {}).get("abbrev", "UNK")
        away_team = game.get("awayTeam", {}).get("abbrev", "UNK")

        print(f"[{i}/{len(games)}] {away_team} @ {home_team}")

        if i > 1:
            time.sleep(1.5)  # Rate limiting between games

        game_details = get_game_details(game_id)

        if game_details:
            finnish_players, game_info = extract_finnish_player_data(
                game_details, game_id, game_date, schedule, finnish_cache
            )
            all_finnish_players.extend(finnish_players)

            game_summaries.append({
                "gameId": game_id,
                "homeTeam": home_team,
                "awayTeam": away_team,
                "homeScore": game_info.get("home_score", 0),
                "awayScore": game_info.get("away_score", 0),
                "gameState": game.get("gameState", "UNKNOWN"),
                "gameType": game.get("gameType", 2),  # 1=preseason, 2=regular, 3=playoffs
                "startTime": game.get("startTimeUTC", ""),
                "finnish_players_count": len(finnish_players),
                "empty_net_goals": len([p for p in finnish_players if p.get('empty_net_goals', 0) > 0])
            })

            if finnish_players:
                print(f"      ✅ Found {len(finnish_players)} Finnish players")
                scorers = [f"{p['name']} ({p['points']}pts)" for p in finnish_players if p['points'] > 0]
                empty_net_scorers = [p['name'] for p in finnish_players if p.get('empty_net_goals', 0) > 0]

                if scorers:
                    print(f"         Scorers: {', '.join(scorers)}")
                if empty_net_scorers:
                    print(f"         🥅 Empty Net: {', '.join(empty_net_scorers)}")
            else:
                print(f"      No Finnish players")
        else:
            print(f"      ❌ Failed to fetch game details")

    # Sort players by points (descending) then by name
    all_finnish_players.sort(key=lambda x: (-x.get("points", 0), x.get("name", "")))

    return {
        "date": game_date,
        "games": game_summaries,
        "players": all_finnish_players,
        "total_players": len(all_finnish_players),
        "generated_at": datetime.now().isoformat(),
        "source": "NHL API - Enhanced with Empty Net Goal Tracking"
    }


# =============================================================================
# Main Entry Point
# =============================================================================
if __name__ == "__main__":
    if len(sys.argv) > 1:
        date_str = sys.argv[1]
    else:
        date_str = datetime.now().strftime("%Y-%m-%d")

    print("=" * 80)
    print(f"Fetching Finnish NHL players data for {date_str}...")
    print("=" * 80)
    print()

    data = generate_finnish_players_data(date_str)

    # Save using shared utilities
    output_file = GAMES_DIR / f"{date_str}.json"
    save_json(data, output_file)

    print()
    print("=" * 80)
    print(f"✅ Generated data for {len(data['players'])} Finnish players")
    print(f"📁 Saved to: {output_file}")
    print("=" * 80)
