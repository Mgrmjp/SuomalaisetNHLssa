#!/usr/bin/env python3
"""
Fix Game States and Scores

Fixes games that were saved with incomplete CRIT/FINAL states.
Re-fetches from NHL API to get correct final scores and normalizes game state to OFF.

Usage:
    python fix_game_states.py              # Fix all games
    python fix_game_states.py --dry-run    # Show what would be fixed
    python fix_game_states.py --date 2026-01-14  # Fix specific date
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple

# NHL API Base
NHL_API_BASE = "https://api-web.nhle.com"

# Project paths
BASE_DIR = Path(__file__).parent.parent.parent
GAMES_DIR = BASE_DIR / "static/data/prepopulated/games"


def fetch_from_api(url: str, max_retries: int = 2) -> dict | None:
    """Fetch data from NHL API with retry logic."""
    import requests

    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"    ❌ Error fetching {url}: {e}")
                return None
            time.sleep(2)
    return None


def find_games_needing_fix(dry_run: bool = False, target_date: str | None = None) -> List[Tuple[Path, int, dict]]:
    """
    Scan game JSON files for games with CRIT or FINAL states.

    Returns:
        List of (file_path, game_id, game_data) tuples
    """
    games_to_fix = []

    if target_date:
        json_files = [GAMES_DIR / f"{target_date}.json"]
    else:
        json_files = sorted(GAMES_DIR.glob("*.json"), reverse=True)

    print(f"🔍 Scanning for games with CRIT/FINAL states...")

    for file_path in json_files:
        if not file_path.exists():
            continue

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            for game in data.get("games", []):
                game_state = game.get("gameState")
                game_id = game.get("gameId")

                if game_state in ["CRIT", "FINAL"] and game_id:
                    games_to_fix.append((file_path, game_id, game))

        except Exception as e:
            print(f"⚠️ Error reading {file_path.name}: {e}")

    print(f"   Found {len(games_to_fix)} games needing fix")
    return games_to_fix


def fetch_correct_game_data(game_id: int) -> dict | None:
    """Fetch correct game data from NHL API."""
    url = f"{NHL_API_BASE}/v1/gamecenter/{game_id}/boxscore"
    boxscore = fetch_from_api(url)

    if not boxscore:
        return None

    game_state = boxscore.get("gameState")
    pd = boxscore.get("periodDescriptor", {})
    home_team = boxscore.get("homeTeam", {})
    away_team = boxscore.get("awayTeam", {})
    game_type = boxscore.get("gameType", 2)  # 1=preseason, 2=regular, 3=playoffs

    # For regular season and playoffs, only accept OFF state
    # For preseason, FINAL is acceptable (API doesn't change it to OFF)
    if game_type == 2 and game_state not in ["OFF", "FINAL"]:
        print(f"    ⚠️ Game still not OFF (state: {game_state})")
        return None
    elif game_type == 3 and game_state != "OFF":
        print(f"    ⚠️ Playoff game still not OFF (state: {game_state})")
        return None
    elif game_type == 1 and game_state not in ["OFF", "FINAL"]:
        print(f"    ⚠️ Preseason game not final (state: {game_state})")
        return None

    # Normalize FINAL to OFF for consistency
    normalized_state = "OFF" if game_state in ["OFF", "FINAL"] else game_state

    return {
        "gameId": game_id,
        "gameState": normalized_state,
        "gameType": game_type,
        "homeScore": home_team.get("score", 0),
        "awayScore": away_team.get("score", 0),
        "period": pd.get("number", 3),
        "periodType": pd.get("periodType", "REG"),
        "isOT": pd.get("number", 0) > 3,
        "isSO": pd.get("periodType") == "SO",
    }


def update_player_scores_in_file(
    file_path: Path,
    game_id: int,
    correct_home_score: int,
    correct_away_score: int,
    home_team: str,
    away_team: str
) -> bool:
    """
    Update player data in the JSON file for a specific game.
    Updates game_score field and recent_results for affected players.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"    ❌ Error reading file: {e}")
        return False

    updated_players = False

    # Update players who played in this game
    for player in data.get("players", []):
        if player.get("game_id") == game_id:
            # Update game_score field
            player_team = player.get("team")
            opponent = player.get("opponent")

            if player_team == home_team:
                player_score = correct_home_score
                opponent_score = correct_away_score
            elif player_team == away_team:
                player_score = correct_away_score
                opponent_score = correct_home_score
            else:
                continue

            old_score = player.get("game_score", "")
            new_score = f"{player_score}-{opponent_score}"

            if old_score != new_score:
                player["game_score"] = new_score

                # Update game_result
                if player_score > opponent_score:
                    player["game_result"] = "W"
                elif player_score < opponent_score:
                    player["game_result"] = "L"
                else:
                    player["game_result"] = "T"  # Shouldn't happen in NHL

                # Update recent_results
                for recent in player.get("recent_results", []):
                    if recent.get("date") == player.get("game_date"):
                        recent["team_score"] = player_score
                        recent["opponent_score"] = opponent_score

                        # Update result
                        if player_score > opponent_score:
                            recent["result"] = "W"
                        elif player_score < opponent_score:
                            recent["result"] = "L"
                        else:
                            recent["result"] = "T"

                updated_players = True
                print(f"      ✏️ Updated {player['name']}: {old_score} → {new_score}")

    if updated_players:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"    ❌ Error writing file: {e}")
            return False

    return False


