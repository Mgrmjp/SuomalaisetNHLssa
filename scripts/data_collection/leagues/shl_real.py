"""
Real SHL (Swedish Hockey League) data collector
Uses shl.se API endpoints
"""
import requests
import json
from datetime import datetime
from typing import List, Dict, Optional


class SHLRealCollector:
    """Collects real SHL data from public API"""
    
    BASE_URL = "https://www.shl.se/p/api/statistics"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        })
    
    def get_current_season(self) -> str:
        """Get current season"""
        now = datetime.now()
        if now.month >= 8:
            return f"{now.year}-{str(now.year + 1)[-2:]}"
        else:
            return f"{now.year - 1}-{str(now.year)[-2:]}"
    
    def get_player_stats(self, season: Optional[str] = None) -> List[Dict]:
        """Get player statistics"""
        season = season or self.get_current_season()
        url = f"{self.BASE_URL}/players/season/{season}/gametype/regular"
        
        try:
            response = self.session.get(url, timeout=30)
            if response.status_code == 200:
                data = response.json()
                return data if isinstance(data, list) else data.get('statistics', [])
        except Exception as e:
            print(f"Error fetching SHL stats: {e}")
        return []
    
    def get_goalie_stats(self, season: Optional[str] = None) -> List[Dict]:
        """Get goalie statistics"""
        season = season or self.get_current_season()
        url = f"{self.BASE_URL}/goalkeepers/season/{season}/gametype/regular"
        
        try:
            response = self.session.get(url, timeout=30)
            if response.status_code == 200:
                data = response.json()
                return data if isinstance(data, list) else data.get('statistics', [])
        except Exception as e:
            print(f"Error fetching SHL goalie stats: {e}")
        return []
    
    def is_finnish(self, player: Dict) -> bool:
        """Check if player is Finnish"""
        nationality = player.get('nationality', '')
        if nationality and nationality.upper() in ['FIN', 'FI', 'FINLAND']:
            return True
        
        country = player.get('country', player.get('countryOfBirth', ''))
        if country and country.upper() in ['FIN', 'FI', 'FINLAND']:
            return True
        
        # Name heuristics
        first = player.get('firstName', player.get('first_name', ''))
        last = player.get('lastName', player.get('last_name', player.get('familyName', '')))
        full_name = f"{first} {last}"
        
        if any(char in full_name for char in 'äöåÄÖÅ'):
            return True
        if last.endswith(('nen', 'la', 'lä', 'ka', 'kä', 'to')):
            return True
        
        return False
    
    def collect_finnish_players(self, season: Optional[str] = None) -> List[Dict]:
        """Collect Finnish players from SHL"""
        season = season or self.get_current_season()
        print(f"Collecting SHL data for season {season}...")
        
        skater_stats = self.get_player_stats(season)
        goalie_stats = self.get_goalie_stats(season)
        
        finnish_players = []
        
        for player in skater_stats:
            if self.is_finnish(player):
                finnish_players.append({
                    'player_id': f"shl_{player.get('playerId', player.get('id', 'unknown'))}",
                    'name': f"{player.get('firstName', player.get('first_name', ''))} {player.get('lastName', player.get('last_name', player.get('familyName', '')))}".strip(),
                    'team': player.get('teamName', player.get('team', player.get('team_name', 'Unknown'))),
                    'league': 'SHL',
                    'position': player.get('position', 'F'),
                    'games_played': player.get('gamesPlayed', player.get('games', player.get('gp', 0))),
                    'goals': player.get('goals', player.get('g', 0)),
                    'assists': player.get('assists', player.get('a', 0)),
                    'points': player.get('points', player.get('p', 0)),
                    'plus_minus': player.get('plusMinus', player.get('plus_minus', 0)),
                    'penalty_minutes': player.get('penaltyMinutes', player.get('pim', 0)),
                    'save_percentage': None,
                    'goals_against_average': None,
                    'shutouts': None,
                    'birth_date': player.get('dateOfBirth', player.get('birthDate', '')),
                    'height_cm': player.get('height', 0),
                    'weight_kg': player.get('weight', 0),
                    'nationality': 'FIN',
                    'source_league': 'shl'
                })
        
        for goalie in goalie_stats:
            if self.is_finnish(goalie):
                finnish_players.append({
                    'player_id': f"shl_g_{goalie.get('playerId', goalie.get('id', 'unknown'))}",
                    'name': f"{goalie.get('firstName', goalie.get('first_name', ''))} {goalie.get('lastName', goalie.get('last_name', ''))}".strip(),
                    'team': goalie.get('teamName', goalie.get('team', 'Unknown')),
                    'league': 'SHL',
                    'position': 'G',
                    'games_played': goalie.get('gamesPlayed', goalie.get('games', 0)),
                    'goals': 0,
                    'assists': goalie.get('assists', 0),
                    'points': goalie.get('assists', 0),
                    'plus_minus': 0,
                    'penalty_minutes': goalie.get('penaltyMinutes', goalie.get('pim', 0)),
                    'save_percentage': goalie.get('savePercentage', goalie.get('save_percentage', goalie.get('sv%', 0))),
                    'goals_against_average': goalie.get('goalsAgainstAverage', goalie.get('gaa', 0)),
                    'shutouts': goalie.get('shutouts', goalie.get('so', 0)),
                    'birth_date': goalie.get('dateOfBirth', goalie.get('birthDate', '')),
                    'height_cm': goalie.get('height', 0),
                    'weight_kg': goalie.get('weight', 0),
                    'nationality': 'FIN',
                    'source_league': 'shl'
                })
        
        print(f"  Found {len(finnish_players)} Finnish players in SHL")
        return finnish_players


if __name__ == "__main__":
    collector = SHLRealCollector()
    players = collector.collect_finnish_players()
    print(f"\nCollected {len(players)} Finnish players from SHL")
