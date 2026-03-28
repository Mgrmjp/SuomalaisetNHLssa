"""
Real Liiga data collector using liiga.fi API
Public endpoints available without API key
"""

import requests
import json
from datetime import datetime
from typing import List, Dict, Optional


class LiigaRealCollector:
    """Collects real Liiga data from public API endpoints"""

    BASE_URL = "https://liiga.fi/api/v1"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )

    def get_current_season(self) -> str:
        """Get current season identifier (e.g., '2024-2025')"""
        now = datetime.now()
        if now.month >= 8:
            return f"{now.year}-{now.year + 1}"
        else:
            return f"{now.year - 1}-{now.year}"

    def get_players(self, season: Optional[str] = None) -> List[Dict]:
        """Get all players for a season"""
        season = season or self.get_current_season()
        url = f"{self.BASE_URL}/players/{season}"

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching Liiga players: {e}")
            return []

    def get_player_stats(self, season: Optional[str] = None) -> List[Dict]:
        """Get player statistics"""
        season = season or self.get_current_season()
        url = f"{self.BASE_URL}/statistics/{season}/players/regular"

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching Liiga stats: {e}")
            return []

    def get_goalie_stats(self, season: Optional[str] = None) -> List[Dict]:
        """Get goalie statistics from Liiga v2 API (filters all players to goalies only)."""
        season = season or self.get_current_season()
        year_end = int(season.split("-")[1])

        url = f"https://www.liiga.fi/api/v2/players/stats/summed/{year_end}/{year_end}/runkosarja/false"

        try:
            response = self.session.get(
                url,
                timeout=30,
                headers={
                    "Accept": "application/json, text/plain, */*",
                    "Referer": "https://www.liiga.fi/fi/tilastot/pelaajatilastot/",
                },
            )
            response.raise_for_status()
            all_players = response.json()

            if not isinstance(all_players, list):
                print(f"Unexpected Liiga v2 API response format")
                return []

            goalies = [
                p
                for p in all_players
                if p.get("goalkeeper") == True or p.get("role") == "MV"
            ]
            return goalies
        except Exception as e:
            print(f"Error fetching Liiga goalie stats: {e}")
            return []

    def is_finnish(self, player: Dict) -> bool:
        """Check if player is Finnish"""
        # Check nationality field
        nationality = player.get("nationality", "")
        if nationality and nationality.upper() in ["FIN", "FI", "FINLAND"]:
            return True

        # Check country field
        country = player.get("countryOfBirth", player.get("country", ""))
        if country and country.upper() in ["FIN", "FI", "FINLAND"]:
            return True

        # Fallback: Finnish name heuristics
        first = player.get("firstName", "")
        last = player.get("lastName", "")
        full_name = f"{first} {last}"

        # Check for Finnish characters and common suffixes
        if any(char in full_name for char in "äöåÄÖÅ"):
            return True
        if last.endswith(("nen", "la", "lä", "ka", "kä", "to", "lä")):
            return True

        return False

    def collect_finnish_players(self, season: Optional[str] = None) -> List[Dict]:
        """Collect all Finnish players with stats from Liiga v2 API."""
        season = season or self.get_current_season()
        print(f"Collecting Liiga data for season {season}...")

        year_end = int(season.split("-")[1])
        url = f"https://www.liiga.fi/api/v2/players/stats/summed/{year_end}/{year_end}/runkosarja/false"

        try:
            response = self.session.get(
                url,
                timeout=30,
                headers={
                    "Accept": "application/json, text/plain, */*",
                    "Referer": "https://www.liiga.fi/fi/tilastot/pelaajatilastot/",
                },
            )
            response.raise_for_status()
            all_players = response.json()
        except Exception as e:
            print(f"Error fetching Liiga v2 API: {e}")
            return []

        if not isinstance(all_players, list):
            print(f"Unexpected Liiga v2 API response format")
            return []

        finnish_players = []

        for player in all_players:
            if not self.is_finnish(player):
                continue

            is_goalie = player.get("goalkeeper") == True or player.get("role") == "MV"

            if is_goalie:
                # v2 API returns percentage format (89.4), convert to decimal (0.894)
                raw_save_pct = player.get("savePercentage", 0) or 0
                save_pct = raw_save_pct / 100 if raw_save_pct > 1 else raw_save_pct

                finnish_players.append(
                    {
                        "player_id": f"liiga_{player.get('playerId', player.get('id', 'unknown'))}",
                        "name": f"{player.get('firstName', '')} {player.get('lastName', '')}".strip(),
                        "team": player.get("teamName", player.get("team", "Unknown")),
                        "league": "Liiga",
                        "position": "G",
                        "games_played": player.get(
                            "games", player.get("playedGames", 0)
                        ),
                        "goals": 0,
                        "assists": player.get("assists", 0),
                        "points": player.get("assists", 0),
                        "plus_minus": 0,
                        "penalty_minutes": player.get(
                            "penaltyMinutes", player.get("pim", 0)
                        ),
                        "save_percentage": save_pct,
                        "goals_against_average": player.get("goalsAgainstAvg", 0),
                        "shutouts": player.get("shutOut", 0),
                        "birth_date": player.get(
                            "dateOfBirth", player.get("birthDate", "")
                        ),
                        "height_cm": player.get("height", 0),
                        "weight_kg": player.get("weight", 0),
                        "nationality": "FIN",
                        "source_league": "liiga",
                    }
                )
            else:
                finnish_players.append(
                    {
                        "player_id": f"liiga_{player.get('playerId', player.get('id', 'unknown'))}",
                        "name": f"{player.get('firstName', '')} {player.get('lastName', '')}".strip(),
                        "team": player.get("teamName", player.get("team", "Unknown")),
                        "league": "Liiga",
                        "position": player.get(
                            "playerPosition", player.get("position", "F")
                        ),
                        "games_played": player.get(
                            "games", player.get("playedGames", 0)
                        ),
                        "goals": player.get("goals", 0),
                        "assists": player.get("assists", 0),
                        "points": player.get("points", 0),
                        "plus_minus": player.get("plusMinus", 0),
                        "penalty_minutes": player.get(
                            "penaltyMinutes", player.get("pim", 0)
                        ),
                        "save_percentage": None,
                        "goals_against_average": None,
                        "shutouts": None,
                        "birth_date": player.get(
                            "dateOfBirth", player.get("birthDate", "")
                        ),
                        "height_cm": player.get("height", 0),
                        "weight_kg": player.get("weight", 0),
                        "nationality": "FIN",
                        "source_league": "liiga",
                    }
                )

        print(f"  Found {len(finnish_players)} Finnish players in Liiga")
        return finnish_players


if __name__ == "__main__":
    collector = LiigaRealCollector()
    players = collector.collect_finnish_players()

    print(f"\nCollected {len(players)} Finnish players from Liiga")
    print("\nTop 5 scorers:")
    skaters = [p for p in players if p["position"] != "G"]
    for p in sorted(skaters, key=lambda x: x["points"], reverse=True)[:5]:
        print(f"  {p['name']}: {p['goals']}G + {p['assists']}A = {p['points']}P")
