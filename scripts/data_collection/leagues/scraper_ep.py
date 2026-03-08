"""
EliteProspects web scraper
Scrapes player statistics from eliteprospects.com
"""
import requests
import re
import time
from typing import List, Dict, Optional
from datetime import datetime

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False


class EliteProspectsScraper:
    """Scrape player data from EliteProspects"""
    
    BASE_URL = "https://www.eliteprospects.com"
    
    # League slugs for EP
    # Comprehensive list of leagues with Finnish players
    LEAGUES = {
        # 🇫🇮 Finland
        'liiga': 'liiga',
        'mestis': 'mestis',  # Finnish 2nd tier
        
        # 🇸🇪 Sweden
        'shl': 'shl',  # Swedish Hockey League
        'hockeyallsvenskan': 'hockeyallsvenskan',  # Swedish 2nd tier
        
        # 🇩🇪 Germany
        'del': 'del',  # Deutsche Eish Hockey Liga
        
        # 🇨🇭 Switzerland
        'nl': 'nl',  # National League (Swiss)
        
        # 🇨🇿 Czech Republic
        'czech': 'czech',  # Czech Extraliga
        
        # 🇸🇰 Slovakia
        'slovakia': 'slovakia',  # Slovak Extraliga
        'extraliga': 'slovakia',  # Alias
        
        # 🇦🇹🇮🇹🇸🇮 Multinational
        'icehl': 'icehl',  # ICE Hockey League (Austria, Italy, Slovenia, Hungary)
        
        # 🇫🇷 France
        'ligue-magnus': 'ligue-magnus',  # Synerglace Ligue Magnus
        
        # 🇵🇱 Poland
        'phl': 'poland',  # Polska Hokej Liga
        'poland': 'poland',
        
        # 🇬🇧 UK
        'eihl': 'eihl',  # Elite Ice Hockey League
        
        # 🇷🇺 Russia
        'khl': 'khl',
        'vhl': 'vhl',  # Russian 2nd tier
        
        # 🇺🇸🇨🇦 North America - Professional
        'ahl': 'ahl',
        'echl': 'echl',
        'sphl': 'sphl',  # Southern Professional Hockey League
        
        # 🇺🇸🇨🇦 North America - Junior
        'whl': 'whl',  # Western Hockey League
        'ohl': 'ohl',  # Ontario Hockey League
        'qmjhl': 'qmjhl',  # Quebec Major Junior Hockey League
        'ushl': 'ushl',  # United States Hockey League
        'nahl': 'nahl',  # North American Hockey League
        'na3hl': 'na3hl',  # North American 3A Hockey League
        'bchl': 'bchl',  # British Columbia Hockey League
        'ajhl': 'ajhl',  # Alberta Junior Hockey League
        'usphl': 'usphl',  # United States Premier Hockey League
        'ehl': 'ehl',  # Eastern Hockey League
        
        # 🇺🇸🇨🇦 College
        'ncaa': 'ncaa',
    }
    
    def __init__(self):
        if not BS4_AVAILABLE:
            raise ImportError("beautifulsoup4 required. Install: pip install beautifulsoup4")
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
        })
        self.request_delay = 1  # Be nice to the server
    
    def is_finnish(self, name: str, nationality: str = '') -> bool:
        """
        Check if player is Finnish based on name patterns
        
        Note: EliteProspects stats tables don't show nationality,
        so we detect based on name heuristics. This may have some
        false positives (e.g., Swedish players with Finnish names).
        """
        name = name.strip()
        nat = nationality.strip().upper()
        
        # Direct nationality match
        if nat in ['FI', 'FIN', 'FINLAND']:
            return True
        
        # Finnish characters (ä, ö, å) - VERY strong indicator
        # Almost only Finnish names use these in hockey context
        if any(char in name for char in 'äöåÄÖÅ'):
            return True
        
        # Surname analysis
        parts = name.split()
        if not parts:
            return False
        
        # Check last name (surname) for Finnish patterns
        last_name = parts[-1] if len(parts) > 1 else ''
        
        # -nen ending is ~40% of Finnish surnames (very specific)
        if last_name.endswith('nen'):
            return True
        
        # Other Finnish surname endings
        finnish_endings = ('lä', 'lä', 'kkä', 'kkö', 'pää', 'rvi', 'sto', 'nta')
        if last_name.endswith(finnish_endings):
            # But check it's not a common Swedish/Norwegian name that happens to match
            not_finnish = ('gustafsson', 'andersson', 'johansson', 'karlsson',
                          'nilsson', 'ericsson', 'larsson', 'persson')
            if last_name.lower() not in not_finnish:
                return True
        
        return False
    
    def get_league_stats(self, league: str, season: str) -> List[Dict]:
        """
        Get player statistics for a league
        
        Args:
            league: League slug (liiga, shl, ahl, etc.)
            season: Season string (e.g., "2024-2025")
        """
        league_slug = self.LEAGUES.get(league.lower())
        if not league_slug:
            raise ValueError(f"Unknown league: {league}")
        
        url = f"{self.BASE_URL}/league/{league_slug}/stats/{season}"
        print(f"Fetching {url}...")
        
        try:
            time.sleep(self.request_delay)  # Rate limiting
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
        except Exception as e:
            print(f"Error fetching page: {e}")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the stats table
        # EliteProspects uses specific table classes
        players = []
        
        # Look for the main stats table
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables")
        
        for table in tables:
            # Check if this is a player stats table
            # EP tables usually have class 'table' or specific data attributes
            rows = table.find_all('tr')
            if len(rows) < 2:
                continue
            
            # Parse header
            header_cells = rows[0].find_all(['th', 'td'])
            headers = [cell.get_text(strip=True).lower() for cell in header_cells]
            
            # Check if this looks like a player stats table
            # Must have player name AND at least one stat column
            has_player_col = any(h in headers for h in ['player', 'pelaaja', 'name', 'nimi'])
            has_stat_col = any(h in headers for h in ['gp', 'games', 'ott', 'ottelut', 'g', 'goals', 'tp', 'pts'])
            
            if not has_player_col or not has_stat_col:
                continue
            
            print(f"Found stats table with {len(rows)} rows, headers: {headers[:5]}...")
            
            # Map column indices
            col_map = self._map_columns(headers)
            
            # Parse data rows
            for row in rows[1:]:
                player = self._parse_row(row, col_map, league.upper())
                if not player:
                    continue
                is_finn = self.is_finnish(player['name'], player.get('nationality', ''))
    
                if is_finn:
                    players.append(player)
        
        return players
    
    def _map_columns(self, headers: List[str]) -> Dict[str, int]:
        """Map column names to indices"""
        col_map = {}
        
        for i, h in enumerate(headers):
            h_lower = h.lower().strip()
            
            # EliteProspects column names
            if h_lower in ['player', 'pelaaja', 'name', 'nimi']:
                col_map['name'] = i
            elif h_lower in ['team', 'joukkue', 'seura']:
                col_map['team'] = i
            elif h_lower in ['gp', 'ott', 'games', 'ottelut']:
                col_map['games'] = i
            elif h_lower == 'g' or h_lower == 'goals' or h_lower == 'maalit':
                col_map['goals'] = i
            elif h_lower == 'a' or h_lower == 'assists' or h_lower == 'syötöt':
                col_map['assists'] = i
            elif h_lower in ['tp', 'pts', 'points', 'pisteet']:
                col_map['points'] = i
            elif h_lower in ['+/-', 'plus/minus', 'plusmiinus']:
                col_map['plus_minus'] = i
            elif h_lower in ['pim', 'penalty', 'min']:
                col_map['pim'] = i
            elif h_lower in ['nat', 'nationality', 'kansalaisuus']:
                col_map['nationality'] = i
            elif h_lower == '#':
                col_map['rank'] = i
        
        return col_map
    
    def _parse_row(self, row, col_map: Dict, league_name: str) -> Optional[Dict]:
        """Parse a single player row"""
        cells = row.find_all(['td', 'th'])
        if not cells:
            return None
        
        # Get name
        name_idx = col_map.get('name')
        if name_idx is None or name_idx >= len(cells):
            return None
        
        name_cell = cells[name_idx]
        
        # Try to find player link
        link = name_cell.find('a')
        if link:
            name_text = link.get_text(strip=True)
            player_url = link.get('href', '')
            player_id = player_url.split('/')[-1] if player_url else f"unknown_{hash(name_text)}"
        else:
            name_text = name_cell.get_text(strip=True)
            player_id = f"unknown_{hash(name_text)}"
        
        if not name_text:
            return None
        
        # Parse name and position (format: "Name (Position)")
        # e.g., "Atro Leppänen (D)", "Connor McDavid (F)", "Player (C/RW)"
        name = name_text
        position = 'F'  # Default
        
        # Handle position formats like (D), (C), (G), (C/RW), (RW/LW), etc.
        match = re.match(r'(.+?)\s*\(([A-Z/]+)\)\s*$', name_text)
        if match:
            name = match.group(1).strip()
            pos = match.group(2)
            # Take first position if multiple (e.g., C/RW -> C)
            position = pos.split('/')[0] if '/' in pos else pos
        
        # Get other fields
        def get_cell_text(idx, default=''):
            if idx is not None and idx < len(cells):
                return cells[idx].get_text(strip=True)
            return default
        
        def parse_int(val):
            try:
                return int(val.replace(',', '')) if val else 0
            except:
                return 0
        
        def parse_float(val):
            try:
                return float(val.replace(',', '')) if val else 0.0
            except:
                return 0.0
        
        nationality = get_cell_text(col_map.get('nationality'))
        
        # Check if this looks like a goalie (based on position or stats)
        is_goalie = position == 'G'
        
        player = {
            'player_id': f"ep_{player_id}",
            'name': name,
            'team': get_cell_text(col_map.get('team'), 'Unknown'),
            'league': league_name,
            'position': position,
            'games_played': parse_int(get_cell_text(col_map.get('games'))),
            'goals': parse_int(get_cell_text(col_map.get('goals'))),
            'assists': parse_int(get_cell_text(col_map.get('assists'))),
            'points': parse_int(get_cell_text(col_map.get('points'))),
            'plus_minus': parse_int(get_cell_text(col_map.get('plus_minus'))) if col_map.get('plus_minus') else 0,
            'penalty_minutes': parse_int(get_cell_text(col_map.get('pim'))) if col_map.get('pim') else 0,
            'save_percentage': None,
            'goals_against_average': None,
            'shutouts': None,
            'nationality': nationality or '',
            'source_league': league_name.lower(),
            'source': 'eliteprospects',
            'scraped_at': datetime.now().isoformat()
        }
        
        return player
    
    def collect_all_leagues(self, season: str = "2024-2025", league_list: List[str] = None) -> Dict:
        """Collect data from all supported leagues
        
        Args:
            season: Season string (e.g., "2024-2025")
            league_list: Optional list of specific leagues to collect. 
                        If None, collects from priority leagues.
        """
        results = {
            'generated_at': datetime.now().isoformat(),
            'season': season,
            'data_source': 'eliteprospects-scrape',
            'leagues': {},
            'players': []
        }
        
        # Priority leagues (most likely to have Finnish players)
        # Add more leagues as needed
        priority_leagues = [
            # Finnish leagues
            'liiga', 'mestis',
            # Swedish leagues
            'shl', 'hockeyallsvenskan',
            # German
            'del',
            # Swiss
            'nl',
            # Czech
            'czech',
            # North American pro
            'ahl', 'echl',
            # CHL (major junior)
            'whl', 'ohl', 'qmjhl',
            # US junior
            'ushl', 'nahl',
            # NCAA
            'ncaa',
            # European
            'khl', 'vhl',
            # More European
            'icehl', 'slovakia',
        ]
        
        leagues_to_collect = league_list if league_list else priority_leagues
        
        for league_name in leagues_to_collect:
            # Skip if league not in our supported list
            if league_name not in self.LEAGUES:
                print(f"Skipping unsupported league: {league_name}")
                continue
                
            print(f"\n{'='*60}")
            print(f"Collecting {league_name.upper()}")
            print('='*60)
            
            try:
                players = self.get_league_stats(league_name, season)
                results['leagues'][league_name] = len(players)
                results['players'].extend(players)
                print(f"Found {len(players)} Finnish players")
            except Exception as e:
                print(f"Error: {e}")
                results['leagues'][league_name] = 0
        
        # Sort by points
        results['players'].sort(key=lambda x: x['points'], reverse=True)
        results['total_players'] = len(results['players'])
        
        return results


