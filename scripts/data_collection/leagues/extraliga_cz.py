"""Czech Extraliga data adapter."""

import re
from typing import List, Optional, Dict, Any
from bs4 import BeautifulSoup
from .base import BaseLeagueAdapter, PlayerStats


class CzechExtraligaAdapter(BaseLeagueAdapter):
    """Adapter for Czech Extraliga - top Czech league."""
    
    @property
    def league_name(self) -> str:
        return "Extraliga"
    
    @property
    def base_url(self) -> str:
        # Official website stats center
        # Season 24/25 competition ID seems to be 7230
        return "https://www.hokej.cz/tipsport-extraliga/stats-center?season=2024&competition=7230"
    
    def get_all_players(self, season: Optional[str] = None) -> List[PlayerStats]:
        """Fetch all players from Czech Extraliga."""
        # Use season if provided to build the URL (though competition IDs are tricky)
        url = f"{self.base_url}&stranger=1" # Use foreigner filter for better performance
            
        response = self._make_request(url, response_format='text')
        if not response:
            return []
            
        soup = BeautifulSoup(response, 'html.parser')
        # Try finding any table if table-stats is missing
        table = soup.find('table', class_='table-stats') or soup.find('table')
        if not table:
            return []
            
        all_players = []
        rows = table.find('tbody').find_all('tr') if table.find('tbody') else table.find_all('tr')[1:]
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 9:
                continue
                
            stats = self._parse_table_row(cols)
            if stats:
                # Check for Finnish flag specifically to set the nationality field
                # so filter_finnish_players can use it
                name_cell = cols[1]
                flag = name_cell.find('img', class_='country-fin') or \
                       name_cell.select_one('span[title="Finsko"]') or \
                       name_cell.select_one('img[title="Finsko"]')
                if flag:
                    stats.nationality = "FIN"
                else:
                    stats.nationality = None # Let heuristic decide
                    
                all_players.append(stats)
                    
        return self.filter_finnish_players(all_players)
    
    def get_player_stats(self, player_id: str, season: Optional[str] = None) -> Optional[PlayerStats]:
        """Fetch individual player stats."""
        all_players = self.get_all_players(season)
        for p in all_players:
            if p.player_id == player_id or p.name == player_id:
                return p
        return None
    
    def search_players(self, name: str) -> List[PlayerStats]:
        """Search players by name."""
        all_players = self.get_all_players()
        return [p for p in all_players if name.lower() in p.name.lower()]
    
    def _parse_table_row(self, cols: List[Any]) -> Optional[PlayerStats]:
        """Parse Czech Extraliga table row."""
        try:
            name_link = cols[1].find('a')
            name = name_link.get_text(strip=True) if name_link else cols[1].get_text(strip=True)
            player_id = name_link['href'].split('/')[-1] if name_link and 'href' in name_link.attrs else name.replace(' ', '-').lower()
            
            team = cols[2].get_text(strip=True)
            
            # Position mapping: Ú -> F, O -> D, B -> G
            raw_pos = cols[3].get_text(strip=True).upper()
            pos_map = {'Ú': 'F', 'O': 'D', 'B': 'G'}
            position = pos_map.get(raw_pos, 'C')
            
            def to_int(text: str) -> int:
                try:
                    return int(text.strip().replace('\xa0', ''))
                except:
                    return 0
            
            stats = PlayerStats(
                player_id=player_id,
                name=name,
                team=team,
                league="Extraliga",
                position=position,
                games_played=to_int(cols[4].get_text()),
                goals=to_int(cols[6].get_text()),
                assists=to_int(cols[7].get_text()),
                points=to_int(cols[8].get_text()),
                plus_minus=to_int(cols[15].get_text()) if len(cols) > 15 else 0,
                penalty_minutes=to_int(cols[16].get_text()) if len(cols) > 16 else 0,
                save_percentage=None,
                goals_against_average=None,
                shutouts=None,
                birth_date=None,
                height_cm=None,
                weight_kg=None,
                nationality="FIN",
                source_league="extraliga_cz",
                raw_data={'cols': [c.get_text() for c in cols]}
            )
            return stats
        except Exception as e:
            print(f"Error parsing Extraliga table row: {e}")
            return None
