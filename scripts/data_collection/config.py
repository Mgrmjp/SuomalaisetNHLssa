"""
Central configuration for NHL data collection scripts.

Provides consistent paths, API settings, and constants across all data fetchers.
"""

from pathlib import Path

# =============================================================================
# Project Paths
# =============================================================================
# Scripts are in scripts/data_collection/, so we go up 3 levels to reach project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PREPOPULATED_DIR = DATA_DIR / "prepopulated"

# Output directories for different data types
GAMES_DIR = PREPOPULATED_DIR / "games"          # Daily game data (Finnish players)
SEASON_DIR = PREPOPULATED_DIR / "season"        # Full season data (all players)
ALL_PLAYERS_DIR = PREPOPULATED_DIR / "all-players"  # All players by date

# =============================================================================
# NHL API Configuration
# =============================================================================
NHL_API_BASE = "https://api-web.nhle.com"
API_TIMEOUT = 10  # seconds
API_MAX_RETRIES = 5
RATE_LIMIT_DELAY = 1.0  # seconds between requests
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
