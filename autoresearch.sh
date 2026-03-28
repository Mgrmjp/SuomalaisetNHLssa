#!/bin/bash
set -euo pipefail

# Autoresearch shell for headshot coverage optimization
# Measures headshot coverage across all leagues

python3 -c "
import json
import sys

files = [
    'static/data/leagues/league_prospects_official.json',
]

total_players = 0
total_with_headshot = 0
league_stats = {}

for f in files:
    try:
        with open(f) as fp:
            data = json.load(fp)
            for p in data.get('players', []):
                total_players += 1
                league = p.get('league', 'Unknown')
                if league not in league_stats:
                    league_stats[league] = {'total': 0, 'with_headshot': 0}
                league_stats[league]['total'] += 1
                
                if p.get('headshot_url'):
                    total_with_headshot += 1
                    league_stats[league]['with_headshot'] += 1
    except Exception as e:
        print(f'Error reading {f}: {e}', file=sys.stderr)

coverage = (total_with_headshot / total_players * 100) if total_players > 0 else 0

print(f'METRIC headshot_coverage_rate={coverage:.2f}')
print(f'METRIC total_players={total_players}')
print(f'METRIC players_with_headshot={total_with_headshot}')

for league in sorted(league_stats.keys()):
    stats = league_stats[league]
    rate = (stats['with_headshot'] / stats['total'] * 100) if stats['total'] > 0 else 0
    print(f'METRIC league_coverage_{league}={rate:.2f}')
"