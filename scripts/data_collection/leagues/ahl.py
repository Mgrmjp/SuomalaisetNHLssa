"""AHL (American Hockey League) data adapter."""

from typing import List, Optional
from .base import BaseLeagueAdapter, PlayerStats


class AHLAdapter(BaseLeagueAdapter):
    """Adapter for AHL - top North American minor league."""
    
    @property
    def league_name(self) -> str:
        return "AHL"
    
    @property
    def base_url(self) -> str:
        return "https://api.theahl.com/stats/player"
    
    def get_all_players(self, season: Optional[str] = None) -> List[PlayerStats]:
        """Fetch all players from AHL."""
        # AHL requires going team by team
        players = []
        
        # Common AHL teams (simplified list)
        teams = [
            'bakersfield-condors', 'belleville-senators', 'bridgeport-islanders',
            'charlotte-checkers', 'chicago-wolves', 'cleveland-monsters',
            'coachella-valley-firebirds', 'colorado-eagles', 'grand-rapids-griffins',
            'hartford-wolf-pack', 'hershey-bears', 'iowa-wild',
            'laval-rocket', 'lehigh-valley-phantoms', 'manitoba-moose',
            'milwaukee-admirals', 'ontario-reign', 'providence-bruins',
            'rochester-americans', 'rockford-icehogs', 'san-diego-gulls',
            'san-jose-barracuda', 'springfield-thunderbirds', 'syracuse-crunch',
            'texas-stars', 'toronto-marlies', 'tucson-roadrunners',
            'utica-comets', 'wilkes-barre-penguins'
        ]
        
        for team in teams:
            team_players = self._get_team_players(team, season)
            players.extend(team_players)
        
        return players
    
    def _get_team_players(self, team_slug: str, season: Optional[str]) -> List[PlayerStats]:
        """Get players for a specific AHL team."""
        # Use stats API endpoint
        url = f"https://api.theahl.com/stats/team/{team_slug}/roster"
        params = {'season': season} if season else None
        
        data = self._make_request(url, params)
        if not data:
            return []
        
        players = []
        team_name = data.get('team', {}).get('name', team_slug)
        
        for player_data in data.get('roster', []):
            stats = self._parse_player(player_data, team_name)
            if stats:
                players.append(stats)
        
        return players
    
    def get_player_stats(self, player_id: str, season: Optional[str] = None) -> Optional[PlayerStats]:
        """Fetch individual player stats."""
        url = f"{self.base_url}/{player_id}"
        params = {'season': season} if season else None
        
        data = self._make_request(url, params)
        if data:
            return self._parse_player(data)
        return None
    
    def search_players(self, name: str) -> List[PlayerStats]:
        """Search players by name."""
        url = "https://api.theahl.com/stats/search"
        data = self._make_request(url, {'q': name, 'type': 'player'})
        
        if not data:
            return []
        
        return [self._parse_player(p) for p in data.get('players', [])]
    
    def _parse_player(self, data: dict, team_name: str = "Unknown") -> Optional[PlayerStats]:
        """Parse AHL player data to unified format."""
        try:
            is_goalie = data.get('position') == 'G'
            
            # AHL data format varies
            stats_data = data.get('stats', {})
            
            stats = PlayerStats(
                player_id=str(data.get('id', data.get('playerId', ''))),
                name=f"{data.get('firstName', '')} {data.get('lastName', '')}".strip(),
                team=team_name,
                league="AHL",
                position=data.get('position', 'Unknown'),
                games_played=stats_data.get('gamesPlayed', data.get('games', 0)),
                goals=stats_data.get('goals', 0),
                assists=stats_data.get('assists', 0),
                points=stats_data.get('points', 0),
                plus_minus=stats_data.get('plusMinus', 0),
                penalty_minutes=stats_data.get('penaltyMinutes', 0),
                save_percentage=stats_data.get('savePercentage') if is_goalie else None,
                goals_against_average=stats_data.get('goalsAgainstAverage') if is_goalie else None,
                shutouts=stats_data.get('shutouts') if is_goalie else None,
                wins=stats_data.get('wins') if is_goalie else None,
                birth_date=data.get('birthDate'),
                height_cm=data.get('height'),
                weight_kg=data.get('weight'),
                nationality=data.get('nationality'),
                raw_data=data
            )
            return stats
        except Exception as e:
            print(f"Error parsing AHL player: {e}")
            return None
