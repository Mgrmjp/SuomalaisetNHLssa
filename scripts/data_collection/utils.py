"""
Shared utility functions for NHL data collection.

Provides common API handling, rate limiting, file I/O, and data processing.
"""

import json
import time
import random
from pathlib import Path

import requests

from config import (
    NHL_API_BASE,
    API_TIMEOUT,
    API_MAX_RETRIES,
    RATE_LIMIT_DELAY,
    RATE_LIMIT_JITTER,
    JSON_INDENT,
    JSON_ENSURE_ASCII,
)


# =============================================================================
# Rate Limiting
# =============================================================================
_last_request_time = 0


def rate_limit(delay=None):
    """
    Apply rate limiting between API requests.

    Args:
        delay: Minimum seconds between requests (defaults to RATE_LIMIT_DELAY)
    """
    global _last_request_time
    if delay is None:
        delay = RATE_LIMIT_DELAY

    current_time = time.time()
    time_since_last = current_time - _last_request_time

    if time_since_last < delay:
        sleep_time = delay - time_since_last
        time.sleep(sleep_time)

    _last_request_time = time.time()


# =============================================================================
# API Fetching
# =============================================================================
def fetch_from_api(url, max_retries=None, timeout=None):
    """
    Fetch data from NHL API with retry logic and exponential backoff.

    Args:
        url: API endpoint URL
        max_retries: Maximum number of retry attempts (defaults to API_MAX_RETRIES)
        timeout: Request timeout in seconds (defaults to API_TIMEOUT)

    Returns:
        JSON response data or None if all retries fail
    """
    if max_retries is None:
        max_retries = API_MAX_RETRIES
    if timeout is None:
        timeout = API_TIMEOUT

    rate_limit()  # Apply rate limiting before each request

    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=timeout)

            # Handle 429 Too Many Requests specifically
            if response.status_code == 429:
                if attempt == max_retries - 1:
                    print(f"Error fetching {url}: 429 Too Many Requests (max retries exceeded)")
                    return None

                # Exponential backoff with jitter for 429 errors
                base_delay = 2 ** attempt
                jitter_min, jitter_max = RATE_LIMIT_JITTER
                jitter = random.uniform(jitter_min, jitter_max) * base_delay
                delay = base_delay + jitter
                print(f"Rate limited on {url}. Retrying in {delay:.2f} seconds... (attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
                continue

            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            if attempt == max_retries - 1:
                print(f"Error fetching {url}: {e}")
                return None

            # Exponential backoff for other errors
            base_delay = 2 ** attempt
            jitter_min, jitter_max = RATE_LIMIT_JITTER
            jitter = random.uniform(jitter_min, jitter_max) * base_delay
            delay = base_delay + jitter
            print(f"Error fetching {url}: {e}. Retrying in {delay:.2f} seconds... (attempt {attempt + 1}/{max_retries})")
            time.sleep(delay)

    return None


# =============================================================================
# File I/O
# =============================================================================
def ensure_dir(path):
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path (Path object or string)
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_json(data, file_path, indent=None, ensure_ascii=None):
    """
    Save data to JSON file with consistent formatting.

    Args:
        data: Data to serialize
        file_path: Output file path
        indent: JSON indentation (defaults to config.JSON_INDENT)
        ensure_ascii: Whether to escape non-ASCII (defaults to config.JSON_ENSURE_ASCII)
    """
    if indent is None:
        indent = JSON_INDENT
    if ensure_ascii is None:
        ensure_ascii = JSON_ENSURE_ASCII

    file_path = Path(file_path)
    ensure_dir(file_path.parent)

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)

    return file_path


def load_json(file_path):
    """
    Load data from JSON file.

    Args:
        file_path: Path to JSON file

    Returns:
        Parsed JSON data or None if file doesn't exist/is invalid
    """
    file_path = Path(file_path)
    if not file_path.exists():
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading {file_path}: {e}")
        return None


# =============================================================================
# NHL API URL Builders
# =============================================================================
def schedule_url(date):
    """Get schedule URL for a specific date."""
    return f"{NHL_API_BASE}/v1/schedule/{date}"


def game_boxscore_url(game_id):
    """Get boxscore URL for a specific game."""
    return f"{NHL_API_BASE}/v1/gamecenter/{game_id}/boxscore"


def play_by_play_url(game_id):
    """Get play-by-play URL for a specific game."""
    return f"{NHL_API_BASE}/v1/gamecenter/{game_id}/play-by-play"


def player_landing_url(player_id):
    """Get player landing page URL."""
    return f"{NHL_API_BASE}/v1/player/{player_id}/landing"


# =============================================================================
# Data Processing Helpers
# =============================================================================
def extract_team_name(team_data):
    """
    Extract full team name from API response.

    Args:
        team_data: Team data from NHL API

    Returns:
        Full team name (e.g., "Boston Bruins")
    """
    place_name = team_data.get("placeName", {}).get("default", "")
    common_name = team_data.get("commonName", {}).get("default", "")
    return f"{place_name} {common_name}".strip() if place_name and common_name else common_name or place_name


def get_player_name(player_data):
    """
    Extract player name from API response.

    Args:
        player_data: Player data from NHL API

    Returns:
        Player name (stripped)
    """
    name_obj = player_data.get("name", {})
    if isinstance(name_obj, dict):
        return name_obj.get("default", "").strip()
    return str(name_obj).strip()
