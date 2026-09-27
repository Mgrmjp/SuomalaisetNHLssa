#!/usr/bin/env python3
"""Build a short regular-season schedule teaser from the NHL schedule and Finnish roster."""

import json
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import API_TIMEOUT, DATA_DIR, NHL_API_BASE

ROSTER_FILE = DATA_DIR / "players" / "finnish-roster.json"
OUTPUT_FILE = DATA_DIR / "upcoming-finnish-games.json"


def build_upcoming_games(schedule_weeks, roster, current_roster_ids, now, limit=8):
    finnish_players = {
        int(player_id): player["name"]
        for player_id, player in roster.items()
        if player.get("name")
    }
    players_by_team = {}
    for team, ids in current_roster_ids.items():
        players_by_team[team] = sorted(
            finnish_players[player_id]
            for player_id in ids
            if player_id in finnish_players
        )

    games_by_id = {}
    for week in schedule_weeks:
        for game in week:
            if game.get("gameType") != 2 or game.get("gameState") not in ("FUT", "PRE"):
                continue
            try:
                start = datetime.fromisoformat(game["startTimeUTC"].replace("Z", "+00:00"))
                away = game["awayTeam"]["abbrev"]
                home = game["homeTeam"]["abbrev"]
                game_id = int(game["id"])
            except (KeyError, TypeError, ValueError):
                continue
            if start <= now or not (players_by_team.get(away) or players_by_team.get(home)):
                continue

            players = [
                {"name": name, "team": team}
                for team in (away, home)
                for name in sorted(players_by_team.get(team, []))
            ]
            games_by_id[game_id] = {
                "gameId": game_id,
                "startTime": game["startTimeUTC"],
                "awayTeam": away,
                "homeTeam": home,
                "finnishPlayers": players,
            }

    return sorted(games_by_id.values(), key=lambda game: game["startTime"])[:limit]


def fetch_schedule_weeks(today):
    weeks = []
    for offset in (0, 7):
        date = (today + timedelta(days=offset)).isoformat()
        response = requests.get(f"{NHL_API_BASE}/v1/schedule/{date}", timeout=API_TIMEOUT)
        response.raise_for_status()
        game_week = response.json().get("gameWeek")
        if not isinstance(game_week, list):
            raise ValueError(f"NHL schedule has no gameWeek for {date}")
        weeks.extend(day.get("games", []) for day in game_week)
    return weeks


def fetch_current_roster_ids(schedule_weeks, finnish_ids, now, limit=8, getter=requests.get):
    rosters = {}
    games = sorted(
        (game for week in schedule_weeks for game in week),
        key=lambda game: game.get("startTimeUTC", ""),
    )
    seen_games = set()
    found = 0
    for game in games:
        if game.get("gameType") != 2 or game.get("gameState") not in ("FUT", "PRE"):
            continue
        try:
            start = datetime.fromisoformat(game["startTimeUTC"].replace("Z", "+00:00"))
            teams = [game[side]["abbrev"] for side in ("awayTeam", "homeTeam")]
        except (KeyError, TypeError, ValueError):
            continue
        if start <= now:
            continue
        if game.get("id") in seen_games:
            continue
        seen_games.add(game.get("id"))

        for team in teams:
            if team in rosters:
                continue
            if rosters:
                time.sleep(0.25)
            for attempt in range(3):
                response = getter(f"{NHL_API_BASE}/v1/roster/{team}/current", timeout=API_TIMEOUT)
                if response.status_code == 429 and attempt < 2:
                    time.sleep(2 ** attempt)
                    continue
                response.raise_for_status()
                break
            data = response.json()
            if not all(isinstance(data.get(group), list) for group in ("forwards", "defensemen", "goalies")):
                raise ValueError(f"NHL roster has missing player groups for {team}")
            rosters[team] = {
                player["id"]
                for group in ("forwards", "defensemen", "goalies")
                for player in data[group]
                if isinstance(player.get("id"), int)
            }
        if any(rosters[team] & finnish_ids for team in teams):
            found += 1
            if found >= limit:
                break
    return rosters


def main():
    now = datetime.now(timezone.utc)
    with open(ROSTER_FILE, encoding="utf-8") as file:
        roster = json.load(file)

    try:
        schedule_weeks = fetch_schedule_weeks(now.date())
        current_roster_ids = fetch_current_roster_ids(
            schedule_weeks, {int(player_id) for player_id in roster}, now
        )
    except (requests.RequestException, ValueError) as error:
        print(f"Could not fetch upcoming NHL schedule or rosters: {error}")
        return 1

    games = build_upcoming_games(schedule_weeks, roster, current_roster_ids, now)
    output = {"updatedAt": now.isoformat(timespec="seconds").replace("+00:00", "Z"), "games": games}
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(output, file, ensure_ascii=False, indent=2)
        file.write("\n")
    print(f"Saved {len(games)} upcoming games with Finns to {OUTPUT_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
