"""
Web scrapers for leagues with publicly accessible stats pages
Uses BeautifulSoup to extract player data from HTML tables
"""
import requests
import re
from datetime import datetime
from typing import List, Dict, Optional

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    print("Warning: beautifulsoup4 not installed. Scrapers will not work.")
    print("Install with: pip install beautifulsoup4")


class BaseScraper:
    """Base class for league scrapers"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def is_finnish(self, name: str, nationality: str = '') -> bool:
        """Check if player is Finnish based on name and nationality"""
        name = name.strip()
        
        # Direct nationality check
        if nationality.upper() in ['FIN', 'FI', 'FINLAND']:
            return True
        
        # Finnish characters
        if any(char in name for char in 'äöåÄÖÅ'):
            return True
        
        # Finnish name patterns
        parts = name.split()
        for part in parts:
            if part.endswith(('nen', 'lä', 'lä', 'kkä', 'kkö')):
                return True
        
        return False
    
    def fetch_page(self, url: str, timeout: int = 30) -> Optional[str]:
        """Fetch HTML page"""
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None


class LiigaScraper(BaseScraper):
    """Scraper for Liiga (Finnish league)"""
    
    STATS_URL = "https://liiga.fi/fi/tilastot/pelaajat/"
    
    def get_players(self) -> List[Dict]:
        """Scrape Liiga player stats"""
        if not BS4_AVAILABLE:
            return []
        
        print("Scraping Liiga stats...")
        html = self.fetch_page(self.STATS_URL)
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        players = []
        
        # Liiga.fi loads data dynamically, but we can look for embedded JSON
        # or scrape the rendered page structure
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and 'players' in script.string.lower():
                # Try to extract JSON data from scripts
                json_match = re.search(r'var\s+\w+\s*=\s*(\[.*?\]);', script.string, re.DOTALL)
                if json_match:
                    try:
                        import json
                        data = json.loads(json_match.group(1))
                        print(f"Found embedded data with {len(data)} entries")
                        # Process data...
                    except:
                        pass
        
        # Fallback: Try to find tables
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables")
        
        # Liiga likely uses React/Vue, so data might not be in initial HTML
        # Return empty to indicate we need a different approach
        return players


class HockeyDBScraper(BaseScraper):
    """Scraper using hockeydb.com"""
    
    def get_liiga_players(self, season: str = "2025-26") -> List[Dict]:
        """Get Liiga players from HockeyDB"""
        if not BS4_AVAILABLE:
            return []
        
        # HockeyDB has stats for various leagues
        url = f"https://www.hockeydb.com/ihdb/stats/leagues/seasons/leaders/{season.replace('-', '')}/401.html"
        print(f"Scraping HockeyDB Liiga from {url}...")
        
        html = self.fetch_page(url)
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        players = []
        
        # Find stats table
        tables = soup.find_all('table', {'class': 'stats-table'})
        for table in tables:
            rows = table.find_all('tr')
            for row in rows[1:]:  # Skip header
                cells = row.find_all('td')
                if len(cells) >= 10:
                    name_cell = cells[1]
                    name = name_cell.get_text(strip=True)
                    
                    if self.is_finnish(name):
                        player = {
                            'player_id': f"hdb_liiga_{len(players)}",
                            'name': name,
                            'team': cells[2].get_text(strip=True) if len(cells) > 2 else 'Unknown',
                            'league': 'Liiga',
                            'position': cells[3].get_text(strip=True) if len(cells) > 3 else 'F',
                            'games_played': self._parse_int(cells[4]),
                            'goals': self._parse_int(cells[5]),
                            'assists': self._parse_int(cells[6]),
                            'points': self._parse_int(cells[7]),
                            'plus_minus': 0,
                            'penalty_minutes': self._parse_int(cells[9]),
                            'nationality': 'FIN',
                            'source_league': 'liiga',
                            'source': 'hockeydb'
                        }
                        players.append(player)
        
        print(f"  Found {len(players)} Finnish players")
        return players
    
    def get_shl_players(self, season: str = "2025-26") -> List[Dict]:
        """Get SHL players from HockeyDB"""
        if not BS4_AVAILABLE:
            return []
        
        url = f"https://www.hockeydb.com/ihdb/stats/leagues/seasons/leaders/{season.replace('-', '')}/132.html"
        print(f"Scraping HockeyDB SHL from {url}...")
        
        html = self.fetch_page(url)
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        players = []
        
        tables = soup.find_all('table', {'class': 'stats-table'})
        for table in tables:
            rows = table.find_all('tr')
            for row in rows[1:]:
                cells = row.find_all('td')
                if len(cells) >= 10:
                    name = cells[1].get_text(strip=True)
                    
                    if self.is_finnish(name):
                        player = {
                            'player_id': f"hdb_shl_{len(players)}",
                            'name': name,
                            'team': cells[2].get_text(strip=True) if len(cells) > 2 else 'Unknown',
                            'league': 'SHL',
                            'position': cells[3].get_text(strip=True) if len(cells) > 3 else 'F',
                            'games_played': self._parse_int(cells[4]),
                            'goals': self._parse_int(cells[5]),
                            'assists': self._parse_int(cells[6]),
                            'points': self._parse_int(cells[7]),
                            'penalty_minutes': self._parse_int(cells[9]),
                            'nationality': 'FIN',
                            'source_league': 'shl',
                            'source': 'hockeydb'
                        }
                        players.append(player)
        
        print(f"  Found {len(players)} Finnish players")
        return players
    
    def _parse_int(self, cell) -> int:
        """Parse integer from table cell"""
        try:
            text = cell.get_text(strip=True).replace(',', '')
            return int(text) if text else 0
        except:
            return 0


class EPScraper(BaseScraper):
    """
    Scraper for EliteProspects (respectful rate limiting)
    Note: EP prefers API usage for bulk data
    """
    
    BASE_URL = "https://www.eliteprospects.com"
    
    def search_finnish_players(self, league: str) -> List[Dict]:
        """
        Search for Finnish players in a league
        This is limited - better to use API for bulk data
        """
        print(f"Note: EliteProspects scraping limited. Consider API for bulk {league} data.")
        return []


def test_scrapers():
    """Test available scrapers"""
    print("Testing hockey data scrapers...\n")
    
    if not BS4_AVAILABLE:
        print("ERROR: beautifulsoup4 not installed")
        print("Install: pip install beautifulsoup4")
        return
    
    # Test HockeyDB
    scraper = HockeyDBScraper()
    
    print("=" * 60)
    print("Testing HockeyDB scraper")
    print("=" * 60)
    
    # Try current and previous seasons
    for season in ["2025-26", "2024-25"]:
        print(f"\nSeason {season}:")
        liiga = scraper.get_liiga_players(season)
        shl = scraper.get_shl_players(season)
        
        print(f"  Liiga: {len(liiga)} Finnish players")
        print(f"  SHL: {len(shl)} Finnish players")
        
        if liiga or shl:
            print("\n  Sample players:")
            for p in (liiga + shl)[:5]:
                print(f"    {p['name']} ({p['league']}): {p['points']}P")


if __name__ == "__main__":
    test_scrapers()
