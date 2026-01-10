#!/usr/bin/env python3
import json
import os
import time
import requests
from pathlib import Path
from datetime import datetime

NHL_API_BASE = "https://api-web.nhle.com"
GAMES_DIR = Path("static/data/prepopulated/games")

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

def repair_game_data(file_path):
    print(f"Repairing {file_path.name}...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"  ❌ Error reading file: {e}")
        return False

    updated = False
    games = data.get("games", [])
    
    for game in games:
        # Check if already has OT info
        if "isOT" in game and "period" in game:
            continue
            
        game_id = game.get("gameId")
        if not game_id:
            continue
            
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
            updated = True
            print(f"    ✅ Updated: period={period}, isOT={is_ot}, isSO={is_so}")
        else:
            print(f"    ❌ Failed to fetch details for game {game_id}")
            
        time.sleep(1) # Rate limiting

    if updated:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"  💾 Saved updated data to {file_path.name}")
            return True
        except Exception as e:
            print(f"  ❌ Error saving file: {e}")
            return False
    else:
        print(f"  ∅ No updates needed for {file_path.name}")
        return False

def main():
    if not GAMES_DIR.exists():
        print(f"❌ Games directory {GAMES_DIR} not found")
        return

    json_files = sorted(list(GAMES_DIR.glob("*.json")), reverse=True)
    print(f"🔍 Found {len(json_files)} JSON files to check")
    
    repaired_count = 0
    for file_path in json_files:
        if repair_game_data(file_path):
            repaired_count += 1
            
    print(f"\n✅ Repair complete! Repaired {repaired_count} files.")

if __name__ == "__main__":
    main()
