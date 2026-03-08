"""
Liiga.fi scraper using requests-html for JavaScript rendering
This can handle React/Vue apps that load data dynamically
"""
import json
from typing import List, Dict
from datetime import datetime

try:
    from requests_html import HTMLSession
    REQUESTS_HTML_AVAILABLE = True
except ImportError:
    REQUESTS_HTML_AVAILABLE = False
    print("requests-html not installed. Install: pip install requests-html")


class LiigaJSScraper:
    """Scrape Liiga using JavaScript rendering"""
    
    def __init__(self):
        if not REQUESTS_HTML_AVAILABLE:
            raise ImportError("requests-html required")
        self.session = HTMLSession()
    
    def get_player_stats(self, season: str = "2024-2025") -> List[Dict]:
        """Get player stats by rendering the page with JavaScript"""
        url = f"https://liiga.fi/fi/tilastot/pelaajat/"
        print(f"Rendering {url} with JavaScript...")
        print("(This may take 10-30 seconds)")
        
        try:
            # Render the page with JavaScript
            r = self.session.get(url, timeout=60)
            r.html.render(timeout=30, sleep=2)
            
            print(f"Page rendered. Looking for data...")
            
            # Look for tables that appeared after JS rendered
            tables = r.html.find('table')
            print(f"Found {len(tables)} tables after rendering")
            
            players = []
            
            # Try to extract data from tables
            for table in tables:
                rows = table.find('tr')
                if len(rows) < 2:
                    continue
                
                # Check if this is a player stats table
                header = rows[0].text
                if 'pelaaja' in header.lower() or 'player' in header.lower() or 'nimi' in header.lower():
                    print(f"Found player table with {len(rows)} rows")
                    
                    for row in rows[1:10]:  # First 10 for testing
                        cells = row.find('td')
                        if len(cells) >= 4:
                            name = cells[1].text if len(cells) > 1 else ''
                            print(f"  Player: {name}")
            
            return players
            
        except Exception as e:
            print(f"Error: {e}")
            return []
    
    def is_finnish(self, name: str) -> bool:
        """Check if name appears Finnish"""
        if any(char in name for char in 'äöåÄÖÅ'):
            return True
        if name.split()[-1].endswith(('nen', 'lä', 'la')):
            return True
        return False


def main():
    print("=" * 60)
    print("Liiga JS Scraper Test")
    print("=" * 60)
    
    try:
        scraper = LiigaJSScraper()
        players = scraper.get_player_stats()
        print(f"\nFound {len(players)} players")
    except ImportError as e:
        print(f"Error: {e}")
        print("\nTo use this scraper:")
        print("  pip install requests-html")
        print("  # Also requires Chrome/Chromium browser")


if __name__ == "__main__":
    main()
