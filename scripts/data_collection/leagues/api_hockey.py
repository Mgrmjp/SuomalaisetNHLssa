"""
API-Hockey data collector
Get free API key at: https://api-hockey.io/
Free tier: 100 requests/day
"""
import os
import time
import requests
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

# Try to load .env.local file
def _load_env_file():
    """Load environment variables from .env.local"""
    env_paths = [
        Path('.env.local'),
        Path(__file__).parent.parent.parent.parent / '.env.local',
        Path('.env'),
    ]
    
    for env_path in env_paths:
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"\'')
                        if key not in os.environ:
                            os.environ[key] = value
            break

_load_env_file()


class APIHockeyCollector:
    """
    Collect prospect data using API-Hockey
    
    Sign up: https://api-hockey.io/
    Pricing: Free (100 req/day) or €15/month (10k req/day)
    """
    
    BASE_URL = "https://v1.hockey.api-sports.io"
    
    # League IDs from API-Hockey
    # Fetched dynamically via: GET /leagues?season=2024
    LEAGUES = {
        'nhl': 57,
        'ahl': 58,        # American Hockey League
        'echl': 12,
        'liiga': 16,      # Finnish Liiga ✓
        'shl': 47,        # Swedish Hockey League ✓
        'khl': 32,        # Kontinental Hockey League
        'del': 19,        # German DEL
        'czech': 22,      # Czech Extraliga
        'switzerland': 20, # Swiss National League
        'slovakia': 23,    # Slovak Extraliga
        'ncaa': 11,        # NCAA
        'mestis': 14,      # Finnish Mestis
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize collector
        
        Args:
            api_key: API-Hockey API key. If not provided, looks for APIHOCKEY_KEY env var.
        """
        self.api_key = api_key or os.getenv('APIHOCKEY_KEY')
        if not self.api_key:
            raise ValueError(
                "API-Hockey key required.\n"
                "Get free key at: https://api-hockey.io/\n"
                "Set APIHOCKEY_KEY environment variable or pass to constructor."
            )
        
        self.headers = {
            'x-rapidapi-key': self.api_key,
            'x-rapidapi-host': 'v1.hockey.api-sports.io'
        }
        self.request_count = 0
        self.max_requests = 100  # Free tier limit
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make API request with rate limiting"""
        if self.request_count >= self.max_requests:
            raise Exception(f"Daily request limit reached ({self.max_requests})")
        
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            response = requests.get(
                url, 
                headers=self.headers, 
                params=params, 
                timeout=30
            )
            response.raise_for_status()
            self.request_count += 1
            
            # Rate limiting - be nice to the API
            time.sleep(0.5)
            
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return {}
    
    def get_teams(self, league: str, season: str) -> List[Dict]:
        """
        Get teams in a league
        
        Args:
            league: League name or ID (e.g., 'liiga', 'shl', 'ahl')
            season: Season (e.g., '2024' for 2024-2025 season)
        """
        league_id = self._get_league_id(league)
        
        data = self._make_request('teams', {
            'league': league_id,
            'season': season
        })
        
        return data.get('response', [])
    
    def get_players(self, team_id: int, season: str) -> List[Dict]:
        """Get players for a team"""
        data = self._make_request('players', {
            'team': team_id,
            'season': season
        })
        
        return data.get('response', [])
    
    def get_standings(self, league: str, season: str) -> List[Dict]:
        """Get league standings"""
        league_id = self._get_league_id(league)
        
        data = self._make_request('standings', {
            'league': league_id,
            'season': season
        })
        
        return data.get('response', [])
    
    def get_player_stats(self, player_id: int, season: str) -> Dict:
        """Get detailed stats for a player"""
        data = self._make_request('players', {
            'id': player_id,
            'season': season
        })
        
        results = data.get('response', [])
        return results[0] if results else {}
    
    def _get_league_id(self, league: str) -> int:
        """Convert league name to ID"""
        if league.isdigit():
            return int(league)
        
        league_id = self.LEAGUES.get(league.lower())
        if not league_id:
            raise ValueError(
                f"Unknown league: {league}\n"
                f"Supported: {', '.join(self.LEAGUES.keys())}"
            )
        return league_id
    
    def collect_finnish_players(
        self, 
        league: str, 
        season: str,
        include_stats: bool = True
    ) -> List[Dict]:
        """
        Collect all Finnish players from a league
        
        Args:
            league: League name (e.g., 'liiga', 'shl', 'ahl')
            season: Season (e.g., '2024')
            include_stats: Whether to fetch detailed stats (uses more requests)
        
        Returns:
            List of Finnish player dictionaries
        """
        print(f"Collecting Finnish players from {league.upper()} (season {season})...")
        print(f"Requests used: {self.request_count}/{self.max_requests}")
        
        teams = self.get_teams(league, season)
        if not teams:
            print(f"  No teams found for {league}")
            return []
        
        print(f"  Found {len(teams)} teams")
        
        finnish_players = []
        
        for team in teams:
            team_name = team.get('name', 'Unknown')
            team_id = team.get('id')
            
            players = self.get_players(team_id, season)
            
            for player in players:
                nationality = player.get('nationality', '')
                if nationality and nationality.upper() in ['FI', 'FIN']:
                    player_data = {
                        'player_id': f"ah_{player.get('id')}",
                        'name': f"{player.get('firstname', '')} {player.get('lastname', '')}".strip(),
                        'team': team_name,
                        'league': league.upper(),
                        'position': player.get('position', 'F'),
                        'nationality': 'FIN',
                        'age': player.get('age'),
                        'height': player.get('height'),
                        'weight': player.get('weight'),
                        'source_league': league.lower(),
                        'data_source': 'api-hockey'
                    }
                    
                    # Fetch detailed stats if requested
                    if include_stats:
                        stats = self.get_player_stats(player.get('id'), season)
                        if stats:
                            player_data['stats'] = stats.get('statistics', [{}])[0]
                    
                    finnish_players.append(player_data)
            
            print(f"    {team_name}: {len([p for p in players if p.get('nationality') == 'FI'])} Finnish players")
        
        print(f"  Total Finnish players: {len(finnish_players)}")
        return finnish_players
    
    def collect_multiple_leagues(
        self, 
        leagues: List[str], 
        season: str,
        priority_only: bool = False
    ) -> Dict:
        """
        Collect from multiple leagues
        
        Args:
            leagues: List of league names
            season: Season
            priority_only: If True, stop when approaching request limit
        """
        all_players = []
        results = {
            'generated_at': datetime.now().isoformat(),
            'season': season,
            'data_source': 'api-hockey',
            'requests_used': 0,
            'leagues': {},
            'players': []
        }
        
        for league in leagues:
            if priority_only and self.request_count >= self.max_requests * 0.8:
                print(f"\n⚠️  Approaching request limit. Stopping.")
                results['incomplete'] = True
                break
            
            try:
                players = self.collect_finnish_players(league, season, include_stats=False)
                all_players.extend(players)
                results['leagues'][league] = len(players)
            except Exception as e:
                print(f"  Error collecting {league}: {e}")
                results['leagues'][league] = 0
        
        # Sort by name
        all_players.sort(key=lambda x: x['name'])
        
        results['players'] = all_players
        results['requests_used'] = self.request_count
        results['total_players'] = len(all_players)
        
        return results


def main():
    """Demo usage"""
    import json
    from pathlib import Path
    
    print("=" * 60)
    print("API-Hockey Collector Demo")
    print("=" * 60)
    print()
    
    # Check for API key
    api_key = os.getenv('APIHOCKEY_KEY')
    
    if not api_key:
        print("❌ No API key found!")
        print()
        print("To use real data collection:")
        print("1. Sign up for free at https://api-hockey.io/")
        print("2. Get your API key")
        print("3. Set environment variable:")
        print("   export APIHOCKEY_KEY='your-key-here'")
        print()
        print("With free tier (100 requests/day), you can:")
        print("- Get all teams from 3-4 leagues (~10-20 requests)")
        print("- Get all Finnish players (~20-40 requests)")
        print("- Perfect for tracking priority leagues!")
        return
    
    # Initialize collector
    try:
        collector = APIHockeyCollector(api_key)
    except ValueError as e:
        print(f"Error: {e}")
        return
    
    # Collect from priority leagues
    priority_leagues = ['liiga', 'shl', 'ahl']
    season = '2024'
    
    print(f"Collecting data for season {season}...")
    print(f"Priority leagues: {', '.join(priority_leagues)}")
    print()
    
    data = collector.collect_multiple_leagues(
        priority_leagues, 
        season,
        priority_only=True
    )
    
    # Print results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"\nRequests used: {data['requests_used']}/100")
    print(f"Total players: {data['total_players']}")
    print()
    
    for league, count in data['leagues'].items():
        print(f"  {league.upper()}: {count} Finnish players")
    
    if data['players']:
        print("\nSample players:")
        for p in data['players'][:10]:
            print(f"  {p['name']} ({p['league']}, {p['team']})")
    
    # Save data
    output_dir = Path(__file__).parent.parent.parent.parent / 'static' / 'data' / 'leagues'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / 'league_prospects_apihockey.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Data saved to {output_file}")


if __name__ == "__main__":
    main()
