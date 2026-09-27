#!/usr/bin/env python3
"""
Tests for sync_roster.py field preservation logic.

Verifies that lastTeam and gamesPlayed fields are preserved
when syncing the cache to the roster file.

Run: python scripts/data_collection/finnish/test_sync_roster.py
"""

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import FINNISH_CACHE_FILE
import sync_roster as sr


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent


def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def make_player(pid, name, team="", active=True, **extra):
    return {
        "playerId": pid,
        "name": name,
        "firstName": {"default": name.split()[0]},
        "lastName": {"default": name.split()[-1]},
        "position": "C",
        "sweaterNumber": 10,
        "birthDate": "1990-01-01",
        "birthCity": {"default": "Helsinki"},
        "birthCountry": "FIN",
        "birthplace": "Helsinki, FIN",
        "heightInches": 72,
        "weightLbs": 190,
        "shootsCatches": "L",
        "headshot": "",
        "isActive": active,
        "currentTeam": team,
        **extra,
    }


def test_latest_move_wins_even_when_moves_are_newest_first():
    moves = [
        {"playerId": "8482447", "newTeam": "VAN", "date": "2026-09-25"},
        {"playerId": "8482447", "newTeam": "OTT", "date": "2026-07-02"},
        {"playerId": "8470001", "newTeam": "DAL", "date": "2026-08-01"},
    ]
    latest = sr.latest_moves_by_player(moves)
    assert latest["8482447"]["newTeam"] == "VAN"
    assert latest["8470001"]["newTeam"] == "DAL"
    print("PASSED: latest move wins even when moves are newest first")


def test_sync_preserves_last_team():
    """lastTeam/gamesPlayed from existing roster should survive sync."""
    cache = {
        "8470001": make_player(8470001, "Active Player", "ANA", active=True),
        "8470002": make_player(8470002, "Retired Player", "", active=False),
    }

    existing_roster = {
        "8470001": make_player(8470001, "Active Player", "ANA", active=True),
        "8470002": make_player(
            8470002,
            "Retired Player",
            "",
            active=False,
            lastTeam="CHI",
            gamesPlayed=450,
        ),
    }

    tmpdir = tempfile.mkdtemp()
    cache_file = Path(tmpdir) / "cache.json"
    roster_file = Path(tmpdir) / "roster.json"

    with open(cache_file, "w") as f:
        json.dump(cache, f)
    with open(roster_file, "w") as f:
        json.dump(existing_roster, f)

    tmp_data = Path(tmpdir) / "players"
    tmp_data.mkdir(parents=True, exist_ok=True)

    with open(tmp_data / "finnish-roster.json", "w") as f:
        json.dump(existing_roster, f)

    with open(cache_file, "w") as f:
        json.dump(cache, f)

    with (
        patch.object(sr, "FINNISH_CACHE_FILE", cache_file),
        patch.object(sr, "DATA_DIR", Path(tmpdir)),
    ):
        with open(roster_file, "w") as f:
            json.dump(existing_roster, f)

        result = sr.sync_roster()
        assert result is True, "sync_roster should return True"

        with open(Path(tmpdir) / "players" / "finnish-roster.json") as f:
            roster_written = json.load(f)

    retired = roster_written["8470002"]
    assert "lastTeam" in retired, f"lastTeam missing from retired player: {retired}"
    assert retired["lastTeam"] == "CHI", (
        f"Expected lastTeam=CHI, got {retired['lastTeam']}"
    )
    assert "gamesPlayed" in retired, (
        f"gamesPlayed missing from retired player: {retired}"
    )
    assert retired["gamesPlayed"] == 450, (
        f"Expected gamesPlayed=450, got {retired['gamesPlayed']}"
    )

    print("PASSED: sync_roster preserves lastTeam and gamesPlayed")


def test_sync_does_not_overwrite_active_team():
    """Active players should keep currentTeam, not get lastTeam from roster."""
    cache = {
        "8470001": make_player(8470001, "Active Player", "ANA", active=True),
    }

    existing_roster = {
        "8470001": make_player(
            8470001,
            "Active Player",
            "ANA",
            active=True,
            lastTeam="CGY",
            gamesPlayed=200,
        ),
    }

    tmpdir = tempfile.mkdtemp()
    cache_file = Path(tmpdir) / "cache.json"
    tmp_data = Path(tmpdir) / "players"
    tmp_data.mkdir(parents=True, exist_ok=True)

    with open(cache_file, "w") as f:
        json.dump(cache, f)
    with open(tmp_data / "finnish-roster.json", "w") as f:
        json.dump(existing_roster, f)

    with (
        patch.object(sr, "FINNISH_CACHE_FILE", cache_file),
        patch.object(sr, "DATA_DIR", Path(tmpdir)),
    ):
        sr.sync_roster()
        with open(Path(tmpdir) / "players" / "finnish-roster.json") as f:
            roster_written = json.load(f)

    active = roster_written["8470001"]
    assert active["currentTeam"] == "ANA", (
        f"Active player team should be ANA, got {active['currentTeam']}"
    )
    print("PASSED: sync_roster keeps active player's currentTeam")


def test_sync_handles_missing_roster_file():
    """Verify that the production roster and cache files exist and are valid."""
    roster = load_json(
        PROJECT_ROOT / "static" / "data" / "players" / "finnish-roster.json"
    )
    cache = load_json(FINNISH_CACHE_FILE)

    assert roster is not None, "Roster file should load"
    assert cache is not None, "Cache file should load"
    assert len(roster) > 0, "Roster should have players"
    assert len(cache) > 0, "Cache should have players"
    assert set(roster.keys()) == set(cache.keys()), (
        "Roster and cache should have same player IDs"
    )

    inactive = [
        p
        for p in roster.values()
        if not p.get("isActive", True) or not p.get("currentTeam")
    ]
    with_last_team = [p for p in inactive if p.get("lastTeam")]
    assert len(with_last_team) > 0, (
        "At least some inactive players should have lastTeam"
    )

    print("PASSED: production data files are valid and consistent")


if __name__ == "__main__":
    print("Running sync_roster field preservation tests...")
    print()
    test_latest_move_wins_even_when_moves_are_newest_first()
    test_sync_preserves_last_team()
    test_sync_does_not_overwrite_active_team()
    test_sync_handles_missing_roster_file()
    print()
    print("All tests passed!")
