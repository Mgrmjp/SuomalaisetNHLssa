"""
Real data collection options WITHOUT EliteProspects API

This module documents and implements various approaches to get real
hockey data from public sources.
"""
import requests
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple


class DataSource:
    """Represents a data source option"""
    def __init__(self, name: str, url: str, method: str, 
                 requires_key: bool = False, key_info: str = '',
                 reliability: str = 'unknown', coverage: List[str] = None):
        self.name = name
        self.url = url
        self.method = method
        self.requires_key = requires_key
        self.key_info = key_info
        self.reliability = reliability
        self.coverage = coverage or []


# Document all available data sources
DATA_SOURCES = {
    'liiga_api': DataSource(
        name='Liiga Official API',
        url='https://liiga.fi/api/v1',
        method='REST API',
        requires_key=False,
        reliability='broken',
        coverage=['Liiga'],
        key_info='API appears to have been removed or protected in 2024 site redesign'
    ),
    
    'shl_api': DataSource(
        name='SHL Official API',
        url='https://www.shl.se/p/api',
        method='REST API',
        requires_key=False,
        reliability='broken',
        coverage=['SHL'],
        key_info='Now requires authentication, not publicly accessible'
    ),
    
    'ahl_api': DataSource(
        name='AHL HockeyTech API',
        url='https://lscluster.hockeytech.com/feed',
        method='REST API',
        requires_key=True,
        reliability='working',
        coverage=['AHL', 'ECHL'],
        key_info='Requires HockeyTech API key. Free tier may be available.'
    ),
    
    'nhl_api': DataSource(
        name='NHL Official API',
        url='https://api-web.nhle.com/v1',
        method='REST API',
        requires_key=False,
        reliability='working',
        coverage=['NHL'],
        key_info='Already used by this project for NHL data'
    ),
    
    'hockeydb': DataSource(
        name='HockeyDB',
        url='https://www.hockeydb.com',
        method='Web Scraping',
        requires_key=False,
        reliability='partial',
        coverage=['Liiga', 'SHL', 'AHL', 'KHL', 'NCAA', 'Most leagues'],
        key_info='HTML scraping. Site structure changes frequently.'
    ),
    
    'flashscore': DataSource(
        name='Flashscore',
        url='https://www.flashscore.com',
        method='Web Scraping / API',
        requires_key=False,
        reliability='working',
        coverage=['Liiga', 'SHL', 'Most European leagues'],
        key_info='Has embeddable widgets, scraping possible but TOS restricts'
    ),
    
    'eurohockey': DataSource(
        name='EuroHockey',
        url='https://www.eurohockey.com',
        method='Web Scraping',
        requires_key=False,
        reliability='partial',
        coverage=['European leagues'],
        key_info='Basic stats available via HTML'
    ),
    
    'api_hockey': DataSource(
        name='API-Hockey (API-Football)',
        url='https://api-hockey.io',
        method='REST API',
        requires_key=True,
        reliability='working',
        coverage=['Liiga', 'SHL', 'AHL', 'KHL', 'Most leagues'],
        key_info='Free tier: 100 requests/day. Paid tiers available.'
    ),
    
    'sportradar': DataSource(
        name='Sportradar',
        url='https://sportradar.com',
        method='REST API',
        requires_key=True,
        reliability='working',
        coverage=['All major leagues'],
        key_info='Professional service, paid only'
    ),
    
    'liiga_fever': DataSource(
        name='Liiga Fever (Community)',
        url='https://github.com/liiga/fever',
        method='REST API',
        requires_key=False,
        reliability='community',
        coverage=['Liiga'],
        key_info='Community-maintained API, reliability varies'
    ),
}


