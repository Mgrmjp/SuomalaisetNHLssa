"""A failed or incomplete NHL response must not replace saved results."""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent))
import fetch


class FetchResultsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.games_dir = Path(self.temp.name)
        self.date = "2026-10-01"
        self.file = self.games_dir / f"{self.date}.json"
        self.previous = '{"date":"2026-10-01","games":[{"gameId":1}],"players":[]}\n'
        self.file.write_text(self.previous)

    def collect(self, schedule, details=None):
        with patch.object(fetch, "GAMES_DIR", self.games_dir), patch.object(
            fetch, "load_finnish_player_cache", return_value={1: {"name": "Finn"}}
        ), patch.object(fetch, "get_schedule_for_date", return_value=schedule), patch.object(
            fetch, "get_game_details", return_value=details
        ), patch.object(fetch.time, "sleep"):
            return fetch.generate_and_save_for_date(self.date)

    def test_schedule_failure_preserves_existing_file(self):
        with self.assertRaises(RuntimeError):
            self.collect(None)
        self.assertEqual(self.file.read_text(), self.previous)

    def test_missing_boxscore_preserves_existing_file(self):
        with self.assertRaises(RuntimeError):
            self.collect({"date": self.date, "games": [{"id": 1}]})
        self.assertEqual(self.file.read_text(), self.previous)

    def test_unresolved_boxscore_preserves_existing_file(self):
        with self.assertRaises(RuntimeError):
            self.collect({"date": self.date, "games": [{"id": 1}]}, {
                "gameState": "CRIT", "periodDescriptor": {"number": 3},
            })
        self.assertEqual(self.file.read_text(), self.previous)

    def test_confirmed_day_without_games_is_saved(self):
        result = self.collect({"date": self.date, "games": []})
        self.assertEqual(result["games"], [])
        self.assertEqual(json.loads(self.file.read_text())["date"], self.date)

    def test_schedule_selects_the_requested_day(self):
        schedule = {"gameWeek": [
            {"date": "2026-09-30", "games": [{"id": 9}]},
            {"date": self.date, "games": []},
        ]}
        with patch.object(fetch, "fetch_from_api", return_value=schedule):
            self.assertEqual(fetch.get_schedule_for_date(self.date)["games"], [])

    def test_schedule_omitting_requested_day_is_an_error(self):
        with patch.object(fetch, "fetch_from_api", return_value={"gameWeek": []}):
            with self.assertRaises(RuntimeError):
                fetch.get_schedule_for_date(self.date)


if __name__ == "__main__":
    unittest.main()
