#!/usr/bin/env python3
"""
Test NHL API endpoints with same approach as working script
"""

import requests
import json
import time
from datetime import datetime

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

def test_api():
    print("🏒 Testing NHL API with various dates...")
    print("=" * 50)

    # Test dates that your working script successfully processed
    test_dates = [
        "2025-11-04",  # We know this had 13 games
        "2025-11-08",  # We know this had 13 games
        "2025-11-01",  # We know this had 13 games
        "2025-11-21",  # Today
    ]

    for date in test_dates:
        print(f"\n📅 Testing {date}:")
        schedule = get_schedule_for_date(date)

        if schedule:
            games = schedule.get("games", [])
            print(f"   ✅ Found {len(games)} games")

            if games:
                for i, game in enumerate(games[:3]):  # Show first 3
                    home = game.get("homeTeam", {}).get("abbrev", "UNK")
                    away = game.get("awayTeam", {}).get("abbrev", "UNK")
                    state = game.get("gameState", "UNK")
                    game_id = game.get("id", "UNK")
                    print(f"   {i+1}. {away} @ {home} ({state}) - ID: {game_id}")
            else:
                print("   ❌ No games found")
        else:
            print("   ❌ Failed to fetch schedule")

if __name__ == "__main__":
    test_api()