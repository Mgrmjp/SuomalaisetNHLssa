"""EliteProspects API adapter - covers all major leagues worldwide."""

from typing import List, Optional
from .base import BaseLeagueAdapter, PlayerStats


class EliteProspectsAdapter(BaseLeagueAdapter):
    """
    Adapter for EliteProspects API.
    Covers: Liiga, SHL, Czech, DEL, Swiss, Slovak, ICEHL, KHL, AHL, NCAA, etc.
    """
    
    @property
    def league_name(self) -> str:
        return "EliteProspects"
    
    @property
    def base_url(self) -> str:
        return "https://api.eliteprospects.com/v1"
    
    # League slugs in EliteProspects
    LEAGUES = {
        'liiga': 'Liiga',
        'shl': 'SHL',
        'czech': 'Czechia',
        'del': 'DEL',
        'swiss': 'National League',
        'slovak': 'Slovakia',
        'icehl': 'ICE Hockey League',
        'ahl': 'AHL',
        'echl': 'ECHL',
        'ncaa': 'NCAA',
    }
    
    def get_all_players(self, season: Optional[str] = None, specific_league: Optional[str] = None) -> List[PlayerStats]:
        """
        Fetch players from all supported leagues.
        
        Args:
            season: Format '2024-2025' or None for current
            specific_league: If provided, only fetch this league
        """
        players = []
        
        leagues_to_fetch = [specific_league] if specific_league else list(self.LEAGUES.keys())
        
        for league_slug in leagues_to_fetch:
            league_name = self.LEAGUES.get(league_slug, league_slug)
            print(f"  Fetching {league_name}...")
            
            league_players = self._get_league_players(league_slug, season)
            for player in league_players:
                player.league = league_name  # Override with proper name
            
            players.extend(league_players)
            print(f"    ✓ {len(league_players)} players")
        
        return players
    
    def _get_league_players(self, league_slug: str, season: Optional[str]) -> List[PlayerStats]:
        """Get all Finnish players from a specific league."""
        players = []
        page = 1
        
        while True:
            # Search for Finnish players in this league
            url = f"{self.base_url}/players"
            params = {
                'filter[type]': 'stats',
                'filter[league]': league_slug,
                'filter[nationality]': 'FIN',
                'page': page,
                'limit': 100,
            }
            if season:
                params['filter[season]'] = season
            
            data = self._make_request(url, params)
            if not data or not data.get('data'):
                break
            
            for player_data in data['data']:
                stats = self._parse_player(player_data)
                if stats:
                    players.append(stats)
            
            # Check if there are more pages
            meta = data.get('meta', {})
            if page >= meta.get('last_page', 1):
                break
            page += 1
            
            # Rate limiting
            import time
            time.sleep(0.5)
        
        return players
    
    def get_player_stats(self, player_id: str, season: Optional[str] = None) -> Optional[PlayerStats]:
        """Fetch individual player stats."""
        url = f"{self.base_url}/players/{player_id}"
        params = {'stats': 'true'}
        if season:
            params['season'] = season
        
        data = self._make_request(url, params)
        if data:
            return self._parse_player(data.get('data', {}))
        return None
    
    def search_players(self, name: str) -> List[PlayerStats]:
        """Search players by name."""
        url = f"{self.base_url}/players"
        data = self._make_request(url, {'filter[name]': name})
        
        if not data:
            return []
        
        return [self._parse_player(p) for p in data.get('data', [])]
    
    def _parse_player(self, data: dict) -> Optional[PlayerStats]:
        """Parse EliteProspects player data to unified format."""
        try:
            # Get stats from the most recent season data
            stats_data = data.get('stats', [{}])[0] if data.get('stats') else {}
            
            # Position mapping
            position_map = {
                'G': 'G', 'Gardien': 'G', 'Torwart': 'G', 'Maalivahti': 'G',
                'D': 'D', 'Defenseman': 'D', 'Verteidiger': 'D', 'Puolustaja': 'D',
                'F': 'C', 'Forward': 'C', 'Stürmer': 'C', 'Hyökkääjä': 'C',
                'C': 'C', 'Center': 'C', 'Keskushyökkääjä': 'C',
                'LW': 'LW', 'Left Wing': 'LW', 'Vasen laita': 'LW',
                'RW': 'RW', 'Right Wing': 'RW', 'Oikea laita': 'RW',
            }
            
            raw_pos = data.get('position', 'Unknown')
            position = position_map.get(raw_pos, raw_pos)
            is_goalie = position == 'G'
            
            # Parse height (format: "6'2\"" or "188 cm")
            height_cm = None
            height_str = data.get('height')
            if height_str:
                if 'cm' in height_str:
                    height_cm = int(height_str.replace('cm', '').strip())
                elif "'" in height_str:
                    parts = height_str.replace('"', '').split("'")
                    feet = int(parts[0])
                    inches = int(parts[1]) if len(parts) > 1 else 0
                    height_cm = int((feet * 30.48) + (inches * 2.54))
            
            # Parse weight (format: "190 lbs" or "85 kg")
            weight_kg = None
            weight_str = data.get('weight')
            if weight_str:
                if 'kg' in weight_str:
                    weight_kg = int(weight_str.replace('kg', '').strip())
                elif 'lbs' in weight_str:
                    lbs = int(weight_str.replace('lbs', '').strip())
                    weight_kg = round(lbs * 0.453592)
            
            stats = PlayerStats(
                player_id=str(data.get('playerId', data.get('id', ''))),
                name=data.get('name', '').strip(),
                team=data.get('latestStats', {}).get('team', {}).get('name', 'Unknown'),
                league=data.get('latestStats', {}).get('league', {}).get('name', 'Unknown'),
                position=position,
                games_played=stats_data.get('GP', 0),
                goals=stats_data.get('G', 0),
                assists=stats_data.get('A', 0),
                points=stats_data.get('TP', stats_data.get('PTS', 0)),
                plus_minus=stats_data.get('+/-', 0),
                penalty_minutes=stats_data.get('PIM', 0),
                save_percentage=stats_data.get('SV%') if is_goalie else None,
                goals_against_average=stats_data.get('GAA') if is_goalie else None,
                shutouts=stats_data.get('SO') if is_goalie else None,
                birth_date=data.get('dateOfBirth'),
                height_cm=height_cm,
                weight_kg=weight_kg,
                nationality=data.get('nationality', {}).get('name') if isinstance(data.get('nationality'), dict) else data.get('nationality'),
                raw_data=data
            )
            return stats
        except Exception as e:
            print(f"Error parsing EP player: {e}")
            return None
    
    def get_prospects_by_draft(self, draft_year: int) -> List[PlayerStats]:
        """Get Finnish prospects for a specific draft year."""
        url = f"{self.base_url}/drafts/{draft_year}"
        data = self._make_request(url)
        
        if not data:
            return []
        
        players = []
        for pick in data.get('data', {}).get('picks', []):
            player_data = pick.get('player', {})
            if player_data.get('nationality', {}).get('alpha2') == 'FI':
                stats = self._parse_player(player_data)
                if stats:
                    players.append(stats)
        
        return players
