#!/usr/bin/env python3
"""
Tests for fetch_offseason_moves.py

Verifies trade/free-agent parsing, Finnish player matching,
deduplication, exclusion rules, and offseason boundaries.

Run: python scripts/data_collection/finnish/test_fetch_offseason_moves.py
"""

import io
import json
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from fetch_offseason_moves import (
    strip_diacritics,
    normalize_name_key,
    team_full_to_abbrev,
    match_player_to_roster,
    is_re_signing,
    is_non_nhl_destination,
    generate_move_id,
    parse_trade_entries,
    parse_free_agent_entries,
    parse_free_agent_departures,
    validate_free_agent_coverage,
    collect_offseason_moves,
    parse_signing_line,
    merge_moves,
    build_output,
    parse_date_prefix,
    extract_signing_links,
    extract_move_date_from_article,
    enrich_free_agent_dates,
)


def make_roster():
    return {
        "8471234": {
            "playerId": 8471234,
            "name": "Joonas Korpisalo",
            "firstName": {"default": "Joonas"},
            "lastName": {"default": "Korpisalo"},
            "position": "G",
            "currentTeam": "BOS",
            "isActive": True,
        },
        "8478123": {
            "playerId": 8478123,
            "name": "Joel Kiviranta",
            "firstName": {"default": "Joel"},
            "lastName": {"default": "Kiviranta"},
            "position": "LW",
            "currentTeam": "COL",
            "isActive": True,
        },
        "8480456": {
            "playerId": 8480456,
            "name": "Kasperi Kapanen",
            "firstName": {"default": "Kasperi"},
            "lastName": {"default": "Kapanen"},
            "position": "RW",
            "currentTeam": "EDM",
            "isActive": True,
        },
        "8475798": {
            "playerId": 8475798,
            "name": "Mikael Granlund",
            "firstName": {"default": "Mikael"},
            "lastName": {"default": "Granlund"},
            "position": "C",
            "currentTeam": "ANA",
            "isActive": True,
        },
        "8480999": {
            "playerId": 8480999,
            "name": "Eeli Tolvanen",
            "firstName": {"default": "Eeli"},
            "lastName": {"default": "Tolvanen"},
            "position": "RW",
            "currentTeam": "SEA",
            "isActive": True,
        },
        "8479000": {
            "playerId": 8479000,
            "name": "Patrik Laine",
            "firstName": {"default": "Patrik"},
            "lastName": {"default": "Laine"},
            "position": "RW",
            "currentTeam": "MTL",
            "isActive": True,
        },
    }


def build_lookups(roster):
    by_last = {}
    by_full = {}
    for pid_str, player in roster.items():
        first = player.get("firstName", {}).get("default", "")
        last = player.get("lastName", {}).get("default", "")
        name = player.get("name", "")
        info = {
            "playerId": player["playerId"],
            "name": name,
            "firstName": first,
            "lastName": last,
            "position": player.get("position", ""),
            "currentTeam": player.get("currentTeam", ""),
            "isActive": player.get("isActive", True),
        }
        last_key = normalize_name_key(last)
        if last_key not in by_last:
            by_last[last_key] = []
        by_last[last_key].append(info)
        full_key = normalize_name_key(name)
        by_full[full_key] = info
    return by_last, by_full


def test_strip_diacritics():
    assert strip_diacritics("Mäkinen") == "Makinen"
    assert strip_diacritics("Hämäläinen") == "Hamalainen"
    assert strip_diacritics("Jokinen") == "Jokinen"
    print("PASSED: strip_diacritics")


def test_normalize_name_key():
    assert normalize_name_key("Korpisalo") == "korpisalo"
    assert normalize_name_key("Joonas Korpisalo") == "joonas korpisalo"
    assert normalize_name_key("Kapanen") == "kapanen"
    assert normalize_name_key("  Smith  ") == "smith"
    print("PASSED: normalize_name_key")


def test_team_full_to_abbrev():
    assert team_full_to_abbrev("New York Rangers") == "NYR"
    assert team_full_to_abbrev("Boston Bruins") == "BOS"
    assert team_full_to_abbrev("Dallas Stars") == "DAL"
    assert team_full_to_abbrev("Utah Mammoth") == "UTA"
    assert team_full_to_abbrev("Unknown Team") is None
    print("PASSED: team_full_to_abbrev")