def get_api_hockey_players(api_key: str, league_id: str, season: str) -> List[Dict]:
    """
    Fetch players using API-Hockey (api-hockey.io)
    
    Args:
        api_key: Your API-Hockey API key
        league_id: League identifier (see API docs)
        season: Season string (e.g., '2024')
    
    Free tier: 100 requests/day
    """
    url = "https://v1.hockey.api-sports.io/players"
    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': 'v1.hockey.api-sports.io'
    }
    params = {
        'league': league_id,
        'season': season
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        players = []
        for player in data.get('response', []):
            if player.get('nationality') == 'FI':
                players.append({
                    'player_id': f"ah_{player.get('id')}",
                    'name': f"{player.get('firstname', '')} {player.get('lastname', '')}".strip(),
                    'team': player.get('team', {}).get('name', 'Unknown'),
                    'league': league_id,
                    'position': player.get('position', 'F'),
                    'nationality': 'FIN',
                    'source_league': league_id.lower(),
                    'source': 'api-hockey'
                })
        
        return players
    except Exception as e:
        print(f"API-Hockey error: {e}")
        return []


def get_nhl_api_prospects() -> List[Dict]:
    """
    Get prospect data from NHL API
    This works and is already used by the project
    """
    url = "https://api-web.nhle.com/v1/draft/prospects"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        finnish_prospects = []
        for prospect in data.get('prospects', []):
            if prospect.get('birthCountry') == 'FIN':
                finnish_prospects.append({
                    'player_id': f"nhl_{prospect.get('id')}",
                    'name': prospect.get('firstName', {}).get('default', '') + ' ' + 
                           prospect.get('lastName', {}).get('default', ''),
                    'league': 'NHL Prospects',
                    'nationality': 'FIN',
                    'source': 'nhl-api'
                })
        
        return finnish_prospects
    except Exception as e:
        print(f"NHL API error: {e}")
        return []


def print_data_source_guide():
    """Print guide for getting real data without EliteProspects"""
    print("=" * 70)
    print("REAL DATA COLLECTION OPTIONS (No EliteProspects Required)")
    print("=" * 70)
    
    print("\n🟢 RECOMMENDED APPROACHES:\n")
    
    print("1. API-Hockey (Free Tier Available)")
    print("   URL: https://api-hockey.io")
    print("   Cost: Free (100 req/day) or €15/month")
    print("   Coverage: Liiga, SHL, AHL, KHL, DEL, etc.")
    print("   Pros: Simple REST API, good documentation")
    print("   Cons: Limited free tier, need multiple requests for full data")
    print("\n   Usage:")
    print("   - Sign up at api-hockey.io")
    print("   - Get API key")
    print("   - League IDs: Liiga=57, SHL=45, AHL=10, KHL=32, DEL=19")
    print("   - Call: get_api_hockey_players(YOUR_KEY, '57', '2024')")
    
    print("\n2. Web Scraping (Free)")
    print("   Target: Individual league websites")
    print("   Cost: Free")
    print("   Coverage: Per-league implementation needed")
    print("   Pros: No API limits, real-time data")
    print("   Cons: Fragile (sites change), requires maintenance, TOS concerns")
    print("\n   Leagues with scrapable stats:")
    print("   - Liiga: liiga.fi (React app, data in JS)")
    print("   - SHL: shl.se (Dynamic loading)")
    print("   - AHL: theahl.com (HockeyTech - requires key)")
    print("   - Czech: hokej.cz (HTML tables)")
    
    print("\n3. NHL API (Free - Already Implemented)")
    print("   URL: https://api-web.nhle.com")
    print("   Cost: Free")
    print("   Coverage: NHL only")
    print("   Status: ✅ Already integrated in this project")
    
    print("\n\n🟡 ALTERNATIVE PAID OPTIONS:\n")
    
    print("4. Sportradar")
    print("   Cost: ~$500-2000/month")
    print("   Coverage: All major leagues")
    print("   Best for: Commercial projects")
    
    print("\n5. HockeyTech Direct")
    print("   Cost: Contact for pricing")
    print("   Coverage: AHL, ECHL, CHL, USHL")
    print("   Best for: North American prospects")
    
    print("\n\n🔴 CURRENT STATUS:\n")
    
    for key, source in DATA_SOURCES.items():
        status = "✅" if source.reliability == 'working' else "⚠️" if source.reliability == 'partial' else "❌"
        key_required = "🔑" if source.requires_key else ""
        print(f"{status} {source.name} {key_required}")
        if source.reliability == 'broken':
            print(f"   Note: {source.key_info}")
    
    print("\n" + "=" * 70)
    print("QUICK START RECOMMENDATION")
    print("=" * 70)
    print("""
For immediate real data with minimal cost:

1. Sign up for API-Hockey free tier (100 requests/day)
2. Implement API-Hockey collector for priority leagues:
   - Liiga (top priority - Finnish league)
   - SHL (many Finnish players)
   - AHL (NHL prospects)
3. Use demo/placeholder for other leagues initially
4. Add web scraping for leagues not covered by API

Expected cost: €0-15/month
Implementation time: 1-2 days
Data quality: High
    """)


def generate_sample_api_hockey_implementation():
    """Generate sample implementation code for API-Hockey"""
    code = '''
# api_hockey_collector.py - Sample implementation
# Sign up at https://api-hockey.io for API key

import requests
import os
from typing import List, Dict

class APIHockeyCollector:
    """Collect data using API-Hockey (api-hockey.io)"""
    
    BASE_URL = "https://v1.hockey.api-sports.io"
    
    # League IDs from API-Hockey
    LEAGUES = {
        'nhl': 57,
        'ahl': 10,
        'liiga': 57,  # Verify this
        'shl': 45,
        'khl': 32,
        'del': 19,
        'czech': 19,  # Verify
    }
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('APIHOCKEY_KEY')
        if not self.api_key:
            raise ValueError("API key required. Get one at api-hockey.io")
        
        self.headers = {
            'x-rapidapi-key': self.api_key,
            'x-rapidapi-host': 'v1.hockey.api-sports.io'
        }
    
    def get_teams(self, league_id: int, season: str) -> List[Dict]:
        """Get teams in a league"""
        url = f"{self.BASE_URL}/teams"
        params = {'league': league_id, 'season': season}
        
        response = requests.get(url, headers=self.headers, params=params)
        data = response.json()
        return data.get('response', [])
    
    def get_players(self, team_id: int, season: str) -> List[Dict]:
        """Get players for a team"""
        url = f"{self.BASE_URL}/players"
        params = {'team': team_id, 'season': season}
        
        response = requests.get(url, headers=self.headers, params=params)
        data = response.json()
        return data.get('response', [])
    
    def get_player_stats(self, player_id: int, season: str) -> Dict:
        """Get stats for a player"""
        url = f"{self.BASE_URL}/players"
        params = {'id': player_id, 'season': season}
        
        response = requests.get(url, headers=self.headers, params=params)
        data = response.json()
        results = data.get('response', [])
        return results[0] if results else {}
    
    def collect_finnish_players(self, league: str, season: str) -> List[Dict]:
        """Collect all Finnish players from a league"""
        league_id = self.LEAGUES.get(league.lower())
        if not league_id:
            raise ValueError(f"Unknown league: {league}")
        
        teams = self.get_teams(league_id, season)
        finnish_players = []
        
        for team in teams:
            team_id = team.get('id')
            players = self.get_players(team_id, season)
            
            for player in players:
                if player.get('nationality') == 'FI':
                    # Get detailed stats
                    stats = self.get_player_stats(player.get('id'), season)
                    
                    finnish_players.append({
                        'player_id': f"ah_{player.get('id')}",
                        'name': f"{player.get('firstname', '')} {player.get('lastname', '')}".strip(),
                        'team': team.get('name'),
                        'league': league.upper(),
                        'position': player.get('position'),
                        'nationality': 'FIN',
                        'stats': stats.get('statistics', [{}])[0] if stats else {}
                    })
        
        return finnish_players

# Usage:
# collector = APIHockeyCollector('your-api-key')
# players = collector.collect_finnish_players('liiga', '2024')
'''
    return code


if __name__ == "__main__":
    print_data_source_guide()
    
    print("\n\n" + "=" * 70)
    print("SAMPLE API-HOCKEY IMPLEMENTATION")
    print("=" * 70)
    print(generate_sample_api_hockey_implementation())
