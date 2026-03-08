"""NCAA (College hockey) data adapter."""

from typing import List, Optional
from .base import BaseLeagueAdapter, PlayerStats


class NCAAAdapter(BaseLeagueAdapter):
    """Adapter for NCAA college hockey."""
    
    @property
    def league_name(self) -> str:
        return "NCAA"
    
    @property
    def base_url(self) -> str:
        return "https://www.collegehockeynews.com/api/v1"
    
    def get_all_players(self, season: Optional[str] = None) -> List[PlayerStats]:
        """Fetch all players from NCAA."""
        players = []
        
        # Get all Division I teams
        teams_url = f"{self.base_url}/teams"
        teams_data = self._make_request(teams_url)
        
        if not teams_data:
            return players
        
        # Process each team (limit to first 20 to avoid rate limits)
        for team in teams_data[:20]:
            team_id = team.get('id')
            team_name = team.get('name', 'Unknown')
            
            team_players = self._get_team_players(team_id, team_name, season)
            players.extend(team_players)
        
        return players
    
    def _get_team_players(self, team_id: str, team_name: str, season: Optional[str]) -> List[PlayerStats]:
        """Get players for a specific NCAA team."""
        url = f"{self.base_url}/teams/{team_id}/roster"
        params = {'season': season} if season else None
        
        data = self._make_request(url, params)
        if not data:
            return []
        
        players = []
        for player_data in data.get('roster', []):
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
        """Parse NCAA player data to unified format."""
        try:
            # NCAA position mapping
            position_map = {
                'G': 'G', 'Goalie': 'G',
                'D': 'D', 'Defense': 'D', 'Defenseman': 'D',
                'F': 'C', 'Forward': 'C',
                'C': 'C', 'Center': 'C',
                'LW': 'LW', 'Left Wing': 'LW',
                'RW': 'RW', 'Right Wing': 'RW',
            }
            
            raw_pos = data.get('position', 'Unknown')
            position = position_map.get(raw_pos, raw_pos)
            is_goalie = position == 'G'
            
            # NCAA stats might be in different format
            stats = data.get('stats', {})
            
            stats_obj = PlayerStats(
                player_id=str(data.get('id', data.get('playerId', ''))),
                name=data.get('name', '').strip(),
                team=team_name,
                league="NCAA",
                position=position,
                games_played=stats.get('games', stats.get('gamesPlayed', 0)),
                goals=stats.get('goals', 0),
                assists=stats.get('assists', 0),
                points=stats.get('points', 0),
                plus_minus=stats.get('plusMinus', 0),
                penalty_minutes=stats.get('penaltyMinutes', stats.get('pim', 0)),
                save_percentage=stats.get('savePct') if is_goalie else None,
                goals_against_average=stats.get('gaa') if is_goalie else None,
                shutouts=stats.get('shutouts') if is_goalie else None,
                birth_date=data.get('birthDate'),
                height_cm=self._parse_height(data.get('height')),
                weight_kg=self._parse_weight(data.get('weight')),
                nationality=data.get('nationality', 'USA'),
                raw_data=data
            )
            return stats_obj
        except Exception as e:
            print(f"Error parsing NCAA player: {e}")
            return None
    
    def _parse_height(self, height_str: Optional[str]) -> Optional[int]:
        """Parse height string to cm (e.g., '6\'2"' -> 188)."""
        if not height_str:
            return None
        try:
            # Handle formats like "6'2" or "6-2"
            feet, inches = 0, 0
            if "'" in height_str:
                parts = height_str.replace('"', '').split("'")
                feet = int(parts[0])
                inches = int(parts[1]) if len(parts) > 1 else 0
            elif "-" in height_str:
                parts = height_str.split("-")
                feet = int(parts[0])
                inches = int(parts[1]) if len(parts) > 1 else 0
            return (feet * 30.48) + (inches * 2.54)
        except:
            return None
    
    def _parse_weight(self, weight_str: Optional[str]) -> Optional[int]:
        """Parse weight string to kg (e.g., '190 lbs' -> 86)."""
        if not weight_str:
            return None
        try:
            # Remove 'lbs' and convert
            weight_lbs = int(weight_str.replace('lbs', '').replace('lb', '').strip())
            return round(weight_lbs * 0.453592)
        except:
            return None