def test_match_player_exact():
    roster = make_roster()
    by_last, by_full = build_lookups(roster)
    result = match_player_to_roster("Joonas Korpisalo", by_last, by_full)
    assert result is not None
    assert result["playerId"] == 8471234
    print("PASSED: match_player_exact")


def test_match_player_last_name_only():
    roster = make_roster()
    by_last, by_full = build_lookups(roster)
    result = match_player_to_roster("Kiviranta", by_last, by_full)
    assert result is not None
    assert result["playerId"] == 8478123
    print("PASSED: match_player_last_name_only")


def test_match_player_non_finnish_returns_none():
    roster = make_roster()
    by_last, by_full = build_lookups(roster)
    result = match_player_to_roster("Connor McDavid", by_last, by_full)
    assert result is None
    print("PASSED: match_player_non_finnish_returns_none")


def test_match_player_diacritics():
    roster = make_roster()
    by_last, by_full = build_lookups(roster)
    result = match_player_to_roster("Kapanen", by_last, by_full)
    assert result is not None
    assert result["playerId"] == 8480456
    print("PASSED: match_player_diacritics")


def test_is_re_signing():
    player = {"currentTeam": "EDM", "name": "Kasperi Kapanen"}
    assert is_re_signing(player, "EDM") is True
    assert is_re_signing(player, "TOR") is False
    print("PASSED: is_re_signing")


def test_is_non_nhl_destination():
    assert is_non_nhl_destination("signed: HV71, Sweden") is True
    assert is_non_nhl_destination("signs with Dallas Stars") is False
    assert is_non_nhl_destination("signed: AHL") is True
    print("PASSED: is_non_nhl_destination")


def test_parse_date_prefix():
    month, day = parse_date_prefix("JULY 1: Some trade text")
    assert month == 7
    assert day == 1
    month, day = parse_date_prefix("JUNE 28: Another entry")
    assert month == 6
    assert day == 28
    month, day = parse_date_prefix("No date here")
    assert month is None
    assert day is None
    print("PASSED: parse_date_prefix")


def test_parse_trade_korpisalo():
    roster = make_roster()
    by_last, by_full = build_lookups(roster)
    paragraphs = [
        "JULY 1: New York Rangers acquire goalie Joonas Korpisalo from the Boston Bruins for forward Kalle Vaisanen. | Korpisalo traded to Rangers by Bruins"
    ]
    moves = parse_trade_entries(paragraphs, by_last, by_full, "2026-07-02")
    finnish_moves = [m for m in moves if m["player"]["playerId"] == 8471234]
    assert len(finnish_moves) == 1
    move = finnish_moves[0]
    assert move["oldTeam"] == "BOS"
    assert move["newTeam"] == "NYR"
    assert move["moveType"] == "trade"
    assert move["date"] == "2026-07-01"
    print("PASSED: parse_trade_korpisalo")


def test_parse_trade_excludes_non_finnish():
    roster = make_roster()
    by_last, by_full = build_lookups(roster)
    paragraphs = [
        "JULY 1: Detroit Red Wings acquire forward Keegan Kolesar from the Vegas Golden Knights for a 3rd-round pick in the 2029 NHL Draft."
    ]
    moves = parse_trade_entries(paragraphs, by_last, by_full, "2026-07-02")
    assert len(moves) == 0
    print("PASSED: parse_trade_excludes_non_finnish")


def test_parse_signing_line_single():
    names = parse_signing_line(
        "Kiviranta signs 1-year contract with Stars", "DAL"
    )
    assert "Kiviranta" in names
    print("PASSED: parse_signing_line_single")


def test_parse_signing_line_grouped():
    names = parse_signing_line(
        "Hyry, Shlaine, Halverson each signs contract with Stars", "DAL"
    )
    assert "Hyry" in names
    assert "Shlaine" in names
    assert "Halverson" in names
    print("PASSED: parse_signing_line_grouped")


def test_parse_free_agent_kiviranta():
    roster = make_roster()
    by_last, by_full = build_lookups(roster)
    paragraphs = [
        "DALLAS STARS",
        "Signings",
        "Kiviranta signs 1-year contract with Stars",
        "Hyry, Shlaine, Halverson each signs contract with Stars",
        "Free agents",
        "Group 3 Unrestricted Free Agents: Nathan Bastian, Jamie Benn",
    ]
    moves = parse_free_agent_entries(paragraphs, by_last, by_full, "2026-07-02")
    finnish_moves = [m for m in moves if m["player"]["playerId"] == 8478123]
    assert len(finnish_moves) == 1
    move = finnish_moves[0]
    assert move["oldTeam"] == "COL"
    assert move["newTeam"] == "DAL"
    assert move["moveType"] == "free_agent"
    print("PASSED: parse_free_agent_kiviranta")


