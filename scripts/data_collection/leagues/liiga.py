"""Liiga (Finnish league) data adapter."""

from typing import List, Optional
from .base import BaseLeagueAdapter, PlayerStats


class LiigaAdapter(BaseLeagueAdapter):
    """Adapter for Liiga - Finnish top league."""
    
    @property
    def league_name(self) -> str:
        return "Liiga"
    
    @property
    def base_url(self) -> str:
        return "https://liiga.fi/api/v1"
    
    def get_all_players(self, season: Optional[str] = None) -> List[PlayerStats]:
        """Fetch all players from Liiga."""
        players = []
        
        # Get all teams first
        teams_url = f"{self.base_url}/teams"
        teams_data = self._make_request(teams_url)
        
        if not teams_data:
            return players
        
        for team in teams_data:
            team_id = team.get('id')
            team_name = team.get('name', 'Unknown')
            
            # Get team roster
            roster_url = f"{self.base_url}/teams/{team_id}/roster"
            roster_data = self._make_request(roster_url)
            
            if roster_data:
                for player_data in roster_data.get('players', []):
                    stats = self._parse_player(player_data, team_name)
                    if stats:
                        players.append(stats)
        
        return players
    
    def get_player_stats(self, player_id: str, season: Optional[str] = None) -> Optional[PlayerStats]:
        """Fetch individual player stats."""
        url = f"{self.base_url}/players/{player_id}/stats"
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
        """Parse Liiga player data to unified format."""
        try:
            is_goalie = data.get('position') == 'MV'
            
            stats = PlayerStats(
                player_id=str(data.get('id', '')),
                name=f"{data.get('firstName', '')} {data.get('lastName', '')}".strip(),
                team=team_name,
                league="Liiga",
                position=data.get('position', 'Unknown'),
                games_played=data.get('games', 0),
                goals=data.get('goals', 0),
                assists=data.get('assists', 0),
                points=data.get('points', 0),
                plus_minus=data.get('plusMinus', 0),
                penalty_minutes=data.get('penaltyMinutes', 0),
                save_percentage=data.get('savePercentage') if is_goalie else None,
                goals_against_average=data.get('goalsAgainstAverage') if is_goalie else None,
                shutouts=data.get('shutouts') if is_goalie else None,
                birth_date=data.get('dateOfBirth'),
                height_cm=data.get('height'),
                weight_kg=data.get('weight'),
                nationality=data.get('nationality'),
                raw_data=data
            )
            return stats
        except Exception as e:
            print(f"Error parsing player: {e}")
            return None
