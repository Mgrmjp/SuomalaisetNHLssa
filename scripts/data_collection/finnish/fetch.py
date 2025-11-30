#!/usr/bin/env python3
"""
Enhanced Finnish NHL Players Data Fetcher with Empty Net Goal Tracking
"""

import json
import sys
import time
import re
import random
from datetime import datetime, timedelta
from pathlib import Path

# NHL API endpoints
NHL_API_BASE = "https://api-web.nhle.com"

# Geocoding cache for venue addresses (avoid repeated API calls)
_VENUE_ADDRESS_CACHE = {}

def geocode_venue_address(venue_name, city):
    """
    Get full address for a venue using OpenStreetMap Nominatim API
    Returns: {street, state, country, full_address} or None
    """
    global _VENUE_ADDRESS_CACHE

    cache_key = f"{venue_name}|{city}"
    if cache_key in _VENUE_ADDRESS_CACHE:
        return _VENUE_ADDRESS_CACHE[cache_key]

    try:
        import requests
        # Use Nominatim (OpenStreetMap) - free geocoding service
        headers = {
            'User-Agent': 'FinnishNHLPlayers/1.0'
        }
        query = f"{venue_name}, {city}, USA"
        url = f"https://nominatim.openstreetmap.org/search?format=json&addressdetails=1&q={requests.utils.quote(query)}&limit=1"

        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        results = response.json()

        if results:
            result = results[0]
            address = result.get('address', {})

            # Extract address components
            street = address.get('road', '')
            house_number = address.get('house_number', '')
            city_name = address.get('city', address.get('town', address.get('village', '')))
            state = address.get('state', '')
            country = address.get('country', '')
            postcode = address.get('postcode', '')

            # Build full address
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

# Global rate limiter
_last_request_time = 0
_min_request_interval = 1.0  # Minimum seconds between requests

def rate_limit():
    """Implement rate limiting between API requests"""
    global _last_request_time
    current_time = time.time()
    time_since_last = current_time - _last_request_time
    
    if time_since_last < _min_request_interval:
        sleep_time = _min_request_interval - time_since_last
        time.sleep(sleep_time)
    
    _last_request_time = time.time()

