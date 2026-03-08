"""
Real Liiga data collector using liiga.fi API
Public endpoints available without API key
"""
import requests
import json
from datetime import datetime
from typing import List, Dict, Optional


class LiigaRealCollector:
    """Collects real Liiga data from public API endpoints"""
    
    BASE_URL = "https://liiga.fi/api/v1"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_current_season(self) -> str:
        """Get current season identifier (e.g., '2024-2025')"""
        now = datetime.now()
        if now.month >= 8:
            return f"{now.year}-{now.year + 1}"
        else:
            return f"{now.year - 1}-{now.year}"
    
    def get_players(self, season: Optional[str] = None) -> List[Dict]:
        """Get all players for a season"""
        season = season or self.get_current_season()
        url = f"{self.BASE_URL}/players/{season}"
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching Liiga players: {e}")
            return []
    
    def get_player_stats(self, season: Optional[str] = None) -> List[Dict]:
        """Get player statistics"""
        season = season or self.get_current_season()
        url = f"{self.BASE_URL}/statistics/{season}/players/regular"
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching Liiga stats: {e}")
            return []
    
    def get_goalie_stats(self, season: Optional[str] = None) -> List[Dict]:
        """Get goalie statistics"""
        season = season or self.get_current_season()
        url = f"{self.BASE_URL}/statistics/{season}/goalkeepers/regular"
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching Liiga goalie stats: {e}")
            return []
    
    def is_finnish(self, player: Dict) -> bool:
        """Check if player is Finnish"""
        # Check nationality field
        nationality = player.get('nationality', '')
        if nationality and nationality.upper() in ['FIN', 'FI', 'FINLAND']:
            return True
        
        # Check country field
        country = player.get('countryOfBirth', player.get('country', ''))
        if country and country.upper() in ['FIN', 'FI', 'FINLAND']:
            return True
        
        # Fallback: Finnish name heuristics
        first = player.get('firstName', '')
        last = player.get('lastName', '')
        full_name = f"{first} {last}"
        
        # Check for Finnish characters and common suffixes
        if any(char in full_name for char in 'äöåÄÖÅ'):
            return True
        if last.endswith(('nen', 'la', 'lä', 'ka', 'kä', 'to', 'lä')):
            return True
        
        return False
    
    def collect_finnish_players(self, season: Optional[str] = None) -> List[Dict]:
        """Collect all Finnish players with stats"""
        season = season or self.get_current_season()
        print(f"Collecting Liiga data for season {season}...")
        
        # Get player stats
        skater_stats = self.get_player_stats(season)
        goalie_stats = self.get_goalie_stats(season)
        
        finnish_players = []
        
        # Process skaters
        for player in skater_stats:
            if self.is_finnish(player):
                finnish_players.append({
                    'player_id': f"liiga_{player.get('playerId', player.get('id', 'unknown'))}",
                    'name': f"{player.get('firstName', '')} {player.get('lastName', '')}".strip(),
                    'team': player.get('teamName', player.get('team', 'Unknown')),
                    'league': 'Liiga',
                    'position': player.get('playerPosition', player.get('position', 'F')),
                    'games_played': player.get('gamesPlayed', player.get('games', 0)),
                    'goals': player.get('goals', 0),
                    'assists': player.get('assists', 0),
                    'points': player.get('points', 0),
                    'plus_minus': player.get('plusMinus', 0),
                    'penalty_minutes': player.get('penaltyMinutes', player.get('pim', 0)),
                    'save_percentage': None,
                    'goals_against_average': None,
                    'shutouts': None,
                    'birth_date': player.get('dateOfBirth', player.get('birthDate', '')),
                    'height_cm': player.get('height', 0),
                    'weight_kg': player.get('weight', 0),
                    'nationality': 'FIN',
                    'source_league': 'liiga'
                })
        
        # Process goalies
        for goalie in goalie_stats:
            if self.is_finnish(goalie):
                finnish_players.append({
                    'player_id': f"liiga_g_{goalie.get('playerId', goalie.get('id', 'unknown'))}",
                    'name': f"{goalie.get('firstName', '')} {goalie.get('lastName', '')}".strip(),
                    'team': goalie.get('teamName', goalie.get('team', 'Unknown')),
                    'league': 'Liiga',
                    'position': 'G',
                    'games_played': goalie.get('gamesPlayed', goalie.get('games', 0)),
                    'goals': 0,
                    'assists': goalie.get('assists', 0),
                    'points': goalie.get('assists', 0),
                    'plus_minus': 0,
                    'penalty_minutes': goalie.get('penaltyMinutes', goalie.get('pim', 0)),
                    'save_percentage': goalie.get('savePercentage', goalie.get('sv%', 0)),
                    'goals_against_average': goalie.get('goalAgainstAverage', goalie.get('gaa', 0)),
                    'shutouts': goalie.get('shutouts', 0),
                    'birth_date': goalie.get('dateOfBirth', goalie.get('birthDate', '')),
                    'height_cm': goalie.get('height', 0),
                    'weight_kg': goalie.get('weight', 0),
                    'nationality': 'FIN',
                    'source_league': 'liiga'
                })
        
        print(f"  Found {len(finnish_players)} Finnish players in Liiga")
        return finnish_players


if __name__ == "__main__":
    collector = LiigaRealCollector()
    players = collector.collect_finnish_players()
    
    print(f"\nCollected {len(players)} Finnish players from Liiga")
    print("\nTop 5 scorers:")
    skaters = [p for p in players if p['position'] != 'G']
    for p in sorted(skaters, key=lambda x: x['points'], reverse=True)[:5]:
        print(f"  {p['name']}: {p['goals']}G + {p['assists']}A = {p['points']}P")
