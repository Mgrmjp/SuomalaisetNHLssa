#!/usr/bin/env python3
"""
Fetch draft rankings from EliteProspects for the upcoming NHL draft.
Uses the Next.js data API to get filtered rankings for Finnish players.
"""

import requests
import re
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import DATA_DIR, upcoming_nhl_draft_year
from utils import save_json

DRAFT_YEAR = upcoming_nhl_draft_year()
BASE_URL = "https://www.eliteprospects.com"
RANKINGS_OUTPUT = DATA_DIR / "finnish_draft_rankings_ep.json"

# The HTML pages sit behind a Cloudflare managed challenge, but /rss is served
# to feed readers and still carries the Next.js build id. The data route itself
# is open, so the rankings stay reachable without a browser. /draft-center is
# kept as a fallback for when the challenge policy changes again.
BUILD_ID_PAGES = ("/rss", "/draft-center")

# Ranking slugs to fetch
SOURCES = {
    "eliteprospects.com": "EliteProspects.com",
    "mckeen-s-hockey": "McKeen's Hockey",
    "tsn-craig-button": "TSN (Craig Button)",
    "draft-prospects-hockey": "Draft Prospects Hockey",
    "daily-faceoff": "Daily Faceoff",
    "consolidated-ranking": "Consolidated Ranking"
}


def build_id_from_html(text):
    """Extract the Next.js build id from a page's HTML."""
    match = re.search(r'"buildId":"(.*?)"', text or "")
    return match.group(1) if match else None


def get_build_id():
    """Find the current Next.js build id from an unprotected page."""
    for path in BUILD_ID_PAGES:
        try:
            r = requests.get(f"{BASE_URL}{path}", timeout=15)
            r.raise_for_status()
        except Exception as e:
            print(f"Error getting buildId from {path}: {e}")
            continue

        build_id = build_id_from_html(r.text)
        if build_id:
            print(f"Build ID: {build_id} (from {path})")
            return build_id

        print(f"No buildId found in {path}")

    return None


def extract_ranking_rows(payload):
    """Pull the ranking rows out of the Next.js page props."""
    page_props = payload.get("pageProps", {})
    draft_rankings = page_props.get("draftRankings", {})
    rows = draft_rankings.get("rankings", [])

    if not rows:
        # Fallback for consolidated or other variations
        data_field = page_props.get("data", {})
        rows = data_field.get("picks", []) or data_field.get("rankings", [])

    return rows


def _metric_value(value):
    """Height and weight arrive either as numbers or as {'metrics': ..., ...}."""
    if isinstance(value, dict):
        return value.get("metrics")
    return value


def normalize_ranking_row(row):
    """Map an EliteProspects ranking row onto our stored player schema.

    The payload shape has changed before: position, team and league used to be
    top level and now live on player.detailedPosition and playerStats, while
    height and weight became objects. Read every known layout so a schema
    change degrades to a partial row instead of raising.
    """
    player = row.get("player") or {}
    stats = row.get("playerStats") or {}
    latest = player.get("latestStats") or {}

    team = row.get("team") or stats.get("team") or latest.get("team") or {}
    league = row.get("league") or stats.get("league") or latest.get("league") or {}

    position = player.get("position") or player.get("detailedPosition")
    if isinstance(position, (list, tuple)):
        position = position[0] if position else None

    return {
        "rank": row.get("rank") or row.get("midtermRank"),
        "name": player.get("name"),
        "firstName": player.get("firstName"),
        "lastName": player.get("lastName"),
        "position": position,
        "team": team.get("name"),
        "league": league.get("name"),
        "birthDate": player.get("dateOfBirth") or player.get("birthDate"),
        "height": _metric_value(player.get("height")),
        "weight": _metric_value(player.get("weight")),
        "playerId": player.get("id"),
    }


def fetch_ranking(build_id, slug, name):
    """Fetch a specific ranking from the Next.js data API."""
    # Pattern: https://www.eliteprospects.com/_next/data/{buildId}/draft-center/{slug}.json?params={slug}&nation=FIN&sort=rank
    url = f"{BASE_URL}/_next/data/{build_id}/draft-center/{slug}.json"
    params = {
        "params": slug,
        "nation": "FIN",
        "sort": "rank"
    }

    try:
        print(f"Fetching {name} rankings...")
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        rows = extract_ranking_rows(r.json())

        players = []
        for row in rows:
            player = normalize_ranking_row(row)
            if not player["name"]:
                continue
            players.append(player)

        print(f"  Found {len(players)} Finnish players")
        return players
    except Exception as e:
        print(f"  Error fetching {name}: {e}")
        return []


def main():
    build_id = get_build_id()
    if not build_id:
        raise SystemExit("Could not find EliteProspects buildId; rankings were not updated.")

    all_rankings = {
        "year": DRAFT_YEAR,
        "updatedAt": datetime.now().isoformat(),
        "sources": []
    }

    for slug, name in SOURCES.items():
        players = fetch_ranking(build_id, slug, name)
        if players:
            all_rankings["sources"].append({
                "name": name,
                "slug": slug,
                "players": players
            })

    if all_rankings["sources"]:
        save_json(all_rankings, RANKINGS_OUTPUT)
        print(f"Saved {len(all_rankings['sources'])} ranking sources to {RANKINGS_OUTPUT}")
    else:
        raise SystemExit("No draft rankings were fetched; existing data was left untouched.")


if __name__ == "__main__":
    main()
