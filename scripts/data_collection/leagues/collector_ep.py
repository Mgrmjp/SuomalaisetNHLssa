"""Working league data collector using EliteProspects API."""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from leagues.eliteprospects import EliteProspectsAdapter
from leagues.base import PlayerStats


class EPLeagueCollector:
    """Collect prospect data from EliteProspects (covers all major leagues)."""
    
    def __init__(self, data_dir: str = "static/data/leagues"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.adapter = EliteProspectsAdapter()
    
    def collect_all_leagues(self, season: str = None, finnish_only: bool = True) -> Dict[str, List[PlayerStats]]:
        """Collect data from all leagues via EliteProspects."""
        results = {}
        
        print(f"Collecting prospect data via EliteProspects...")
        print("=" * 60)
        
        # Collect each league separately
        for league_slug, league_name in self.adapter.LEAGUES.items():
            print(f"\n{league_name}...")
            try:
                players = self.adapter.get_all_players(season, specific_league=league_slug)
                results[league_slug] = players
                print(f"  ✓ {len(players)} Finnish players")
            except Exception as e:
                print(f"  ✗ Error: {e}")
                results[league_slug] = []
        
        return results
    
    def merge_and_deduplicate(self, league_data: Dict[str, List[PlayerStats]]) -> List[Dict]:
        """Merge data and deduplicate players."""
        all_players = []
        seen_ids = set()
        
        for league, players in league_data.items():
            for player in players:
                # Deduplicate by player ID
                if player.player_id not in seen_ids:
                    seen_ids.add(player.player_id)
                    player_dict = player.to_dict()
                    player_dict['source_league'] = league
                    all_players.append(player_dict)
        
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
    
    def get_summary(self, data: List[Dict], league_data: Dict[str, List[PlayerStats]]) -> Dict:
        """Generate summary statistics."""
        leagues = {}
        positions = {}
        total_points = 0
        
        # Count by original league
        for league_slug, players in league_data.items():
            leagues[self.adapter.LEAGUES.get(league_slug, league_slug)] = len(players)
        
        # Count positions from merged data
        for player in data:
            position = player.get('position', 'Unknown')
            positions[position] = positions.get(position, 0) + 1
            total_points += player.get('points', 0)
        
        return {
            'total_players': len(data),
            'by_league': leagues,
            'by_position': positions,
            'total_points': total_points,
            'top_scorers': data[:15]
        }


def main():
    """CLI entry point."""
    collector = EPLeagueCollector()
    
    # Collect data from all leagues
    league_data = collector.collect_all_leagues(finnish_only=True)
    
    # Merge and deduplicate
    merged = collector.merge_and_deduplicate(league_data)
    
    # Generate summary
    summary = collector.get_summary(merged, league_data)
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total Finnish prospects: {summary['total_players']}")
    print(f"\nBy league:")
    for league, count in sorted(summary['by_league'].items(), key=lambda x: -x[1]):
        print(f"  {league}: {count}")
    print(f"\nBy position:")
    for pos, count in sorted(summary['by_position'].items(), key=lambda x: -x[1]):
        print(f"  {pos}: {count}")
    
    print(f"\nTop 15 scorers:")
    for i, player in enumerate(summary['top_scorers'], 1):
        print(f"  {i}. {player['name']} ({player['league']}) - "
              f"{player['goals']}G + {player['assists']}A = {player['points']}P")
    
    # Save to file
    collector.save_data(merged)


if __name__ == "__main__":
    main()
