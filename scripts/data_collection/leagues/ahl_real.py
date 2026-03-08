"""
Real AHL data collector using theahl.com API
"""
import requests
import json
from datetime import datetime
from typing import List, Dict, Optional


class AHLRealCollector:
    """Collects real AHL data"""
    
    BASE_URL = "https://lscluster.hockeytech.com/feed"
    API_KEY = "c69b9f5fa34c524c"  # Public API key used by theahl.com
    CLIENT_CODE = "ahl"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://theahl.com/'
        })
    
    def get_current_season(self) -> str:
        """Get current season"""
        now = datetime.now()
        if now.month >= 9:
            return f"{now.year}{now.year + 1}"
        else:
            return f"{now.year - 1}{now.year}"
    
    def get_skater_stats(self, season: Optional[str] = None) -> List[Dict]:
        """Get skater statistics"""
        season = season or self.get_current_season()
        url = f"{self.BASE_URL}"
        params = {
            'feed': 'statviewfeed',
            'view': 'players',
            'group': 'skaters',
            'context': 'league',
            'league_code': self.CLIENT_CODE,
            'season': season,
            'key': self.API_KEY,
            'client_code': self.CLIENT_CODE,
            'language': 'en',
            'fmt': 'json'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'siteKit' in data:
                    return data['siteKit'].get('players', [])
                return data if isinstance(data, list) else []
        except Exception as e:
            print(f"Error fetching AHL skater stats: {e}")
        return []
    
    def get_goalie_stats(self, season: Optional[str] = None) -> List[Dict]:
        """Get goalie statistics"""
        season = season or self.get_current_season()
        url = f"{self.BASE_URL}"
        params = {
            'feed': 'statviewfeed',
            'view': 'players',
            'group': 'goalies',
            'context': 'league',
            'league_code': self.CLIENT_CODE,
            'season': season,
            'key': self.API_KEY,
            'client_code': self.CLIENT_CODE,
            'language': 'en',
            'fmt': 'json'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'siteKit' in data:
                    return data['siteKit'].get('players', [])
                return data if isinstance(data, list) else []
        except Exception as e:
            print(f"Error fetching AHL goalie stats: {e}")
        return []
    
    def is_finnish(self, player: Dict) -> bool:
        """Check if player is Finnish"""
        # Check nationality/birthplace
        birthplace = player.get('birthplace', '')
        nationality = player.get('nationality', player.get('nation', ''))
        
        if nationality and nationality.upper() in ['FIN', 'FI']:
            return True
        if 'finland' in birthplace.lower():
            return True
        
        # Name heuristics
        name = player.get('name', '')
        first = player.get('firstName', player.get('first_name', ''))
        last = player.get('lastName', player.get('last_name', player.get('familyName', '')))
        
        if not name and (first or last):
            name = f"{first} {last}".strip()
        
        if any(char in name for char in 'äöåÄÖÅ'):
            return True
        if last and last.endswith(('nen', 'la', 'lä')):
            return True
        
        return False
    
    def collect_finnish_players(self, season: Optional[str] = None) -> List[Dict]:
        """Collect Finnish players from AHL"""
        season = season or self.get_current_season()
        print(f"Collecting AHL data for season {season}...")
        
        skater_stats = self.get_skater_stats(season)
        goalie_stats = self.get_goalie_stats(season)
        
        finnish_players = []
        
        for player in skater_stats:
            if self.is_finnish(player):
                name = player.get('name', '')
                if not name:
                    name = f"{player.get('firstName', player.get('first_name', ''))} {player.get('lastName', player.get('last_name', ''))}".strip()
                
                finnish_players.append({
                    'player_id': f"ahl_{player.get('id', player.get('playerId', 'unknown'))}",
                    'name': name,
                    'team': player.get('teamName', player.get('team', player.get('team_name', 'Unknown'))),
                    'league': 'AHL',
                    'position': player.get('position', player.get('pos', 'F')),
                    'games_played': player.get('gamesPlayed', player.get('games', player.get('gp', 0))),
                    'goals': player.get('goals', player.get('g', 0)),
                    'assists': player.get('assists', player.get('a', 0)),
                    'points': player.get('points', player.get('pts', 0)),
                    'plus_minus': player.get('plusMinus', player.get('plus_minus', 0)),
                    'penalty_minutes': player.get('penaltyMinutes', player.get('pim', 0)),
                    'save_percentage': None,
                    'goals_against_average': None,
                    'shutouts': None,
                    'birth_date': player.get('birthdate', player.get('birthDate', '')),
                    'height_cm': player.get('height', 0),
                    'weight_kg': player.get('weight', 0),
                    'nationality': 'FIN',
                    'source_league': 'ahl'
                })
        
        for goalie in goalie_stats:
            if self.is_finnish(goalie):
                name = goalie.get('name', '')
                if not name:
                    name = f"{goalie.get('firstName', goalie.get('first_name', ''))} {goalie.get('lastName', goalie.get('last_name', ''))}".strip()
                
                finnish_players.append({
                    'player_id': f"ahl_g_{goalie.get('id', goalie.get('playerId', 'unknown'))}",
                    'name': name,
                    'team': goalie.get('teamName', goalie.get('team', 'Unknown')),
                    'league': 'AHL',
                    'position': 'G',
                    'games_played': goalie.get('gamesPlayed', goalie.get('games', goalie.get('gp', 0))),
                    'goals': 0,
                    'assists': goalie.get('assists', 0),
                    'points': goalie.get('assists', 0),
                    'plus_minus': 0,
                    'penalty_minutes': goalie.get('penaltyMinutes', goalie.get('pim', 0)),
                    'save_percentage': goalie.get('savePercentage', goalie.get('savePct', goalie.get('sv%', 0))),
                    'goals_against_average': goalie.get('goalsAgainstAverage', goalie.get('gaa', 0)),
                    'shutouts': goalie.get('shutouts', goalie.get('so', 0)),
                    'birth_date': goalie.get('birthdate', goalie.get('birthDate', '')),
                    'height_cm': goalie.get('height', 0),
                    'weight_kg': goalie.get('weight', 0),
                    'nationality': 'FIN',
                    'source_league': 'ahl'
                })
        
        print(f"  Found {len(finnish_players)} Finnish players in AHL")
        return finnish_players


if __name__ == "__main__":
    collector = AHLRealCollector()
    players = collector.collect_finnish_players()
    print(f"\nCollected {len(players)} Finnish players from AHL")
    if players:
        print("\nSample players:")
        for p in players[:5]:
            print(f"  {p['name']} ({p['team']}): {p['points']}P")
