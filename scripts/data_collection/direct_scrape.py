#!/usr/bin/env python3
"""
Direct Web Scraper for League Websites
Scrapes Finnish players directly from official league websites using web scraping.
"""
import requests
import json
import time
import re
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    print("Warning: beautifulsoup4 not installed")


class DirectLeagueScraper:
    """Scrape Finnish players directly from league websites."""
    
    def __init__(self):
        if not BS4_AVAILABLE:
            raise ImportError("beautifulsoup4 required")
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
        self.request_delay = 1.5
        
    def _make_request(self, url: str) -> Optional[str]:
        """Make rate-limited request."""
        time.sleep(self.request_delay)
        try:
            response = self.session.get(url, timeout=30, allow_redirects=True)
            if response.status_code == 200:
                return response.text
        except Exception as e:
            print(f"  Error: {e}")
        return None
    
    def is_finnish(self, name: str, nationality: str = '') -> bool:
        """Check if player is Finnish."""
        nat = nationality.strip().upper() if nationality else ''
        
        if nat in ['FI', 'FIN', 'FINLAND']:
            return True
        if any(char in name for char in 'äöåÄÖÅ'):
            return True
        parts = name.split()
        if parts:
            last_name = parts[-1] if len(parts) > 1 else ''
            if last_name.endswith(('nen', 'lä', 'lä', 'kkä', 'kkö', 'pää', 'rvi')):
                return True
        return False
    
    def parse_ahl_stats(self, html: str) -> List[Dict]:
        """Parse AHL stats from HTML."""
        players = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find player tables
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows[1:]:  # Skip header
                cells = row.find_all('td')
                if len(cells) >= 7:
                    name_cell = cells[1]
                    name_link = name_cell.find('a')
                    if name_link:
                        name = name_link.get_text(strip=True)
                        if self.is_finnish(name):
                            players.append({
                                'name': name,
                                'team': cells[2].get_text(strip=True) if len(cells) > 2 else '',
                                'games': cells[3].get_text(strip=True) if len(cells) > 3 else '0',
                                'goals': cells[4].get_text(strip=True) if len(cells) > 4 else '0',
                                'assists': cells[5].get_text(strip=True) if len(cells) > 5 else '0',
                                'points': cells[6].get_text(strip=True) if len(cells) > 6 else '0',
                            })
        
        return players
    
    def get_ahl_direct(self) -> List[Dict]:
        """Get AHL players by scraping directly."""
        print("  Trying direct AHL scrape...")
        
        # Try the main stats page
        urls_to_try = [
            "https://www.theahl.com/stats/players",
            "https://theahl.com/stats/players",
        ]
        
        for url in urls_to_try:
            html = self._make_request(url)
            if html and 'player' in html.lower():
                players = self.parse_ahl_stats(html)
                if players:
                    print(f"  AHL: Found {len(players)} players via direct scrape")
                    return players
        
        print("  AHL: Could not scrape")
        return []
    
    def get_echl_direct(self) -> List[Dict]:
        """Get ECHL players by scraping directly."""
        print("  Trying direct ECHL scrape...")
        
        urls_to_try = [
            "https://www.echl.com/stats/players",
        ]
        
        for url in urls_to_try:
            html = self._make_request(url)
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                tables = soup.find_all('table')
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows[1:]:
                        cells = row.find_all('td')
                        if len(cells) >= 7:
                            name_cell = cells[1]
                            name_link = name_cell.find('a')
                            if name_link:
                                name = name_link.get_text(strip=True)
                                if self.is_finnish(name):
                                    print(f"  ECHL: Found {name}")
        
        print("  ECHL: Could not scrape")
        return []
    
    def get_ushl_direct(self) -> List[Dict]:
        """Get USHL players by scraping directly."""
        print("  Trying direct USHL scrape...")
        
        urls_to_try = [
            "https://www.ushl.com/stats/players",
        ]
        
        for url in urls_to_try:
            html = self._make_request(url)
            if html:
                print(f"  USHL: Got page, length {len(html)}")
        
        print("  USHL: Could not scrape")
        return []
    
    def get_khl_direct(self) -> List[Dict]:
        """Get KHL players by scraping directly."""
        print("  Trying direct KHL scrape...")
        
        urls_to_try = [
            "https://en.khl.ru/stats/players/",
            "https://www.khl.ru/stats/players/",
        ]
        
        for url in urls_to_try:
            html = self._make_request(url)
            if html and 'player' in html.lower():
                soup = BeautifulSoup(html, 'html.parser')
                # Try to find player data
                player_links = soup.find_all('a', href=lambda x: x and '/players/' in x if x else False)
                print(f"  KHL: Found {len(player_links)} player links")
        
        print("  KHL: Could not scrape")
        return []
    
    def get_shl_direct(self) -> List[Dict]:
        """Get SHL players by scraping directly."""
        print("  Trying direct SHL scrape...")
        
        urls_to_try = [
            "https://www.shl.se/statistik/spelare/",
        ]
        
        for url in urls_to_try:
            html = self._make_request(url)
            if html:
                print(f"  SHL: Got page, length {len(html)}")
        
        print("  SHL: Could not scrape")
        return []
    
    def get_liiga_direct(self) -> List[Dict]:
        """Get Liiga players by scraping directly."""
        print("  Trying direct Liiga scrape...")
        
        urls_to_try = [
            "https://liiga.fi/tilastot/pelaajat/",
        ]
        
        for url in urls_to_try:
            html = self._make_request(url)
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                # Liiga often has stats in tables or embedded JSON
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string and 'player' in script.string.lower():
                        print(f"  Liiga: Found script with player data")
                        # Try to extract JSON
                        json_matches = re.findall(r'\[.*?\]', script.string)
                        for match in json_matches:
                            if 'nimi' in match or 'name' in match.lower():
                                print(f"  Liiga: Possible data: {match[:100]}")
        
        print("  Liiga: Could not scrape")
        return []
    
    def collect_all(self) -> Dict:
        """Collect from all leagues."""
        results = {
            'generated_at': datetime.now().isoformat(),
            'season': '2025-2026',
            'data_source': 'direct-league-websites',
            'leagues': {},
            'players': []
        }
        
        print("=" * 60)
        print("Direct League Website Scraping")
        print("=" * 60)
        
        # Try each league
        print("\n--- USA ---")
        results['players'].extend(self.get_ahl_direct())
        results['players'].extend(self.get_echl_direct())
        results['players'].extend(self.get_ushl_direct())
        
        print("\n--- CANADA ---")
        
        print("\n--- EUROPE ---")
        results['players'].extend(self.get_khl_direct())
        results['players'].extend(self.get_shl_direct())
        results['players'].extend(self.get_liiga_direct())
        
        results['total_players'] = len(results['players'])
        return results


def main():
    if not BS4_AVAILABLE:
        print("Please install beautifulsoup4: pip install beautifulsoup4")
        return
    
    scraper = DirectLeagueScraper()
    results = scraper.collect_all()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total players found: {results['total_players']}")
    
    # Save
    output_dir = Path(__file__).parent.parent / 'static' / 'data' / 'leagues'
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / 'league_prospects_direct.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {output_path}")


if __name__ == "__main__":
    main()
