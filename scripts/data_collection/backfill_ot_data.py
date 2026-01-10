#!/usr/bin/env python3
"""
Backfill missing OT/SO/period data for existing games.

This script reads all game files, fetches boxscore data for games
missing period/OT information, and updates the files with complete data.
"""

import json
import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import GAMES_DIR
from utils import fetch_from_api, game_boxscore_url, save_json, load_json

# =============================================================================
# Backfill Functions
# =============================================================================
def fetch_game_period_info(game_id):
    """Fetch period information for a game from NHL API."""
    try:
        game_data = fetch_from_api(game_boxscore_url(game_id))
        if not game_data:
            return None

        pd = game_data.get("periodDescriptor", {})
        return {
            "period": pd.get("number", 3),
            "isOT": pd.get("number", 0) > 3,
            "isSO": pd.get("periodType") == "SO"
        }
    except Exception as e:
        print(f"      ERROR fetching game {game_id}: {e}")
        return None


def backfill_date_file(date_str, dry_run=False):
    """Backfill missing data for a single date file."""
    json_file = GAMES_DIR / f"{date_str}.json"

    if not json_file.exists():
        return False

    data = load_json(json_file)
    if not data:
        return False

    games = data.get("games", [])
    updated_games = []
    needs_update = False
    updates_made = 0

    for game in games:
        game_id = game.get("gameId")

        # Skip if game already has period data
        if game.get("period") is not None:
            updated_games.append(game)
            continue

        # Skip FUT games
        if game.get("gameState") == "FUT":
            updated_games.append(game)
            continue

        # Fetch period info
        print(f"  Fetching period info for game {game_id}...")
        period_info = fetch_game_period_info(game_id)

        if period_info:
            game.update(period_info)
            updates_made += 1
            needs_update = True

        updated_games.append(game)
        time.sleep(0.5)  # Rate limiting

    if needs_update and not dry_run:
        data["games"] = updated_games
        save_json(data, json_file)
        print(f"  ✅ Updated {updates_made} games in {date_str}.json")
        return True
    elif needs_update:
        print(f"  Would update {updates_made} games in {date_str}.json (dry run)")
        return True
    else:
        print(f"  No updates needed for {date_str}.json")
        return False


# =============================================================================
# Main Entry Point
# =============================================================================
def main():
    print("=" * 80)
    print("NHL Game OT/SO Data Backfill Tool")
    print("=" * 80)
    print()

    dry_run = "--dry-run" in sys.argv

    if dry_run:
        print("🔍 DRY RUN MODE - No files will be modified")
        print()

    # Find all date files with games missing period data
    files_to_update = []
    total_games_to_fix = 0

    print("Scanning for games missing period data...")
    for json_file in sorted(GAMES_DIR.glob("*.json")):
        date_str = json_file.stem
        data = load_json(json_file)
        if not data:
            continue

        games = data.get("games", [])
        games_needing_fix = 0

        for game in games:
            if (game.get("period") is None and
                game.get("gameState") != "FUT" and
                game.get("gameType") == 2):
                games_needing_fix += 1

        if games_needing_fix > 0:
            files_to_update.append(date_str)
            total_games_to_fix += games_needing_fix
            print(f"  {date_str}.json: {games_needing_fix} games")

    print()
    print(f"Found {total_games_to_fix} games in {len(files_to_update)} files missing period data")
    print()

    if dry_run:
        print("Dry run complete. Use without --dry-run to apply changes.")
        return

    response = input(f"Proceed to update {total_games_to_fix} games? (y/N): ")
    if response.lower() != 'y':
        print("Aborted.")
        return

    print()
    print("Updating files...")
    print()

    for i, date_str in enumerate(files_to_update, 1):
        print(f"[{i}/{len(files_to_update)}] {date_str}:")
        backfill_date_file(date_str, dry_run=False)
        print()

    print("=" * 80)
    print("✅ Backfill complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
