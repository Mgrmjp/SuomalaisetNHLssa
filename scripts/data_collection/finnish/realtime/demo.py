#!/usr/bin/env python3
"""
Real-Time NHL Monitor - Demo Script

Demonstrates the real-time monitoring system functionality
without running as a daemon.
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from state_manager import GameStateManager
from data_updater import DataUpdater


def demo_state_manager():
    """Demonstrate state manager functionality"""
    print("\n" + "="*70)
    print("DEMO 1: Game State Manager")
    print("="*70)

    mgr = GameStateManager()
    print(f"✓ Initialized: {mgr}")

    # Show current stats
    stats = mgr.get_stats()
    print(f"\n📊 Current Stats:")
    for key, value in stats.items():
        print(f"   {key}: {value}")

    print("\n✅ State manager demonstration complete")


def demo_data_updater():
    """Demonstrate data updater functionality"""
    print("\n" + "="*70)
    print("DEMO 2: Data Updater")
    print("="*70)

    updater = DataUpdater()
    print(f"✓ Initialized")
    print(f"   Data directory: {updater.DATA_DIR}")
    print(f"   Directory exists: {updater.DATA_DIR.exists()}")

    # Check if we have data files
    data_files = sorted(updater.DATA_DIR.glob("2025-10-*.json"))
    if data_files:
        print(f"\n📁 Found {len(data_files)} data files")
        print(f"   Latest: {data_files[-1].name}")
        print(f"   Earliest: {data_files[0].name}")

        # Show a sample of the latest file
        with open(data_files[-1], 'r') as f:
            sample = json.load(f)
            print(f"\n📋 Sample Data Structure:")
            print(f"   Date: {sample.get('date')}")
            print(f"   Games: {len(sample.get('games', []))}")
            print(f"   Players: {len(sample.get('players', []))}")
    else:
        print("\n⚠️  No October data files found")

    print("\n✅ Data updater demonstration complete")


def demo_api_schedule():
    """Demonstrate NHL API schedule fetch"""
    print("\n" + "="*70)
    print("DEMO 3: NHL API - Schedule Fetch")
    print("="*70)

    import requests

    today = datetime.now().strftime('%Y-%m-%d')
    url = f"https://api-web.nhle.com/v1/schedule/{today}"

    print(f"Fetching schedule for {today}...")

    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        games_count = sum(len(dg.get('games', [])) for dg in data.get('gameWeek', []))

        print(f"\n✅ API Response:")
        print(f"   URL: {url}")
        print(f"   Status: {response.status_code}")
        print(f"   Total games: {games_count}")

        # Show sample games
        for date_info in data.get('gameWeek', []):
            games = date_info.get('games', [])
            if games:
                print(f"\n🏒 Sample Games ({len(games)} total):")
                for game in games[:3]:
                    away = game['awayTeam']['abbrev']
                    home = game['homeTeam']['abbrev']
                    state = game.get('gameState', 'N/A')
                    print(f"   {away} @ {home} - State: {state}")
                break

        return data

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None


def demo_api_boxscore():
    """Demonstrate NHL API boxscore fetch"""
    print("\n" + "="*70)
    print("DEMO 4: NHL API - Boxscore Fetch")
    print("="*70)

    import requests

    # Use a known game ID from schedule
    today = datetime.now().strftime('%Y-%m-%d')
    url = f"https://api-web.nhle.com/v1/schedule/{today}"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        # Find first game
        game = None
        for date_info in data.get('gameWeek', []):
            if date_info.get('games'):
                game = date_info['games'][0]
                break

        if not game:
            print("No games scheduled today")
            return

        game_id = game['id']
        away = game['awayTeam']['abbrev']
        home = game['homeTeam']['abbrev']

        print(f"Fetching boxscore for game {game_id}: {away} @ {home}")

        # Fetch boxscore
        boxscore_url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/boxscore"
        response = requests.get(boxscore_url, timeout=10)
        boxscore = response.json()

        home_team = boxscore.get('homeTeam', {})
        away_team = boxscore.get('awayTeam', {})

        print(f"\n✅ Boxscore Data:")
        print(f"   Home: {home_team.get('abbrev')} - Score: {home_team.get('score', 0)}")
        print(f"   Away: {away_team.get('abbrev')} - Score: {away_team.get('score', 0)}")
        print(f"   Game State: {boxscore.get('gameState')}")
        print(f"   Period: {boxscore.get('period', {}).get('ordinalNum', 'N/A')}")

        home_players = len(home_team.get('players', []))
        away_players = len(away_team.get('players', []))

        print(f"\n   Players:")
        print(f"   Home: {home_players} players")
        print(f"   Away: {away_players} players")

        return boxscore

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None


def demo_finnish_cache():
    """Demonstrate Finnish player cache"""
    print("\n" + "="*70)
    print("DEMO 5: Finnish Player Cache")
    print("="*70)

    cache_path = Path(__file__).parent.parent / "cache" / "finnish-players.json"

    if not cache_path.exists():
        print(f"⚠️  Cache not found at {cache_path}")
        print("   Run the cache builder first:")
        print("   python3 scripts/data_collection/finnish/build_cache.py")
        return

    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache = json.load(f)
            cache_int = {int(k): v for k, v in cache.items()}

        print(f"✅ Cache loaded:")
        print(f"   Path: {cache_path}")
        print(f"   Total players: {len(cache_int)}")
        print(f"   Cache size: {cache_path.stat().st_size} bytes")

        # Show sample players
        print(f"\n👤 Sample Finnish Players:")
        sample_ids = list(cache_int.keys())[:5]
        for pid in sample_ids:
            info = cache_int[pid]
            print(f"   {pid}: {info.get('name')} ({info.get('position')}) - {info.get('team')}")

    except Exception as e:
        print(f"\n❌ Error: {e}")


def demo_live_monitoring_simulation():
    """Simulate live monitoring"""
    print("\n" + "="*70)
    print("DEMO 6: Live Monitoring Simulation")
    print("="*70)

    print("This simulation shows how the system would monitor live games:")
    print()

    # Simulate a game timeline
    timeline = [
        ("2025-11-22 19:00:00", "FUT", "Scheduled"),
        ("2025-11-22 19:30:00", "LIVE", "Game started!"),
        ("2025-11-22 19:35:00", "LIVE", "First period in progress"),
        ("2025-11-22 20:00:00", "LIVE", "First period ended"),
        ("2025-11-22 20:15:00", "LIVE", "Second period in progress"),
        ("2025-11-22 21:00:00", "LIVE", "Second period ended"),
        ("2025-11-22 21:15:00", "LIVE", "Third period in progress"),
        ("2025-11-22 22:00:00", "LIVE", "Third period ended"),
        ("2025-11-22 22:15:00", "OFF", "Game finished"),
    ]

    mgr = GameStateManager()

    for timestamp, state, description in timeline:
        print(f"[{timestamp}] State: {state:6} - {description}")

        # Show what would happen
        if state == "LIVE":
            print("  ➤ Update Finnish players every 30 seconds")
            print("  ➤ Fetch boxscore data")
            print("  ➤ Update JSON files with live stats")
            print("  ➤ Log changes")
        elif state == "OFF":
            print("  ➤ Stop monitoring this game")
            print("  ➤ Mark as final")

        time.sleep(0.5)

    print("\n✅ Simulation complete")


def main():
    """Run all demos"""
    print("\n" + "="*70)
    print("REAL-TIME NHL MONITOR - DEMONSTRATION")
    print("="*70)
    print("This demo showcases the real-time monitoring system components")
    print()

    demos = [
        ("State Manager", demo_state_manager),
        ("Data Updater", demo_data_updater),
        ("Finnish Player Cache", demo_finnish_cache),
        ("API Schedule Fetch", demo_api_schedule),
        ("API Boxscore Fetch", demo_api_boxscore),
        ("Live Monitoring Simulation", demo_live_monitoring_simulation),
    ]

    for name, func in demos:
        try:
            func()
        except KeyboardInterrupt:
            print("\n\n⚠️  Demo interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Error in {name}: {e}")

    print("\n" + "="*70)
    print("DEMONSTRATION COMPLETE")
    print("="*70)
    print("\nTo run the actual system:")
    print("  1. Install service: sudo ./manage.sh install")
    print("  2. Start service:   sudo ./manage.sh start")
    print("  3. Check status:    sudo ./manage.sh status")
    print("  4. View logs:       sudo ./manage.sh logs")
    print("\nOr run manually (foreground):")
    print("  ./manage.sh manual")
    print()


if __name__ == '__main__':
    main()
