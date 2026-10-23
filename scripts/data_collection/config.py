"""
Central configuration for NHL data collection scripts.

Provides consistent paths, API settings, and constants across all data fetchers.
"""

from pathlib import Path
from datetime import date


def current_nhl_season_id(today=None):
    """Return the NHL season ID for the current date."""
    today = today or date.today()
    season_start = today.year if today.month >= 9 else today.year - 1
    return season_start * 10000 + season_start + 1


def current_nhl_season_label(today=None):
    """Return the current NHL season as YYYY-YYYY."""
    season_id = current_nhl_season_id(today)
    return f"{season_id // 10000}-{season_id % 10000}"


def upcoming_nhl_draft_year(today=None):
    """Return the next NHL draft year, switching after the June draft window."""
    today = today or date.today()
    return today.year + (today.month >= 7)

# =============================================================================
# Project Paths
# =============================================================================
# Scripts are in scripts/data_collection/, so we go up 3 levels to reach project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "static" / "data"
PREPOPULATED_DIR = DATA_DIR / "prepopulated"

# Output directories for different data types
GAMES_DIR = PREPOPULATED_DIR / "games"          # Daily game data (Finnish players)
SEASON_DIR = PREPOPULATED_DIR / "season"        # Full season data (all players)
ALL_PLAYERS_DIR = PREPOPULATED_DIR / "all-players"  # All players by date

# =============================================================================
# NHL API Configuration
# =============================================================================
NHL_API_BASE = "https://api-web.nhle.com"
API_TIMEOUT = 15  # seconds (increased for slower responses)
API_MAX_RETRIES = 5
RATE_LIMIT_DELAY = 0.5  # seconds between requests (reduced, handled elsewhere)
RATE_LIMIT_JITTER = (0.1, 0.5)  # random jitter range for retries

# =============================================================================
# Data File Settings
# =============================================================================
JSON_INDENT = 2
JSON_ENSURE_ASCII = False

# =============================================================================
# Cache Settings
# =============================================================================
FINNISH_CACHE_DIR = PROJECT_ROOT / "scripts" / "data_collection" / "finnish" / "cache"
FINNISH_CACHE_FILE = FINNISH_CACHE_DIR / "finnish-players.json"

# =============================================================================
# External Services
# =============================================================================
# OpenStreetMap Nominatim for geocoding
NOMINATIM_BASE = "https://nominatim.openstreetmap.org/search"
NOMINATIM_TIMEOUT = 5  # seconds
