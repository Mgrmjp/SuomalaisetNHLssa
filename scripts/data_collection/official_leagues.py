#!/usr/bin/env python3
"""
Official League Websites Scraper
Collects Finnish player stats directly from league websites:
- AHL, ECHL, USHL, NAHL (USA)
- OHL, WHL, QMJHL (Canada)
- KHL, SHL, Liiga, DEL, NL, etc. (Europe)
"""
import requests
import json
import time
import re
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
from leagues import (
    DELAdapter, SwissNLAdapter, CzechExtraligaAdapter, ICEHLAdapter
)


class OfficialLeagueCollector:
    """Collect Finnish players from official league websites."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
        self.request_delay = 1.0
        
    def _make_request(self, url: str) -> Optional[str]:
        """Make rate-limited request."""
        time.sleep(self.request_delay)
        try:
            response = self.session.get(url, timeout=30)
            if response.status_code == 200:
                return response.text
        except Exception as e:
            print(f"  Error: {e}")
        return None
    
    def is_finnish(self, name: str, nationality: str = '', birthplace: str = '') -> bool:
        """Check if player is Finnish."""
        nat = nationality.strip().upper() if nationality else ''
        
        if nat in ['FI', 'FIN', 'FINLAND']:
            return True
        if birthplace and 'finland' in birthplace.lower():
            return True
        if any(char in name for char in 'äöåÄÖÅ'):
            return True
        parts = name.split()
        if parts:
            last_name = parts[-1] if len(parts) > 1 else ''
            if last_name.endswith(('nen', 'lä', 'lä', 'kkä', 'kkö', 'pää', 'rvi')):
                return True
        return False
    
    def _get_hockeytech_params(self, league_name: str, base_stats_url: str) -> Dict[str, str]:
        """Dynamically extract the valid key and season from the league's stats page."""
        try:
            print(f"  [{league_name}] Fetching valid API key...")
            html = self._make_request(base_stats_url)
            if not html:
                return {}
            
            # Try to find the API key in the page source
            # Keys are typically 16-char hex strings (e.g. 50c2cd9b5e18e390 or c69b9f5fa34c524c)
            key_match = re.search(r'key=([a-f0-9]{16})', html)
            season_match = re.search(r'season=([0-9]+)', html)
            client_match = re.search(r'client_code=([a-zA-Z0-9_]+)', html)
            
            if key_match and season_match:
                key = key_match.group(1)
                season = season_match.group(1)
                client_code = client_match.group(1) if client_match else league_name.lower()
                print(f"  [{league_name}] Found key: {key}, season: {season}")
                return {
                    'key': key,
                    'season': season,
                    'client_code': client_code
                }
        except Exception as e:
            print(f"  [{league_name}] Failed to extract params: {e}")
            
        return {}

    # USA LEAGUES
    
    def get_ahl_players(self, season: str = "2025-2026") -> List[Dict]:
        """Get AHL players from theahl.com via HockeyTech JSONP feed."""
        players = []
        
        # Try to extract the current key from the stats page (it rotates each season)
        ht_params = self._get_hockeytech_params('AHL', 'https://theahl.com/stats/player-stats')
        
        # Real AHL HockeyTech JSONP endpoint (discovered via browser network inspection)
        # Key and season are extracted dynamically, with fallbacks for 2025-26 season
        key = ht_params.get('key', 'ccb91f29d6744675') if ht_params else 'ccb91f29d6744675'
        ahl_season = ht_params.get('season', '90') if ht_params else '90'
        
        # AHL uses JSONP (Angular callback format), get all players sorted by points
        url = "https://lscluster.hockeytech.com/feed/index.php"
        params = {
            'feed': 'statviewfeed',
            'view': 'players',
            'season': ahl_season,
            'team': 'all',
            'position': 'skaters',
            'rookies': '0',
            'statsType': 'standard',
            'rosterstatus': 'undefined',
            'site_id': '3',
            'first': '0',
            'limit': '1000',
            'sort': 'points',
            'lang': 'en',
            'division': '-1',
            'conference': '-1',
            'key': key,
            'client_code': 'ahl',
            'league_id': '4',
            'callback': 'angular.callbacks._0',
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            if response.status_code == 200:
                # Response is JSONP: angular.callbacks._0([{...}])
                text = response.text.strip()
                # Strip JSONP wrapper
                json_str = re.sub(r'^[^(]+\(', '', text).rstrip(');').rstrip(')')
                data = json.loads(json_str)
                
                # AHL JSONP structure: [{sections: [{data: [{row: {...}, prop: {...}}, ...]}]}]
                # The 'row' key contains flat player fields (name, goals, assists, etc.)
                player_rows = []
                if isinstance(data, list):
                    for top_item in data:
                        for section in top_item.get('sections', []):
                            player_rows.extend(section.get('data', []))
                
                for item in player_rows:
                    row = item.get('row', {}) if isinstance(item, dict) else {}
                    name = row.get('name', '').strip()
                    team_code = row.get('team_code', '')
                    
                    if not name:
                        continue
                    # AHL doesn't expose nationality in the JSONP row, detect by name
                    if not self.is_finnish(name):
                        continue
                    
                    players.append({
                        'player_id': f"ahl_{row.get('player_id', '')}",
                        'name': name,
                        'team': team_code,
                        'league': 'AHL',
                        'position': row.get('position', 'F'),
                        'games_played': int(row.get('games_played', 0) or 0),
                        'goals': int(row.get('goals', 0) or 0),
                        'assists': int(row.get('assists', 0) or 0),
                        'points': int(row.get('points', 0) or 0),
                        'plus_minus': int(row.get('plus_minus', 0) or 0),
                        'penalty_minutes': int(row.get('penalty_minutes', 0) or 0),
                        'nationality': 'FIN',
                        'source': 'hockeytech',
                        'source_league': 'ahl',
                        'scraped_at': datetime.now().isoformat()
                    })
        except Exception as e:
            print(f"  AHL error: {e}")
        
        print(f"  AHL: {len(players)} Finnish players")
        return players
    
    def _parse_modulekit_skaters(self, data: dict, league: str, league_code: str) -> List[Dict]:
        """Parse HockeyTech modulekit SiteKit.Skaters response."""
        players = []
        skaters = data.get('SiteKit', {}).get('Skaters', [])
        for p in skaters:
            first = p.get('first_name', '')
            last = p.get('last_name', '')
            name = f"{first} {last}".strip()
            if not name:
                continue
            # Nationality field is empty in CHL response; use name-based detection
            if not self.is_finnish(name):
                continue
            players.append({
                'player_id': f"{league_code}_{p.get('player_id', '')}",
                'name': name,
                'team': p.get('team_name', p.get('team_code', 'Unknown')),
                'league': league,
                'position': p.get('position', 'F'),
                'games_played': int(p.get('games_played', 0) or 0),
                'goals': int(p.get('goals', 0) or 0),
                'assists': int(p.get('assists', 0) or 0),
                'points': int(p.get('points', 0) or 0),
                'plus_minus': int(p.get('plus_minus', 0) or 0),
                'penalty_minutes': int(p.get('penalty_minutes', 0) or 0),
                'nationality': 'FIN',
                'source': 'hockeytech-modulekit',
                'source_league': league_code,
                'scraped_at': datetime.now().isoformat()
            })
        return players

    def get_echl_players(self, season: str = "2025-2026") -> List[Dict]:
        """Get ECHL players via livewire HockeyTech JSONP endpoint."""
        players = []
        
        # ECHL uses livewire.echl.com (custom subdomain), key discovered via browser inspection
        # season_id=74 corresponds to 2025-26 season
        url = "https://livewire.echl.com/feed/index.php"
        params = {
            'feed': 'statviewfeed',
            'view': 'players',
            'season': '74',
            'team': 'all',
            'position': 'skaters',
            'rookies': '0',
            'statsType': 'standard',
            'rosterstatus': 'undefined',
            'site_id': '0',
            'first': '0',
            'limit': '1000',
            'sort': 'points',
            'lang': 'en',
            'division': '-1',
            'conference': '-1',
            'key': '7648342416f0e4b8',
            'client_code': 'echl',
            'callback': 'angular.callbacks._0',
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            if response.status_code == 200:
                text = response.text.strip()
                json_str = re.sub(r'^[^(]+\(', '', text).rstrip(');').rstrip(')')
                data = json.loads(json_str)
                # Same structure as AHL: data[0].sections[*].data[*].row
                for top_item in (data if isinstance(data, list) else []):
                    for section in top_item.get('sections', []):
                        for item in section.get('data', []):
                            row = item.get('row', {})
                            name = row.get('name', '').strip()
                            if not name or not self.is_finnish(name):
                                continue
                            players.append({
                                'player_id': f"echl_{row.get('player_id', '')}",
                                'name': name,
                                'team': row.get('team_code', 'Unknown'),
                                'league': 'ECHL',
                                'position': row.get('position', 'F'),
                                'games_played': int(row.get('games_played', 0) or 0),
                                'goals': int(row.get('goals', 0) or 0),
                                'assists': int(row.get('assists', 0) or 0),
                                'points': int(row.get('points', 0) or 0),
                                'plus_minus': int(row.get('plus_minus', 0) or 0),
                                'penalty_minutes': int(row.get('penalty_minutes', 0) or 0),
                                'nationality': 'FIN',
                                'source': 'hockeytech',
                                'source_league': 'echl',
                                'scraped_at': datetime.now().isoformat()
                            })
            else:
                print(f"  ECHL HTTP {response.status_code}")
        except Exception as e:
            print(f"  ECHL error: {e}")
        
        print(f"  ECHL: {len(players)} Finnish players")
        return players
    
    def get_ushl_players(self, season: str = "2025-2026") -> List[Dict]:
        """Get USHL players via HockeyTech JSONP (same structure as AHL)."""
        players = []
        
        # Key discovered via browser network inspection (March 2026)
        # season=88 = 2025-26 USHL season
        url = "https://lscluster.hockeytech.com/feed/index.php"
        params = {
            'feed': 'statviewfeed',
            'view': 'players',
            'season': '88',
            'team': 'all',
            'position': 'skaters',
            'rookies': '0',
            'statsType': 'standard',
            'rosterstatus': 'undefined',
            'site_id': '0',
            'first': '0',
            'limit': '1000',
            'sort': 'points',
            'lang': 'en',
            'division': '-1',
            'conference': '-1',
            'key': 'e828f89b243dc43f',
            'client_code': 'ushl',
            'league_id': '1',
            'callback': 'angular.callbacks._0',
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            if response.status_code == 200:
                text = response.text.strip()
                json_str = re.sub(r'^[^(]+\(', '', text).rstrip(');').rstrip(')')
                data = json.loads(json_str)
                for top_item in (data if isinstance(data, list) else []):
                    for section in top_item.get('sections', []):
                        for item in section.get('data', []):
                            row = item.get('row', {})
                            name = row.get('name', '').strip()
                            if not name or not self.is_finnish(name):
                                continue
                            players.append({
                                'player_id': f"ushl_{row.get('player_id', '')}",
                                'name': name,
                                'team': row.get('team_code', 'Unknown'),
                                'league': 'USHL',
                                'position': row.get('position', 'F'),
                                'games_played': int(row.get('games_played', 0) or 0),
                                'goals': int(row.get('goals', 0) or 0),
                                'assists': int(row.get('assists', 0) or 0),
                                'points': int(row.get('points', 0) or 0),
                                'plus_minus': int(row.get('plus_minus', 0) or 0),
                                'penalty_minutes': int(row.get('penalty_minutes', 0) or 0),
                                'nationality': 'FIN',
                                'source': 'hockeytech',
                                'source_league': 'ushl',
                                'scraped_at': datetime.now().isoformat()
                            })
            else:
                print(f"  USHL HTTP {response.status_code}")
        except Exception as e:
            print(f"  USHL error: {e}")
        
        print(f"  USHL: {len(players)} Finnish players")
        return players
    
    def get_nahl_players(self, season: str = "2025-2026") -> List[Dict]:
        """Get NAHL players. NAHL uses GameSheet API (requires partner key) - skip gracefully."""
        # NAHL migrated from HockeyTech to GameSheet API which requires a partner API key
        # Very few if any Finnish players are in the NAHL, so we skip this league
        print("  NAHL: Skipping (GameSheet API requires partner key)")
        return []
    
    # CANADIAN MAJOR JUNIOR
    
    def get_ohl_players(self, season: str = "2025-2026") -> List[Dict]:
        """Get OHL players via HockeyTech modulekit (SiteKit.Skaters)."""
        players = []
        
        # Key f1aa699db3d81487 shared across all CHL leagues; season_id=83 = 2025-26
        url = "https://lscluster.hockeytech.com/feed/"
        params = {
            'feed': 'modulekit',
            'key': 'f1aa699db3d81487',
            'view': 'skaters',
            'client_code': 'ohl',
            'season_id': '83',
            'fmt': 'json'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            if response.status_code == 200:
                players = self._parse_modulekit_skaters(response.json(), 'OHL', 'ohl')
            else:
                print(f"  OHL HTTP {response.status_code}")
        except Exception as e:
            print(f"  OHL error: {e}")
        
        print(f"  OHL: {len(players)} Finnish players")
        return players
    
    def get_whl_players(self, season: str = "2025-2026") -> List[Dict]:
        """Get WHL players via HockeyTech modulekit (SiteKit.Skaters)."""
        players = []
        
        # season_id=289 = 2025-26 WHL season
        url = "https://lscluster.hockeytech.com/feed/"
        params = {
            'feed': 'modulekit',
            'key': 'f1aa699db3d81487',
            'view': 'skaters',
            'client_code': 'whl',
            'season_id': '289',
            'fmt': 'json'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            if response.status_code == 200:
                players = self._parse_modulekit_skaters(response.json(), 'WHL', 'whl')
            else:
                print(f"  WHL HTTP {response.status_code}")
        except Exception as e:
            print(f"  WHL error: {e}")
        
        print(f"  WHL: {len(players)} Finnish players")
        return players
    
    def get_qmjhl_players(self, season: str = "2025-2026") -> List[Dict]:
        """Get QMJHL players via HockeyTech modulekit (SiteKit.Skaters)."""
        players = []
        
        # season_id=211 = 2025-26 QMJHL/LHJMQ season; client_code is 'lhjmq'
        url = "https://lscluster.hockeytech.com/feed/"
        params = {
            'feed': 'modulekit',
            'key': 'f1aa699db3d81487',
            'view': 'skaters',
            'client_code': 'lhjmq',
            'season_id': '211',
            'fmt': 'json'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            if response.status_code == 200:
                players = self._parse_modulekit_skaters(response.json(), 'QMJHL', 'qmjhl')
            else:
                print(f"  QMJHL HTTP {response.status_code}")
        except Exception as e:
            print(f"  QMJHL error: {e}")
        
        print(f"  QMJHL: {len(players)} Finnish players")
        return players
    
    # EUROPEAN LEAGUES
    
    def get_khl_players(self, season: str = "2025-2026") -> List[Dict]:
        """Get KHL players."""
        players = []
        
        # KHL uses different API
        url = "https://api.khl.ru/v1/players"
        
        # Try to get data
        try:
            response = self.session.get(url, timeout=30)
            if response.status_code == 200:
                data = response.json()
                # Parse KHL data
                if 'players' in data:
                    for player in data['players']:
                        name = f"{player.get('name', {}).get('first', '')} {player.get('name', {}).get('last', '')}".strip()
                        if self.is_finnish(name):
                            players.append({
                                'player_id': f"khl_{player.get('id', '')}",
                                'name': name,
                                'team': player.get('team', {}).get('name', 'Unknown'),
                                'league': 'KHL',
                                'position': player.get('position', 'F'),
                                'games_played': player.get('games', 0),
                                'goals': player.get('goals', 0),
                                'assists': player.get('assists', 0),
                                'points': player.get('points', 0),
                                'plus_minus': player.get('plusMinus', 0),
                                'penalty_minutes': player.get('penaltyMinutes', 0),
                                'nationality': 'FIN',
                                'source': 'khl-api',
                                'source_league': 'khl',
                                'scraped_at': datetime.now().isoformat()
                            })
        except Exception as e:
            print(f"  KHL error: {e}")
        
        print(f"  KHL: {len(players)} Finnish players")
        return players
    
    def get_shl_players(self, season: str = "2025-2026") -> List[Dict]:
        """Get SHL players from the stats-v2 API (React SPA, not the old /p/api endpoint).
        
        The SHL website is a React SPA - the old URL returns HTML.
        Real data comes from /api/statistics-v2/stats-info/players_summary.
        Season UUID 'iuzqg7dqk9' = 2025-26 season (discovered via browser network inspection).
        Each stat row has an 'info' object with fullName, nationality, team.
        """
        players = []
        
        url = "https://www.shl.se/api/statistics-v2/stats-info/players_summary"
        params = {
            'count': '1000',
            'ssgtUuid': 'iuzqg7dqk9',  # 2025-26 season UUID
            'provider': 'statnet',
        }
        headers = {
            'Accept': 'application/json',
            'x-s8y-instance-id': 'shl1_shl',
            'Referer': 'https://www.shl.se/statistik/spelare',
        }
        
        try:
            response = self.session.get(url, params=params, headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                # Response is a list with one object; stats are in data[0]['stats']
                # Each stat row has an 'info' key with player details
                stats = data[0].get('stats', []) if data else []
                for row in stats:
                    info = row.get('info', {})
                    name = info.get('fullName', '').strip()
                    nat = info.get('nationality', '')
                    if not name:
                        continue
                    if not self.is_finnish(name, nat):
                        continue
                    team = info.get('team', {}).get('name', 'Unknown') if isinstance(info.get('team'), dict) else 'Unknown'
                    players.append({
                        'player_id': f"shl_{info.get('uuid', '')}",
                        'name': name,
                        'team': team,
                        'league': 'SHL',
                        'position': info.get('position', 'F'),
                        'games_played': int(row.get('GP', 0) or 0),
                        'goals': int(row.get('G', 0) or 0),
                        'assists': int(row.get('A', 0) or 0),
                        'points': int(row.get('TP', 0) or 0),
                        'plus_minus': int(row.get('PlusMinus', 0) or 0),
                        'penalty_minutes': int(row.get('PIM', 0) or 0),
                        'nationality': nat or 'FIN',
                        'source': 'shl-statsv2',
                        'source_league': 'shl',
                        'scraped_at': datetime.now().isoformat()
                    })
            else:
                print(f"  SHL HTTP {response.status_code}")
        except Exception as e:
            print(f"  SHL error: {e}")
        
        print(f"  SHL: {len(players)} Finnish players")
        return players
    
    def get_liiga_players(self, season: str = "2025-2026") -> List[Dict]:
        """Get Liiga players from liiga.fi v2 API."""
        players = []
        
        # Discovered API: /api/v2/players/stats/summed/{startYear}/{endYear}/{tournament}/false
        # Season 2025-26 => year 2026
        year_end = int(season.split('-')[1]) if '-' in season else datetime.now().year + 1
        
        url = f"https://www.liiga.fi/api/v2/players/stats/summed/{year_end}/{year_end}/runkosarja/false"
        params = {
            'dataType': 'basicStats',
            'splitTeams': 'true',
            'team': ''
        }
        
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://www.liiga.fi/fi/tilastot/pelaajatilastot/',
        }
        
        try:
            response = self.session.get(url, params=params, headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                for player in (data if isinstance(data, list) else []):
                    first = player.get('firstName', '')
                    last = player.get('lastName', '')
                    nat = player.get('nationality', '')
                    name = f"{first} {last}".strip()
                    
                    if not self.is_finnish(name, nat):
                        continue
                    
                    players.append({
                        'player_id': f"liiga_{player.get('playerId', '')}",
                        'name': name,
                        'team': player.get('teamName', 'Unknown'),
                        'league': 'Liiga',
                        'position': player.get('role', 'F'),
                        'games_played': player.get('games', 0),
                        'goals': player.get('goals', 0),
                        'assists': player.get('assists', 0),
                        'points': player.get('points', 0),
                        'plus_minus': player.get('plusMinus', 0),
                        'penalty_minutes': player.get('penaltyMinutes', 0),
                        'nationality': nat or 'FIN',
                        'source': 'liiga-api-v2',
                        'source_league': 'liiga',
                        'scraped_at': datetime.now().isoformat()
                    })
            else:
                print(f"  Liiga HTTP {response.status_code}")
        except Exception as e:
            print(f"  Liiga error: {e}")
        
        print(f"  Liiga: {len(players)} Finnish players")
        return players
    
    def get_del_players(self, season: str = "2025-2026") -> List[Dict]:
        """Get DEL players using specialized adapter."""
        print(f"  [DEL] Fetching players using DELAdapter...")
        try:
            adapter = DELAdapter()
            players = adapter.get_all_players(season)
            return [p.to_dict() for p in players]
        except Exception as e:
            print(f"  DEL error: {e}")
            return []
    
    def get_nl_players(self, season: str = "2025-2026") -> List[Dict]:
        """Get NL players using specialized adapter."""
        print(f"  [NL] Fetching players using SwissNLAdapter...")
        try:
            adapter = SwissNLAdapter()
            players = adapter.get_all_players(season)
            return [p.to_dict() for p in players]
        except Exception as e:
            print(f"  NL error: {e}")
            return []
    
    def get_czech_players(self, season: str = "2025-2026") -> List[Dict]:
        """Get Czech players using specialized adapter."""
        print(f"  [Czech] Fetching players using CzechExtraligaAdapter...")
        try:
            adapter = CzechExtraligaAdapter()
            players = adapter.get_all_players(season)
            return [p.to_dict() for p in players]
        except Exception as e:
            print(f"  Czech error: {e}")
            return []
    
    def get_icehl_players(self, season: str = "2025-2026") -> List[Dict]:
        """Get ICEHL players using specialized adapter."""
        print(f"  [ICEHL] Fetching players using ICEHLAdapter...")
        try:
            adapter = ICEHLAdapter()
            players = adapter.get_all_players(season)
            return [p.to_dict() for p in players]
        except Exception as e:
            print(f"  ICEHL error: {e}")
            return []
        
        try:
            response = self.session.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                for player in (data if isinstance(data, list) else []):
                    nat = player.get('nationality', '')
                    name = player.get('name', f"{player.get('firstname', '')} {player.get('surname', '')}").strip()
                    
                    if not name:
                        continue
                    if not self.is_finnish(name, nat):
                        continue
                    
                    stats = player.get('statistics', {})
                    
                    def sum_stat(key):
                        v = stats.get(key, {})
                        if isinstance(v, dict):
                            return int((v.get('home', 0) or 0) + (v.get('away', 0) or 0))
                        return int(v or 0)
                    
                    players.append({
                        'player_id': f"icehl_{player.get('id', '')}",
                        'name': name,
                        'team': stats.get('teamShortcut', 'Unknown'),
                        'league': 'ICEHL',
                        'position': player.get('position', 'F'),
                        'games_played': int(stats.get('games', 0) or 0),
                        'goals': sum_stat('goals'),
                        'assists': sum_stat('assists'),
                        'points': sum_stat('points'),
                        'plus_minus': int(stats.get('plusMinus', 0) or 0),
                        'penalty_minutes': int(stats.get('penaltyMinutes', 0) or 0),
                        'nationality': 'FIN',
                        'source': 'icehl-hokejovyzapis',
                        'source_league': 'icehl',
                        'scraped_at': datetime.now().isoformat()
                    })
            else:
                print(f"  ICEHL HTTP {response.status_code}")
        except Exception as e:
            print(f"  ICEHL error: {e}")
        
        print(f"  ICEHL: {len(players)} Finnish players")
        return players
    
    def collect_all(self, season: str = "2025-2026") -> Dict:
        """Collect from all leagues."""
        results = {
            'generated_at': datetime.now().isoformat(),
            'season': season,
            'data_source': 'official-league-websites',
            'leagues': {},
            'players': []
        }
        
        print("=" * 60)
        print("Collecting from Official League Websites")
        print("=" * 60)
        
        # USA
        print("\n--- USA LEAGUES ---")
        results['players'].extend(self.get_ahl_players(season))
        results['leagues']['ahl'] = len([p for p in results['players'] if p['source_league'] == 'ahl'])
        
        results['players'].extend(self.get_echl_players(season))
        results['leagues']['echl'] = len([p for p in results['players'] if p['source_league'] == 'echl'])
        
        results['players'].extend(self.get_ushl_players(season))
        results['leagues']['ushl'] = len([p for p in results['players'] if p['source_league'] == 'ushl'])
        
        results['players'].extend(self.get_nahl_players(season))
        results['leagues']['nahl'] = len([p for p in results['players'] if p['source_league'] == 'nahl'])
        
        # Canada
        print("\n--- CANADIAN LEAGUES ---")
        results['players'].extend(self.get_ohl_players(season))
        results['leagues']['ohl'] = len([p for p in results['players'] if p['source_league'] == 'ohl'])
        
        results['players'].extend(self.get_whl_players(season))
        results['leagues']['whl'] = len([p for p in results['players'] if p['source_league'] == 'whl'])
        
        results['players'].extend(self.get_qmjhl_players(season))
        results['leagues']['qmjhl'] = len([p for p in results['players'] if p['source_league'] == 'qmjhl'])
        
        # Europe
        print("\n--- EUROPEAN LEAGUES ---")
        results['players'].extend(self.get_khl_players(season))
        results['leagues']['khl'] = len([p for p in results['players'] if p['source_league'] == 'khl'])
        
        results['players'].extend(self.get_shl_players(season))
        results['leagues']['shl'] = len([p for p in results['players'] if p['source_league'] == 'shl'])
        
        results['players'].extend(self.get_liiga_players(season))
        results['leagues']['liiga'] = len([p for p in results['players'] if p['source_league'] == 'liiga'])
        
        results['players'].extend(self.get_del_players(season))
        results['leagues']['del'] = len([p for p in results['players'] if p['source_league'] == 'del'])
        
        results['players'].extend(self.get_nl_players(season))
        results['leagues']['nl'] = len([p for p in results['players'] if p['source_league'] == 'nl'])
        
        results['players'].extend(self.get_czech_players(season))
        results['leagues']['czech'] = len([p for p in results['players'] if p['source_league'] == 'czech'])
        
        results['players'].extend(self.get_icehl_players(season))
        results['leagues']['icehl'] = len([p for p in results['players'] if p['source_league'] == 'icehl'])
        
        # Sort by points
        results['players'].sort(key=lambda x: x.get('points', 0), reverse=True)
        results['total_players'] = len(results['players'])
        
        return results


def save_data(data: Dict, filename: str = "league_prospects_official.json"):
    """Save scraped data to JSON."""
    output_dir = Path(__file__).parent.parent / 'static' / 'data' / 'leagues'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / filename
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Data saved to {output_path}")
    return output_path


def main():
    """Main entry point."""
    print("=" * 70)
    print("Official League Websites - Finnish Prospect Collector")
    print("=" * 70)
    print()
    
    collector = OfficialLeagueCollector()
    
    # Get current season: NHL/hockey seasons run Sept-June
    # So if current month < 9 (September), we're in the season PREV-CURRENT year
    current_year = datetime.now().year
    current_month = datetime.now().month
    if current_month < 9:  # Jan-Aug: still in the season that started last fall
        season = f"{current_year - 1}-{current_year}"
    else:  # Sept-Dec: new season has started
        season = f"{current_year}-{current_year + 1}"
    
    results = collector.collect_all(season)
    
    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total Finnish players: {results['total_players']}")
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
    
    return results


if __name__ == "__main__":
    main()
