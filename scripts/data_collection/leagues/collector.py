"""Main league data collection orchestrator."""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import concurrent.futures

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from leagues import (
    LiigaAdapter, SHLAdapter, AHLAdapter, NCAAAdapter,
    DELAdapter, CzechExtraligaAdapter, SwissNLAdapter,
    ICEHLAdapter, SlovakExtraligaAdapter, KHLAdapter
)
from leagues.base import PlayerStats


class LeagueDataCollector:
    """Collect and merge prospect data from multiple leagues."""
    
    def __init__(self, data_dir: str = "static/data/leagues"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.adapters = {
            # European leagues
            'liiga': LiigaAdapter(),
            'shl': SHLAdapter(),
            'czech': CzechExtraligaAdapter(),
            'del': DELAdapter(),
            'swiss': SwissNLAdapter(),
            'icehl': ICEHLAdapter(),
            'slovak': SlovakExtraligaAdapter(),
            'khl': KHLAdapter(),
            # North American leagues
            'ahl': AHLAdapter(),
            'ncaa': NCAAAdapter(),
        }
    
    def collect_all_leagues(self, season: str = None, finnish_only: bool = True) -> Dict[str, List[PlayerStats]]:
        """Collect data from all supported leagues."""
        results = {}
        
        print(f"Collecting prospect data from {len(self.adapters)} leagues...")
        print("=" * 60)
        
        for league_name, adapter in self.adapters.items():
            print(f"\nCollecting from {league_name.upper()}...")
            try:
                players = adapter.get_all_players(season)
                
                if finnish_only:
                    players = adapter.filter_finnish_players(players)
                
                results[league_name] = players
                print(f"  ✓ Found {len(players)} {'Finnish ' if finnish_only else ''}players")
                
            except Exception as e:
                print(f"  ✗ Error collecting from {league_name}: {e}")
                results[league_name] = []
        
        return results
    
    def collect_parallel(self, season: str = None, finnish_only: bool = True, max_workers: int = 3) -> Dict[str, List[PlayerStats]]:
        """Collect data from all leagues in parallel."""
        results = {}
        
        print(f"Collecting prospect data from {len(self.adapters)} leagues (parallel)...")
        print("=" * 60)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_league = {
                executor.submit(self._collect_single_league, name, adapter, season, finnish_only): name
                for name, adapter in self.adapters.items()
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_league):
                league_name = future_to_league[future]
                try:
                    players = future.result()
                    results[league_name] = players
                except Exception as e:
                    print(f"  ✗ Error in {league_name}: {e}")
                    results[league_name] = []
        
        return results
    
    def _collect_single_league(self, name: str, adapter, season: str, finnish_only: bool) -> List[PlayerStats]:
        """Helper to collect from a single league."""
        print(f"  Starting {name.upper()}...")
        players = adapter.get_all_players(season)
        
        if finnish_only:
            players = adapter.filter_finnish_players(players)
        
        print(f"  ✓ {name.upper()}: {len(players)} players")
        return players
    
    def merge_and_deduplicate(self, league_data: Dict[str, List[PlayerStats]]) -> List[Dict]:
        """Merge data from all leagues and deduplicate players."""
        all_players = []
        seen_names = set()
        
        for league, players in league_data.items():
            for player in players:
                # Simple deduplication by name
                name_key = player.name.lower().replace(" ", "")
                if name_key not in seen_names:
                    seen_names.add(name_key)
                    all_players.append(player.to_dict())
        
        # Sort by points
        all_players.sort(key=lambda x: x.get('points', 0), reverse=True)
        
        return all_players
    
    def save_data(self, data: List[Dict], filename: str = None):
        """Save collected data to JSON."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d")
            filename = f"league_prospects_{timestamp}.json"
        
        filepath = self.data_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'generated_at': datetime.now().isoformat(),
                'count': len(data),
                'players': data
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Data saved to {filepath}")
        print(f"  Total players: {len(data)}")
        return filepath
    
    def get_prospect_summary(self, data: List[Dict]) -> Dict:
        """Generate summary statistics."""
        leagues = {}
        positions = {}
        total_points = 0
        
        for player in data:
            league = player.get('league', 'Unknown')
            position = player.get('position', 'Unknown')
            
            leagues[league] = leagues.get(league, 0) + 1
            positions[position] = positions.get(position, 0) + 1
            total_points += player.get('points', 0)
        
        return {
            'total_players': len(data),
            'by_league': leagues,
            'by_position': positions,
            'total_points': total_points,
            'top_scorers': data[:10]
        }


def main():
    """CLI entry point."""
    collector = LeagueDataCollector()
    
    # Collect data from all leagues (Finnish players only)
    league_data = collector.collect_parallel(finnish_only=True)
    
    # Merge and deduplicate
    merged = collector.merge_and_deduplicate(league_data)
    
    # Generate summary
    summary = collector.get_prospect_summary(merged)
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total Finnish prospects: {summary['total_players']}")
    print(f"\nBy league:")
    for league, count in summary['by_league'].items():
        print(f"  {league}: {count}")
    print(f"\nBy position:")
    for pos, count in summary['by_position'].items():
        print(f"  {pos}: {count}")
    
    print(f"\nTop 10 scorers:")
    for i, player in enumerate(summary['top_scorers'][:10], 1):
        print(f"  {i}. {player['name']} ({player['league']}) - "
              f"{player['goals']}G + {player['assists']}A = {player['points']}P")
    
    # Save to file
    collector.save_data(merged)


if __name__ == "__main__":
    main()
