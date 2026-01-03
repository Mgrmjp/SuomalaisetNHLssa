"""
NHL Data Collection Scripts

This package provides scripts for fetching NHL game and player data.
"""

from .config import (
    PROJECT_ROOT,
    DATA_DIR,
    PREPOPULATED_DIR,
    GAMES_DIR,
    SEASON_DIR,
    ALL_PLAYERS_DIR,
    NHL_API_BASE,
    API_TIMEOUT,
    API_MAX_RETRIES,
    RATE_LIMIT_DELAY,
)

from .utils import (
    fetch_from_api,
    rate_limit,
    ensure_dir,
    save_json,
    load_json,
    schedule_url,
    game_boxscore_url,
    play_by_play_url,
    player_landing_url,
    extract_team_name,
    get_player_name,
)

__all__ = [
    # Paths
    "PROJECT_ROOT",
    "DATA_DIR",
    "PREPOPULATED_DIR",
    "GAMES_DIR",
    "SEASON_DIR",
    "ALL_PLAYERS_DIR",
    # API config
    "NHL_API_BASE",
    "API_TIMEOUT",
    "API_MAX_RETRIES",
    "RATE_LIMIT_DELAY",
    # Utilities
    "fetch_from_api",
    "rate_limit",
    "ensure_dir",
    "save_json",
    "load_json",
    "schedule_url",
    "game_boxscore_url",
    "play_by_play_url",
    "player_landing_url",
    "extract_team_name",
    "get_player_name",
]
