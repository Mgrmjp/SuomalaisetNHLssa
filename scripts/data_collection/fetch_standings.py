#!/usr/bin/env python3
"""Collect official standings, preserving the last valid snapshot on failure."""

import argparse
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from utils import fetch_from_api

SOURCE = "https://api-web.nhle.com/v1/standings/now"
OUTPUT = Path(__file__).resolve().parents[2] / "static/data/standings.json"


def build_snapshot(data, now=None):
    now = now or datetime.now(timezone.utc)
    rows = data.get("standings") if isinstance(data, dict) else None
    if not isinstance(rows, list) or len(rows) != 32:
        raise ValueError("Official standings must contain 32 teams")
    teams, seasons, dates, league_ranks = set(), set(), set(), set()
    divisions = {}
    for row in rows:
        team = row.get("teamAbbrev", {}).get("default")
        season, date = row.get("seasonId"), row.get("date")
        conference, division = row.get("conferenceAbbrev"), row.get("divisionAbbrev")
        if not team or team in teams or conference not in ("E", "W"):
            raise ValueError("Invalid or duplicate team")
        if division not in ({"A", "M"} if conference == "E" else {"C", "P"}):
            raise ValueError("Invalid conference/division")
        if not isinstance(season, int) or season % 10000 != season // 10000 + 1:
            raise ValueError("Invalid season")
        datetime.strptime(date, "%Y-%m-%d")
        for key in ("gamesPlayed", "wins", "losses", "otLosses", "points", "goalFor", "goalAgainst"):
            if type(row.get(key)) is not int or row[key] < 0:
                raise ValueError(f"Invalid {key} for {team}")
        if row["gamesPlayed"] != row["wins"] + row["losses"] + row["otLosses"]:
            raise ValueError(f"Inconsistent record for {team}")
        if row["points"] != 2 * row["wins"] + row["otLosses"]:
            raise ValueError(f"Inconsistent points for {team}")
        for key, limit in (("divisionSequence", 8), ("conferenceSequence", 16), ("leagueSequence", 32)):
            if type(row.get(key)) is not int or not 1 <= row[key] <= limit:
                raise ValueError(f"Invalid {key} for {team}")
        divisions.setdefault(division, []).append(row["divisionSequence"])
        league_ranks.add(row["leagueSequence"])
        teams.add(team)
        seasons.add(season)
        dates.add(date)
    if len(seasons) != 1 or len(dates) != 1 or league_ranks != set(range(1, 33)):
        raise ValueError("Mixed seasons, dates, or incomplete rankings")
    if len(divisions) != 4 or any(sorted(ranks) != list(range(1, 9)) for ranks in divisions.values()):
        raise ValueError("Incomplete division rankings")
    for conference in ("E", "W"):
        ranks = sorted(row["conferenceSequence"] for row in rows if row["conferenceAbbrev"] == conference)
        if ranks != list(range(1, 17)):
            raise ValueError("Incomplete conference rankings")
    return {"seasonId": seasons.pop(), "sourceDate": dates.pop(),
            "fetchedAt": now.isoformat().replace("+00:00", "Z"), "source": SOURCE, "standings": rows}


def read_snapshot(path):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return {}


def refresh_snapshot(path=OUTPUT, force=False, now=None, fetcher=fetch_from_api):
    now = now or datetime.now(timezone.utc)
    previous = read_snapshot(path)
    valid_previous = False
    if previous:
        try:
            validated = build_snapshot({"standings": previous["standings"]}, now)
            if any(previous.get(key) != validated[key] for key in ("seasonId", "sourceDate", "source")):
                raise ValueError("Inconsistent snapshot metadata")
            fetched = datetime.fromisoformat(previous["fetchedAt"].replace("Z", "+00:00"))
            valid_previous = True
            if not force and 0 <= (now - fetched).total_seconds() < 3600:
                return False
        except (ValueError, KeyError, TypeError):
            pass
    snapshot = build_snapshot(fetcher(SOURCE), now)
    if valid_previous and (snapshot["seasonId"], snapshot["sourceDate"]) < (previous["seasonId"], previous["sourceDate"]):
        raise ValueError("Refusing to overwrite newer standings with older data")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(snapshot, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        temporary.replace(path)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Refresh even if checked within the last hour")
    args = parser.parse_args()
    updated = False
    try:
        updated = refresh_snapshot(force=args.force)
        print("Official standings refreshed" if updated else "Official standings checked within the last hour")
        return 0
    except Exception as error:
        print(f"Standings refresh failed; previous snapshot preserved: {error}")
        return 1
    finally:
        if "GITHUB_OUTPUT" in os.environ:
            with open(os.environ["GITHUB_OUTPUT"], "a") as stream:
                stream.write(f"updated={'true' if updated else 'false'}\n")


if __name__ == "__main__":
    raise SystemExit(main())
