#!/usr/bin/env python3
"""
NCAA and North American Junior Leagues Data Collector
Collects Finnish player stats from:
- NCAA (collegehockeynews.com)
- USHL (United States Hockey League)
- NAHL (North American Hockey League)
- Canadian Junior Leagues (WHL, OHL, QMJHL)
"""
import requests
import urllib3
import json
import time
import os
import re
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class CollegeAndJuniorCollector:
    """Collect Finnish players from NCAA and North American junior leagues."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        })
        self.session.verify = False  # Allow self-signed certs if needed
        self.request_delay = 0.5
        
    def _make_request(self, url: str) -> Optional[Dict]:
        """Make rate-limited request."""
        time.sleep(self.request_delay)
        try:
            response = self.session.get(url, timeout=30)
            print(f"  Requesting: {url}")
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                text = response.text.strip()
                if text:
                    return response.json()
                else:
                    print(f"  Empty response")
            else:
                print(f"  Error: {response.status_code}")
        except requests.exceptions.JSONDecodeError as e:
            print(f"  JSON decode error: {e}")
        except Exception as e:
            print(f"  Request error: {e}")
        return None

    def _make_text_request(self, url: str) -> str:
        """Make rate-limited request and return response text."""
        time.sleep(self.request_delay)
        try:
            response = self.session.get(url, timeout=30)
            print(f"  Requesting: {url}")
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                return response.text
            print(f"  Error: {response.status_code}")
        except Exception as e:
            print(f"  Request error: {e}")
        return ""

    def _normalize_ncaa_name(self, name: str) -> str:
        cleaned = (name or "").strip()
        if not cleaned:
            return ""
        if "," in cleaned:
            parts = [part.strip() for part in cleaned.split(",") if part.strip()]
            if len(parts) >= 2:
                cleaned = " ".join(parts[1:] + [parts[0]])
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned

    def _parse_ncaa_teams_from_html(self, html: str) -> List[Dict]:
        soup = BeautifulSoup(html, "html.parser")
        teams = []
        seen = set()

        for link in soup.find_all("a", href=True):
            href = link["href"].strip()
            match = re.match(r"^/reports/team/([^/]+)/(\d+)$", href)
            if not match:
                continue

            slug, team_id = match.groups()
            if team_id in seen:
                continue
            seen.add(team_id)

            team_name = " ".join(link.get_text(" ", strip=True).split())
            if not team_name:
                team_name = slug.replace("-", " ")

            teams.append({
                "id": team_id,
                "slug": slug,
                "name": team_name,
            })

        return teams

    def _parse_ncaa_stats_table(self, html: str) -> Dict[str, Dict]:
        soup = BeautifulSoup(html, "html.parser")
        tables = soup.find_all("table")
        stats_by_name: Dict[str, Dict] = {}

        def parse_int(value: str) -> int:
            try:
                return int(str(value).strip())
            except Exception:
                return 0

        def parse_float(value: str) -> float:
            try:
                return float(str(value).strip())
            except Exception:
                return 0.0

        if tables:
            for row in tables[0].find_all("tr"):
                cells = [cell.get_text(" ", strip=True) for cell in row.find_all("td")]
                if len(cells) < 9:
                    continue
                name = self._normalize_ncaa_name(cells[0].split(" , ", 1)[0])
                if not name:
                    continue
                stats_by_name[name] = {
                    "position": cells[0].split(" , ")[1] if " , " in cells[0] else "F",
                    "games_played": parse_int(cells[1]),
                    "goals": parse_int(cells[2]),
                    "assists": parse_int(cells[3]),
                    "points": parse_int(cells[4]),
                    "penalty_minutes": parse_int(cells[8]),
                }

        if len(tables) > 1:
            for row in tables[1].find_all("tr"):
                cells = [cell.get_text(" ", strip=True) for cell in row.find_all("td")]
                if len(cells) < 11:
                    continue
                name = self._normalize_ncaa_name(cells[0].split(" , ", 1)[0])
                if not name:
                    continue
                stats_by_name[name] = {
                    "position": "G",
                    "games_played": parse_int(cells[1]),
                    "wins": parse_int(cells[2]),
                    "goals_against_average": parse_float(cells[7]),
                    "shutouts": parse_int(cells[8]),
                    "save_percentage": parse_float(cells[10]),
                }

        return stats_by_name
    
    def is_finnish(self, name: str, nationality: str = '', birthplace: str = '') -> bool:
        """Check if player is Finnish."""
        nat = nationality.strip().upper() if nationality else ''
        
        if nat in ['FI', 'FIN', 'FINLAND']:
            return True
        if birthplace and 'finland' in birthplace.lower():
            return True
        if any(char in name for char in 'äöåÄÖÅ'):
            return True
        parts = name.split()
        if parts:
            last_name = parts[-1] if len(parts) > 1 else ''
            if last_name.endswith(('nen', 'lä', 'lä', 'kkä', 'kkö', 'pää', 'rvi')):
                return True
        return False
    
    def get_ncaa_teams(self) -> List[Dict]:
        """Get list of NCAA Division I teams."""
        url = "https://www.collegehockeynews.com/api/v1/teams"
        html = self._make_text_request(url)
        if not html:
            return []
        return self._parse_ncaa_teams_from_html(html)
    
    def get_ncaa_player_stats(self, season: str = "2024-2025") -> List[Dict]:
        """
        Get NCAA player stats from collegehockeynews.com HTML pages.
        """
        players = []
        
        print("Fetching NCAA teams...")
        teams = self.get_ncaa_teams()
        print(f"Found {len(teams)} NCAA teams")
        
        # Process first 60 teams (to avoid rate limiting)
        for i, team in enumerate(teams[:60]):
            team_name = team.get('name', 'Unknown')
            team_id = team.get('id', '')
            team_slug = team.get('slug', '')
            
            if not team_id or not team_slug:
                continue

            roster_url = f"https://www.collegehockeynews.com/reports/roster/{team_slug}/{team_id}"
            stats_url = f"https://www.collegehockeynews.com/stats/team/{team_slug}/{team_id}"
            roster_html = self._make_text_request(roster_url)
            stats_html = self._make_text_request(stats_url)

            if not roster_html:
                continue

            stats_by_name = self._parse_ncaa_stats_table(stats_html) if stats_html else {}
            soup = BeautifulSoup(roster_html, "html.parser")
            tables = soup.find_all("table")
            if not tables:
                continue

            for row in tables[0].find_all("tr"):
                cells = [cell.get_text(" ", strip=True) for cell in row.find_all("td")]
                if len(cells) < 10:
                    continue

                name = self._normalize_ncaa_name(cells[2])
                birth_date = cells[7]
                hometown = cells[8]

                if not name or not self.is_finnish(name, '', hometown):
                    continue

                stat_row = stats_by_name.get(name, {})
                player_id = f"ncaa_{team_id}_{re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')}"

                players.append({
                    'player_id': player_id,
                    'name': name,
                    'team': team_name,
                    'league': 'NCAA',
                    'position': stat_row.get('position') or cells[4] or 'F',
                    'games_played': stat_row.get('games_played', 0),
                    'goals': stat_row.get('goals', 0),
                    'assists': stat_row.get('assists', 0),
                    'points': stat_row.get('points', 0),
                    'plus_minus': 0,
                    'penalty_minutes': stat_row.get('penalty_minutes', 0),
                    'save_percentage': stat_row.get('save_percentage'),
                    'goals_against_average': stat_row.get('goals_against_average'),
                    'shutouts': stat_row.get('shutouts'),
                    'wins': stat_row.get('wins'),
                    'birth_date': birth_date,
                    'nationality': 'FIN',
                    'source': 'collegehockeynews-html',
                    'source_league': 'ncaa',
                    'scraped_at': datetime.now().isoformat()
                })
            
            if (i + 1) % 10 == 0:
                print(f"  Processed {i + 1}/{min(len(teams), 60)} teams, found {len(players)} Finnish players")
        
        print(f"\nTotal NCAA Finnish players: {len(players)}")
        return players
    
    def get_ushl_players(self, season: str = "2024-2025") -> List[Dict]:
        """
        Get USHL players.
        USHL doesn't have a public API, so we use a workaround.
        """
        # USHL uses the same HockeyTech platform as AHL
        # But let's try a different approach - use the stats feed
        players = []
        
        # USHL API endpoint (similar to AHL)
        base_url = "http://lscluster.hockeytech.com/feed"
        
        # Try to get USHL stats
        params = {
            'feed': 'statviewfeed',
            'view': 'players',
            'group': 'skaters',
            'context': 'league',
            'league_code': 'ushl',
            'season': season.replace('-', ''),
            'key': 'c69b9f5fa34c524c',  # Public key
            'client_code': 'ushl',
            'language': 'en',
            'fmt': 'json'
        }
        
        try:
            response = self.session.get(base_url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'siteKit' in data:
                    all_players = data['siteKit'].get('players', [])
                    
                    for player in all_players:
                        name = player.get('name', '')
                        if not name:
                            name = f"{player.get('firstName', '')} {player.get('lastName', '')}".strip()
                        
                        if not name:
                            continue
                        
                        nationality = player.get('nationality', '')
                        birthplace = player.get('birthplace', '')
                        
                        if self.is_finnish(name, nationality, birthplace):
                            players.append({
                                'player_id': f"ushl_{player.get('id', name.replace(' ', '_'))}",
                                'name': name,
                                'team': player.get('teamName', 'Unknown'),
                                'league': 'USHL',
                                'position': player.get('position', 'F'),
                                'games_played': player.get('gamesPlayed', 0),
                                'goals': player.get('goals', 0),
                                'assists': player.get('assists', 0),
                                'points': player.get('points', 0),
                                'plus_minus': player.get('plusMinus', 0),
                                'penalty_minutes': player.get('penaltyMinutes', 0),
                                'nationality': nationality or 'FIN',
                                'source': 'hockeytech',
                                'source_league': 'ushl',
                                'scraped_at': datetime.now().isoformat()
                            })
        except Exception as e:
            print(f"USHL API error: {e}")
        
        print(f"USHL Finnish players: {len(players)}")
        return players
    
    def get_ohl_players(self, season: str = "2024-2025") -> List[Dict]:
        """Get OHL (Ontario Hockey League) players."""
        players = []
        
        # OHL uses the same HockeyTech platform
        base_url = "http://lscluster.hockeytech.com/feed"
        
        params = {
            'feed': 'statviewfeed',
            'view': 'players',
            'group': 'skaters',
            'context': 'league',
            'league_code': 'ohl',
            'season': season.replace('-', ''),
            'key': 'c69b9f5fa34c524c',
            'client_code': 'ohl',
            'language': 'en',
            'fmt': 'json'
        }
        
        try:
            response = self.session.get(base_url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'siteKit' in data:
                    all_players = data['siteKit'].get('players', [])
                    
                    for player in all_players:
                        name = player.get('name', '')
                        if not name:
                            name = f"{player.get('firstName', '')} {player.get('lastName', '')}".strip()
                        
                        if not name:
                            continue
                        
                        nationality = player.get('nationality', '')
                        birthplace = player.get('birthplace', '')
                        
                        if self.is_finnish(name, nationality, birthplace):
                            players.append({
                                'player_id': f"ohl_{player.get('id', name.replace(' ', '_'))}",
                                'name': name,
                                'team': player.get('teamName', 'Unknown'),
                                'league': 'OHL',
                                'position': player.get('position', 'F'),
                                'games_played': player.get('gamesPlayed', 0),
                                'goals': player.get('goals', 0),
                                'assists': player.get('assists', 0),
                                'points': player.get('points', 0),
                                'plus_minus': player.get('plusMinus', 0),
                                'penalty_minutes': player.get('penaltyMinutes', 0),
                                'nationality': nationality or 'FIN',
                                'source': 'hockeytech',
                                'source_league': 'ohl',
                                'scraped_at': datetime.now().isoformat()
                            })
        except Exception as e:
            print(f"OHL API error: {e}")
        
        print(f"OHL Finnish players: {len(players)}")
        return players
    
    def get_whl_players(self, season: str = "2024-2025") -> List[Dict]:
        """Get WHL (Western Hockey League) players."""
        players = []
        
        base_url = "http://lscluster.hockeytech.com/feed"
        
        params = {
            'feed': 'statviewfeed',
            'view': 'players',
            'group': 'skaters',
            'context': 'league',
            'league_code': 'whl',
            'season': season.replace('-', ''),
            'key': 'c69b9f5fa34c524c',
            'client_code': 'whl',
            'language': 'en',
            'fmt': 'json'
        }
        
        try:
            response = self.session.get(base_url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'siteKit' in data:
                    all_players = data['siteKit'].get('players', [])
                    
                    for player in all_players:
                        name = player.get('name', '')
                        if not name:
                            name = f"{player.get('firstName', '')} {player.get('lastName', '')}".strip()
                        
                        if not name:
                            continue
                        
                        nationality = player.get('nationality', '')
                        birthplace = player.get('birthplace', '')
                        
                        if self.is_finnish(name, nationality, birthplace):
                            players.append({
                                'player_id': f"whl_{player.get('id', name.replace(' ', '_'))}",
                                'name': name,
                                'team': player.get('teamName', 'Unknown'),
                                'league': 'WHL',
                                'position': player.get('position', 'F'),
                                'games_played': player.get('gamesPlayed', 0),
                                'goals': player.get('goals', 0),
                                'assists': player.get('assists', 0),
                                'points': player.get('points', 0),
                                'plus_minus': player.get('plusMinus', 0),
                                'penalty_minutes': player.get('penaltyMinutes', 0),
                                'nationality': nationality or 'FIN',
                                'source': 'hockeytech',
                                'source_league': 'whl',
                                'scraped_at': datetime.now().isoformat()
                            })
        except Exception as e:
            print(f"WHL API error: {e}")
        
        print(f"WHL Finnish players: {len(players)}")
        return players
    
    def get_qmjhl_players(self, season: str = "2024-2025") -> List[Dict]:
        """Get QMJHL (Quebec Major Junior Hockey League) players."""
        players = []
        
        base_url = "http://lscluster.hockeytech.com/feed"
        
        params = {
            'feed': 'statviewfeed',
            'view': 'players',
            'group': 'skaters',
            'context': 'league',
            'league_code': 'qmjhl',
            'season': season.replace('-', ''),
            'key': 'c69b9f5fa34c524c',
            'client_code': 'qmjhl',
            'language': 'en',
            'fmt': 'json'
        }
        
        try:
            response = self.session.get(base_url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'siteKit' in data:
                    all_players = data['siteKit'].get('players', [])
                    
                    for player in all_players:
                        name = player.get('name', '')
                        if not name:
                            name = f"{player.get('firstName', '')} {player.get('lastName', '')}".strip()
                        
                        if not name:
                            continue
                        
                        nationality = player.get('nationality', '')
                        birthplace = player.get('birthplace', '')
                        
                        if self.is_finnish(name, nationality, birthplace):
                            players.append({
                                'player_id': f"qmjhl_{player.get('id', name.replace(' ', '_'))}",
                                'name': name,
                                'team': player.get('teamName', 'Unknown'),
                                'league': 'QMJHL',
                                'position': player.get('position', 'F'),
                                'games_played': player.get('gamesPlayed', 0),
                                'goals': player.get('goals', 0),
                                'assists': player.get('assists', 0),
                                'points': player.get('points', 0),
                                'plus_minus': player.get('plusMinus', 0),
                                'penalty_minutes': player.get('penaltyMinutes', 0),
                                'nationality': nationality or 'FIN',
                                'source': 'hockeytech',
                                'source_league': 'qmjhl',
                                'scraped_at': datetime.now().isoformat()
                            })
        except Exception as e:
            print(f"QMJHL API error: {e}")
        
        print(f"QMJHL Finnish players: {len(players)}")
        return players
    
    def collect_all(self, season: str = "2024-2025") -> Dict:
        """Collect from all leagues."""
        results = {
            'generated_at': datetime.now().isoformat(),
            'season': season,
            'data_source': 'college-northamerican-juniors',
            'leagues': {},
            'players': []
        }
        
        print("=" * 60)
        print("Collecting NCAA and North American Junior League Data")
        print("=" * 60)
        
        # Collect from each league
        print("\n--- NCAA ---")
        ncaa_players = self.get_ncaa_player_stats(season)
        results['leagues']['ncaa'] = len(ncaa_players)
        results['players'].extend(ncaa_players)
        
        print("\n--- USHL ---")
        ushl_players = self.get_ushl_players(season)
        results['leagues']['ushl'] = len(ushl_players)
        results['players'].extend(ushl_players)
        
        print("\n--- OHL ---")
        ohl_players = self.get_ohl_players(season)
        results['leagues']['ohl'] = len(ohl_players)
        results['players'].extend(ohl_players)
        
        print("\n--- WHL ---")
        whl_players = self.get_whl_players(season)
        results['leagues']['whl'] = len(whl_players)
        results['players'].extend(whl_players)
        
        print("\n--- QMJHL ---")
        qmjhl_players = self.get_qmjhl_players(season)
        results['leagues']['qmjhl'] = len(qmjhl_players)
        results['players'].extend(qmjhl_players)
        
        # Sort by points
        results['players'].sort(key=lambda x: x.get('points', 0), reverse=True)
        results['total_players'] = len(results['players'])
        
        return results


def save_data(data: Dict, filename: str = "league_prospects_na.json"):
    """Save scraped data to JSON."""
    output_dir = Path(__file__).parent.parent.parent / 'static' / 'data' / 'leagues'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / filename
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Data saved to {output_path}")
    return output_path


def main():
    """Main entry point."""
    print("=" * 70)
    print("NCAA and North American Junior Leagues - Finnish Prospect Collector")
    print("=" * 70)
    print()
    
    collector = CollegeAndJuniorCollector()
    
    # Get current season
    current_year = datetime.now().year
    season = f"{current_year}-{current_year + 1}"
    
    results = collector.collect_all(season)
    
    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total Finnish players: {results['total_players']}")
    print("\nBy league:")
    for league, count in results['leagues'].items():
        print(f"  {league.upper()}: {count} players")
    
    # Show top prospects
    if results['players']:
        print("\nTop 20 Finnish prospects by points:")
        for i, p in enumerate(results['players'][:20], 1):
            print(f"  {i}. {p['name']} ({p['league']}, {p['team']}): {p['goals']}G + {p['assists']}A = {p['points']}P")
    
    # Save data
    save_data(results)
    
    return results


if __name__ == "__main__":
    main()
