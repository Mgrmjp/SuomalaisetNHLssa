#!/usr/bin/env python3
"""Tests for the EliteProspects rankings fetcher.

The payload shape has changed before, so these tests pin the mapping to a
recorded response and to the older layout. When EliteProspects changes the
schema again, the mapping test should fail instead of silently writing nulls.
"""

import contextlib
import functools
import io
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent))

import fetch_ep_rankings as ep

# Trimmed from a live /_next/data/.../consolidated-ranking.json response
# (2026-10-25): position moved to player.detailedPosition, team and league to
# playerStats, and height/weight became objects.
RECORDED_PAYLOAD = {
    "pageProps": {
        "draftRankings": {
            "rankings": [
                {
                    "rank": 18,
                    "player": {
                        "id": "1009106",
                        "name": "Luca Santala",
                        "dateOfBirth": "2009-07-28",
                        "detailedPosition": ["C", "W"],
                        "height": {"metrics": 189, "imperial": "6'2\""},
                        "weight": {"metrics": 86, "imperial": 190},
                    },
                    "playerStats": {
                        "team": {"name": "London Knights"},
                        "league": {"name": "OHL"},
                    },
                },
                {
                    "rank": 46,
                    "player": {
                        "id": "1009107",
                        "name": "Lenni Kokkonen",
                        "dateOfBirth": "2009-02-14",
                        "detailedPosition": ["D"],
                        "height": {"metrics": 185},
                        "weight": {"metrics": 82},
                    },
                    "playerStats": {
                        "team": {"name": "Kärpät U20"},
                        "league": {"name": "U20 SM-sarja"},
                    },
                },
                {"rank": 99, "player": {}, "playerStats": {}},
            ]
        }
    }
}

LEGACY_ROW = {
    "rank": 12,
    "player": {
        "id": 8480001,
        "name": "Eeli Tolvanen",
        "firstName": "Eeli",
        "lastName": "Tolvanen",
        "position": "LW",
        "dateOfBirth": "1999-06-18",
        "height": 179,
        "weight": 82,
    },
    "team": {"name": "Jokerit"},
    "league": {"name": "Liiga"},
}


def quiet(func):
    """Silence the fetch/build-id logging these guards print on purpose."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with contextlib.redirect_stdout(io.StringIO()):
            return func(*args, **kwargs)

    return wrapper


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code
        self.text = ""

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class BuildIdTests(unittest.TestCase):
    def test_extracts_build_id_from_page_html(self):
        html = '<script id="__NEXT_DATA__" type="application/json">{"buildId":"OiMq78Sf","page":"/rss"}</script>'

        self.assertEqual(ep.build_id_from_html(html), "OiMq78Sf")

    def test_missing_build_id_is_none(self):
        self.assertIsNone(ep.build_id_from_html("<html></html>"))
        self.assertIsNone(ep.build_id_from_html(None))

    @quiet
    def test_falls_back_to_the_draft_centre_when_rss_lacks_a_build_id(self):
        responses = {
            "https://www.eliteprospects.com/rss": FakeResponse({}, 403),
            "https://www.eliteprospects.com/draft-center": FakeResponse({}),
            "https://www.eliteprospects.com/leagues": FakeResponse({}),
        }

        calls = []

        def fake_get(url, **kwargs):
            calls.append(url)
            response = responses.get(url)
            if response is None:
                raise RuntimeError(f"unexpected url {url}")
            if response.status_code >= 400:
                raise RuntimeError("HTTP 403")
            response.text = '{"buildId":"Fallback123"}'
            return response

        with patch.object(ep.requests, "get", side_effect=fake_get):
            build_id = ep.get_build_id()

        self.assertEqual(build_id, "Fallback123")
        self.assertEqual(calls[0], "https://www.eliteprospects.com/rss")
        self.assertEqual(calls[1], "https://www.eliteprospects.com/draft-center")


class PayloadShapeTests(unittest.TestCase):
    def test_extracts_rows_from_page_props(self):
        self.assertEqual(len(ep.extract_ranking_rows(RECORDED_PAYLOAD)), 3)

    def test_falls_back_to_data_picks(self):
        payload = {"pageProps": {"data": {"picks": [{"rank": 1}]}}}

        self.assertEqual(ep.extract_ranking_rows(payload), [{"rank": 1}])

    def test_normalizes_the_current_payload(self):
        player = ep.normalize_ranking_row(RECORDED_PAYLOAD["pageProps"]["draftRankings"]["rankings"][0])

        self.assertEqual(
            player,
            {
                "rank": 18,
                "name": "Luca Santala",
                "firstName": None,
                "lastName": None,
                "position": "C",
                "team": "London Knights",
                "league": "OHL",
                "birthDate": "2009-07-28",
                "height": 189,
                "weight": 86,
                "playerId": "1009106",
            },
        )

    def test_normalizes_the_legacy_payload(self):
        player = ep.normalize_ranking_row(LEGACY_ROW)

        self.assertEqual(player["position"], "LW")
        self.assertEqual(player["team"], "Jokerit")
        self.assertEqual(player["league"], "Liiga")
        self.assertEqual(player["height"], 179)
        self.assertEqual(player["playerId"], 8480001)

    def test_missing_player_fields_degrade_to_none(self):
        player = ep.normalize_ranking_row({"rank": 99, "player": {}})

        self.assertEqual(player["rank"], 99)
        self.assertIsNone(player["name"])
        self.assertIsNone(player["height"])


class FetchRankingTests(unittest.TestCase):
    @quiet
    def test_drops_rows_without_a_name(self):
        with patch.object(ep.requests, "get", return_value=FakeResponse(RECORDED_PAYLOAD)):
            players = ep.fetch_ranking("build", "consolidated-ranking", "Consolidated Ranking")

        self.assertEqual([p["name"] for p in players], ["Luca Santala", "Lenni Kokkonen"])

    @quiet
    def test_returns_empty_on_http_error(self):
        with patch.object(ep.requests, "get", return_value=FakeResponse({}, 403)):
            players = ep.fetch_ranking("build", "eliteprospects.com", "EliteProspects.com")

        self.assertEqual(players, [])


if __name__ == "__main__":
    unittest.main()
