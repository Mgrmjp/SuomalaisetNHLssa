#!/usr/bin/env python3
"""
Deduplicate NHL game data files.

Each game should only exist in ONE file - the file matching the date
the game was actually played (based on startTimeUTC).

This script:
1. Reads all game data files
2. For each game, determines its correct date from startTimeUTC
3. Only keeps the game in the correct date file
4. Updates the games_manifest.json to remove dates with no games
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Paths
GAMES_DIR = Path("/home/miikka/dev/suomalaisetnhlssa/static/data/prepopulated/games")
MANIFEST_FILE = Path("/home/miikka/dev/suomalaisetnhlssa/static/data/games_manifest.json")

def get_local_date_from_utc(utc_timestamp):
    """
    Convert UTC timestamp to local date (YYYY-MM-DD).
    Games are organized by LOCAL date, not UTC date.
    """
    if not utc_timestamp:
        return None

    try:
        # Parse UTC timestamp
        dt = datetime.fromisoformat(utc_timestamp.replace('Z', '+00:00'))
        # Convert to Eastern timezone (where most NHL games are played)
        eastern = timezone(datetime.timedelta(hours=-5))
        local_dt = dt.astimezone(eastern)
        return local_dt.strftime("%Y-%m-%d")
    except:
        return None

def load_all_games():
    """
    Load all games from all date files and determine their correct file.
    Returns dict mapping date -> list of games that belong in that file.
    """
    print("Loading all games from data files...")
    games_by_correct_date = {}
    game_ids_seen = set()
    duplicate_count = 0

    for json_file in sorted(GAMES_DIR.glob("*.json")):
        date_str = json_file.stem
        print(f"  Processing {json_file.name}...")

        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            games = data.get("games", [])

            for game in games:
                game_id = game.get("gameId")
                if not game_id:
                    continue

                # Track duplicates
                if game_id in game_ids_seen:
                    duplicate_count += 1
                    continue

                game_ids_seen.add(game_id)

                # Determine correct date from startTimeUTC
                start_time = game.get("startTime", "")
                correct_date = get_local_date_from_utc(start_time)

                if not correct_date:
                    # Fallback: use the file's date
                    correct_date = date_str

                if correct_date not in games_by_correct_date:
                    games_by_correct_date[correct_date] = []

                games_by_correct_date[correct_date].append(game)

        except Exception as e:
            print(f"    ERROR: {e}")

    print(f"\nTotal unique games: {len(game_ids_seen)}")
    print(f"Duplicate games found: {duplicate_count}")
    print(f"Dates with games: {len(games_by_correct_date)}")

    return games_by_correct_date

def save_deduplicated_data(games_by_date):
    """Save deduplicated game data to files."""
    print("\nSaving deduplicated data...")

    saved_count = 0
    for date_str, games in sorted(games_by_date.items()):
        # Load original data to preserve non-game data (players, etc)
        json_file = GAMES_DIR / f"{date_str}.json"

        try:
            # Try to load existing file to preserve players data
            with open(json_file, 'r') as f:
                data = json.load(f)
        except:
            # Create new structure if file doesn't exist
            data = {
                "date": date_str,
                "games": [],
                "players": [],
                "total_players": 0,
                "generated_at": datetime.now().isoformat(),
                "source": "NHL API - Deduplicated"
            }

        # Update games list
        data["games"] = games
        data["date"] = date_str

        # Save back
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        saved_count += len(games)
        print(f"  {date_str}: {len(games)} games")

    print(f"\nTotal games saved: {saved_count}")

def update_manifest(games_by_date):
    """Update games_manifest.json with only dates that have games."""
    print("\nUpdating games_manifest.json...")

    try:
        with open(MANIFEST_FILE, 'r') as f:
            manifest = json.load(f)
    except:
        manifest = {"games": [], "lastUpdated": datetime.now().isoformat()}

    # Get sorted dates that have games
    dates_with_games = sorted(games_by_date.keys())

    # Update manifest
    manifest["games"] = dates_with_games
    manifest["lastUpdated"] = datetime.now().isoformat()

    # Save
    with open(MANIFEST_FILE, 'w') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"  Updated manifest with {len(dates_with_games)} dates")
    print(f"  Date range: {dates_with_games[0]} to {dates_with_games[-1]}")

def remove_empty_files(games_by_date):
    """Remove any JSON files that are not in the games_by_date dict."""
    print("\nRemoving empty/unused files...")

    all_files = set(GAMES_DIR.glob("*.json"))
    valid_files = {GAMES_DIR / f"{date}.json" for date in games_by_date.keys()}
    files_to_remove = all_files - valid_files

    for file in files_to_remove:
        try:
            file.unlink()
            print(f"  Removed: {file.name}")
        except Exception as e:
            print(f"  ERROR removing {file.name}: {e}")

    print(f"Removed {len(files_to_remove)} unused files")

def main():
    print("=" * 80)
    print("NHL Game Data Deduplication Tool")
    print("=" * 80)
    print()

    # Load all games and determine correct dates
    games_by_date = load_all_games()

    if not games_by_date:
        print("ERROR: No games found!")
        sys.exit(1)

    # Save deduplicated data
    save_deduplicated_data(games_by_date)

    # Update manifest
    update_manifest(games_by_date)

    # Remove empty files
    remove_empty_files(games_by_date)

    print("\n" + "=" * 80)
    print("✅ Deduplication complete!")
    print("=" * 80)

if __name__ == "__main__":
    main()