def fetch_from_api(url, max_retries=5):
    """
    Fetch data from NHL API with retry logic and exponential backoff
    
    Args:
        url: API endpoint URL
        max_retries: Maximum number of retry attempts
        
    Returns:
        JSON response data or None if all retries fail
    """
    rate_limit()  # Apply rate limiting before each request
    
    for attempt in range(max_retries):
        try:
            import requests
            response = requests.get(url, timeout=10)
            
            # Handle 429 Too Many Requests specifically
            if response.status_code == 429:
                if attempt == max_retries - 1:
                    print(f"Error fetching {url}: 429 Too Many Requests (max retries exceeded)")
                    return None
                
                # Exponential backoff with jitter for 429 errors
                base_delay = 2 ** attempt
                jitter = random.uniform(0.1, 0.5) * base_delay
                delay = base_delay + jitter
                print(f"Rate limited on {url}. Retrying in {delay:.2f} seconds... (attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
                continue
                
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Error fetching {url}: {e}")
                return None
            
            # Exponential backoff for other errors
            base_delay = 2 ** attempt
            jitter = random.uniform(0.1, 0.3) * base_delay
            delay = base_delay + jitter
            print(f"Error fetching {url}: {e}. Retrying in {delay:.2f} seconds... (attempt {attempt + 1}/{max_retries})")
            time.sleep(delay)
    
    return None

# Cache for teams data (fetched once per session)
_TEAMS_DATA_CACHE = None

def get_teams_data():
    """
    Fetch and cache teams data from NHL API.
    Returns dict mapping team abbrev to {venue_name, venue_city, team_name, location_name}
    """
    global _TEAMS_DATA_CACHE

    if _TEAMS_DATA_CACHE is not None:
        return _TEAMS_DATA_CACHE

    # Use a sample game to get teams data since there's no dedicated teams endpoint
    # We'll fetch from a recent game's boxscore
    sample_game_id = 2025020376  # Use a known game ID
    game_data = fetch_from_api(f"{NHL_API_BASE}/v1/gamecenter/{sample_game_id}/boxscore")

    teams_cache = {}

    if game_data:
        # Process home team
        home_team = game_data.get("homeTeam", {})
        home_abbrev = home_team.get("abbrev", "")
        if home_abbrev:
            home_name = home_team.get("commonName", {}).get("default", "")
            home_place = home_team.get("placeName", {}).get("default", "")
            venue = home_team.get("venue", {})
            teams_cache[home_abbrev] = {
                "venue_name": venue.get("name", ""),
                "venue_city": venue.get("city", ""),
                "team_name": home_name,
                "location_name": home_place
            }

        # Process away team
        away_team = game_data.get("awayTeam", {})
        away_abbrev = away_team.get("abbrev", "")
        if away_abbrev:
            away_name = away_team.get("commonName", {}).get("default", "")
            away_place = away_team.get("placeName", {}).get("default", "")
            venue = away_team.get("venue", {})
            teams_cache[away_abbrev] = {
                "venue_name": venue.get("name", ""),
                "venue_city": venue.get("city", ""),
                "team_name": away_name,
                "location_name": away_place
            }

    _TEAMS_DATA_CACHE = teams_cache
    return teams_cache

# Backward compatibility alias
def get_teams_venue_data():
    """Legacy alias for get_teams_data()"""
    teams_data = get_teams_data()
    # Return only venue info for backward compatibility
    venue_data = {}
    for abbrev, data in teams_data.items():
        venue_data[abbrev] = {
            "venue_name": data["venue_name"],
            "venue_city": data["venue_city"]
        }
    return venue_data

def load_finnish_player_cache():
    """Load cached Finnish player information"""
    cache_file = Path(__file__).parent / "cache" / "finnish-players.json"
    if cache_file.exists():
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                str_cache = json.load(f)
                return {int(k): v for k, v in str_cache.items()}
        except Exception as e:
            print(f"Error loading cache: {e}")
    return {}

def get_play_by_play_data(game_id):
    """Get play-by-play data to detect empty net goals"""
    url = f"{NHL_API_BASE}/v1/gamecenter/{game_id}/play-by-play"
    return fetch_from_api(url)

def detect_empty_net_goals(play_by_play_data, game_id, finnish_cache, game_data=None):
    """
    Parse play-by-play data to find empty net goals

    NHL API indicates empty net goals via:
    1. zoneCode: 'N' (Neutral zone)
    2. highlightClipSharingUrl containing 'empty-net'

    Returns:
    - empty_net_goals_scored: dict of scoring players (for skaters)
    - empty_net_goals_allowed: dict of goalie IDs (for goalies)
    """
    empty_net_goals_scored = {}
    empty_net_goals_allowed = {}

    if not play_by_play_data or 'plays' not in play_by_play_data:
        return empty_net_goals_scored, empty_net_goals_allowed

    # Create reverse cache mapping: playerId -> position (for goalie detection)
    finnish_positions = {}
    for pid, info in finnish_cache.items():
        if info.get('position') == 'G' or info.get('position') == 'Goalie':
            finnish_positions[pid] = 'G'

    for play in play_by_play_data['plays']:
        # Look for goal events
        if play.get('typeDescKey') == 'goal':
            details = play.get('details', {})
            zone_code = details.get('zoneCode', '')
            highlight_url = details.get('highlightClipSharingUrl', '')

            # Detect empty net goals using multiple indicators
            is_empty_net = False

            # Method 1: zoneCode 'N' means Neutral zone (empty net)
            if zone_code == 'N':
                is_empty_net = True

            # Method 2: Highlight URL contains "empty-net"
            if 'empty-net' in (highlight_url or '').lower():
                is_empty_net = True

            # If it's an empty net goal
            if is_empty_net:
                # Track scoring player (for skater stats)
                player_id = details.get('scoringPlayerId')
                if player_id:
                    if player_id not in empty_net_goals_scored:
                        empty_net_goals_scored[player_id] = 0
                    empty_net_goals_scored[player_id] += 1

                # Track goalie who allowed it (for goalie stats)
                goalie_id = details.get('goalieInNetId')
                if goalie_id and goalie_id in finnish_positions:
                    # This is a Finnish goalie who allowed an empty net goal
                    if goalie_id not in empty_net_goals_allowed:
                        empty_net_goals_allowed[goalie_id] = 0
                    empty_net_goals_allowed[goalie_id] += 1
                elif not goalie_id and game_data:
                    # Empty net goal - no goalieInNetId means net was empty
                    # Determine which team had the empty net by checking eventOwnerTeamId
                    event_owner_team_id = details.get('eventOwnerTeamId')
                    home_team_id = game_data.get('homeTeam', {}).get('id')
                    away_team_id = game_data.get('awayTeam', {}).get('id')
                    
                    if event_owner_team_id and home_team_id and away_team_id:
                        # The team with eventOwnerTeamId scored the goal
                        # So the OTHER team had the empty net
                        defending_team_id = away_team_id if event_owner_team_id == home_team_id else home_team_id

                        # Get all goalies who played in the game
                        player_stats = game_data.get('playerByGameStats', {})
                        game_goalies = set()
                        
                        for team_side in ['awayTeam', 'homeTeam']:
                            team_data = player_stats.get(team_side, {})
                            for goalie in team_data.get('goalies', []):
                                game_goalies.add(goalie.get('playerId'))

                        # Find Finnish goalies from the defending team who played in the game
                        for team_side in ['awayTeam', 'homeTeam']:
                            team_data = player_stats.get(team_side, {})
                            goalie_team_id = game_data.get(team_side, {}).get('id')
                            
                            if goalie_team_id == defending_team_id:
                                # This is the defending team - check their goalies
                                for goalie in team_data.get('goalies', []):
                                    goalie_id = goalie.get('playerId')
                                    toi = goalie.get('toi', '00:00')
                                    
                                    # Only count goalies who actually played (TOI > 0)
                                    if goalie_id in finnish_positions and toi != '00:00' and toi != '0':
                                        if goalie_id not in empty_net_goals_allowed:
                                            empty_net_goals_allowed[goalie_id] = 0
                                        empty_net_goals_allowed[goalie_id] += 1

    # Always return, even if we didn't find any empty net goals
    return empty_net_goals_scored, empty_net_goals_allowed

def detect_shorthanded_goals(play_by_play_data, finnish_cache):
    """
    Detect shorthanded goals from play-by-play data
    
    NHL API indicates shorthanded goals via:
    - highlightClipSharingUrl containing 'shg' (shorthanded goal)
    
    Returns:
    - shorthanded_goals: dict of player IDs to goal counts (for skaters)
    """
    shorthanded_goals = {}
    
    if not play_by_play_data or 'plays' not in play_by_play_data:
        return shorthanded_goals
    
    for play in play_by_play_data['plays']:
        if play.get('typeDescKey') == 'goal':
            details = play.get('details', {})
            url = details.get('highlightClipSharingUrl', '')
            
            # Detect shorthanded goals from URL
            if 'shg' in (url or '').lower():
                player_id = details.get('scoringPlayerId')
                if player_id and player_id in finnish_cache:
                    shorthanded_goals[player_id] = shorthanded_goals.get(player_id, 0) + 1
    
    return shorthanded_goals

def get_schedule_for_date(date):
    """Get NHL schedule for a specific date"""
    url = f"{NHL_API_BASE}/v1/schedule/{date}"
    data = fetch_from_api(url)
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
    """Get detailed game information including player stats"""
    url = f"{NHL_API_BASE}/v1/gamecenter/{game_id}/boxscore"
    return fetch_from_api(url)

def get_player_recent_games(player_id, player_team, limit=10):
    """
    Fetch recent games for a player
    Returns list of recent game results
    
    Note: The NHL API has changed - /v1/player/{id}/gamelog endpoint no longer exists.
    We now use /v1/player/{id}/landing endpoint which provides last5Games data.
    """
    try:
        # NHL API endpoint for player landing page (contains recent games)
        url = f"{NHL_API_BASE}/v1/player/{player_id}/landing"
        data = fetch_from_api(url)

        if not data or 'last5Games' not in data:
            return []

        recent_games = []
        for game in data['last5Games'][:limit]:
            # Extract basic game info
            game_date = game.get('gameDate', '')
            opponent_abbrev = game.get('opponentAbbrev', '')
            game_id = game.get('gameId')
            
            # Try to get actual game scores by fetching game details
            team_score = 0
            opponent_score = 0
            result = 'OT'  # Default
            
            if game_id:
                game_details = get_game_details(game_id)
                if game_details:
                    home_team = game_details.get("homeTeam", {})
                    away_team = game_details.get("awayTeam", {})
                    
                    # Determine which team is the player's team
                    player_is_home = home_team.get("abbrev", "") == player_team
                    
                    if player_is_home:
                        team_score = home_team.get("score", 0)
                        opponent_score = away_team.get("score", 0)
                        opponent_full = f"{away_team.get('placeName', {}).get('default', '')} {away_team.get('commonName', {}).get('default', '')}".strip()
                    else:
                        team_score = away_team.get("score", 0)
                        opponent_score = home_team.get("score", 0)
                        opponent_full = f"{home_team.get('placeName', {}).get('default', '')} {home_team.get('commonName', {}).get('default', '')}".strip()
                    
                    # Determine actual result
                    if team_score > opponent_score:
                        result = 'W'
                    elif team_score < opponent_score:
                        result = 'L'
                    else:
                        result = 'OT'
                else:
                    # Fallback if game details fetch fails
                    opponent_full = opponent_abbrev
                    # Use plus/minus as a rough indicator
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

def extract_finnish_player_data(game_data, game_id, date_str, schedule_data, finnish_cache):
    """Extract Finnish player data with empty net goal tracking"""
    finnish_players = []

    if not game_data:
        return finnish_players, {}

    player_stats = game_data.get("playerByGameStats", {})
    if not player_stats:
        return finnish_players, {}

    # Get empty net goal data (both scored and allowed)
    play_by_play_data = get_play_by_play_data(game_id)
    empty_net_goals_scored, empty_net_goals_allowed = detect_empty_net_goals(
        play_by_play_data, game_id, finnish_cache, game_data
    )
    
    # Get shorthanded goal data
    shorthanded_goals = detect_shorthanded_goals(play_by_play_data, finnish_cache) if play_by_play_data else {}

    # Get game context
    home_team = game_data.get("homeTeam", {}).get("abbrev", "UNK")
    away_team = game_data.get("awayTeam", {}).get("abbrev", "UNK")
    home_score = game_data.get("homeTeam", {}).get("score", 0)
    away_score = game_data.get("awayTeam", {}).get("score", 0)

    # Get venue info from game data (already fetched)
    venue_info = {}
    home_team_data = game_data.get("homeTeam", {})
    if home_team_data and home_team_data.get("venue"):
        venue = home_team_data.get("venue", {})
        venue_info["venue"] = venue.get("name", "")
        venue_info["city"] = venue.get("city", "")
    elif schedule_data and "week_data" in schedule_data:
        # Fallback to schedule data - get venue and city from home team
        for game in schedule_data["week_data"].get("games", []):
            if game.get("id") == game_id:
                venue_info["venue"] = game.get("venue", {}).get("default", "")
                # City is in the home team's placeName
                home_team_in_schedule = game.get("homeTeam", {})
                venue_info["city"] = home_team_in_schedule.get("placeName", {}).get("default", "")
                break

    # Get full venue address via geocoding
    if venue_info.get("venue") and venue_info.get("city"):
        venue_address = geocode_venue_address(venue_info["venue"], venue_info["city"])
        if venue_address:
            venue_info["address"] = venue_address.get("full_address", "")
            venue_info["street"] = venue_address.get("street", "")
            venue_info["state"] = venue_address.get("state", "")
            venue_info["postcode"] = venue_address.get("postcode", "")

    # Get team names directly from game data
    team_names = {}
    home_team_name = home_team_data.get("commonName", {}).get("default", "")
    home_team_place = home_team_data.get("placeName", {}).get("default", "")
    away_team_data = game_data.get("awayTeam", {})
    away_team_name = away_team_data.get("commonName", {}).get("default", "")
    away_team_place = away_team_data.get("placeName", {}).get("default", "")

    # Compose full team names (e.g., "Boston Bruins")
    team_names[home_team] = f"{home_team_place} {home_team_name}" if home_team_place and home_team_name else home_team
    team_names[away_team] = f"{away_team_place} {away_team_name}" if away_team_place and away_team_name else away_team

    # Collect all player IDs
    all_players = []

    for team_side in ["awayTeam", "homeTeam"]:
        team_stats = player_stats.get(team_side, {})
        for player_category in ["forwards", "defense", "goalies"]:
            for player in team_stats.get(player_category, []):
                all_players.append((team_side, player))

    # Process only Finnish players using cache
    finnish_player_data = {}

    for team_side, player in all_players:
        player_id = player.get("playerId")

        if player_id in finnish_player_data:
            continue

        if player_id in finnish_cache:
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
        else:  # homeTeam
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

        # Count empty net goals for this player
        player_name = player_cache.get("name", "")
        position = player_cache.get("position", "")

        # For goalies, count empty net goals ALLOWED
        # For skaters, count empty net goals SCORED
        if position == "G" or position == "Goalie":
            empty_net_count = empty_net_goals_allowed.get(player_id, 0)
        else:
            # Try both player_id and player_name as keys (for backward compatibility)
            empty_net_count = empty_net_goals_scored.get(player_id, 0) or empty_net_goals_scored.get(player_name, 0)

        # Build record with empty net goal tracking
        record = {
            "playerId": player_id,
            "name": player_cache.get("name", ""),
            "position": player_cache.get("position", game_stats.get("position", "N/A")),
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
            "empty_net_goals": empty_net_count,  # 🆕 NEW FIELD
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

        # Get recent games for this player (last 10 games)
        # Add small delay to avoid rate limiting on player API calls
        time.sleep(0.5)  # 0.5 second delay between player requests
        record["recent_results"] = get_player_recent_games(player_id, player_team, limit=10)

        finnish_players.append(record)

    return finnish_players, {
        "home_team": home_team,
        "away_team": away_team,
        "home_score": home_score,
        "away_score": away_score
    }

def generate_finnish_players_data(game_date):
    """Generate data for Finnish players on a specific date"""

    finnish_cache = load_finnish_player_cache()
    print(f"Loaded {len(finnish_cache)} Finnish player records from cache")
    print()

    schedule = get_schedule_for_date(game_date)
    if not schedule:
        return {"date": game_date, "games": [], "players": [], "total_players": 0, "source": "NHL API - Enhanced"}

    games = schedule.get("games", [])
    all_finnish_players = []
    game_summaries = []

    print(f"Fetching Finnish players for {game_date}...")
    print(f"Found {len(games)} games")
    print()

    for i, game in enumerate(games, 1):
        game_id = game.get("id")
        home_team = game.get("homeTeam", {}).get("abbrev", "UNK")
        away_team = game.get("awayTeam", {}).get("abbrev", "UNK")

        print(f"[{i}/{len(games)}] {away_team} @ {home_team}")

        # Add delay between games to avoid rate limiting
        if i > 1:
            time.sleep(1.5)  # 1.5 second delay between games

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
                "startTime": game.get("startTimeUTC", ""),
                "finnish_players_count": len(finnish_players),
                "empty_net_goals": len([p for p in finnish_players if p.get('empty_net_goals', 0) > 0])
            })

            if finnish_players:
                print(f"      ✅ Found {len(finnish_players)} Finnish players")
                finnish_names = [f"{p['name']} ({p['points']}pts)" for p in finnish_players if p['points'] > 0]
                empty_net_scorers = [p['name'] for p in finnish_players if p.get('empty_net_goals', 0) > 0]
                
                if finnish_names:
                    print(f"         Scorers: {', '.join(finnish_names)}")
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

    # Save to file
    output_file = Path(__file__).parent.parent.parent / "data" / "prepopulated" / "games" / f"{date_str}.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print()
    print("=" * 80)
    print(f"✅ Generated data for {len(data['players'])} Finnish players")
    print(f"📁 Saved to: {output_file}")
    print("=" * 80)
