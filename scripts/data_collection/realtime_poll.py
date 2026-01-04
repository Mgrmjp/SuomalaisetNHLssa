#!/usr/bin/env python3
"""
Realtime NHL Polling Script for Finnish Player Tracker.
Checks for live games and updates data files accordingly.
"""

import sys
import time
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Add necessary directories to sys.path for imports
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))
sys.path.insert(0, str(scripts_dir / "finnish"))

# Import from existing modules
try:
    from finnish.fetch import generate_finnish_players_data
    from utils import fetch_from_api, schedule_url, save_json
    from config import GAMES_DIR
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

def check_for_live_games(date_str):
    """
    Check if there are any live or critical games for the given date.
    
    Returns:
        bool: True if live games are found, False otherwise.
    """
    schedule = fetch_from_api(schedule_url(date_str))
    if not schedule:
        return False
    
    game_week = schedule.get("gameWeek", [])
    if not game_week:
        return False
    
    # We look at the first day in the week data which should be the requested date
    day_data = game_week[0]
    games = day_data.get("games", [])
    
    live_states = ["LIVE", "CRIT", "PRE"] # PRE included to catch just before start
    
    live_games = [g for g in games if g.get("gameState") in live_states]
    
    if live_games:
        print(f"Found {len(live_games)} live/upcoming games.")
        for g in live_games:
            print(f"  - {g.get('awayTeam', {}).get('abbrev')} @ {g.get('homeTeam', {}).get('abbrev')} ({g.get('gameState')})")
        return True
    
    return False

def run_update(date_str):
    """
    Run the full data update for the specified date.
    """
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Updating data for {date_str}...")
    try:
        data = generate_finnish_players_data(date_str)
        output_file = GAMES_DIR / f"{date_str}.json"
        save_json(data, output_file)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Update complete. Saved to {output_file}")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error during update: {e}")

def main():
    parser = argparse.ArgumentParser(description="Realtime NHL Polling Script")
    parser.add_argument("--date", help="Date to check (YYYY-MM-DD), defaults to today")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--interval", type=int, default=60, help="Poll interval in seconds (default: 60)")
    parser.add_argument("--force", action="store_true", help="Force update even if no live games are found")
    
    args = parser.parse_args()
    
    # Determine date (NHL "today" might be yesterday in some timezones, but we use server date)
    if args.date:
        date_str = args.date
    else:
        # If it's early morning in Europe, we might still want yesterday's games
        now = datetime.now()
        if now.hour < 12:
            date_str = (now - timedelta(days=1)).strftime("%Y-%m-%d")
            print(f"Early morning detected, checking yesterday's games: {date_str}")
        else:
            date_str = now.strftime("%Y-%m-%d")
    
    if args.once:
        if args.force or check_for_live_games(date_str):
            run_update(date_str)
        else:
            print(f"No live games found for {date_str}. Skipping update.")
        return

    print(f"Starting polling loop for {date_str} every {args.interval} seconds...")
    print("Press Ctrl+C to stop.")
    
    try:
        while True:
            if args.force or check_for_live_games(date_str):
                run_update(date_str)
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] No live games. Waiting...")
            
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nPolling stopped by user.")

if __name__ == "__main__":
    main()
