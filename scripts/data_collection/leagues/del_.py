"""DEL (Deutsche Eishockey Liga - Germany) data adapter."""

import re
from typing import List, Optional, Dict, Any
from bs4 import BeautifulSoup
from .base import BaseLeagueAdapter, PlayerStats


class DELAdapter(BaseLeagueAdapter):
    """Adapter for DEL - German top league."""
    
    @property
    def league_name(self) -> str:
        return "DEL"
    
    @property
    def base_url(self) -> str:
        # Official website stats page
        return "https://www.penny-del.org/statistik/saison-2024-25/hauptrunde/playerstats/basis"
    
    def get_all_players(self, season: Optional[str] = None) -> List[PlayerStats]:
        """Fetch all players from DEL."""
        # Use season if provided to build the URL, but default to current active one
        url = self.base_url
        if season:
            # Handle both '2024-25' and '2024-2025' formats
            if '-' in season:
                parts = season.split('-')
                start = parts[0]
                end = parts[1][-2:] # Take last 2 digits
                season_path = f"saison-{start}-{end}"
            else:
                season_path = f"saison-{season}"
            url = f"https://www.penny-del.org/statistik/{season_path}/hauptrunde/playerstats/basis"
            
        response = self._make_request(url, response_format='text')
        if not response:
            return []
            
        soup = BeautifulSoup(response, 'html.parser')
        table = soup.find('table')
        if not table:
            # Sometimes tables are loaded via JS, but discovery showed them in SSR or accessible via request
            return []
            
        all_players = []
        rows = table.find_all('tr')[1:] # Skip header
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 10:
                continue
                
            nat = cols[4].get_text(strip=True).upper()
            stats = self._parse_table_row(cols, nat)
            if stats:
                all_players.append(stats)
                    
        return self.filter_finnish_players(all_players)
    
    def get_player_stats(self, player_id: str, season: Optional[str] = None) -> Optional[PlayerStats]:
        """Fetch individual player stats (by name for now since scrapers use names)."""
        all_players = self.get_all_players(season)
        for p in all_players:
            if p.player_id == player_id or p.name == player_id:
                return p
        return None
    
    def search_players(self, name: str) -> List[PlayerStats]:
        """Search players by name."""
        all_players = self.get_all_players()
        return [p for p in all_players if name.lower() in p.name.lower()]
    
    def _parse_table_row(self, cols: List[Any], nationality: str) -> Optional[PlayerStats]:
        """Parse DEL player table row."""
        try:
            # Player Name: often "LastName, FirstName"
            full_name = cols[3].get_text(strip=True)
            if ',' in full_name:
                parts = full_name.split(',')
                name = f"{parts[1].strip()} {parts[0].strip()}"
            else:
                name = full_name
                
            # Team Name: cols[1] usually has a logo or text
            team_text = cols[1].get_text(strip=True)
            if not team_text:
                # Try to find team name in img title or alt if text is empty
                img = cols[1].find('img')
                if img:
                    team_text = img.get('title', img.get('alt', 'Unknown'))
            
            # Position mapping: S -> F, V -> D, G -> G
            raw_pos = cols[5].get_text(strip=True).upper()
            pos_map = {'S': 'F', 'V': 'D', 'G': 'G'}
            position = pos_map.get(raw_pos, 'C') # Default center/forward
            
            def to_int(text: str) -> int:
                try:
                    return int(text.strip())
                except:
                    return 0
            
            stats = PlayerStats(
                player_id=name.replace(' ', '-').lower(), # Fallback ID
                name=name,
                team=team_text,
                league="DEL",
                position=position,
                games_played=to_int(cols[6].get_text()),
                goals=to_int(cols[7].get_text()),
                assists=to_int(cols[8].get_text()),
                points=to_int(cols[9].get_text()),
                plus_minus=to_int(cols[13].get_text()) if len(cols) > 13 else 0,
                penalty_minutes=to_int(cols[10].get_text()),
                save_percentage=None, # Need Goalie specific page for this
                goals_against_average=None,
                shutouts=None,
                birth_date=None,
                height_cm=None,
                weight_kg=None,
                nationality=nationality,
                source_league="del",
                raw_data={'cols': [c.get_text() for c in cols]}
            )
            return stats
        except Exception as e:
            print(f"Error parsing DEL table row: {e}")
            return None
