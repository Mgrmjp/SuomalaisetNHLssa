#!/usr/bin/env python3
"""
Sync Finnish players cache to static roster file.

This script copies the built cache from:
  scripts/data_collection/finnish/cache/finnish-players.json
To:
  static/data/players/finnish-roster.json

The frontend reads from the static location, so this sync must happen
after any cache updates.

Usage: python sync_roster.py
"""

import json
import shutil
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import FINNISH_CACHE_FILE, DATA_DIR


def sync_roster():
    """
    Sync the Finnish players cache to the static roster location.
    Preserves extra fields (lastTeam, gamesPlayed) from the existing roster
    that are populated by fetch-last-teams.cjs but not by build_cache.py.
    """
    cache_file = FINNISH_CACHE_FILE
    roster_file = DATA_DIR / "players" / "finnish-roster.json"

    print(f"📂 Cache: {cache_file}")
    print(f"📂 Roster: {roster_file}")
    print()

    # Verify cache exists
    if not cache_file.exists():
        print(f"❌ Cache file not found: {cache_file}")
        print("   Run build_cache.py first to generate the cache.")
        return False

    # Read cache
    print("📖 Reading cache...")
    with open(cache_file, "r", encoding="utf-8") as f:
        cache_data = json.load(f)

    player_count = len(cache_data)
    print(f"   Found {player_count} Finnish players")

    # Preserve extra fields from the existing roster (e.g., lastTeam, gamesPlayed)
    preserved_fields = {}
    if roster_file.exists():
        try:
            with open(roster_file, "r", encoding="utf-8") as f:
                existing_roster = json.load(f)
            for pid, pdata in existing_roster.items():
                extra = {}
                if "lastTeam" in pdata and pdata["lastTeam"] is not None:
                    extra["lastTeam"] = pdata["lastTeam"]
                if "gamesPlayed" in pdata and pdata["gamesPlayed"] is not None:
                    extra["gamesPlayed"] = pdata["gamesPlayed"]
                if extra:
                    preserved_fields[pid] = extra
        except Exception:
            pass

    # Merge preserved fields into cache data
    merged_count = 0
    for pid, fields in preserved_fields.items():
        if pid in cache_data:
            for key, value in fields.items():
                if value is not None and (
                    key not in cache_data[pid] or cache_data[pid].get(key) is None
                ):
                    cache_data[pid][key] = value
                    merged_count += 1

    if merged_count:
        print(f"   Preserved {merged_count} extra field(s) from existing roster")

    # Ensure output directory exists
    roster_file.parent.mkdir(parents=True, exist_ok=True)

    # Write to roster location
    print(f"💾 Writing to roster file...")
    with open(roster_file, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, indent=2, ensure_ascii=False)

    print(f"   ✅ Synced {player_count} players")
    print()

    # Show players by team
    teams = {}
    for player_id, player in cache_data.items():
        team = player.get("currentTeam", "UNKNOWN")
        if team not in teams:
            teams[team] = []
        teams[team].append(player["name"])

    print("📊 Players by team:")
    for team in sorted(teams.keys()):
        players = teams[team]
        print(f"   {team}: {len(players)} players")

    print()
    print("✅ Roster sync complete!")
    return True


if __name__ == "__main__":
    success = sync_roster()
    sys.exit(0 if success else 1)
