
#!/usr/bin/env python3
import requests
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Config
SEASON_START = "2025-10-01" 
SEASON_END = "2026-04-18" 
OUTPUT_FILE = Path("static/data/breaks.json")

def get_schedule_week(date_str):
    url = f"https://api-web.nhle.com/v1/schedule/{date_str}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching schedule for {date_str}: {e}")
        return None

def determine_day_status(games):
    game_types = set(g.get("gameType") for g in games)
    
    if not games:
        # Check if it looks like a break (no games at all)
        return "No Games"
        
    if 9 in game_types:
        return "Olympic Break"
    elif 19 in game_types:
        return "International Break" # 4 Nations
    elif 4 in game_types:
        return "All-Star Break"
    elif 2 in game_types:
        return "Regular Season"
    else:
        # Pre-season (1), Playoffs (3) or just unknown
        return "Other"

def main():
    print(f"Scanning schedule from {SEASON_START} to {SEASON_END}...")
    
    current_date = datetime.strptime(SEASON_START, "%Y-%m-%d")
    end_date = datetime.strptime(SEASON_END, "%Y-%m-%d")
    
    # Store status for each day
    day_statuses = {}
    
    # We can jump by weeks to be efficient, as the API returns a week key
    # But to be precise on start/end dates of breaks, we might need to parse the daily data from the week response
    
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        
        # Check if we already have data for this date (from a previous week fetch)
        if date_str in day_statuses:
            current_date += timedelta(days=1)
            continue
            
        print(f"Fetching week of {date_str}...", end="\r")
        data = get_schedule_week(date_str)
        
        if not data:
            current_date += timedelta(days=1)
            continue
            
        # Process the week
        if "gameWeek" in data:
            for day_data in data["gameWeek"]:
                d_str = day_data["date"]
                d_games = day_data.get("games", [])
                status = determine_day_status(d_games)
                day_statuses[d_str] = status
        
        # Move to next week (approx) or just let the loop handle it
        # The API returns current week usually. 
        # Safest is to just increment current_date until we find a missing one, 
        # but realistically we just fetched a chunk.
        
        # Let's just increment by 1 day to be safe loop-wise, 
        # but the check "if date_str in day_statuses" will skip efficiently
        current_date += timedelta(days=1)

    print("\nProcessing breaks...")
    breaks = []
    
    sorted_dates = sorted(day_statuses.keys())
    
    # 1. Group consecutive days into chunks of non-regular season days
    chunks = []
    current_chunk = []
    
    for date_str in sorted_dates:
        status = day_statuses[date_str]
        
        is_regular_game = (status == "Regular Season" or status == "Playoffs")
        
        if not is_regular_game:
            current_chunk.append({"date": date_str, "status": status})
        else:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = []
    
    # Don't forget the last chunk
    if current_chunk:
        chunks.append(current_chunk)
        
    # 2. Analyze chunks to see if they are valid breaks (contain special events)
    for chunk in chunks:
        # Check if this chunk contains any specific break types
        break_types = set(d["status"] for d in chunk)
        
        # We are looking for break indicators
        found_break_type = None
        if "Olympic Break" in break_types:
            found_break_type = "Olympic Break"
        elif "International Break" in break_types:
            found_break_type = "International Break"
        elif "All-Star Break" in break_types:
            found_break_type = "All-Star Break"
            
        if found_break_type:
            # This chunk is a valid break of type `found_break_type`
            # It starts at the first day of the chunk and ends at the last day
            start_date = chunk[0]["date"]
            end_date = chunk[-1]["date"]
            
            breaks.append({
                "startDate": start_date,
                "endDate": end_date,
                "type": found_break_type,
                "description": get_break_description(found_break_type)
            })

    # Save to file
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(breaks, f, indent=2)
        
    print(f"Saved {len(breaks)} breaks to {OUTPUT_FILE}")
    for b in breaks:
        print(f"  - {b['type']}: {b['startDate']} to {b['endDate']}")

def get_break_description(break_type):
    if break_type == "Olympic Break":
        return "Olympialaiset (Milano-Cortina 2026)"
    elif break_type == "International Break":
        return "4 Nations Face-Off"
    elif break_type == "All-Star Break":
        return "NHL All-Star -tapahtuma"
    return break_type

if __name__ == "__main__":
    main()