def test_parse_free_agent_excludes_re_signing():
    roster = make_roster()
    by_last, by_full = build_lookups(roster)
    paragraphs = [
        "EDMONTON OILERS",
        "Signings",
        "Kapanen signs 1-year contract with Oilers",
        "Free agents",
        "Group 3 Unrestricted Free Agents: Kasperi Kapanen (re-signed)",
    ]
    moves = parse_free_agent_entries(paragraphs, by_last, by_full, "2026-07-02")
    finnish_moves = [m for m in moves if m["player"]["playerId"] == 8480456]
    assert len(finnish_moves) == 0
    print("PASSED: parse_free_agent_excludes_re_signing")


def test_free_agent_move_survives_roster_refresh():
    paragraphs = [
        "NEW YORK RANGERS",
        "Signings",
        "Tolvanen signs 1-year contract with Rangers",
        "Free agents",
        "SEATTLE KRAKEN",
        "Free agents",
        "Group 3 Unrestricted Free Agents: Eeli Tolvanen (signed: NYR).",
    ]
    identities = set()
    for cached_team in ["SEA", "NYR", "", "NSH"]:
        roster = make_roster()
        roster["8480999"]["currentTeam"] = cached_team
        by_last, by_full = build_lookups(roster)
        moves = parse_free_agent_entries(paragraphs, by_last, by_full, "2026-09-02")
        assert len(moves) == 1, f"Missing move with cached team {cached_team!r}"
        move = moves[0]
        assert (move["oldTeam"], move["newTeam"]) == ("SEA", "NYR")
        assert validate_free_agent_coverage(paragraphs, moves, by_last, by_full)
        identities.add(generate_move_id(
            move["player"]["playerId"], move["moveType"],
            move["oldTeam"], move["newTeam"],
        ))
    assert len(identities) == 1
    print("PASSED: free_agent_move_survives_roster_refresh")


def test_free_agent_departure_must_match_signing_destination():
    roster = make_roster()
    roster["8480999"]["currentTeam"] = "NYR"
    by_last, by_full = build_lookups(roster)
    paragraphs = [
        "NEW YORK RANGERS", "Signings",
        "Tolvanen signs 1-year contract with Rangers", "Free agents",
        "SEATTLE KRAKEN", "Free agents", "Eeli Tolvanen (signed: NSH).",
    ]
    assert parse_free_agent_entries(paragraphs, by_last, by_full, "2026-09-02") == []
    print("PASSED: free_agent_departure_must_match_signing_destination")


def test_collector_flags_unparsed_confirmed_signing():
    # A changed signing headline must not silently erase the confirmed departure.
    html = """
      <h2>NEW YORK RANGERS</h2><h3>Signings</h3>
      <p>Tolvanen agrees to terms with Rangers</p>
      <h3>Free agents</h3><h2>SEATTLE KRAKEN</h2><h3>Free agents</h3>
      <p>Eeli Tolvanen (signed: NYR), Connor McDavid (signed: DAL).</p>
    """
    roster = make_roster()
    by_last, by_full = build_lookups(roster)
    logs = io.StringIO()
    with (
        patch("fetch_offseason_moves.build_roster_lookup", return_value=(roster, by_last, by_full)),
        patch("fetch_offseason_moves.fetch_page_html", side_effect=["<p>No trades</p>", html]),
        patch("fetch_offseason_moves.load_existing_moves", return_value={
            "offseasonYear": 2026,
            "moves": [{"playerId": "8480999", "moveType": "free_agent",
                       "oldTeam": "SEA", "newTeam": "NYR", "date": "2026-09-02"}],
        }),
        patch("fetch_offseason_moves.get_offseason_window", return_value={}),
        patch("fetch_offseason_moves.save_output") as save,
        redirect_stdout(logs),
    ):
        assert collect_offseason_moves() is False
    output = save.call_args.args[0]
    assert output["sourceStatus"]["freeAgentTracker"] == "error"
    assert len(output["moves"]) == 1  # Retain already recorded history.
    assert "::warning::Unparsed Finnish signing: Eeli Tolvanen SEA -> NYR" in logs.getvalue()
    assert "Connor McDavid" not in logs.getvalue()
    print("PASSED: collector_flags_unparsed_confirmed_signing")


