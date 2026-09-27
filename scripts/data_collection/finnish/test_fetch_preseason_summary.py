"""Tests for the Finnish preseason scoring and results summary."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from fetch_preseason_summary import build_preseason_summary


def boxscore(game_id, date, state="FINAL", game_type=1, finn_goals=0, finn_assists=0):
    return {
        "id": game_id,
        "gameType": game_type,
        "gameState": state,
        "startTimeUTC": f"{date}T23:00:00Z",
        "gameDate": date,
        "periodDescriptor": {"number": 3},
        "awayTeam": {"abbrev": "CAR", "score": 3},
        "homeTeam": {"abbrev": "NSH", "score": 2},
        "playerByGameStats": {
            "awayTeam": {
                "forwards": [{"playerId": 1, "goals": finn_goals, "assists": finn_assists}],
                "defense": [], "goalies": [],
            },
            "homeTeam": {"forwards": [], "defense": [], "goalies": []},
        },
    }


class PreseasonSummaryTests(unittest.TestCase):
    def test_aggregates_only_final_preseason_games_once(self):
        roster = {"1": {"name": "Sebastian Aho"}}
        games = [
            boxscore(10, "2026-09-19", finn_goals=1, finn_assists=1),
            boxscore(11, "2026-09-20", finn_assists=1),
            boxscore(10, "2026-09-19", finn_goals=1, finn_assists=1),
            boxscore(12, "2026-09-21", state="LIVE", finn_goals=2),
            boxscore(13, "2026-09-22", game_type=2, finn_goals=2),
        ]

        result = build_preseason_summary(games, roster, 2026, "2026-09-29")

        self.assertEqual(result["completedGames"], 2)
        self.assertEqual(result["finnishGames"], 2)
        self.assertEqual(result["scorers"], [{
            "playerId": 1, "name": "Sebastian Aho", "team": "CAR",
            "gamesPlayed": 2, "goals": 1, "assists": 2, "points": 3,
        }])
        self.assertEqual([game["gameId"] for game in result["games"]], [11, 10])
        self.assertEqual(result["games"][0]["finnishPlayers"][0]["points"], 1)

    def test_keeps_final_result_without_finns_for_coverage(self):
        game = boxscore(10, "2026-09-19")
        game["playerByGameStats"]["awayTeam"]["forwards"] = [{"playerId": 99, "goals": 2, "assists": 0}]

        result = build_preseason_summary([game], {"1": {"name": "Sebastian Aho"}}, 2026, "2026-09-29")

        self.assertEqual(result["completedGames"], 1)
        self.assertEqual(result["finnishGames"], 0)
        self.assertEqual(result["scorers"], [])

    def test_backup_goalie_with_zero_ice_time_is_not_counted(self):
        game = boxscore(10, "2026-09-19")
        game["playerByGameStats"]["awayTeam"]["forwards"] = []
        game["playerByGameStats"]["awayTeam"]["goalies"] = [
            {"playerId": 1, "toi": "00:00", "saves": 0},
        ]

        result = build_preseason_summary([game], {"1": {"name": "Finnish Goalie"}}, 2026, "2026-09-29")

        self.assertEqual(result["finnishGames"], 0)


if __name__ == "__main__":
    unittest.main()
