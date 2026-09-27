"""Focused tests for the upcoming Finnish games teaser."""

import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from fetch_upcoming_games import build_upcoming_games, fetch_current_roster_ids


class UpcomingGamesTests(unittest.TestCase):
    def test_only_future_regular_season_games_with_rostered_finns(self):
        roster = {
            "1": {"playerId": 1, "name": "Sebastian Aho", "currentTeam": "CAR", "isActive": True},
            "2": {"playerId": 2, "name": "Retired Finn", "currentTeam": "CAR", "isActive": False},
            "3": {"playerId": 3, "name": "Miro Heiskanen", "currentTeam": "DAL", "isActive": True},
            "4": {"playerId": 4, "name": "Former player", "currentTeam": "CAR", "isActive": True},
        }
        games = [
            {"id": 1, "gameType": 2, "gameState": "FUT", "startTimeUTC": "2026-09-29T21:00:00Z", "awayTeam": {"abbrev": "FLA"}, "homeTeam": {"abbrev": "CAR"}},
            {"id": 2, "gameType": 1, "gameState": "FUT", "startTimeUTC": "2026-09-28T21:00:00Z", "awayTeam": {"abbrev": "DAL"}, "homeTeam": {"abbrev": "CAR"}},
            {"id": 3, "gameType": 2, "gameState": "OFF", "startTimeUTC": "2026-09-26T21:00:00Z", "awayTeam": {"abbrev": "DAL"}, "homeTeam": {"abbrev": "CAR"}},
            {"id": 4, "gameType": 2, "gameState": "FUT", "startTimeUTC": "2026-09-30T21:00:00Z", "awayTeam": {"abbrev": "BOS"}, "homeTeam": {"abbrev": "NYR"}},
        ]
        now = datetime(2026, 9, 27, tzinfo=timezone.utc)

        result = build_upcoming_games([games, games], roster, {"CAR": {1}, "DAL": {3}}, now)

        self.assertEqual([game["gameId"] for game in result], [1])
        self.assertEqual(result[0]["finnishPlayers"], [{"name": "Sebastian Aho", "team": "CAR"}])

    def test_orders_and_limits_games_by_start_time(self):
        roster = {"1": {"playerId": 1, "name": "Miro Heiskanen", "currentTeam": "DAL", "isActive": True}}
        games = [
            {"id": 3, "gameType": 2, "gameState": "FUT", "startTimeUTC": "2026-10-03T21:00:00Z", "awayTeam": {"abbrev": "DAL"}, "homeTeam": {"abbrev": "CAR"}},
            {"id": 2, "gameType": 2, "gameState": "FUT", "startTimeUTC": "2026-10-02T21:00:00Z", "awayTeam": {"abbrev": "DAL"}, "homeTeam": {"abbrev": "CAR"}},
        ]

        result = build_upcoming_games([games], roster, {"DAL": {1}}, datetime(2026, 9, 27, tzinfo=timezone.utc), limit=1)

        self.assertEqual([game["gameId"] for game in result], [2])

    def test_current_nhl_roster_handles_a_stale_team_in_player_data(self):
        roster = {"1": {"playerId": 1, "name": "Finnish Player", "currentTeam": "OTT", "isActive": True}}
        games = [{"id": 1, "gameType": 2, "gameState": "FUT", "startTimeUTC": "2026-09-29T21:00:00Z", "awayTeam": {"abbrev": "VAN"}, "homeTeam": {"abbrev": "CAR"}}]

        result = build_upcoming_games([games], roster, {"VAN": {1}}, datetime(2026, 9, 27, tzinfo=timezone.utc))

        self.assertEqual(result[0]["finnishPlayers"], [{"name": "Finnish Player", "team": "VAN"}])

    def test_roster_fetch_stops_after_enough_games_with_finns(self):
        games = [
            {"id": 1, "gameType": 2, "gameState": "FUT", "startTimeUTC": "2026-09-29T21:00:00Z", "awayTeam": {"abbrev": "ANA"}, "homeTeam": {"abbrev": "BOS"}},
            {"id": 2, "gameType": 2, "gameState": "FUT", "startTimeUTC": "2026-09-30T21:00:00Z", "awayTeam": {"abbrev": "BOS"}, "homeTeam": {"abbrev": "CAR"}},
            {"id": 3, "gameType": 2, "gameState": "FUT", "startTimeUTC": "2026-10-01T21:00:00Z", "awayTeam": {"abbrev": "DAL"}, "homeTeam": {"abbrev": "EDM"}},
        ]
        requested = []

        class Response:
            status_code = 200

            def __init__(self, team):
                self.team = team

            def raise_for_status(self):
                pass

            def json(self):
                return {"forwards": [{"id": 1}] if self.team == "CAR" else [], "defensemen": [], "goalies": []}

        def fake_get(url, **_kwargs):
            team = url.split("/")[-2]
            requested.append(team)
            return Response(team)

        from unittest.mock import patch
        with patch("fetch_upcoming_games.time.sleep"):
            rosters = fetch_current_roster_ids([games], {1}, datetime(2026, 9, 27, tzinfo=timezone.utc), limit=1, getter=fake_get)

        self.assertEqual(requested, ["ANA", "BOS", "CAR"])
        self.assertEqual(rosters["CAR"], {1})


if __name__ == "__main__":
    unittest.main()
