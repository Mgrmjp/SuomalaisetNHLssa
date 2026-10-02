"""Regression tests for collecting results after the live polling window."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent))
import realtime_poll


class RealtimePollTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.games_dir = Path(self.temp_dir.name)
        self.date = "2026-10-01"
        self.game = {
            "id": 2026020009,
            "gameState": "OFF",
            "startTimeUTC": "2026-10-01T23:00:00Z",
            "homeTeam": {"abbrev": "PHI", "score": 3},
            "awayTeam": {"abbrev": "NJD", "score": 2},
        }

    def poll(self, games=None):
        schedule = {"gameWeek": [{"date": self.date, "games": games or [self.game]}]}
        with patch.object(realtime_poll, "GAMES_DIR", self.games_dir), patch.object(
            realtime_poll, "fetch_from_api", return_value=schedule
        ):
            return realtime_poll.check_for_live_games(self.date)

    def save_game(self, state="OFF", home_score=3, away_score=2):
        (self.games_dir / f"{self.date}.json").write_text(json.dumps({
            "games": [{"gameId": self.game["id"], "gameState": state,
                       "homeScore": home_score, "awayScore": away_score}]
        }))

    def test_finished_games_replace_stale_upcoming_data(self):
        self.save_game("FUT", 0, 0)
        self.assertTrue(self.poll())

    def test_finished_games_replace_last_live_snapshot(self):
        self.save_game("LIVE", 2, 2)
        self.assertTrue(self.poll())

    def test_missing_results_are_collected_after_games_finish(self):
        self.assertTrue(self.poll())

    def test_correct_final_results_do_not_trigger_another_deployment(self):
        self.save_game()
        self.assertFalse(self.poll())

    def test_corrected_final_scores_are_collected(self):
        self.save_game(home_score=2)
        self.assertTrue(self.poll())

    def test_live_games_still_trigger_updates(self):
        self.assertTrue(self.poll([{**self.game, "gameState": "LIVE"}]))

    def test_only_requested_schedule_day_is_checked(self):
        schedule = {"gameWeek": [
            {"date": "2026-09-30", "games": [{**self.game, "gameState": "LIVE"}]},
            {"date": self.date, "games": []},
        ]}
        with patch.object(realtime_poll, "fetch_from_api", return_value=schedule):
            self.assertFalse(realtime_poll.check_for_live_games(self.date))

    def test_failed_update_does_not_report_updated_to_actions(self):
        output = self.games_dir / "github-output"
        with patch.object(sys, "argv", ["realtime_poll.py", "--once", "--force", "--date", self.date]), patch.dict(
            os.environ, {"GITHUB_OUTPUT": str(output)}
        ), patch.object(realtime_poll, "run_update", return_value=False):
            with self.assertRaises(SystemExit) as raised:
                realtime_poll.main()
        self.assertEqual(raised.exception.code, 1)
        self.assertEqual(output.read_text(), "updated=false\n")

    def test_both_utc_days_are_checked_even_after_noon(self):
        for hour in (0, 15, 23):
            with self.subTest(hour=hour):
                self.assertEqual(
                    realtime_poll.poll_dates(now=datetime(2026, 10, 2, hour, tzinfo=timezone.utc)),
                    ["2026-10-01", "2026-10-02"],
                )

    def test_poll_recovers_yesterday_without_skipping_todays_games(self):
        with patch.object(realtime_poll, "check_for_live_games", side_effect=[True, True]) as check, patch.object(
            realtime_poll, "run_update", return_value=True
        ) as update:
            self.assertTrue(realtime_poll.poll_once(["2026-10-01", "2026-10-02"]))
        self.assertEqual([call.args[0] for call in check.call_args_list], ["2026-10-01", "2026-10-02"])
        self.assertEqual(update.call_count, 2)

    def test_api_failure_is_reported_instead_of_a_successful_noop(self):
        with patch.object(realtime_poll, "fetch_from_api", return_value=None):
            with self.assertRaises(RuntimeError):
                realtime_poll.check_for_live_games(self.date)

    def test_workflow_pushes_results_and_manifest_before_rebasing(self):
        workflow_path = Path(__file__).resolve().parents[2] / ".github/workflows/realtime-update.yml"
        step = workflow_path.read_text().split(
            "      - name: Commit and push updated data\n", 1
        )[1].split("\n      - name:", 1)[0]
        script = "\n".join(
            line[10:] for line in step.split("        run: |\n", 1)[1].splitlines()
        )
        remote = self.games_dir / "remote.git"
        checkout = self.games_dir / "checkout"

        def git(*args, cwd=None):
            return subprocess.run(
                ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
            )

        git("init", "--bare", "--initial-branch=main", str(remote))
        git("clone", str(remote), str(checkout))
        git("config", "user.name", "Test", cwd=checkout)
        git("config", "user.email", "test@example.invalid", cwd=checkout)
        git("config", "commit.gpgsign", "false", cwd=checkout)
        git("config", "rebase.autoStash", "false", cwd=checkout)
        files = [
            "static/data/prepopulated/games/2026-10-01.json",
            "static/data/players/finnish-roster.json",
            "static/data/games_manifest.json",
        ]
        for filename in files:
            path = checkout / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("{}\n")
        git("add", ".", cwd=checkout)
        git("commit", "-m", "Initial data", cwd=checkout)
        git("push", "origin", "main", cwd=checkout)
        for filename in (files[0], files[2]):
            (checkout / filename).write_text('{"updated":true}\n')

        result = subprocess.run(
            ["bash", "-e", "-c", script], cwd=checkout, capture_output=True, text=True
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(git("status", "--porcelain", cwd=checkout).stdout, "")
        for filename in (files[0], files[2]):
            self.assertEqual(
                git("show", f"main:{filename}", cwd=remote).stdout,
                '{"updated":true}\n',
            )


if __name__ == "__main__":
    unittest.main()
