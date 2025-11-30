#!/usr/bin/env python3
"""
Check what NHL season data is available
"""

import requests
import json
from datetime import datetime, timedelta

NHL_API_BASE = "https://api-web.nhle.com"

def check_schedule(date_str):
    """Check schedule for a specific date"""
    url = f"{NHL_API_BASE}/v1/schedule/{date_str}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            games = data.get("games", [])
            return len(games), games
        else:
            return 0, f"Error: {response.status_code}"
    except Exception as e:
        return 0, f"Error: {e}"

def main():
    print("🏒 Checking NHL season availability...")
    print("=" * 50)

    # Check various dates to find games
    test_dates = [
        "2024-10-01",  # Typical season start
        "2024-10-15",
        "2024-11-01",
        "2024-11-21",
        "2024-12-01",
        "2025-01-01",
        "2025-04-01",  # End of regular season
        "2025-10-01",  # Next season start
        "2025-10-15",
        "2025-11-01",  # Today's date
    ]

    for date in test_dates:
        game_count, result = check_schedule(date)
        print(f"📅 {date}: {game_count} games")

        if game_count > 0 and isinstance(result, list):
            for game in result[:3]:  # Show first 3 games
                home = game.get("homeTeam", {}).get("abbrev", "UNK")
                away = game.get("awayTeam", {}).get("abbrev", "UNK")
                state = game.get("gameState", "UNK")
                print(f"   {away} @ {home} ({state})")
        elif isinstance(result, str):
            print(f"   {result}")
        print()

if __name__ == "__main__":
    main()