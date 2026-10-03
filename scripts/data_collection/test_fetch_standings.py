"""Focused tests for official standings refresh and last-good preservation."""
import copy
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).parent))
from fetch_standings import build_snapshot, refresh_snapshot

NOW = datetime(2026, 10, 3, 8, tzinfo=timezone.utc)

def response(season=20262027):
    rows = []
    for division_index, division in enumerate(("A", "M", "C", "P")):
        for index in range(8):
            rows.append({
                "teamAbbrev": {"default": f"T{division_index}{index}"},
                "seasonId": season, "date": "2026-10-03",
                "conferenceAbbrev": "E" if division_index < 2 else "W", "divisionAbbrev": division,
                "gamesPlayed": 0, "wins": 0, "losses": 0, "otLosses": 0, "points": 0,
                "goalFor": 0, "goalAgainst": 0, "divisionSequence": index + 1,
                "conferenceSequence": (division_index % 2) * 8 + index + 1,
                "leagueSequence": division_index * 8 + index + 1,
            })
    return {"standings": rows}

class StandingsTests(unittest.TestCase):
    def test_zero_game_teams_and_missing_optional_fields_are_valid(self):
        snapshot = build_snapshot(response(), NOW)
        self.assertEqual(len(snapshot["standings"]), 32)
        self.assertEqual(snapshot["seasonId"], 20262027)
        self.assertEqual(snapshot["fetchedAt"], "2026-10-03T08:00:00Z")

    def test_rejects_incomplete_duplicate_mixed_and_invalid_records(self):
        for mutation in ("missing", "duplicate", "season", "rank", "record", "points", "conference"):
            data = copy.deepcopy(response())
            if mutation == "missing": data["standings"].pop()
            if mutation == "duplicate": data["standings"][1]["teamAbbrev"] = data["standings"][0]["teamAbbrev"]
            if mutation == "season": data["standings"][0]["seasonId"] = 20252026
            if mutation == "rank": data["standings"][0]["divisionSequence"] = 2
            if mutation == "record": data["standings"][0]["wins"] = 1
            if mutation == "points": data["standings"][0]["points"] = 1
            if mutation == "conference": data["standings"][0]["conferenceAbbrev"] = "W"
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                build_snapshot(data, NOW)

    def test_failed_refresh_does_not_change_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "standings.json"
            refresh_snapshot(path, now=NOW, fetcher=lambda _: response())
            before = path.read_bytes()
            for result in (None, {"standings": []}):
                with self.assertRaises(ValueError):
                    refresh_snapshot(path, force=True, now=NOW + timedelta(hours=4), fetcher=lambda _: result)
                self.assertEqual(path.read_bytes(), before)

    def test_hourly_throttle_and_forced_result_refresh(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "standings.json"
            fetcher = Mock(return_value=response())
            self.assertTrue(refresh_snapshot(path, now=NOW, fetcher=fetcher))
            self.assertFalse(refresh_snapshot(path, now=NOW + timedelta(minutes=59), fetcher=fetcher))
            self.assertEqual(fetcher.call_count, 1)
            self.assertTrue(refresh_snapshot(path, now=NOW + timedelta(hours=1), fetcher=fetcher))
            self.assertTrue(refresh_snapshot(path, force=True, now=NOW + timedelta(minutes=61), fetcher=fetcher))
            self.assertEqual(fetcher.call_count, 3)

    def test_season_rollover_and_old_response_protection(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "standings.json"
            refresh_snapshot(path, now=NOW, fetcher=lambda _: response(20252026))
            refresh_snapshot(path, force=True, now=NOW, fetcher=lambda _: response())
            before = path.read_bytes()
            with self.assertRaises(ValueError):
                refresh_snapshot(path, force=True, now=NOW, fetcher=lambda _: response(20252026))
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(json.loads(before)["seasonId"], 20262027)

if __name__ == "__main__":
    unittest.main()
