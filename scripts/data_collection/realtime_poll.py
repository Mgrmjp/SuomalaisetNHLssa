#!/usr/bin/env python3
"""
Realtime NHL Polling Script for Finnish Player Tracker.
Checks for live games and updates data files accordingly.
"""

import sys
import time
import argparse
import os
from datetime import datetime, timedelta, timezone
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
    from generate_manifest import generate_manifest
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

def check_for_live_games(date_str, near_hours=2):
    """
    Check if there are any live, critical, or games starting soon for the given date.
    
    Args:
        date_str: Date to check (YYYY-MM-DD)
        near_hours: Hours to look ahead for upcoming games
        
    Returns:
        bool: True if live or near-starting games are found, False otherwise.
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
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Found {len(live_games)} live/upcoming games.")
        for g in live_games:
            print(f"  - {g.get('awayTeam', {}).get('abbrev')} @ {g.get('homeTeam', {}).get('abbrev')} ({g.get('gameState')})")
        return True
    
    # Check for games starting within the next N hours
    now_utc = datetime.now(timezone.utc)
    near_threshold = now_utc + timedelta(hours=near_hours)
    
    near_games = []
    for g in games:
        start_time_str = g.get("startTimeUTC")
        if not start_time_str:
            continue
            
        try:
            # Format is typically 2024-10-12T23:00:00Z
            start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            if now_utc <= start_time <= near_threshold:
                near_games.append(g)
        except ValueError:
            continue

    if near_games:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Found {len(near_games)} games starting within {near_hours} hours.")
        for g in near_games:
            print(f"  - {g.get('awayTeam', {}).get('abbrev')} @ {g.get('homeTeam', {}).get('abbrev')} (Starts: {g.get('startTimeUTC')})")
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
        
        # Regenerate manifest to include the new/updated file
        generate_manifest()
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
        should_update = args.force or check_for_live_games(date_str)
        if should_update:
            run_update(date_str)
        else:
            print(f"No live or near games found for {date_str}. Skipping update.")
        
        # Set GitHub Action output if running in GA
        if "GITHUB_OUTPUT" in os.environ:
            with open(os.environ["GITHUB_OUTPUT"], "a") as f:
                f.write(f"updated={'true' if should_update else 'false'}\n")
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
