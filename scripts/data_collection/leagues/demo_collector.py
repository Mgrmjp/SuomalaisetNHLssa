"""Demo collector - generates sample data to show system capabilities."""

import json
import random
from pathlib import Path
from datetime import datetime

# Sample Finnish prospects data (simulated)
SAMPLE_PLAYERS = {
    'liiga': [
        {'name': 'Oliver Suvanto', 'team': 'Tappara', 'pos': 'C', 'gp': 42, 'g': 12, 'a': 18, 'p': 30},
        {'name': 'Juho Piiparinen', 'team': 'Tappara', 'pos': 'D', 'gp': 38, 'g': 5, 'a': 15, 'p': 20},
        {'name': 'Vilho Vanhatalo', 'team': 'Tappara Jr.', 'pos': 'RW', 'gp': 35, 'g': 14, 'a': 11, 'p': 25},
        {'name': 'Samu Alalauri', 'team': 'Pelicans', 'pos': 'D', 'gp': 40, 'g': 3, 'a': 12, 'p': 15},
        {'name': 'Luka Arkko', 'team': 'Pelicans Jr.', 'pos': 'LW', 'gp': 32, 'g': 8, 'a': 9, 'p': 17},
        {'name': 'Ossi Tukio', 'team': 'Ilves Jr.', 'pos': 'D', 'gp': 36, 'g': 2, 'a': 14, 'p': 16},
        {'name': 'Jiko Laitinen', 'team': 'Ilves Jr.', 'pos': 'C', 'gp': 39, 'g': 10, 'a': 13, 'p': 23},
        {'name': 'Joel Tarvainen', 'team': 'KalPa Jr.', 'pos': 'D', 'gp': 34, 'g': 4, 'a': 8, 'p': 12},
    ],
    'shl': [
        {'name': 'Leo Tuuva', 'team': 'Lukko', 'pos': 'RW', 'gp': 38, 'g': 7, 'a': 10, 'p': 17},
        {'name': 'Vertti Svensk', 'team': 'SaiPa Jr.', 'pos': 'D', 'gp': 41, 'g': 3, 'a': 11, 'p': 14},
        {'name': 'Anttoni Uronen', 'team': 'HIFK', 'pos': 'C', 'gp': 37, 'g': 9, 'a': 12, 'p': 21},
        {'name': 'Olli Wahlroos', 'team': 'TPS Jr.', 'pos': 'LW', 'gp': 33, 'g': 6, 'a': 8, 'p': 14},
        {'name': 'Oiva Juntunen', 'team': 'KooKoo Jr.', 'pos': 'LW', 'gp': 35, 'g': 5, 'a': 9, 'p': 14},
    ],
    'czech': [
        {'name': 'Eelis Uronen', 'team': 'HIFK Jr.', 'pos': 'D', 'gp': 31, 'g': 2, 'a': 7, 'p': 9},
        {'name': 'Vilmeri Vaananen', 'team': 'Jokerit Jr.', 'pos': 'D', 'gp': 29, 'g': 1, 'a': 6, 'p': 7},
    ],
    'del': [
        {'name': 'Veeti Rasanen', 'team': 'Jokerit Jr.', 'pos': 'LW', 'gp': 30, 'g': 4, 'a': 5, 'p': 9},
        {'name': 'Miko Vatjus', 'team': 'Lukko Jr.', 'pos': 'C', 'gp': 28, 'g': 3, 'a': 8, 'p': 11},
    ],
    'ahl': [
        {'name': 'Ville Koivunen', 'team': 'Chicago Wolves', 'pos': 'C', 'gp': 45, 'g': 11, 'a': 19, 'p': 30},
        {'name': 'Jani Nyman', 'team': 'Coachella Valley', 'pos': 'LW', 'gp': 42, 'g': 13, 'a': 14, 'p': 27},
        {'name': 'Juho Piiparinen', 'team': 'Henderson Silver Knights', 'pos': 'C', 'gp': 40, 'g': 8, 'a': 16, 'p': 24},
        {'name': 'Brad Lambert', 'team': 'Manitoba Moose', 'pos': 'C', 'gp': 38, 'g': 10, 'a': 15, 'p': 25},
    ],
    'ncaa': [
        {'name': 'Oscar Hemming', 'team': 'Boston College', 'pos': 'LW', 'gp': 36, 'g': 9, 'a': 13, 'p': 22},
        {'name': 'Matias Vanhanen', 'team': 'Everett Silvertips', 'pos': 'LW', 'gp': 34, 'g': 7, 'a': 11, 'p': 18},
        {'name': 'Jasper Kuhta', 'team': 'Ottawa 67s', 'pos': 'C', 'gp': 33, 'g': 6, 'a': 10, 'p': 16},
    ],
}


def generate_demo_data():
    """Generate demo prospect data."""
    print("=" * 60)
    print("DEMO: League Prospect Collection System")
    print("=" * 60)
    print("\nCollecting data from 6 major leagues...\n")
    
    all_players = []
    league_counts = {}
    
    for league, players in SAMPLE_PLAYERS.items():
        league_name = {
            'liiga': 'Liiga (Finland)',
            'shl': 'SHL (Sweden)',
            'czech': 'Czech Extraliga',
            'del': 'DEL (Germany)',
            'ahl': 'AHL (North America)',
            'ncaa': 'NCAA (College)',
        }.get(league, league)
        
        print(f"{league_name}...")
        print(f"  ✓ {len(players)} Finnish players")
        
        for p in players:
            player_data = {
                'player_id': f"demo_{p['name'].lower().replace(' ', '_')}",
                'name': p['name'],
                'team': p['team'],
                'league': league.upper() if league in ['ahl', 'ncaa'] else league.capitalize(),
                'position': p['pos'],
                'games_played': p['gp'],
                'goals': p['g'],
                'assists': p['a'],
                'points': p['p'],
                'plus_minus': random.randint(-10, 20),
                'penalty_minutes': random.randint(10, 60),
                'source_league': league,
            }
            all_players.append(player_data)
        
        league_counts[league_name] = len(players)
    
    # Sort by points
    all_players.sort(key=lambda x: x['points'], reverse=True)
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total Finnish prospects: {len(all_players)}")
    print(f"\nBy league:")
    for league, count in sorted(league_counts.items(), key=lambda x: -x[1]):
        print(f"  {league}: {count}")
    
    print(f"\nTop 10 scorers:")
    for i, p in enumerate(all_players[:10], 1):
        print(f"  {i}. {p['name']} ({p['league']}) - "
              f"{p['goals']}G + {p['assists']}A = {p['points']}P")
    
    # Save to file
    data_dir = Path("static/data/leagues")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    filepath = data_dir / "league_prospects_demo.json"
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump({
            'generated_at': datetime.now().isoformat(),
            'demo': True,
            'note': 'This is demo data. Real implementation requires EliteProspects API key.',
            'count': len(all_players),
            'players': all_players
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Demo data saved to {filepath}")
    print(f"\nNote: This is sample data demonstrating the system architecture.")
    print("For production use, obtain an EliteProspects API key or implement")
    print("individual league scrapers/adapters.")
    
    return all_players


if __name__ == "__main__":
    generate_demo_data()
