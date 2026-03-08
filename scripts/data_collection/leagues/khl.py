"""KHL (Kontinental Hockey League) data adapter."""

from typing import List, Optional
from .base import BaseLeagueAdapter, PlayerStats


class KHLAdapter(BaseLeagueAdapter):
    """Adapter for KHL - Russian-based international league."""
    
    @property
    def league_name(self) -> str:
        return "KHL"
    
    @property
    def base_url(self) -> str:
        return "https://api.khl.ru/v1"
    
    def get_all_players(self, season: Optional[str] = None) -> List[PlayerStats]:
        """Fetch all players from KHL."""
        players = []
        
        # Western Conference teams with Finnish players historically
        teams = [
            'ska', 'cska', 'spartak', 'dynamo-moscow',
            'severstal', 'lokomotiv', 'dinamo-minsk', 'kunlun-red-star',
            'jokerit',  # Finnish team (if still participating)
        ]
        
        for team_id in teams:
            team_players = self._get_team_players(team_id, season)
            players.extend(team_players)
        
        return players
    
    def _get_team_players(self, team_id: str, season: Optional[str]) -> List[PlayerStats]:
        """Get players for a specific KHL team."""
        url = f"{self.base_url}/clubs/{team_id}/players"
        params = {'season': season} if season else None
        
        data = self._make_request(url, params)
        if not data:
            return []
        
        players = []
        team_name = data.get('club', {}).get('name', team_id)
        
        for player_data in data.get('players', []):
            stats = self._parse_player(player_data, team_name)
            if stats:
                players.append(stats)
        
        return players
    
    def get_player_stats(self, player_id: str, season: Optional[str] = None) -> Optional[PlayerStats]:
        """Fetch individual player stats."""
        url = f"{self.base_url}/players/{player_id}"
        params = {'season': season} if season else None
        
        data = self._make_request(url, params)
        if data:
            return self._parse_player(data)
        return None
    
    def search_players(self, name: str) -> List[PlayerStats]:
        """Search players by name."""
        url = f"{self.base_url}/players/search"
        data = self._make_request(url, {'name': name})
        
        if not data:
            return []
        
        return [self._parse_player(p) for p in data.get('players', [])]
    
    def _parse_player(self, data: dict, team_name: str = "Unknown") -> Optional[PlayerStats]:
        """Parse KHL player data."""
        try:
            position_map = {
                'G': 'G', 'Вр': 'G', 'Вратарь': 'G',  # Russian
                'D': 'D', 'Защ': 'D', 'Защитник': 'D',
                'F': 'C', 'Нап': 'C', 'Нападающий': 'C',
                'C': 'C', 'Центр': 'C',
                'LW': 'LW', 'ЛК': 'LW', 'Левый край': 'LW',
                'RW': 'RW', 'ПК': 'RW', 'Правый край': 'RW',
            }
            
            raw_pos = data.get('position', data.get('amplua', 'Unknown'))
            position = position_map.get(raw_pos, raw_pos)
            is_goalie = position == 'G'
            
            # KHL uses Russian format sometimes
            name = data.get('name', '')
            if not name and 'firstName' in data:
                name = f"{data.get('firstName', '')} {data.get('lastName', '')}".strip()
            
            stats = PlayerStats(
                player_id=str(data.get('id', data.get('player_id', ''))),
                name=name.strip(),
                team=team_name,
                league="KHL",
                position=position,
                games_played=data.get('games', data.get('matches', 0)),
                goals=data.get('goals', 0),
                assists=data.get('assists', data.get('passes', 0)),
                points=data.get('points', data.get('score', 0)),
                plus_minus=data.get('plusMinus', data.get('plus_minus', 0)),
                penalty_minutes=data.get('penaltyMinutes', data.get('penalty_minutes', 0)),
                save_percentage=data.get('savePercentage') if is_goalie else None,
                goals_against_average=data.get('gaa') if is_goalie else None,
                shutouts=data.get('shutouts', data.get('dry_matches')) if is_goalie else None,
                birth_date=data.get('dateOfBirth', data.get('birthday')),
                height_cm=data.get('height'),
                weight_kg=data.get('weight'),
                nationality=data.get('nationality', data.get('citizenship')),
                raw_data=data
            )
            return stats
        except Exception as e:
            print(f"Error parsing KHL player: {e}")
            return None
