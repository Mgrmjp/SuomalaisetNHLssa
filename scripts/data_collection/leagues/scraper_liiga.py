"""
Liiga.fi web scraper
Scrapes player statistics directly from liiga.fi
"""
import requests
import re
import json
from typing import List, Dict, Optional
from datetime import datetime

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False


class LiigaScraper:
    """Scrape Liiga player data from liiga.fi"""
    
    BASE_URL = "https://liiga.fi"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fi-FI,fi;q=0.9,en-US;q=0.8,en;q=0.7',
        })
    
    def is_finnish(self, name: str, nationality: str = '') -> bool:
        """Check if player is Finnish"""
        name = name.strip()
        
        if nationality.upper() in ['FIN', 'FI', 'FINLAND', 'FINNISH']:
            return True
        
        # Finnish characters
        if any(char in name for char in 'äöåÄÖÅ'):
            return True
        
        # Finnish name patterns
        parts = name.split()
        for part in parts:
            if part.endswith(('nen', 'nen', 'lä', 'la', 'kä', 'ka', 'kkä', 'kkö')):
                return True
        
        return False
    
    def get_player_stats(self, season: str = "2024-2025") -> List[Dict]:
        """
        Get player statistics from Liiga
        
        Liiga.fi loads data dynamically via JavaScript, but we can try to:
        1. Find embedded JSON in the page
        2. Call their internal API endpoints
        3. Parse the rendered HTML
        """
        if not BS4_AVAILABLE:
            print("Error: beautifulsoup4 required. Install: pip install beautifulsoup4")
            return []
        
        url = f"{self.BASE_URL}/fi/tilastot/pelaajat/"
        print(f"Fetching Liiga stats from {url}...")
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
        except Exception as e:
            print(f"Error fetching page: {e}")
            return []
        
        # Try to find data in the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for script tags with player data
        scripts = soup.find_all('script')
        print(f"Found {len(scripts)} script tags, searching for data...")
        
        players = []
        
        # Method 1: Look for __INITIAL_STATE__ or similar
        for script in scripts:
            if not script.string:
                continue
            
            # Look for JSON data
            patterns = [
                r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\});',
                r'window\.__DATA__\s*=\s*(\{.*?\});',
                r'"players":\s*(\[.*?\])',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, script.string, re.DOTALL)
                for match in matches:
                    try:
                        data = json.loads(match)
                        if isinstance(data, list):
                            players = self._parse_players_from_json(data)
                            if players:
                                print(f"Found {len(players)} players from embedded JSON")
                                return players
                    except json.JSONDecodeError:
                        continue
        
        # Method 2: Look for data attributes or tables
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables")
        
        for table in tables:
            # Check if this is a player stats table
            headers = [th.get_text(strip=True).lower() for th in table.find_all('th')]
            if any(h in headers for h in ['pelaaja', 'player', 'nimi', 'name', 'ottelut', 'games']):
                players = self._parse_table(table)
                if players:
                    return players
        
        # Method 3: Try to find API calls in the page and call them directly
        api_urls = self._extract_api_urls(response.text)
        for api_url in api_urls[:3]:  # Try first few
            try:
                players = self._fetch_api_data(api_url)
                if players:
                    return players
            except Exception as e:
                print(f"API fetch failed for {api_url}: {e}")
                continue
        
        print("No player data found via standard scraping methods")
        return []
    
    def _parse_players_from_json(self, data: List[Dict]) -> List[Dict]:
        """Parse player data from JSON"""
        players = []
        
        for item in data:
            name = item.get('name') or f"{item.get('firstName', '')} {item.get('lastName', '')}".strip()
            nationality = item.get('nationality', '')
            
            if not self.is_finnish(name, nationality):
                continue
            
            player = {
                'player_id': f"liiga_{item.get('id', len(players))}",
                'name': name,
                'team': item.get('team', item.get('teamName', 'Unknown')),
                'league': 'Liiga',
                'position': item.get('position', 'F'),
                'games_played': item.get('games', item.get('gamesPlayed', 0)),
                'goals': item.get('goals', 0),
                'assists': item.get('assists', 0),
                'points': item.get('points', 0),
                'plus_minus': item.get('plusMinus', 0),
                'penalty_minutes': item.get('penaltyMinutes', item.get('pim', 0)),
                'save_percentage': None,
                'goals_against_average': None,
                'shutouts': None,
                'nationality': 'FIN',
                'source_league': 'liiga',
                'source': 'liiga.fi scrape',
                'scraped_at': datetime.now().isoformat()
            }
            players.append(player)
        
        return players
    
    def _parse_table(self, table) -> List[Dict]:
        """Parse player data from HTML table"""
        players = []
        rows = table.find_all('tr')
        
        # Find column indices from header
        header_row = rows[0] if rows else None
        if not header_row:
            return []
        
        headers = [th.get_text(strip=True).lower() for th in header_row.find_all(['th', 'td'])]
        
        # Map column names to indices
        col_map = {}
        for i, h in enumerate(headers):
            if any(x in h for x in ['pelaaja', 'player', 'nimi', 'name']):
                col_map['name'] = i
            elif any(x in h for x in ['joukkue', 'team', 'seura']):
                col_map['team'] = i
            elif any(x in h for x in ['ottelut', 'ott', 'gp', 'games']):
                col_map['games'] = i
            elif any(x in h for x in ['maalit', 'm', 'goals', 'g']):
                col_map['goals'] = i
            elif any(x in h for x in ['syötöt', 's', 'assists', 'a']):
                col_map['assists'] = i
            elif any(x in h for x in ['pisteet', 'p', 'points', 'pts']):
                col_map['points'] = i
        
        # Parse data rows
        for row in rows[1:]:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 4:
                continue
            
            name_idx = col_map.get('name', 1)
            if name_idx >= len(cells):
                continue
            
            name = cells[name_idx].get_text(strip=True)
            
            if not self.is_finnish(name):
                continue
            
            player = {
                'player_id': f"liiga_scrape_{len(players)}",
                'name': name,
                'team': cells[col_map.get('team', 2)].get_text(strip=True) if col_map.get('team', 2) < len(cells) else 'Unknown',
                'league': 'Liiga',
                'position': 'F',  # Default, could be parsed from another column
                'games_played': self._parse_int(cells[col_map.get('games', 3)]) if col_map.get('games', 3) < len(cells) else 0,
                'goals': self._parse_int(cells[col_map.get('goals', 4)]) if col_map.get('goals', 4) < len(cells) else 0,
                'assists': self._parse_int(cells[col_map.get('assists', 5)]) if col_map.get('assists', 5) < len(cells) else 0,
                'points': self._parse_int(cells[col_map.get('points', 6)]) if col_map.get('points', 6) < len(cells) else 0,
                'plus_minus': 0,
                'penalty_minutes': 0,
                'save_percentage': None,
                'goals_against_average': None,
                'shutouts': None,
                'nationality': 'FIN',
                'source_league': 'liiga',
                'source': 'liiga.fi scrape',
                'scraped_at': datetime.now().isoformat()
            }
            players.append(player)
        
        return players
    
    def _extract_api_urls(self, html: str) -> List[str]:
        """Extract potential API URLs from HTML"""
        urls = []
        
        # Look for fetch calls
        patterns = [
            r'["\'](https?://[^"\']*liiga\.fi[^"\']*api[^"\']*)["\']',
            r'["\'](https?://[^"\']*api[^"\']*liiga[^"\']*)["\']',
            r'["\'](/api/[^"\']*)["\']',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html)
            for match in matches:
                if match.startswith('/'):
                    match = f"{self.BASE_URL}{match}"
                urls.append(match)
        
        return list(set(urls))
    
    def _fetch_api_data(self, url: str) -> List[Dict]:
        """Fetch data from internal API"""
        response = self.session.get(url, timeout=30)
        data = response.json()
        
        if isinstance(data, list):
            return self._parse_players_from_json(data)
        elif isinstance(data, dict):
            # Look for player arrays in the response
            for key in ['players', 'data', 'items', 'results']:
                if key in data and isinstance(data[key], list):
                    return self._parse_players_from_json(data[key])
        
        return []
    
    def _parse_int(self, cell) -> int:
        """Parse integer from table cell"""
        try:
            text = cell.get_text(strip=True).replace(',', '')
            return int(text) if text.isdigit() else 0
        except:
            return 0


def main():
    """Test the scraper"""
    print("=" * 60)
    print("Liiga.fi Scraper Test")
    print("=" * 60)
    
    scraper = LiigaScraper()
    players = scraper.get_player_stats()
    
    print(f"\nFound {len(players)} Finnish players")
    
    if players:
        print("\nTop 10 by points:")
        for p in sorted(players, key=lambda x: x['points'], reverse=True)[:10]:
            print(f"  {p['name']} ({p['team']}): {p['goals']}G + {p['assists']}A = {p['points']}P")
    
    return players


if __name__ == "__main__":
    main()
