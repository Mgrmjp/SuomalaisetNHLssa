#!/usr/bin/env python3
"""
Realtime NHL Polling Script for Finnish Player Tracker.
Checks for live games and missing final results, then updates data files.
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
    from utils import fetch_from_api, schedule_url, save_json, load_json
    from config import GAMES_DIR
    from generate_manifest import generate_manifest
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

def check_for_live_games(date_str, near_hours=2):
    """
    Check for live/near-starting games or final results missing from saved data.
    
    Args:
        date_str: Date to check (YYYY-MM-DD)
        near_hours: Hours to look ahead for upcoming games
        
    Returns:
        bool: True if this date needs a data update, False otherwise.
    """
    schedule = fetch_from_api(schedule_url(date_str))
    if not schedule:
        raise RuntimeError(f"Could not fetch NHL schedule for {date_str}")
    
    game_week = schedule.get("gameWeek", [])
    day_data = next((day for day in game_week if day.get("date") == date_str), None)
    if day_data is None or not isinstance(day_data.get("games"), list):
        raise RuntimeError(f"NHL schedule is missing the requested day: {date_str}")
    games = day_data["games"]

    # Polling may miss the last live snapshot, or its deployment may fail.
    # Reconcile completed games so the next poll can recover their final results.
    finished_games = [g for g in games if g.get("gameState") in ("OFF", "FINAL")]
    if finished_games:
        saved_data = load_json(GAMES_DIR / f"{date_str}.json") or {}
        saved_games = {g.get("gameId"): g for g in saved_data.get("games", [])}
        for game in finished_games:
            saved = saved_games.get(game.get("id"), {})
            if (
                saved.get("gameState") not in ("OFF", "FINAL")
                or saved.get("homeScore") != game.get("homeTeam", {}).get("score")
                or saved.get("awayScore") != game.get("awayTeam", {}).get("score")
            ):
                print(f"Final results need updating for {date_str}: {game.get('id')}")
                return True
    
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
        return True
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error during update: {e}")
        return False

def poll_dates(explicit_date=None, now=None):
    """Cover both sides of UTC midnight and recalculate dates on every poll."""
    if explicit_date:
        return [explicit_date]
    now = now or datetime.now(timezone.utc)
    return [(now - timedelta(days=1)).strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d")]


def poll_once(dates, force=False):
    updated = False
    for date_str in dates:
        if force or check_for_live_games(date_str):
            if not run_update(date_str):
                raise RuntimeError(f"Update failed for {date_str}")
            updated = True
        else:
            print(f"No live/near games or missing final results for {date_str}. Skipping update.")
    return updated


def main():
    parser = argparse.ArgumentParser(description="Realtime NHL Polling Script")
    parser.add_argument("--date", help="Date to check (YYYY-MM-DD), defaults to yesterday and today UTC")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--interval", type=int, default=60, help="Poll interval in seconds (default: 60)")
    parser.add_argument("--force", action="store_true", help="Force update even if no live games are found")
    
    args = parser.parse_args()
    
    if args.once:
        updated = False
        failed = False
        try:
            updated = poll_once(poll_dates(args.date), args.force)
        except Exception as error:
            print(f"Polling failed: {error}")
            failed = True
        
        # Set GitHub Action output if running in GA
        if "GITHUB_OUTPUT" in os.environ:
            with open(os.environ["GITHUB_OUTPUT"], "a") as f:
                f.write(f"updated={'true' if updated else 'false'}\n")
        if failed:
            sys.exit(1)
        return

    print(f"Starting polling every {args.interval} seconds...")
    print("Press Ctrl+C to stop.")
    
    try:
        while True:
            try:
                poll_once(poll_dates(args.date), args.force)
            except Exception as error:
                print(f"Polling failed, will retry: {error}")
            
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nPolling stopped by user.")

if __name__ == "__main__":
    main()
