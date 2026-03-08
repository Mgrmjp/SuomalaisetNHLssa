"""Slovak Extraliga data adapter."""

from typing import List, Optional
from .base import BaseLeagueAdapter, PlayerStats


class SlovakExtraligaAdapter(BaseLeagueAdapter):
    """Adapter for Slovak Extraliga - top Slovak league."""
    
    @property
    def league_name(self) -> str:
        return "Slovak"
    
    @property
    def base_url(self) -> str:
        return "https://www.hockeyslovakia.sk/api/v1"
    
    def get_all_players(self, season: Optional[str] = None) -> List[PlayerStats]:
        """Fetch all players from Slovak Extraliga."""
        players = []
        
        # Slovak Extraliga teams
        teams = [
            'hk-dukla-igemangels-trencin', 'hk-slovan-bratislava', 'hk-dukla-trenčín',
            'hkm-zvolen', 'hkm-nové-zámky', 'mhk-32-liptovský-mikuláš',
            'hc-koŠice', 'hc-05-banská-bystrica', 'dynamics-hk-poprad',
            'macron-hk-nitra', 'hc-grotto-prešov'
        ]
        
        for team_slug in teams:
            team_players = self._get_team_players(team_slug, season)
            players.extend(team_players)
        
        return players
    
    def _get_team_players(self, team_slug: str, season: Optional[str]) -> List[PlayerStats]:
        """Get players for a specific team."""
        url = f"{self.base_url}/teams/{team_slug}/players"
        params = {'season': season} if season else None
        
        data = self._make_request(url, params)
        if not data:
            return []
        
        players = []
        team_name = data.get('team', {}).get('name', team_slug)
        
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
        data = self._make_request(url, {'q': name})
        
        if not data:
            return []
        
        return [self._parse_player(p) for p in data.get('players', [])]
    
    def _parse_player(self, data: dict, team_name: str = "Unknown") -> Optional[PlayerStats]:
        """Parse Slovak Extraliga player data."""
        try:
            position_map = {
                'G': 'G', 'Brankár': 'G',
                'D': 'D', 'Obranca': 'D',
                'F': 'C', 'Útočník': 'C',
                'C': 'C', 'Center': 'C',
                'LW': 'LW', 'Ľavé krídlo': 'LW',
                'RW': 'RW', 'Pravé krídlo': 'RW',
            }
            
            raw_pos = data.get('position', 'Unknown')
            position = position_map.get(raw_pos, raw_pos)
            is_goalie = position == 'G'
            
            stats = PlayerStats(
                player_id=str(data.get('id', '')),
                name=data.get('name', '').strip(),
                team=team_name,
                league="Slovak",
                position=position,
                games_played=data.get('games', 0),
                goals=data.get('goals', 0),
                assists=data.get('assists', 0),
                points=data.get('points', 0),
                plus_minus=data.get('plusMinus', 0),
                penalty_minutes=data.get('penaltyMinutes', 0),
                save_percentage=data.get('savePercentage') if is_goalie else None,
                goals_against_average=data.get('gaa') if is_goalie else None,
                shutouts=data.get('shutouts') if is_goalie else None,
                birth_date=data.get('dateOfBirth'),
                height_cm=data.get('height'),
                weight_kg=data.get('weight'),
                nationality=data.get('nationality'),
                raw_data=data
            )
            return stats
        except Exception as e:
            print(f"Error parsing Slovak player: {e}")
            return None
