#!/usr/bin/env python3
"""
Generate a manifest file listing all available game data files.
This allows the frontend to dynamically discover available dates
instead of relying on a hardcoded list.
"""

import json
import sys
from pathlib import Path

# Add shared utils to path
sys.path.insert(0, str(Path(__file__).parent))

from config import GAMES_DIR, DATA_DIR
from utils import save_json

def generate_manifest():
    """
    Scan the games directory and create a manifest of available dates.
    """
    print(f"Scanning {GAMES_DIR} for game data files...")
    
    if not GAMES_DIR.exists():
        print(f"Error: Games directory {GAMES_DIR} does not exist.")
        return []

    # Find all JSON files in the games directory that match YYYY-MM-DD format
    # We do a simple glob and then basic validation
    files = sorted(GAMES_DIR.glob("*.json"))
    dates = []
    
    for file_path in files:
        # Check if filename is a date (YYYY-MM-DD.json)
        filename = file_path.name
        if len(filename) == 15 and filename.count("-") == 2 and filename.endswith(".json"):
            date_str = filename.replace(".json", "")
            dates.append(date_str)
            
    if not dates:
        print("Warning: No game data files found.")
    else:
        print(f"Found {len(dates)} game data files (from {dates[0]} to {dates[-1]}).")
        
    # Create the manifest structure
    manifest = {
        "games": dates,
        "lastUpdated": import_datetime().now().isoformat()
    }
    
    # Save to static/data/games_manifest.json
    output_file = DATA_DIR / "games_manifest.json"
    save_json(manifest, output_file)
    
    print(f"✅ Manifest generated: {output_file}")
    return dates

def import_datetime():
    from datetime import datetime
    return datetime

if __name__ == "__main__":
    generate_manifest()
