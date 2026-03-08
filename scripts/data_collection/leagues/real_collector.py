"""
Real data collector combining available league APIs
Falls back to demo for leagues without accessible public APIs
"""
import sys
import json
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from liiga_real import LiigaRealCollector
from shl_real import SHLRealCollector
from ahl_real import AHLRealCollector


class RealDataCollector:
    """
    Collects real prospect data from available league APIs
    Uses demo data for leagues without accessible APIs
    """
    
    def __init__(self):
        self.liiga = LiigaRealCollector()
        self.shl = SHLRealCollector()
        self.ahl = AHLRealCollector()
        
        # Track which leagues have real data vs demo
        self.real_leagues = []
        self.demo_leagues = []
    
    def collect_liiga(self) -> List[Dict]:
        """Collect Liiga data"""
        try:
            data = self.liiga.collect_finnish_players()
            if data:
                self.real_leagues.append('Liiga')
                return data
        except Exception as e:
            print(f"Liiga collection failed: {e}")
        
        self.demo_leagues.append('Liiga')
        return self._demo_data_for_league('Liiga', 8)
    
    def collect_shl(self) -> List[Dict]:
        """Collect SHL data"""
        try:
            data = self.shl.collect_finnish_players()
            if data:
                self.real_leagues.append('SHL')
                return data
        except Exception as e:
            print(f"SHL collection failed: {e}")
        
        self.demo_leagues.append('SHL')
        return self._demo_data_for_league('SHL', 5)
    
    def collect_ahl(self) -> List[Dict]:
        """Collect AHL data"""
        try:
            data = self.ahl.collect_finnish_players()
            if data:
                self.real_leagues.append('AHL')
                return data
        except Exception as e:
            print(f"AHL collection failed: {e}")
        
        self.demo_leagues.append('AHL')
        return self._demo_data_for_league('AHL', 4)
    
    def collect_other_leagues(self) -> List[Dict]:
        """Collect from leagues without accessible APIs (demo data)"""
        other_leagues = [
            ('Czech Extraliga', 2),
            ('DEL', 2),
            ('NCAA', 3),
            ('Slovak Extraliga', 1),
            ('Swiss NL', 1),
        ]
        
        all_players = []
        for league_name, count in other_leagues:
            self.demo_leagues.append(league_name)
            all_players.extend(self._demo_data_for_league(league_name, count))
        
        return all_players
    
    def _demo_data_for_league(self, league: str, count: int) -> List[Dict]:
        """Generate demo data for a specific league"""
        # Import demo generator
        sys.path.insert(0, str(Path(__file__).parent))
        from demo_generator import DemoDataGenerator
        
        generator = DemoDataGenerator()
        league_key = league.lower().replace(' ', '_')
        
        # Generate players and convert to dict format
        players = []
        for _ in range(count):
            p = generator.generate_player(league_key)
            players.append({
                'player_id': p.player_id,
                'name': p.name,
                'team': p.team,
                'league': p.league,
                'position': p.position,
                'games_played': p.games_played,
                'goals': p.goals,
                'assists': p.assists,
                'points': p.points,
                'plus_minus': p.plus_minus,
                'penalty_minutes': p.penalty_minutes,
                'save_percentage': p.save_percentage,
                'goals_against_average': p.goals_against_average,
                'shutouts': p.shutouts,
                'birth_date': p.birth_date,
                'height_cm': p.height_cm,
                'weight_kg': p.weight_kg,
                'nationality': p.nationality,
                'source_league': p.source_league,
                'demo': True
            })
        
        return players
    
    def collect_all(self, use_parallel: bool = True) -> Dict:
        """Collect data from all leagues"""
        print("=" * 60)
        print("REAL DATA COLLECTION")
        print("=" * 60)
        print("\nAttempting to collect from available league APIs...\n")
        
        all_players = []
        
        if use_parallel:
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = {
                    executor.submit(self.collect_liiga): 'Liiga',
                    executor.submit(self.collect_shl): 'SHL',
                    executor.submit(self.collect_ahl): 'AHL',
                }
                
                for future in as_completed(futures):
                    league_name = futures[future]
                    try:
                        players = future.result()
                        all_players.extend(players)
                    except Exception as e:
                        print(f"Error collecting {league_name}: {e}")
        else:
            all_players.extend(self.collect_liiga())
            all_players.extend(self.collect_shl())
            all_players.extend(self.collect_ahl())
        
        # Add demo data for other leagues
        all_players.extend(self.collect_other_leagues())
        
        # Sort by points
        all_players.sort(key=lambda x: x['points'], reverse=True)
        
        return {
            'generated_at': datetime.now().isoformat(),
            'real_leagues': self.real_leagues,
            'demo_leagues': self.demo_leagues,
            'note': f"Real data from: {', '.join(self.real_leagues) if self.real_leagues else 'None'}. "
                    f"Demo data for: {', '.join(self.demo_leagues)}",
            'count': len(all_players),
            'players': all_players
        }
    
    def save_data(self, data: Dict, output_path: Optional[Path] = None):
        """Save collected data to JSON"""
        if output_path is None:
            output_path = Path(__file__).parent.parent.parent.parent / 'static' / 'data' / 'leagues' / 'league_prospects_real.json'
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Data saved to {output_path}")
        return output_path


def main():
    collector = RealDataCollector()
    data = collector.collect_all(use_parallel=True)
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"\nTotal players: {data['count']}")
    print(f"Real data leagues: {', '.join(data['real_leagues']) if data['real_leagues'] else 'None'}")
    print(f"Demo data leagues: {', '.join(data['demo_leagues'])}")
    
    # Show by league
    print("\nBy league:")
    league_counts = {}
    for p in data['players']:
        league = p['league']
        league_counts[league] = league_counts.get(league, 0) + 1
    
    for league, count in sorted(league_counts.items(), key=lambda x: -x[1]):
        real_marker = " ✓" if league in data['real_leagues'] else " (demo)"
        print(f"  {league}: {count}{real_marker}")
    
    # Show top 10
    print("\nTop 10 scorers:")
    for i, p in enumerate(data['players'][:10], 1):
        real_marker = "" if p.get('demo') else " ✓"
        print(f"  {i}. {p['name']} ({p['league']}) - {p['goals']}G + {p['assists']}A = {p['points']}P{real_marker}")
    
    collector.save_data(data)
    
    print("\n" + "=" * 60)
    print("NOTES")
    print("=" * 60)
    print("""
✓ = Real data from league API
(demo) = Synthetic data for demonstration

To get real data for all leagues:
- Czech Extraliga: Contact league for API access
- DEL: Contact league for API access  
- NCAA: Use college hockey stats APIs
- Swiss NL: Contact league for API access
- Slovak: Contact league for API access

Or use EliteProspects API (paid) for unified access.
""")


if __name__ == "__main__":
    from typing import Optional
    main()