def fix_game(
    file_path: Path,
    game_id: int,
    old_game_data: dict,
    dry_run: bool = False
) -> bool:
    """Fix a single game's state and scores."""
    print(f"\n🏒 Game {game_id} ({old_game_data.get('awayTeam')} @ {old_game_data.get('homeTeam')})")
    print(f"   Old: {old_game_data.get('awayScore')}-{old_game_data.get('homeScore')} {old_game_data.get('gameState')} P{old_game_data.get('period')}")

    # Fetch correct data
    correct_data = fetch_correct_game_data(game_id)
    if not correct_data:
        print(f"   ⚠️ Skipping - could not get correct data")
        return False

    print(f"   New: {correct_data['awayScore']}-{correct_data['homeScore']} {correct_data['gameState']} P{correct_data['period']}")

    # Check if scores actually changed
    scores_changed = (
        correct_data['homeScore'] != old_game_data.get('homeScore') or
        correct_data['awayScore'] != old_game_data.get('awayScore')
    )

    if not scores_changed and correct_data['gameState'] == "OFF":
        print(f"   ℹ️ Scores unchanged, just normalizing state")
    elif not scores_changed:
        print(f"   ℹ️ No changes needed")
        return False

    if dry_run:
        print(f"   [DRY RUN] Would update game state and scores")
        return True

    # Update the game in the JSON file
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            file_data = json.load(f)
    except Exception as e:
        print(f"   ❌ Error reading file: {e}")
        return False

    # Find and update the game
    game_updated = False
    for game in file_data.get("games", []):
        if game.get("gameId") == game_id:
            game["gameState"] = "OFF"
            game["homeScore"] = correct_data["homeScore"]
            game["awayScore"] = correct_data["awayScore"]
            game["isOT"] = correct_data["isOT"]
            game["isSO"] = correct_data["isSO"]
            game["period"] = correct_data["period"]
            game_updated = True
            break

    if not game_updated:
        print(f"   ⚠️ Game {game_id} not found in file")
        return False

    # Save updated game data
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(file_data, f, indent=2, ensure_ascii=False)
        print(f"   ✅ Updated game summary")
    except Exception as e:
        print(f"   ❌ Error writing file: {e}")
        return False

    # Update player data
    if scores_changed:
        update_player_scores_in_file(
            file_path,
            game_id,
            correct_data["homeScore"],
            correct_data["awayScore"],
            old_game_data.get("homeTeam"),
            old_game_data.get("awayTeam")
        )

    return True


def main():
    dry_run = "--dry-run" in sys.argv
    target_date = None

    if "--date" in sys.argv:
        date_idx = sys.argv.index("--date")
        if date_idx + 1 < len(sys.argv):
            target_date = sys.argv[date_idx + 1]

    print("=" * 80)
    print("NHL Game State and Score Fixer")
    print("=" * 80)

    if dry_run:
        print("🧪 DRY RUN MODE - No changes will be made\n")

    # Find games needing fixes
    games_to_fix = find_games_needing_fix(dry_run=dry_run, target_date=target_date)

    if not games_to_fix:
        print("\n✅ No games need fixing!")
        return

    print(f"\n📋 Games to fix:")
    for file_path, game_id, game_data in games_to_fix[:10]:
        print(f"   {game_id}: {game_data.get('awayTeam')} {game_data.get('awayScore')} @ {game_data.get('homeTeam')} {game_data.get('homeScore')} ({game_data.get('gameState')})")

    if len(games_to_fix) > 10:
        print(f"   ... and {len(games_to_fix) - 10} more")

    if dry_run:
        print("\n🧪 Dry run complete - no changes made")
        return

    # Fix each game
    print(f"\n🔧 Fixing {len(games_to_fix)} games...")

    fixed_count = 0
    failed_count = 0

    # Group by file to avoid re-reading
    by_file: Dict[Path, List[Tuple[int, dict]]] = {}
    for file_path, game_id, game_data in games_to_fix:
        if file_path not in by_file:
            by_file[file_path] = []
        by_file[file_path].append((game_id, game_data))

    for file_path, games in sorted(by_file.items()):
        print(f"\n📁 {file_path.name}")
        for game_id, game_data in games:
            if fix_game(file_path, game_id, game_data, dry_run=dry_run):
                fixed_count += 1
            else:
                failed_count += 1

            time.sleep(1)  # Rate limiting

    print("\n" + "=" * 80)
    print(f"✅ Fixed: {fixed_count} games")
    if failed_count > 0:
        print(f"❌ Failed: {failed_count} games")
    print("=" * 80)


if __name__ == "__main__":
    main()
