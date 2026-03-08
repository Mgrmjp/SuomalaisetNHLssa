"""ICEHL (International Central European Hockey League) - Austria/Slovenia/etc."""

from typing import List, Optional, Dict, Any
from .base import BaseLeagueAdapter, PlayerStats


class ICEHLAdapter(BaseLeagueAdapter):
    """Adapter for ICEHL - Austrian/Slovenian/Czech/Hungarian league."""
    
    @property
    def league_name(self) -> str:
        return "ICEHL"
    
    @property
    def base_url(self) -> str:
        # Public S3 bucket endpoint discovered
        return "https://s3.dualstack.eu-west-1.amazonaws.com/icehl.hokejovyzapis.cz/league-team-stats"
    
    def get_all_players(self, season: Optional[str] = None) -> List[PlayerStats]:
        """Fetch all players from ICEHL."""
        # Season 24/25 is '2024' (start year) or '2025' depending on how it's indexed
        # Based on curl, 2025/1.json exists for current season
        year = "2025"
        if season:
            if "-" in season:
                year = season.split('-')[0]
            else:
                year = season
                
        url = f"{self.base_url}/{year}/1.json"
        
        data = self._make_request(url)
        if not data or not isinstance(data, list):
            return []
        
        all_players = []
        for player_data in data:
            stats = self._parse_player(player_data)
            if stats:
                all_players.append(stats)
                    
        return self.filter_finnish_players(all_players)
    
    def get_player_stats(self, player_id: str, season: Optional[str] = None) -> Optional[PlayerStats]:
        """Fetch individual player stats."""
        all_players = self.get_all_players(season)
        for p in all_players:
            if p.player_id == player_id:
                return p
        return None
    
    def search_players(self, name: str) -> List[PlayerStats]:
        """Search players by name."""
        all_players = self.get_all_players()
        return [p for p in all_players if name.lower() in p.name.lower()]
    
    def _parse_player(self, data: Dict[str, Any]) -> Optional[PlayerStats]:
        """Parse ICEHL player data."""
        try:
            position_map = {
                'G': 'G', 'Goalie': 'G', 'GK': 'G',
                'D': 'D', 'Defense': 'D', 'DF': 'D',
                'F': 'C', 'Forward': 'C', 'FW': 'C',
            }
            
            raw_pos = data.get('position', 'Unknown')
            position = position_map.get(raw_pos, raw_pos)
            is_goalie = position == 'G'
            
            # Stats are in the 'statistics' key
            s = data.get('statistics', {})
            
            def get_stat(field: str) -> int:
                val = s.get(field, 0)
                if isinstance(val, dict):
                    return (val.get('home', 0) or 0) + (val.get('away', 0) or 0)
                try:
                    return int(val or 0)
                except:
                    return 0
            
            stats = PlayerStats(
                player_id=str(data.get('id', '')),
                name=f"{data.get('firstname', '')} {data.get('surname', '')}".strip(),
                team=s.get('teamShortcut', 'Unknown'),
                league="ICEHL",
                position=position,
                games_played=get_stat('games'),
                goals=get_stat('goals'),
                assists=get_stat('assists'),
                points=get_stat('points'),
                plus_minus=get_stat('positive') - get_stat('negative'),
                penalty_minutes=get_stat('penaltyMinutes'),
                save_percentage=s.get('savePercentage') if is_goalie else None,
                goals_against_average=s.get('gaa') if is_goalie else None,
                shutouts=s.get('shutouts') if is_goalie else None,
                birth_date=data.get('birthdate'),
                height_cm=data.get('height'),
                weight_kg=data.get('weight'),
                nationality=data.get('nationalityShort', data.get('nationality')),
                source_league="icehl",
                raw_data=data
            )
            return stats
        except Exception as e:
            print(f"Error parsing ICEHL player: {e}")
            return None
