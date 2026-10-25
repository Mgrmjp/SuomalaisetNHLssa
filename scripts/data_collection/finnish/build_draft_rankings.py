#!/usr/bin/env python3
"""
Build Finnish draft rankings cache for the upcoming NHL Draft.
Fetches North American and International skater rankings and filters for Finns.
"""

import json
import os
import requests
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import DATA_DIR, upcoming_nhl_draft_year
from utils import save_json

DRAFT_YEAR = upcoming_nhl_draft_year()
# Central Scouting publishes a draft class during its draft season, so the
# upcoming year can still be unpublished in the summer and early autumn.
DRAFT_FALLBACK_YEARS = 3
RANKINGS_CACHE_FILE = DATA_DIR / "finnish_draft_rankings.json"
EP_RANKINGS_FILE = DATA_DIR / "finnish_draft_rankings_ep.json"

# 1 = NA Skaters, 2 = International Skaters
CATEGORIES = {
    "north_american_skaters": 1,
    "international_skaters": 2,
    # "north_american_goalies": 3,
    # "international_goalies": 4
}

def fetch_rankings(year, category_id):
    url = f"https://api-web.nhle.com/v1/draft/rankings/{year}/{category_id}"
    try:
        print(f"Fetching {url}...")
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"Error fetching rankings for category {category_id}: {e}")
        return None

def fetch_published_rankings(draft_years):
    """Return both ranking categories for the newest draft class the NHL publishes."""
    for year in draft_years:
        na_data = fetch_rankings(year, CATEGORIES["north_american_skaters"])
        int_data = fetch_rankings(year, CATEGORIES["international_skaters"])
        if (
            isinstance(na_data, dict)
            and "rankings" in na_data
            and isinstance(int_data, dict)
            and "rankings" in int_data
        ):
            return year, na_data, int_data
        print(f"NHL Central Scouting has published no rankings for {year} yet")
    return None, None, None


def main():
    print(f"Building Finnish Draft Rankings Cache for the upcoming {DRAFT_YEAR} draft...")
    
    combined_data = {
        "north_american_skaters": [],
        "international_skaters": []
    }
    
    # Resolve the newest published draft class before touching any data.
    draft_years = [DRAFT_YEAR - offset for offset in range(DRAFT_FALLBACK_YEARS + 1)]
    draft_year, na_data, int_data = fetch_published_rankings(draft_years)
    if draft_year is None:
        raise SystemExit(
            "No published NHL draft rankings were found for "
            f"{', '.join(str(year) for year in draft_years)}; "
            "existing data was left untouched."
        )
    if draft_year != DRAFT_YEAR:
        notice = (
            f"NHL has not published {DRAFT_YEAR} rankings yet; keeping the "
            f"{draft_year} class."
        )
        print(notice)
        if os.getenv("GITHUB_ACTIONS"):
            print(f"::notice title=Draft rankings not published yet::{notice}")

    if na_data and "rankings" in na_data:
        finns = [p for p in na_data["rankings"] if p.get("birthCountry") == "FIN"]
        print(f"Found {len(finns)} Finnish NA skaters")
        combined_data["north_american_skaters"] = finns
    
    # Process International Skaters
    if int_data and "rankings" in int_data:
        finns = [p for p in int_data["rankings"] if p.get("birthCountry") == "FIN"]
        print(f"Found {len(finns)} Finnish International skaters")
        combined_data["international_skaters"] = finns

    # Load EP rankings if available. They can cover a newer draft class than the
    # NHL Central Scouting list, because EliteProspects publishes ahead of the
    # NHL, so keep the class on every source instead of dropping the snapshot.
    ep_sources = []
    ep_year = None
    if EP_RANKINGS_FILE.exists():
        try:
            with open(EP_RANKINGS_FILE, 'r') as f:
                ep_data = json.load(f)
                ep_sources = ep_data.get("sources", [])
                ep_year = ep_data.get("year")
                if ep_year == draft_year:
                    print(f"Loaded {len(ep_sources)} EP ranking sources for {ep_year}")
                else:
                    print(
                        f"Keeping {len(ep_sources)} EP ranking sources for {ep_year} "
                        f"alongside the {draft_year} Central Scouting class"
                    )
        except Exception as e:
            print(f"Error loading EP rankings: {e}")
            ep_sources = []
            ep_year = None

    # Build multi-source structure
    final_data = {
        "year": draft_year,
        "updatedAt": datetime.now().isoformat(),
        "sources": [
            {
                "name": "NHL Central Scouting",
                "slug": "nhl-central",
                "type": "official",
                "year": draft_year,
                "categories": {
                    "north_american": combined_data["north_american_skaters"],
                    "international": combined_data["international_skaters"]
                }
            }
        ]
    }
    
    # Add EP sources
    for source in ep_sources:
        final_data["sources"].append({
            "name": source["name"],
            "slug": source["slug"],
            "type": "independent",
            "year": ep_year,
            "players": source["players"]
        })

    # Save unified data
    save_json(final_data, RANKINGS_CACHE_FILE)
    print(f"Saved unified rankings to {RANKINGS_CACHE_FILE}")

if __name__ == "__main__":
    main()
