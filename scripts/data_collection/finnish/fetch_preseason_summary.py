#!/usr/bin/env python3
"""Collect Finnish NHL preseason scoring and final results from official boxscores."""

import json
import sys
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import API_TIMEOUT, DATA_DIR, NHL_API_BASE

ROSTER_FILE = DATA_DIR / "players" / "finnish-roster.json"
OUTPUT_FILE = DATA_DIR / "preseason-summary.json"


def normalize_boxscore(boxscore, roster):
    if boxscore.get("gameType") != 1 or boxscore.get("gameState") not in ("FINAL", "OFF"):
        return None

    away = boxscore["awayTeam"]
    home = boxscore["homeTeam"]
    players = []
    seen_players = set()
    for side, team in (("awayTeam", away["abbrev"]), ("homeTeam", home["abbrev"])):
        stats = boxscore.get("playerByGameStats", {}).get(side, {})
        for group in ("forwards", "defense", "goalies"):
            for player in stats.get(group, []):
                if group == "goalies" and player.get("toi") in (None, "", "0:00", "00:00"):
                    continue
                player_id = player.get("playerId")
                finn = roster.get(str(player_id))
                if not finn or player_id in seen_players:
                    continue
                seen_players.add(player_id)
                goals = int(player.get("goals") or 0)
                assists = int(player.get("assists") or 0)
                players.append({
                    "playerId": player_id,
                    "name": finn["name"],
                    "team": team,
                    "goals": goals,
                    "assists": assists,
                    "points": goals + assists,
                })

    start_time = boxscore["startTimeUTC"]
    period = boxscore.get("periodDescriptor", {})
    players.sort(key=lambda player: (-player["points"], player["name"]))
    return {
        "gameId": boxscore["id"],
        "gameDate": boxscore.get("gameDate") or start_time[:10],
        "startTime": start_time,
        "awayTeam": away["abbrev"],
        "homeTeam": home["abbrev"],
        "awayScore": away["score"],
        "homeScore": home["score"],
        "isOT": period.get("number", 3) > 3,
        "isSO": period.get("periodType") == "SO",
        "finnishPlayers": players,
    }


def summarize_games(games, season_year, regular_start):
    unique_games = {game["gameId"]: game for game in games}
    ordered_games = sorted(unique_games.values(), key=lambda game: game["startTime"], reverse=True)
    scorers = {}
    for game in ordered_games:
        for player in game["finnishPlayers"]:
            player_id = player["playerId"]
            if player_id not in scorers:
                scorers[player_id] = {
                    "playerId": player_id,
                    "name": player["name"],
                    "team": player["team"],
                    "gamesPlayed": 0,
                    "goals": 0,
                    "assists": 0,
                    "points": 0,
                }
            stats = scorers[player_id]
            stats["gamesPlayed"] += 1
            for stat in ("goals", "assists", "points"):
                stats[stat] += player[stat]

    scoring_players = sorted(
        (player for player in scorers.values() if player["points"] > 0),
        key=lambda player: (-player["points"], -player["goals"], player["name"]),
    )
    return {
        "schemaVersion": 2,
        "seasonYear": season_year,
        "regularSeasonStartDate": regular_start,
        "completedGames": len(ordered_games),
        "finnishGames": sum(bool(game["finnishPlayers"]) for game in ordered_games),
        "scorers": scoring_players,
        "games": ordered_games,
    }


def build_preseason_summary(boxscores, roster, season_year, regular_start):
    games = [game for boxscore in boxscores if (game := normalize_boxscore(boxscore, roster))]
    return summarize_games(games, season_year, regular_start)


def get_json(url):
    for attempt in range(4):
        response = requests.get(url, timeout=API_TIMEOUT)
        if response.status_code == 429 and attempt < 3:
            time.sleep(2 ** attempt)
            continue
        response.raise_for_status()
        return response.json()


def fetch_final_preseason_games(season_year):
    overview = get_json(f"{NHL_API_BASE}/v1/schedule/{season_year}-09-01")
    preseason_start = date.fromisoformat(overview["preSeasonStartDate"])
    regular_start = date.fromisoformat(overview["regularSeasonStartDate"])
    games = {}
    cursor = preseason_start
    while cursor < regular_start:
        schedule = get_json(f"{NHL_API_BASE}/v1/schedule/{cursor.isoformat()}")
        for day in schedule.get("gameWeek", []):
            for game in day.get("games", []):
                if game.get("gameType") == 1 and game.get("gameState") in ("FINAL", "OFF"):
                    games[game["id"]] = game
        cursor += timedelta(days=7)
    return preseason_start, regular_start, games


def main():
    now = datetime.now(timezone.utc)
    season_year = now.year if now.month >= 7 else now.year - 1
    with open(ROSTER_FILE, encoding="utf-8") as file:
        roster = json.load(file)

    existing = None
    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE, encoding="utf-8") as file:
            existing = json.load(file)
    if existing and (
        existing.get("seasonYear") != season_year
        or existing.get("schemaVersion") != 2
    ):
        existing = None
    if existing and now.date() > date.fromisoformat(existing["regularSeasonStartDate"]) + timedelta(days=14):
        print("Preseason recap window has ended")
        return 0

    try:
        preseason_start, regular_start, schedule_games = fetch_final_preseason_games(season_year)
    except (requests.RequestException, KeyError, ValueError) as error:
        print(f"Could not fetch NHL preseason schedule: {error}")
        return 1

    if now.date() < preseason_start:
        print("Preseason has not started; keeping the previous summary")
        return 0

    cached_games = {game["gameId"]: game for game in (existing or {}).get("games", [])}
    final_games = []
    try:
        for game_id, game in sorted(schedule_games.items()):
            game_date = game.get("gameDate") or game["startTimeUTC"][:10]
            if game_id in cached_games and game_date < (now.date() - timedelta(days=2)).isoformat():
                final_games.append(cached_games[game_id])
                continue
            boxscore = get_json(f"{NHL_API_BASE}/v1/gamecenter/{game_id}/boxscore")
            normalized = normalize_boxscore(boxscore, roster)
            if not normalized:
                raise ValueError(f"Final game {game_id} has no final boxscore")
            final_games.append(normalized)
            time.sleep(0.4)
    except (requests.RequestException, KeyError, TypeError, ValueError) as error:
        print(f"Could not complete NHL preseason boxscores: {error}")
        return 1

    output = summarize_games(final_games, season_year, regular_start.isoformat())
    if existing and all(existing.get(key) == value for key, value in output.items()):
        print("Preseason summary is unchanged")
        return 0
    output["updatedAt"] = now.isoformat(timespec="seconds").replace("+00:00", "Z")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(output, file, ensure_ascii=False, indent=2)
        file.write("\n")
    print(f"Saved {output['completedGames']} preseason results and {len(output['scorers'])} Finnish scorers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
