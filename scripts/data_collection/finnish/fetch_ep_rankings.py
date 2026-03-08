#!/usr/bin/env python3
"""
Fetch draft rankings from EliteProspects for 2026.
Uses the Next.js data API to get filtered rankings for Finnish players.
"""

import json
import requests
import re
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import DATA_DIR
from utils import save_json

DRAFT_YEAR = 2026
BASE_URL = "https://www.eliteprospects.com"
RANKINGS_OUTPUT = DATA_DIR / "finnish_draft_rankings_ep.json"

# Ranking slugs to fetch
SOURCES = {
    "eliteprospects.com": "EliteProspects.com",
    "mckeen-s-hockey": "McKeen's Hockey",
    "tsn-craig-button": "TSN (Craig Button)",
    "draft-prospects-hockey": "Draft Prospects Hockey",
    "daily-faceoff": "Daily Faceoff",
    "consolidated-ranking": "Consolidated Ranking"
}

def get_build_id():
    """Extract Next.js buildId from the site source."""
    try:
        r = requests.get(f"{BASE_URL}/draft-center", timeout=15)
        r.raise_for_status()
        # Look for "buildId":"..."
        match = re.search(r'"buildId":"(.*?)"', r.text)
        if match:
            return match.group(1)
    except Exception as e:
        print(f"Error getting buildId: {e}")
    return None

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
        data = r.json()
        
        # Extract players from the Next.js pageProps structure
        # Exact path according to inspection: pageProps.draftRankings.rankings
        page_props = data.get("pageProps", {})
        draft_rankings = page_props.get("draftRankings", {})
        players = draft_rankings.get("rankings", [])
        
        if not players:
            # Fallback for consolidated or other variations
            data_field = page_props.get("data", {})
            players = data_field.get("picks", []) or data_field.get("rankings", [])
            
        print(f"  Found {len(players)} Finnish players")
        return players
    except Exception as e:
        print(f"  Error fetching {name}: {e}")
        return []

def main():
    build_id = get_build_id()
    if not build_id:
        print("Could not find buildId, aborting.")
        return

    print(f"Build ID: {build_id}")
    
    all_rankings = {
        "year": DRAFT_YEAR,
        "updatedAt": datetime.now().isoformat(),
        "sources": []
    }
    
    for slug, name in SOURCES.items():
        players = fetch_ranking(build_id, slug, name)
        if players:
            # Normalize players for our use
            normalized_players = []
            for p in players:
                # EP structure mapping
                player_info = p.get("player", {})
                normalized_players.append({
                    "rank": p.get("rank") or p.get("midtermRank"),
                    "name": player_info.get("name"),
                    "firstName": player_info.get("firstName"),
                    "lastName": player_info.get("lastName"),
                    "position": player_info.get("position"),
                    "team": p.get("team", {}).get("name") or player_info.get("latestStats", {}).get("team", {}).get("name"),
                    "league": p.get("league", {}).get("name") or player_info.get("latestStats", {}).get("league", {}).get("name"),
                    "birthDate": player_info.get("dateOfBirth"),
                    "height": player_info.get("height"),
                    "weight": player_info.get("weight"),
                    "playerId": player_info.get("id")
                })
            
            all_rankings["sources"].append({
                "name": name,
                "slug": slug,
                "players": normalized_players
            })

    if all_rankings["sources"]:
        save_json(all_rankings, RANKINGS_OUTPUT)
        print(f"Saved {len(all_rankings['sources'])} ranking sources to {RANKINGS_OUTPUT}")
    else:
        print("No rankings found.")

if __name__ == "__main__":
    main()
