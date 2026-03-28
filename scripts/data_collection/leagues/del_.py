"""DEL (Deutsche Eishockey Liga - Germany) data adapter."""

import re
import time
from typing import List, Optional, Dict, Any
from bs4 import BeautifulSoup
from .base import BaseLeagueAdapter, PlayerStats


class DELAdapter(BaseLeagueAdapter):
    """Adapter for DEL - German top league."""

    def __init__(self, rate_limit_delay: float = 1.0):
        super().__init__(rate_limit_delay=rate_limit_delay)
        self._headshot_cache = {}

    @property
    def league_name(self) -> str:
        return "DEL"

    @property
    def base_url(self) -> str:
        return "https://www.penny-del.org/statistik/saison-2024-25/hauptrunde/playerstats/basis"

    def get_all_players(self, season: Optional[str] = None) -> List[PlayerStats]:
        url = self.base_url
        if season:
            if "-" in season:
                parts = season.split("-")
                start = parts[0]
                end = parts[1][-2:]
                season_path = f"saison-{start}-{end}"
            else:
                season_path = f"saison-{season}"
            url = f"https://www.penny-del.org/statistik/{season_path}/hauptrunde/playerstats/basis"

        response = self._make_request(url, response_format="text")
        if not response:
            return []

        soup = BeautifulSoup(response, "html.parser")
        table = soup.find("table")
        if not table:
            return []

        all_players = []
        rows = table.find_all("tr")[1:]

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 10:
                continue

            nat = cols[4].get_text(strip=True).upper()
            stats = self._parse_table_row(cols, nat)
            if stats:
                all_players.append(stats)

        finnish_players = self.filter_finnish_players(all_players)

        for player in finnish_players:
            if player.profile_url and not player.headshot_url:
                player.headshot_url = self._fetch_del_headshot(player.profile_url)
                time.sleep(self.rate_limit_delay)

        return finnish_players

    def _fetch_del_headshot(self, profile_url: str) -> Optional[str]:
        """Fetch player headshot from DEL profile page."""
        if profile_url in self._headshot_cache:
            return self._headshot_cache[profile_url]

        try:
            response = self.session.get(profile_url, timeout=10)
            if response.status_code != 200:
                self._headshot_cache[profile_url] = None
                return None

            soup = BeautifulSoup(response.text, "html.parser")
            banner_img = soup.find("div", class_="alc-player-info-banner__img")
            if banner_img:
                img = banner_img.find("img")
                if img:
                    src = img.get("src") or img.get("data-src")
                    if src:
                        headshot_url = (
                            f"https://www.penny-del.org{src}"
                            if src.startswith("/")
                            else src
                        )
                        self._headshot_cache[profile_url] = headshot_url
                        return headshot_url
        except Exception as e:
            print(f"Error fetching DEL headshot for {profile_url}: {e}")

        self._headshot_cache[profile_url] = None
        return None

    def get_player_stats(
        self, player_id: str, season: Optional[str] = None
    ) -> Optional[PlayerStats]:
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

    def _parse_table_row(
        self, cols: List[Any], nationality: str
    ) -> Optional[PlayerStats]:
        """Parse DEL player table row."""
        try:
            # Player Name: often "LastName, FirstName"
            name_cell = cols[3]
            full_name = name_cell.get_text(strip=True)
            if "," in full_name:
                parts = full_name.split(",")
                name = f"{parts[1].strip()} {parts[0].strip()}"
            else:
                name = full_name

            # Extract profile URL from link in name cell
            profile_url = None
            link = name_cell.find("a")
            if link and link.get("href"):
                href = link.get("href")
                if href.startswith("/"):
                    href = f"https://www.penny-del.org{href}"
                profile_url = href

            # Team Name: cols[1] usually has a logo or text
            team_text = cols[1].get_text(strip=True)
            if not team_text:
                # Try to find team name in img title or alt if text is empty
                img = cols[1].find("img")
                if img:
                    team_text = img.get("title", img.get("alt", "Unknown"))

            # Position mapping: S -> F, V -> D, G -> G
            raw_pos = cols[5].get_text(strip=True).upper()
            pos_map = {"S": "F", "V": "D", "G": "G"}
            position = pos_map.get(raw_pos, "C")  # Default center/forward

            def to_int(text: str) -> int:
                try:
                    return int(text.strip())
                except:
                    return 0

            stats = PlayerStats(
                player_id=name.replace(" ", "-").lower(),  # Fallback ID
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
                save_percentage=None,  # Need Goalie specific page for this
                goals_against_average=None,
                shutouts=None,
                birth_date=None,
                height_cm=None,
                weight_kg=None,
                nationality=nationality,
                source_league="del",
                profile_url=profile_url,
                raw_data={"cols": [c.get_text() for c in cols]},
            )
            return stats
        except Exception as e:
            print(f"Error parsing DEL table row: {e}")
            return None
