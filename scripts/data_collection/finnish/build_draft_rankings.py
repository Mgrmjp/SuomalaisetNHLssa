#!/usr/bin/env python3
"""
Build Finnish draft rankings cache for 2026 NHL Draft.
Fetches North American and International skater rankings and filters for Finns.
"""

import json
import requests
import time
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import DATA_DIR
from utils import save_json

DRAFT_YEAR = 2026
RANKINGS_CACHE_FILE = DATA_DIR / "finnish_draft_rankings.json"
EP_RANKINGS_FILE = DATA_DIR / "finnish_draft_rankings_ep.json"

# 1 = NA Skaters, 2 = International Skaters
CATEGORIES = {
    "north_american_skaters": 1,
    "international_skaters": 2,
    # "north_american_goalies": 3,
    # "international_goalies": 4
}

def fetch_rankings(category_id):
    url = f"https://api-web.nhle.com/v1/draft/rankings/{DRAFT_YEAR}/{category_id}"
    try:
        print(f"Fetching {url}...")
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"Error fetching rankings for category {category_id}: {e}")
        return None

def main():
    print(f"Building Finnish Draft Rankings Cache for {DRAFT_YEAR}...")
    
    combined_data = {
        "year": DRAFT_YEAR,
        "north_american_skaters": [],
        "international_skaters": []
    }
    
    # Process NA Skaters
    na_data = fetch_rankings(CATEGORIES["north_american_skaters"])
    if na_data and "rankings" in na_data:
        finns = [p for p in na_data["rankings"] if p.get("birthCountry") == "FIN"]
        print(f"Found {len(finns)} Finnish NA skaters")
        combined_data["north_american_skaters"] = finns
    
    # Process International Skaters
    int_data = fetch_rankings(CATEGORIES["international_skaters"])
    if int_data and "rankings" in int_data:
        finns = [p for p in int_data["rankings"] if p.get("birthCountry") == "FIN"]
        print(f"Found {len(finns)} Finnish International skaters")
        combined_data["international_skaters"] = finns

    # Load EP rankings if available
    ep_sources = []
    if EP_RANKINGS_FILE.exists():
        try:
            with open(EP_RANKINGS_FILE, 'r') as f:
                ep_data = json.load(f)
                ep_sources = ep_data.get("sources", [])
                print(f"Loaded {len(ep_sources)} EP ranking sources")
        except Exception as e:
            print(f"Error loading EP rankings: {e}")

    # Build multi-source structure
    final_data = {
        "year": DRAFT_YEAR,
        "updatedAt": datetime.now().isoformat(),
        "sources": [
            {
                "name": "NHL Central Scouting",
                "slug": "nhl-central",
                "type": "official",
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
            "players": source["players"]
        })

    # Save unified data
    save_json(final_data, RANKINGS_CACHE_FILE)
    print(f"Saved unified rankings to {RANKINGS_CACHE_FILE}")

if __name__ == "__main__":
    main()
