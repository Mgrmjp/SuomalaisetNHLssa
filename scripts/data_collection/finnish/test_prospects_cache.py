#!/usr/bin/env python3
"""Tests for the prospects cache guards (window, merges, snapshots, id lookup)."""

import contextlib
import functools
import io
import sys
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

import build_prospects_cache as cache


def quiet(func):
    """Silence the SKIP/WARNING chatter these guards print."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with contextlib.redirect_stdout(io.StringIO()):
            return func(*args, **kwargs)

    return wrapper


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def json(self):
        return self._payload


class ProspectWindowTests(unittest.TestCase):
    @quiet
    def test_window_derives_from_the_scanned_draft_history(self):
        today = datetime(2026, 10, 25)
        self.assertEqual(cache.draft_history_start_year(today), 2016)
        self.assertEqual(cache.prospect_min_birth_year(today), 1996)
        # The 2005 floor keeps older repositories from rejecting everything.
        self.assertEqual(cache.prospect_min_birth_year(datetime(2010, 1, 1)), 1985)

    def test_birth_dates_are_classified(self):
        floor = cache.prospect_min_birth_year()
        self.assertTrue(cache.is_prospect_birth_date(f"{floor}-01-01"))
        self.assertTrue(cache.is_prospect_birth_date(None))
        self.assertFalse(cache.is_prospect_birth_date(f"{floor - 1}-12-31"))
        self.assertFalse(cache.is_prospect_birth_date("1916-05-02"))

    @quiet
    def test_upsert_rejects_retired_players(self):
        candidates, by_name = {}, {}

        result = cache.upsert_candidate(
            candidates,
            by_name,
            "8448232",
            "Veli-Pekka Ketola",
            birthDate="1948-03-28",
            source="wikidata",
        )

        self.assertIsNone(result)
        self.assertEqual(candidates, {})

    @quiet
    def test_upsert_accepts_draft_eligible_players(self):
        candidates, by_name = {}, {}

        player_id = cache.upsert_candidate(
            candidates,
            by_name,
            "8484844",
            "Aatos Koivu",
            birthDate="2006-06-22",
            source="draft_picks:2024",
        )

        self.assertEqual(player_id, "8484844")
        self.assertEqual(candidates["8484844"]["sources"], ["draft_picks:2024"])


class MergeGuardTests(unittest.TestCase):
    def setUp(self):
        self.candidates = {}
        self.by_name = {}

    @quiet
    def _upsert(self, player_id, name, birth_date, source):
        return cache.upsert_candidate(
            self.candidates,
            self.by_name,
            player_id,
            name,
            birthDate=birth_date,
            source=source,
        )

    def test_same_player_merges_and_keeps_both_sources(self):
        self._upsert("8480009", "Eeli Tolvanen", "1999-06-18", "draft_picks:2017")
        self._upsert("8480009", "Eeli Tolvanen", "1999-06-18", "wikidata")

        entry = self.candidates["8480009"]
        self.assertEqual(entry["sources"], ["draft_picks:2017", "wikidata"])

    def test_conflicting_name_is_not_merged(self):
        self._upsert("8480009", "Eeli Tolvanen", "1999-06-18", "draft_picks:2017")

        result = self._upsert(
            "8480009", "Eelis Uronen", "2008-08-07", "draft_rankings:2027"
        )

        self.assertIsNone(result)
        entry = self.candidates["8480009"]
        self.assertEqual(entry["name"], "Eeli Tolvanen")
        self.assertEqual(entry["sources"], ["draft_picks:2017"])
        self.assertNotIn("eelis uronen", self.by_name)

    def test_conflicting_birth_date_is_not_merged(self):
        self._upsert("8467369", "Ossi Tukio", "2007-11-03", "draft_picks:2023")

        result = self._upsert(
            "8467369", "Ossi Tukio", "2008-08-13", "draft_rankings:2027"
        )

        self.assertIsNone(result)
        entry = self.candidates["8467369"]
        self.assertEqual(entry["birthDate"], "2007-11-03")
        self.assertEqual(entry["sources"], ["draft_picks:2023"])


class SnapshotGuardTests(unittest.TestCase):
    def test_counts_only_rows_inside_the_window(self):
        players = (
            [{"birthDate": "1948-01-01"}] * 100
            + [{"birthDate": "2005-01-01"}] * 10
            + [{}]
        )

        self.assertEqual(cache.count_prospects_in_window(players), 11)

    def test_rejects_a_collapsed_snapshot(self):
        previous = [{"birthDate": "2005-01-01"} for _ in range(10)]

        with self.assertRaises(SystemExit):
            cache.assert_snapshot_growth(previous[:5], previous)

        cache.assert_snapshot_growth(previous[:6], previous)

    def test_ignores_out_of_window_baseline(self):
        previous = [{"birthDate": "1948-01-01"} for _ in range(100)]

        cache.assert_snapshot_growth([{"birthDate": "2005-01-01"}], previous)


class PlayerIdLookupTests(unittest.TestCase):
    @quiet
    def _lookup(self, rows, name, birth_date=None):
        with patch.object(cache.requests, "get", return_value=FakeResponse(rows)):
            return cache.search_player_id(name, birth_date)

    def test_requires_both_name_and_birth_date(self):
        rows = [
            {"playerId": 1, "name": "Olli Solja", "birthDate": "1923-05-23"},
            {"playerId": 2, "name": "Olli Jokinen", "birthDate": "1978-12-05"},
        ]

        self.assertEqual(self._lookup(rows, "Olli Jokinen", "1978-12-05"), 2)
        self.assertIsNone(self._lookup(rows, "Olli Jokinen", "2008-01-01"))

    def test_refuses_fuzzy_matches(self):
        rows = [{"playerId": 7, "name": "Olli Solja", "birthDate": "1923-05-23"}]

        self.assertIsNone(self._lookup(rows, "Olli Jokinen", "1978-12-05"))
        self.assertIsNone(self._lookup(rows, "Olli Jokinen"))

    def test_accepts_exact_name_without_a_birth_date(self):
        rows = [
            {"playerId": 3, "name": "Olli Solja", "birthDate": "1923-05-23"},
            {"playerId": 4, "name": "Olli Jokinen"},
        ]

        self.assertEqual(self._lookup(rows, "Olli Jokinen", "1978-12-05"), 4)

    def test_no_results_returns_none(self):
        self.assertIsNone(self._lookup([], "Olli Jokinen", "1978-12-05"))
        self.assertIsNone(self._lookup([], "Olli Jokinen"))


if __name__ == "__main__":
    unittest.main()
