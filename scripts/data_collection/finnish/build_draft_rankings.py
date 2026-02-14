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

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import DATA_DIR
from utils import save_json

DRAFT_YEAR = 2026
RANKINGS_CACHE_FILE = DATA_DIR / "finnish_draft_rankings.json"

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

    # Only save if we found something
    total = len(combined_data["north_american_skaters"]) + len(combined_data["international_skaters"])
    if total > 0:
        save_json(combined_data, RANKINGS_CACHE_FILE)
        print(f"Saved {total} players to {RANKINGS_CACHE_FILE}")
    else:
        print("No players found, skipping save.")

if __name__ == "__main__":
    main()