def test_parse_free_agent_excludes_non_nhl():
    roster = make_roster()
    by_last, by_full = build_lookups(roster)
    paragraphs = [
        "SOME TEAM",
        "Signings",
        "Kiviranta signs contract with team in Sweden",
        "Free agents",
    ]
    moves = parse_free_agent_entries(paragraphs, by_last, by_full, "2026-07-02")
    assert len(moves) == 0
    print("PASSED: parse_free_agent_excludes_non_nhl")


def test_parse_free_agent_departures():
    paragraphs = [
        "COLORADO AVALANCHE",
        "Free agents",
        "Group 3 Unrestricted Free Agents: Joel Kiviranta (signed: DAL), Jacob MacDonald",
    ]
    lookup = parse_free_agent_departures(paragraphs)
    key = normalize_name_key("Joel Kiviranta")
    assert lookup.get(key) == {"oldTeam": "COL", "newTeam": "DAL"}
    print("PASSED: parse_free_agent_departures")


def test_generate_move_id_stable():
    id1 = generate_move_id("8471234", "trade", "BOS", "NYR")
    id2 = generate_move_id("8471234", "trade", "BOS", "NYR")
    assert id1 == id2
    id3 = generate_move_id("8471234", "trade", "BOS", "DAL")
    assert id1 != id3
    print("PASSED: generate_move_id_stable")


def test_merge_moves_deduplication():
    existing = {
        "offseasonYear": 2026,
        "moves": [
            {
                "moveId": "old-date-based-id",
                "playerId": "8471234",
                "playerName": "Joonas Korpisalo",
                "oldTeam": "BOS",
                "newTeam": "NYR",
                "moveType": "trade",
                "date": "2026-07-03",
            }
        ],
    }
    new_moves = [
        {
            "moveId": "stable-id",
            "playerId": "8471234",
            "playerName": "Joonas Korpisalo",
            "oldTeam": "BOS",
            "newTeam": "NYR",
            "moveType": "trade",
            "date": "2026-07-01",
            "sourceUrl": "https://nhl.com",
        }
    ]
    merged = merge_moves(existing, new_moves, 2026)
    assert len(merged) == 1
    assert merged[0].get("sourceUrl") == "https://nhl.com"
    assert merged[0]["date"] == "2026-07-01"
    print("PASSED: merge_moves_deduplication")


def test_extract_signing_links():
    html = """
    <a href="/news/joel-kiviranta-signs-with-stars">
      Kiviranta signs 1-year contract with Stars
    </a>
    """
    links = extract_signing_links(html)
    assert links["kiviranta signs 1-year contract with stars"] == (
        "https://www.nhl.com/news/joel-kiviranta-signs-with-stars"
    )
    print("PASSED: extract_signing_links")


def test_article_date_uses_weekday_before_publish_date():
    html = """
    <article>
      <p>Joel Kiviranta signed a one-year contract with Dallas on Wednesday.</p>
    </article>
    """
    date = extract_move_date_from_article(
        html, "Joel Kiviranta", "2026-07-02", 2026
    )
    assert date == "2026-07-01"
    print("PASSED: article_date_uses_weekday_before_publish_date")


def test_article_date_uses_explicit_transaction_date():
    html = """
    <article>
      <p>VEGAS (July 1, 2026): The team announced today, July 1, the following roster transactions.</p>
      <p>The team agreed to terms with defenseman Ville Heinola.</p>
    </article>
    """
    date = extract_move_date_from_article(
        html, "Ville Heinola", "2026-07-02", 2026
    )
    assert date == "2026-07-01"
    print("PASSED: article_date_uses_explicit_transaction_date")


