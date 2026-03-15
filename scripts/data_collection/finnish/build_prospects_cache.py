#!/usr/bin/env python3
"""
Build Finnish prospects cache from multiple NHL API sources.

Sources:
1) Team prospect lists
2) Historical draft classes
3) Draft rankings (NA/INT skaters + goalies)
"""

import requests
import time
import sys
import os
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import DATA_DIR
from utils import save_json

# NHL API endpoints
NHL_API_BASE = "https://api-web.nhle.com"
NHL_SEARCH_API = "https://search.d3.nhle.com/api/v1/search/player"
PROSPECTS_CACHE_FILE = DATA_DIR / "finnish_prospects.json"
CURRENT_SEASON_ID = 20252026
EXTERNAL_PROSPECTS_FILE = DATA_DIR / "external_prospects.json"
LEAGUE_PROSPECTS_FILES = (
    DATA_DIR / "leagues" / "league_prospects_official.json",
    DATA_DIR / "leagues" / "league_prospects_advanced.json",
    DATA_DIR / "leagues" / "league_prospects_na.json",
)
THE_SPORTS_DB_BASE = "https://www.thesportsdb.com/api/v1/json"
WIKIDATA_SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"


def fetch_from_api(url, max_retries=3):
    """Fetch data from NHL API with retry logic"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                print(f"Error fetching {url}: {e}")
                return None
            time.sleep(1)
    return None


def normalize_name(name):
    """Normalize full names for stable matching."""
    return " ".join((name or "").strip().lower().split())


def normalize_person_name(name):
    """Normalize person names and collapse Last, First / First Last into a shared key."""
    normalized = normalize_name(name)
    if not normalized:
        return ""

    cleaned = normalized.replace("*", "").strip()
    if "," in cleaned:
        parts = [part.strip() for part in cleaned.split(",") if part.strip()]
        if len(parts) >= 2:
            cleaned = " ".join(parts[1:] + [parts[0]])

    return " ".join(cleaned.split())


def get_name(first_name, last_name):
    """Handle NHL name fields that may be dicts or plain strings."""
    first = first_name.get("default") if isinstance(first_name, dict) else first_name
    last = last_name.get("default") if isinstance(last_name, dict) else last_name
    return f"{first or ''} {last or ''}".strip()


def _append_source(player_obj, source):
    sources = player_obj.setdefault("sources", [])
    if source and source not in sources:
        sources.append(source)


def upsert_candidate(candidates, by_name, player_id, name, **fields):
    """Insert or merge candidate player data by id/name."""
    normalized = normalize_person_name(name)
    if not normalized:
        return None

    effective_id = player_id or by_name.get(normalized)
    if effective_id is not None:
        effective_id = str(effective_id)
    if not effective_id:
        return None

    if effective_id not in candidates:
        candidates[effective_id] = {"id": effective_id, "name": name}

    target = candidates[effective_id]
    if name and not target.get("name"):
        target["name"] = name

    for key, value in fields.items():
        if key == "source":
            _append_source(target, value)
            continue
        if value is not None and value != "" and not target.get(key):
            target[key] = value

    by_name[normalized] = effective_id
    return effective_id


def dedupe_final_players(players):
    """Collapse duplicate final player rows caused by mixed int/string ids."""
    deduped = {}

    for player in players:
        player_id = player.get("id")
        if player_id is not None:
            player["id"] = str(player_id)

        key = str(player.get("id") or "") or f"{normalize_person_name(player.get('name'))}:{player.get('birthDate') or ''}"
        existing = deduped.get(key)
        if not existing:
            deduped[key] = player
            continue

        existing_sources = existing.get("sources") or []
        current_sources = player.get("sources") or []

        if len(current_sources) > len(existing_sources):
            deduped[key] = player
            existing = deduped[key]

        merged_sources = []
        for source in [*(existing.get("sources") or []), *current_sources]:
            if source and source not in merged_sources:
                merged_sources.append(source)
        existing["sources"] = merged_sources

        if not existing.get("headshot") and player.get("headshot"):
            existing["headshot"] = player["headshot"]
        if not existing.get("headshotCrop") and player.get("headshotCrop"):
            existing["headshotCrop"] = player["headshotCrop"]

    return list(deduped.values())


def get_all_teams():
    """Get list of all active NHL team abbreviations"""
    url = f"{NHL_API_BASE}/v1/standings/now"
    data = fetch_from_api(url)
    teams = []
    if data and "standings" in data:
        for record in data["standings"]:
            teams.append(record.get("teamAbbrev", {}).get("default"))
    return sorted(list(set(filter(None, teams))))


def get_team_prospects(team_abbr):
    """Get prospects for a specific team"""
    url = f"{NHL_API_BASE}/v1/prospects/{team_abbr}"
    return fetch_from_api(url)


def get_player_landing(player_id):
    """Get detailed player info including current stats"""
    url = f"{NHL_API_BASE}/v1/player/{player_id}/landing"
    return fetch_from_api(url)


def normalize_season_stats(stats_list):
    """Extract the most relevant recent season stats."""
    if not stats_list:
        return None

    current_season = str(CURRENT_SEASON_ID)

    for season in stats_list:
        if str(season.get("season")) == current_season:
            return season

    return stats_list[-1] if stats_list else None


def get_draft_class(year):
    """Fetch all players drafted in a specific year."""
    url = f"{NHL_API_BASE}/v1/draft/picks/{year}/all"
    return fetch_from_api(url)


def get_draft_rankings(year, category_id):
    """Fetch draft rankings for a specific year/category."""
    url = f"{NHL_API_BASE}/v1/draft/rankings/{year}/{category_id}"
    return fetch_from_api(url)


def search_player_id(name, birth_date=None):
    """Search player id by name using NHL search API with basic disambiguation."""
    params = {
        "culture": "en-us",
        "limit": 25,
        "q": name,
    }
    try:
        r = requests.get(NHL_SEARCH_API, params=params, timeout=8)
        if r.status_code == 200:
            data = r.json()
            if not data:
                return None

            target_name = normalize_name(name)

            def row_name(row):
                full = row.get("name")
                if full:
                    return normalize_name(full)
                return normalize_name(f"{row.get('firstName', '')} {row.get('lastName', '')}")

            exact_name = [row for row in data if row_name(row) == target_name]
            pool = exact_name or data

            if birth_date:
                birth_match = [
                    row for row in pool
                    if str(row.get("birthDate", "")).startswith(str(birth_date))
                ]
                if birth_match:
                    return birth_match[0].get("playerId")

            return pool[0].get("playerId")
    except Exception as e:
        print(f"Error searching for {name}: {e}")
    return None


def ingest_eliteprospects(candidates, by_name):
    """
    Optionally ingest Finnish players from EliteProspects API.
    Requires ELITEPROSPECTS_API_KEY.
    """
    api_key = os.getenv("ELITEPROSPECTS_API_KEY", "").strip()
    if not api_key:
        print("EliteProspects API key not provided, skipping EP ingestion")
        return 0

    # Keep this configurable because EP endpoint/version may vary by account.
    endpoint = os.getenv("ELITEPROSPECTS_PLAYERS_URL", "https://api.eliteprospects.com/v1/players")
    params = {
        "nationality": os.getenv("ELITEPROSPECTS_NATIONALITY", "FIN"),
        "limit": int(os.getenv("ELITEPROSPECTS_LIMIT", "500")),
    }
    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        r = requests.get(endpoint, headers=headers, params=params, timeout=20)
        r.raise_for_status()
        payload = r.json()
    except Exception as e:
        print(f"EliteProspects fetch failed: {e}")
        return 0

    rows = payload.get("data") or payload.get("players") or payload.get("results") or []
    added = 0
    for row in rows:
        full_name = (
            row.get("name")
            or get_name(row.get("firstName"), row.get("lastName"))
            or get_name(row.get("first_name"), row.get("last_name"))
        )
        if not full_name:
            continue

        birth_date = row.get("birthDate") or row.get("birth_date")
        nhl_id = row.get("nhlPlayerId") or row.get("nhl_player_id")
        if not nhl_id:
            nhl_id = search_player_id(full_name, birth_date)
        if not nhl_id:
            continue

        before = len(candidates)
        upsert_candidate(
            candidates,
            by_name,
            nhl_id,
            full_name,
            birthDate=birth_date,
            currentTeam=row.get("team") or row.get("currentTeam"),
            league=row.get("league"),
            source="eliteprospects",
        )
        if len(candidates) > before:
            added += 1

    print(f"Added {added} candidates from EliteProspects")
    return added


def ingest_external_file(candidates, by_name):
    """
    Optionally ingest additional players from local file:
    static/data/external_prospects.json

    Expected rows: [{\"name\": \"...\", \"birthDate\": \"YYYY-MM-DD\", \"nhlRights\": \"...\"}, ...]
    """
    if not EXTERNAL_PROSPECTS_FILE.exists():
        print(f"No external prospects file at {EXTERNAL_PROSPECTS_FILE}, skipping")
        return 0

    try:
        import json
        rows = json.loads(EXTERNAL_PROSPECTS_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Failed to parse {EXTERNAL_PROSPECTS_FILE}: {e}")
        return 0

    if not isinstance(rows, list):
        print(f"External prospects file must be a list, got {type(rows)}")
        return 0

    added = 0
    for row in rows:
        full_name = row.get("name")
        if not full_name:
            continue
        birth_date = row.get("birthDate")
        nhl_id = row.get("id") or row.get("nhlPlayerId") or search_player_id(full_name, birth_date)
        if not nhl_id:
            continue

        before = len(candidates)
        upsert_candidate(
            candidates,
            by_name,
            nhl_id,
            full_name,
            birthDate=birth_date,
            nhlRights=row.get("nhlRights"),
            currentTeam=row.get("currentTeam"),
            league=row.get("league"),
            source="external_file",
        )
        if len(candidates) > before:
            added += 1

    print(f"Added {added} candidates from external file")
    return added


def ingest_league_prospects_files(candidates, by_name):
    """Merge non-NHL league prospect photos and metadata from generated JSON files."""
    import json

    added = 0
    merged = 0

    for source_file in LEAGUE_PROSPECTS_FILES:
        if not source_file.exists():
            print(f"No league prospects file at {source_file}, skipping")
            continue

        try:
            payload = json.loads(source_file.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"Failed to parse {source_file}: {e}")
            continue

        rows = payload.get("players") if isinstance(payload, dict) else payload
        if not isinstance(rows, list):
            continue

        for row in rows:
            if not isinstance(row, dict):
                continue

            full_name = row.get("name")
            if not full_name:
                continue

            normalized_name = normalize_person_name(full_name)
            candidate_id = by_name.get(normalized_name)

            if not candidate_id:
                nhl_id = search_player_id(full_name)
                if nhl_id:
                    candidate_id = str(nhl_id)

            if not candidate_id:
                continue

            before = len(candidates)
            result_id = upsert_candidate(
                candidates,
                by_name,
                candidate_id,
                full_name,
                currentTeam=row.get("team"),
                league=row.get("league"),
                headshot=row.get("headshot_url") or row.get("headshotUrl") or row.get("headshot") or row.get("image"),
                headshotCrop=row.get("headshot_crop") or row.get("headshotCrop"),
                source=f"league_file:{source_file.stem}",
            )

            if result_id and len(candidates) > before:
                added += 1
            elif result_id:
                merged += 1

    print(f"Merged league prospect data: {merged} existing, {added} new")
    return added + merged


def ingest_the_sports_db(candidates, by_name):
    """
    Optionally ingest players from TheSportsDB free API (key 123 by default).
    Scans configured leagues -> teams -> players.
    """
    key = os.getenv("THE_SPORTS_DB_KEY", "123").strip()
    leagues = [
        league.strip() for league in os.getenv(
            "THE_SPORTS_DB_LEAGUES",
            "NHL,Liiga,SHL,AHL,OHL,WHL,QMJHL,NCAA Hockey",
        ).split(",")
        if league.strip()
    ]
    max_teams = int(os.getenv("THE_SPORTS_DB_MAX_TEAMS", "400"))

    team_ids = []
    for league_name in leagues:
        url = f"{THE_SPORTS_DB_BASE}/{key}/search_all_teams.php"
        try:
            r = requests.get(url, params={"l": league_name}, timeout=20)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            print(f"TheSportsDB teams fetch failed for {league_name}: {e}")
            continue

        for team in data.get("teams") or []:
            team_id = team.get("idTeam")
            if team_id:
                team_ids.append(team_id)

    # dedupe while preserving order
    seen = set()
    ordered_team_ids = []
    for tid in team_ids:
        if tid not in seen:
            seen.add(tid)
            ordered_team_ids.append(tid)
    ordered_team_ids = ordered_team_ids[:max_teams]

    added = 0
    for team_id in ordered_team_ids:
        players_url = f"{THE_SPORTS_DB_BASE}/{key}/lookup_all_players.php"
        try:
            r = requests.get(players_url, params={"id": team_id}, timeout=20)
            r.raise_for_status()
            payload = r.json()
        except Exception:
            continue

        for row in payload.get("player") or []:
            nationality = (row.get("strNationality") or "").upper()
            if "FINLAND" not in nationality and nationality != "FIN":
                continue

            full_name = row.get("strPlayer")
            if not full_name:
                continue

            birth_date = row.get("dateBorn")
            nhl_id = search_player_id(full_name, birth_date)
            if not nhl_id:
                continue

            before = len(candidates)
            upsert_candidate(
                candidates,
                by_name,
                nhl_id,
                full_name,
                birthDate=birth_date,
                position=row.get("strPosition"),
                currentTeam=row.get("strTeam"),
                league=row.get("strLeague"),
                source="thesportsdb",
            )
            if len(candidates) > before:
                added += 1

    print(f"Added {added} candidates from TheSportsDB")
    return added


def ingest_wikidata(candidates, by_name):
    """
    Optionally ingest Finnish ice hockey players from Wikidata SPARQL.
    """
    limit = int(os.getenv("WIKIDATA_MAX_ROWS", "500"))
    query = f"""
SELECT ?playerLabel ?dob WHERE {{
  ?player wdt:P31 wd:Q5;
          wdt:P106 wd:Q11774891;
          wdt:P27 wd:Q33.
  OPTIONAL {{ ?player wdt:P569 ?dob. }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en,fi". }}
}}
LIMIT {limit}
"""
    headers = {
        "Accept": "application/sparql-results+json",
        "User-Agent": "suomalaisetnhlssa-prospects/1.0 (data pipeline)",
    }

    try:
        r = requests.get(
            WIKIDATA_SPARQL_ENDPOINT,
            params={"format": "json", "query": query},
            headers=headers,
            timeout=30,
        )
        r.raise_for_status()
        payload = r.json()
    except Exception as e:
        print(f"Wikidata query failed: {e}")
        return 0

    rows = payload.get("results", {}).get("bindings", [])
    added = 0
    for row in rows:
        full_name = row.get("playerLabel", {}).get("value")
        if not full_name:
            continue
        dob_raw = row.get("dob", {}).get("value", "")
        birth_date = dob_raw[:10] if dob_raw else None
        nhl_id = search_player_id(full_name, birth_date)
        if not nhl_id:
            continue

        before = len(candidates)
        upsert_candidate(
            candidates,
            by_name,
            nhl_id,
            full_name,
            birthDate=birth_date,
            source="wikidata",
        )
        if len(candidates) > before:
            added += 1

    print(f"Added {added} candidates from Wikidata")
    return added


def main():
    print("Building Finnish prospects cache...")
    print("=" * 60)

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    finnish_prospects = {}
    prospects_by_name = {}

    # 1) Team prospect lists
    teams = get_all_teams()
    print(f"Scanning {len(teams)} teams for Finnish prospects...")

    for i, team in enumerate(teams, 1):
        print(f"[{i}/{len(teams)}] Checking {team}...", end=" ")

        prospects_data = get_team_prospects(team)
        if not prospects_data:
            print("Failed to fetch")
            continue

        team_finnish_count = 0

        for category in ["forwards", "defensemen", "goalies"]:
            for player in prospects_data.get(category, []):
                if player.get("birthCountry") == "FIN":
                    player_id = player.get("id")
                    full_name = get_name(player.get("firstName"), player.get("lastName"))

                    upsert_candidate(
                        finnish_prospects,
                        prospects_by_name,
                        player_id,
                        full_name,
                        nhlRights=team,
                        position=player.get("positionCode"),
                        headshot=player.get("headshot"),
                        height=player.get("heightInCentimeters"),
                        weight=player.get("weightInKilograms"),
                        birthDate=player.get("birthDate"),
                        source=f"team_prospects:{team}",
                    )
                    team_finnish_count += 1

        print(f"Found {team_finnish_count}")
        time.sleep(0.1)

    # 2) Draft history
    current_year = datetime.now().year
    draft_start_year = max(2005, current_year - 10)
    draft_years = range(draft_start_year, current_year + 1)

    print(f"\nScanning Draft History ({draft_years[0]}-{draft_years[-1]}) for missing prospects...")

    for year in draft_years:
        print(f"Checking Draft {year}...", end=" ")
        draft_data = get_draft_class(year)

        year_count = 0
        if draft_data and "picks" in draft_data:
            for pick in draft_data["picks"]:
                if pick.get("countryCode") != "FIN":
                    continue

                full_name = get_name(pick.get("firstName"), pick.get("lastName"))
                if not full_name:
                    continue

                pid = search_player_id(full_name, pick.get("birthDate"))
                if not pid:
                    continue

                before = len(finnish_prospects)
                upsert_candidate(
                    finnish_prospects,
                    prospects_by_name,
                    pid,
                    full_name,
                    nhlRights=pick.get("teamAbbrev"),
                    birthDate=pick.get("birthDate"),
                    source=f"draft_picks:{year}",
                )
                if len(finnish_prospects) > before:
                    year_count += 1

        print(f"Added {year_count} new")
        time.sleep(0.5)

    # 3) Draft rankings (captures draft-eligible Finns outside NHL-rights lists)
    ranking_categories = {
        1: "north_american_skaters",
        2: "international_skaters",
        3: "north_american_goalies",
        4: "international_goalies",
    }
    ranking_years = [current_year, current_year + 1]
    print(f"\nScanning draft rankings ({ranking_years[0]} and {ranking_years[1]})...")
    rankings_added = 0

    for year in ranking_years:
        for category_id, category_name in ranking_categories.items():
            rankings_data = get_draft_rankings(year, category_id)
            if not rankings_data:
                continue

            for player in rankings_data.get("rankings", []):
                if player.get("birthCountry") != "FIN":
                    continue

                full_name = get_name(player.get("firstName"), player.get("lastName"))
                if not full_name:
                    continue

                pid = player.get("playerId") or search_player_id(full_name, player.get("birthDate"))
                if not pid:
                    continue

                before = len(finnish_prospects)
                upsert_candidate(
                    finnish_prospects,
                    prospects_by_name,
                    pid,
                    full_name,
                    birthDate=player.get("birthDate"),
                    position=player.get("positionCode"),
                    nhlRights=player.get("teamAbbrev"),
                    source=f"draft_rankings:{year}:{category_name}",
                )
                if len(finnish_prospects) > before:
                    rankings_added += 1

    print(f"Added {rankings_added} candidates from draft rankings")

    # 4) Optional non-NHL sources
    ingest_eliteprospects(finnish_prospects, prospects_by_name)
    ingest_the_sports_db(finnish_prospects, prospects_by_name)
    ingest_wikidata(finnish_prospects, prospects_by_name)
    ingest_external_file(finnish_prospects, prospects_by_name)
    ingest_league_prospects_files(finnish_prospects, prospects_by_name)

    # 5) Enrich with landing data
    print(f"\nEnriching data for {len(finnish_prospects)} total players...")
    final_list = []

    for pid, p_data in finnish_prospects.items():
        if not pid:
            continue

        landing = get_player_landing(pid)
        if not landing:
            p_data.setdefault("nhlRights", "N/A")
            p_data.setdefault("league", "Unknown")
            p_data.setdefault("currentTeam", "Unknown")
            p_data.setdefault("stats", {"gp": 0, "goals": 0, "assists": 0, "points": 0, "savePct": 0.0, "gaa": 0.0, "shutouts": 0})
            final_list.append(p_data)
            continue

        if landing.get("birthCountry") and landing.get("birthCountry") != "FIN":
            continue

        current_stats = None
        league = "Unknown"
        current_team = "Unknown"
        stats = {}

        featured = landing.get("featuredStats", {})
        has_current_season = featured and featured.get("season") == CURRENT_SEASON_ID
        if has_current_season:
            current_stats = featured.get("regularSeason", {}).get("subSeason", {})

        last_season = None
        if not current_stats:
            season_totals = landing.get("seasonTotals", [])
            most_recent = normalize_season_stats(season_totals)
            if most_recent:
                last_season = most_recent.get("season")
                league = most_recent.get("leagueAbbrev", "Unknown")
                current_team = most_recent.get("teamName", {}).get("default", "Unknown")
                stats = {
                    "gp": most_recent.get("gamesPlayed", 0),
                    "goals": most_recent.get("goals", 0),
                    "assists": most_recent.get("assists", 0),
                    "points": most_recent.get("points", 0),
                    "savePct": most_recent.get("savePctg", 0.0),
                    "gaa": most_recent.get("goalsAgainstAverage", 0.0),
                    "shutouts": most_recent.get("shutouts", 0),
                }
        else:
            season_totals = landing.get("seasonTotals", [])
            target = normalize_season_stats(season_totals)
            last_season = CURRENT_SEASON_ID
            if target:
                league = target.get("leagueAbbrev", "Unknown")
                current_team = target.get("teamName", {}).get("default", "Unknown")
                stats = {
                    "gp": target.get("gamesPlayed", 0),
                    "goals": target.get("goals", 0),
                    "assists": target.get("assists", 0),
                    "points": target.get("points", 0),
                    "savePct": current_stats.get("savePctg", 0.0),
                    "gaa": target.get("goalsAgainstAverage", 0.0),
                    "shutouts": target.get("shutouts", 0),
                }

        p_data["currentTeam"] = current_team
        p_data["league"] = league
        p_data["stats"] = stats
        p_data["lastSeason"] = last_season
        p_data["hasCurrentSeasonStats"] = has_current_season
        p_data.setdefault("nhlRights", "N/A")

        if "headshot" not in p_data or not p_data["headshot"]:
            p_data["headshot"] = landing.get("headshot")
        if "position" not in p_data:
            p_data["position"] = landing.get("position", "U")
        if "birthDate" not in p_data or not p_data["birthDate"]:
            p_data["birthDate"] = landing.get("birthDate")

        final_list.append(p_data)
        time.sleep(0.05)

    final_list = dedupe_final_players(final_list)

    final_list.sort(
        key=lambda p: (-(p.get("stats", {}).get("points", 0)), p.get("name", ""))
    )

    print(f"\nFinal count: {len(final_list)}")
    save_json(final_list, PROSPECTS_CACHE_FILE)
    print(f"Saved to {PROSPECTS_CACHE_FILE}")


if __name__ == "__main__":
    main()