def save_data(data: Dict, filename: str = "league_prospects_ep.json"):
    """Save scraped data to JSON"""
    import json
    from pathlib import Path
    
    output_dir = Path(__file__).parent.parent.parent.parent / 'static' / 'data' / 'leagues'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / filename
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Data saved to {output_path}")
    return output_path


def main():
    """Test the scraper"""
    print("=" * 70)
    print("EliteProspects Scraper - Finnish Prospect Collection")
    print("=" * 70)
    print("\n⚠️  Note: Please respect EliteProspects' terms of service")
    print("    This scraper includes rate limiting (1 sec between requests)")
    print("    Only collects publicly available statistics")
    print()
    
    try:
        scraper = EliteProspectsScraper()
        
        # Collect from all leagues
        results = scraper.collect_all_leagues('2025-2026')
        
        # Print summary
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Total Finnish prospects: {results['total_players']}")
        print("\nBy league:")
        for league, count in results['leagues'].items():
            print(f"  {league.upper()}: {count} players")
        
        # Show top prospects
        if results['players']:
            print("\nTop 20 Finnish prospects by points:")
            for i, p in enumerate(results['players'][:20], 1):
                print(f"  {i}. {p['name']} ({p['league']}, {p['team']}): {p['goals']}G + {p['assists']}A = {p['points']}P")
        
        # Save data
        save_data(results)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
