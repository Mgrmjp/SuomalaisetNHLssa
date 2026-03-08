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
import json
import time
import os
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


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
        data = self._make_request(url)
        if data and isinstance(data, list):
            return data
        return []
    
    def get_ncaa_player_stats(self, season: str = "2024-2025") -> List[Dict]:
        """
        Get NCAA player stats from collegehockeynews.com.
        Note: The API provides team rosters, not full season stats.
        We'll get roster data and estimate stats from points if available.
        """
        players = []
        
        print("Fetching NCAA teams...")
        teams = self.get_ncaa_teams()
        print(f"Found {len(teams)} NCAA teams")
        
        # Process first 60 teams (to avoid rate limiting)
        for i, team in enumerate(teams[:60]):
            team_name = team.get('name', 'Unknown')
            team_id = team.get('id', '')
            
            if not team_id:
                continue
                
            # Get team roster
            roster_url = f"https://www.collegehockeynews.com/api/v1/teams/{team_id}/roster"
            roster_data = self._make_request(roster_url)
            
            if roster_data and isinstance(roster_data, dict):
                roster = roster_data.get('roster', [])
                for player in roster:
                    name = player.get('name', '')
                    if not name:
                        # Try firstName + lastName
                        first = player.get('firstName', '')
                        last = player.get('lastName', '')
                        name = f"{first} {last}".strip()
                    
                    if not name:
                        continue
                    
                    nationality = player.get('nationality', '')
                    birthplace = player.get('birthplace', '')
                    
                    if self.is_finnish(name, nationality, birthplace):
                        # Get stats if available
                        stats = player.get('stats', {})
                        
                        players.append({
                            'player_id': f"ncaa_{player.get('id', name.replace(' ', '_'))}",
                            'name': name,
                            'team': team_name,
                            'league': 'NCAA',
                            'position': player.get('position', 'F'),
                            'games_played': stats.get('games', 0),
                            'goals': stats.get('goals', 0),
                            'assists': stats.get('assists', 0),
                            'points': stats.get('points', 0),
                            'plus_minus': stats.get('plusMinus', 0),
                            'penalty_minutes': stats.get('penaltyMinutes', 0),
                            'nationality': nationality or 'FIN',
                            'source': 'collegehockeynews',
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
    output_dir = Path(__file__).parent.parent / 'static' / 'data' / 'leagues'
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
