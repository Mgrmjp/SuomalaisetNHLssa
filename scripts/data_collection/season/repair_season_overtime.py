#!/usr/bin/env python3
"""
Repair Season Overtime Data
Enriches the full season JSON file with isOT, isSO, and period information.
Prefers using local daily game data to avoid API calls.
"""

import json
import sys
import time
import requests
from pathlib import Path
from datetime import datetime

# NHL API Base
NHL_API_BASE = "https://api-web.nhle.com"

# Project paths
BASE_DIR = Path(__file__).parent.parent.parent.parent
GAMES_DIR = BASE_DIR / "static/data/prepopulated/games"
SEASON_DIR = BASE_DIR / "static/data/prepopulated/season"

def fetch_from_api(url, max_retries=2):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Error fetching {url}: {e}")
                return None
            time.sleep(2)
    return None

def load_daily_game_map():
    """Build a map of gameId -> {isOT, isSO, period} from daily files"""
    game_map = {}
    if not GAMES_DIR.exists():
        print(f"⚠️ Games directory {GAMES_DIR} not found")
        return game_map

    json_files = list(GAMES_DIR.glob("*.json"))
    print(f"🔍 Scanning {len(json_files)} daily files for game info...")
    
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for game in data.get("games", []):
                    game_id = game.get("gameId")
                    if game_id and "isOT" in game and "period" in game:
                        game_map[game_id] = {
                            "isOT": game.get("isOT"),
                            "isSO": game.get("isSO"),
                            "period": game.get("period")
                        }
        except:
            continue
            
    print(f"✅ Found detail info for {len(game_map)} games in local files")
    return game_map

def repair_season_file(file_path):
    print(f"Repairing season file: {file_path.name}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

    game_map = load_daily_game_map()
    updated_count = 0
    api_count = 0
    games = data.get("games", [])
    
    for game in games:
        # Only process completed regular season games
        if game.get("gameState") not in ["OFF", "FINAL"] or game.get("gameType") != 2:
            continue
            
        # Check if already has OT info
        if "isOT" in game and "period" in game:
            continue
            
        game_id = game.get("gameId")
        if not game_id:
            continue
            
        # Try local map first
        info = game_map.get(game_id)
        if info:
            game.update(info)
            updated_count += 1
        else:
            # Fallback to API
            print(f"  🏒 Fetching details for game {game_id} ({game.get('awayTeam')} @ {game.get('homeTeam')})...")
            url = f"{NHL_API_BASE}/v1/gamecenter/{game_id}/boxscore"
            details = fetch_from_api(url)
            
            if details:
                pd = details.get("periodDescriptor", {})
                is_ot = pd.get("number", 0) > 3
                is_so = pd.get("periodType") == "SO"
                period = pd.get("number", 3)
                
                game["isOT"] = is_ot
                game["isSO"] = is_so
                game["period"] = period
                updated_count += 1
                api_count += 1
                print(f"    ✅ API Update: period={period}, isOT={is_ot}, isSO={is_so}")
                time.sleep(0.5) # Modest rate limiting
            else:
                print(f"    ❌ Failed to fetch details for game {game_id}")

    if updated_count > 0:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Saved {updated_count} updates ({api_count} from API) to {file_path.name}")
            return True
        except Exception as e:
            print(f"❌ Error saving file: {e}")
            return False
    else:
        print("\n∅ No updates needed for season file")
        return False

def main():
    # Find the latest season file
    season_files = sorted(list(SEASON_DIR.glob("season-*.json")), reverse=True)
    if not season_files:
        print(f"❌ No season JSON files found in {SEASON_DIR}")
        return

    latest_file = season_files[0]
    repair_season_file(latest_file)

if __name__ == "__main__":
    main()
