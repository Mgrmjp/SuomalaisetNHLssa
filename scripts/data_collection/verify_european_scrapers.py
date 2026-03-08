"""Verification script for European hockey league scrapers."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_collection.leagues import (
    SwissNLAdapter, ICEHLAdapter, DELAdapter, CzechExtraligaAdapter
)

def verify_scraper(adapter, name):
    print(f"\nVerifying {name}...")
    try:
        players = adapter.get_all_players()
        # Filter for Finnish players using the adapter's built-in heuristic or nationality check
        # Most of our adapters already filter for Finnish players in get_all_players if we set it up that way,
        # but let's be explicit here based on how we implemented them.
        
        # Some adapters might return all players and expect external filtering, 
        # but my implementations for ICEHL, NL, DEL, and Czech already filter for FIN.
        
        print(f"  Total players found: {len(players)}")
        if players:
            print(f"  Top 3 players:")
            for p in sorted(players, key=lambda x: x.points, reverse=True)[:3]:
                print(f"    - {p.name} ({p.team}): {p.goals}G, {p.assists}A, {p.points}P ({p.nationality})")
        else:
            print("  ⚠️ No Finnish players found (this might be expected if no Finns are in the league or if scraping failed).")
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("=" * 70)
    print("EUROPEAN LEAGUE SCRAPER VERIFICATION")
    print("=" * 70)
    
    adapters = [
        (SwissNLAdapter(), "Swiss National League (NL)"),
        (ICEHLAdapter(), "ICE Hockey League (ICEHL)"),
        (DELAdapter(), "German DEL"),
        (CzechExtraligaAdapter(), "Czech Extraliga")
    ]
    
    for adapter, name in adapters:
        verify_scraper(adapter, name)

if __name__ == "__main__":
    main()
