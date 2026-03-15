"""Swiss National League (NL) data adapter."""

from typing import List, Optional, Dict, Any
from .base import BaseLeagueAdapter, PlayerStats


class SwissNLAdapter(BaseLeagueAdapter):
    """Adapter for Swiss National League - top Swiss league."""
    
    @property
    def league_name(self) -> str:
        return "NL"
    
    @property
    def base_url(self) -> str:
        return "https://www.nationalleague.ch/api"
    
    def get_all_players(self, season: Optional[str] = None) -> List[PlayerStats]:
        """Fetch all players from Swiss National League."""
        # The main player endpoint returns all players for the current regular season
        # We can filter for Finnish players here or in the caller.
        # Discovery showed noc: 1 is Finland.
        url = f"{self.base_url}/player"
        params = {'lang': 'de-CH'}
        
        # If we need a specific phase, it would be e.g. phase=2024 (Regular Season 24/25)
        # For now, let's stick to the default which is usually the current active phase.
        
        data = self._make_request(url, params)
        if not data:
            return []
        
        all_players = []
        # The response is a list of player objects
        for player_data in data:
            stats = self._parse_player(player_data)
            if stats:
                all_players.append(stats)
                    
        return self.filter_finnish_players(all_players)
    
    def get_player_stats(self, player_id: str, season: Optional[str] = None) -> Optional[PlayerStats]:
        """Fetch individual player stats."""
        url = f"{self.base_url}/player/{player_id}"
        params = {'lang': 'de-CH'}
        
        data = self._make_request(url, params)
        if data:
            return self._parse_player(data)
        return None
    
    def search_players(self, name: str) -> List[PlayerStats]:
        """Search players by name."""
        # The API doesn't seem to have a dedicated search endpoint that we found,
        # but we can filter the all_players list if needed.
        all_players = self.get_all_players()
        return [p for p in all_players if name.lower() in p.name.lower()]
    
    def _parse_player(self, data: Dict[str, Any]) -> Optional[PlayerStats]:
        """Parse Swiss NL player data."""
        try:
            position_map = {
                'G': 'G', 'Goalie': 'G', 'Torhüter': 'G', 'Gardien': 'G',
                'D': 'D', 'Defense': 'D', 'Verteidiger': 'D', 'Défenseur': 'D',
                'F': 'C', 'Forward': 'C', 'Stürmer': 'C', 'Attaquant': 'C',
                'C': 'C', 'Center': 'C', 'Centre': 'C',
                'LW': 'LW', 'Left Wing': 'LW',
                'RW': 'RW', 'Right Wing': 'RW',
            }
            
            # The API returns 'position' as a code or string?
            # Discovery saw 'position' as a string like "F" or "D"
            raw_pos = data.get('position', 'Unknown')
            position = position_map.get(raw_pos, raw_pos)
            is_goalie = position == 'G'
            
            # Team name is often in 'team_name' or similar
            team_name = data.get('team_name', data.get('team', {}).get('name', "Unknown"))
            
            player_id = str(data.get('playerId', '') or '')
            headshot_url = f"{self.base_url}/player/{player_id}/image" if player_id else None

            stats = PlayerStats(
                player_id=player_id,
                name=f"{data.get('firstName', '')} {data.get('lastName', '')}".strip(),
                team=data.get('teamName', 'Unknown'),
                league="NL",
                position=position,
                games_played=int(data.get('gp', 0) or 0),
                goals=int(data.get('g', 0) or 0),
                assists=int(data.get('assists', 0) or 0),
                points=int(data.get('points', 0) or 0),
                plus_minus=int(data.get('plusMinus', 0) or 0),
                penalty_minutes=int(data.get('pim', 0) or 0),
                save_percentage=data.get('savePercentage') if is_goalie else None,
                goals_against_average=data.get('gaPerGame') if is_goalie else None,
                shutouts=data.get('so') if is_goalie else None,
                birth_date=data.get('birth'),
                height_cm=data.get('height'),
                weight_kg=data.get('weight'),
                nationality='FIN' if data.get('noc') == 1 else None,
                headshot_url=headshot_url,
                source_league="nl",
                raw_data=data
            )
            return stats
        except Exception as e:
            print(f"Error parsing NL player: {e}")
            return None