def test_enrich_free_agent_dates_uses_linked_article():
    roster = make_roster()
    by_last, by_full = build_lookups(roster)
    tracker_html = """
    <h2>DALLAS STARS</h2>
    <h5>Signings</h5>
    <a href="/news/joel-kiviranta-signs-with-stars">Kiviranta signs 1-year contract with Stars</a>
    """
    paragraphs = [
        "DALLAS STARS",
        "Signings",
        "Kiviranta signs 1-year contract with Stars",
    ]
    moves = parse_free_agent_entries(
        paragraphs, by_last, by_full, "2026-07-03"
    )
    article_html = """
    <script type="application/ld+json">{"datePublished":"2026-07-02T12:00:00Z"}</script>
    <p>Joel Kiviranta signed a one-year contract with Dallas on Wednesday.</p>
    """
    enriched = enrich_free_agent_dates(
        moves, tracker_html, 2026, fetcher=lambda _url: article_html
    )
    assert enriched[0]["date"] == "2026-07-01"
    assert enriched[0]["sourceUrl"].endswith(
        "/news/joel-kiviranta-signs-with-stars"
    )
    print("PASSED: enrich_free_agent_dates_uses_linked_article")


def test_merge_moves_adds_new():
    existing = {
        "offseasonYear": 2026,
        "moves": [
            {
                "moveId": "abc123",
                "playerId": "8471234",
                "playerName": "Joonas Korpisalo",
                "oldTeam": "BOS",
                "newTeam": "NYR",
                "moveType": "trade",
                "date": "2026-07-01",
            }
        ],
    }
    new_moves = [
        {
            "moveId": "def456",
            "playerId": "8478123",
            "playerName": "Joel Kiviranta",
            "oldTeam": "COL",
            "newTeam": "DAL",
            "moveType": "free_agent",
            "date": "2026-07-01",
        }
    ]
    merged = merge_moves(existing, new_moves, 2026)
    assert len(merged) == 2
    print("PASSED: merge_moves_adds_new")


def test_build_output_structure():
    moves = [
        {
            "moveId": "abc123",
            "playerId": "8471234",
            "playerName": "Joonas Korpisalo",
            "moveType": "trade",
            "date": "2026-07-01",
        }
    ]
    with patch("fetch_offseason_moves.get_offseason_window", return_value={
        "start": "2026-06-20", "end": "2026-10-06",
    }):
        output = build_output(2026, moves, {"tradeTracker": "ok", "freeAgentTracker": "ok"})
    assert output["offseasonYear"] == 2026
    assert "window" in output
    assert "start" in output["window"]
    assert "end" in output["window"]
    assert "updatedAt" in output
    assert output["sourceStatus"]["tradeTracker"] == "ok"
    assert len(output["moves"]) == 1
    print("PASSED: build_output_structure")


def test_source_date_fallback():
    roster = make_roster()
    by_last, by_full = build_lookups(roster)
    paragraphs = [
        "Some text without a date prefix: New York Rangers acquire goalie Joonas Korpisalo from the Boston Bruins for forward Kalle Vaisanen."
    ]
    moves = parse_trade_entries(paragraphs, by_last, by_full, "2026-07-02")
    finnish_moves = [m for m in moves if m["player"]["playerId"] == 8471234]
    assert len(finnish_moves) == 1
    assert finnish_moves[0]["date"] == "2026-07-02"
    print("PASSED: source_date_fallback")


if __name__ == "__main__":
    print("Running fetch_offseason_moves tests...")
    print()
    test_strip_diacritics()
    test_normalize_name_key()
    test_team_full_to_abbrev()
    test_match_player_exact()
    test_match_player_last_name_only()
    test_match_player_non_finnish_returns_none()
    test_match_player_diacritics()
    test_is_re_signing()
    test_is_non_nhl_destination()
    test_parse_date_prefix()
    test_parse_trade_korpisalo()
    test_parse_trade_excludes_non_finnish()
    test_parse_signing_line_single()
    test_parse_signing_line_grouped()
    test_parse_free_agent_kiviranta()
    test_parse_free_agent_excludes_re_signing()
    test_free_agent_move_survives_roster_refresh()
    test_free_agent_departure_must_match_signing_destination()
    test_collector_flags_unparsed_confirmed_signing()
    test_parse_free_agent_excludes_non_nhl()
    test_parse_free_agent_departures()
    test_generate_move_id_stable()
    test_merge_moves_deduplication()
    test_extract_signing_links()
    test_article_date_uses_weekday_before_publish_date()
    test_article_date_uses_explicit_transaction_date()
    test_enrich_free_agent_dates_uses_linked_article()
    test_merge_moves_adds_new()
    test_build_output_structure()
    test_source_date_fallback()
    print()
    print("All tests passed!")
