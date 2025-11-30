#!/usr/bin/env python3
"""
Integration Test for Real-Time NHL Monitor

Tests API connectivity, game state detection, and data updates.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from state_manager import GameStateManager
from data_updater import DataUpdater


def test_api_connectivity():
    """Test NHL API connectivity"""
    print("\n" + "="*60)
    print("TEST 1: NHL API Connectivity")
    print("="*60)

    import requests

    today = datetime.now().strftime('%Y-%m-%d')
    url = f"https://api-web.nhle.com/v1/schedule/{today}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        game_count = sum(len(dg.get('games', [])) for dg in data.get('gameWeek', []))
        print(f"✅ API accessible")
        print(f"   URL: {url}")
        print(f"   Status: {response.status_code}")
        print(f"   Games today: {game_count}")

        return True
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False


def test_game_state_manager():
    """Test game state manager"""
    print("\n" + "="*60)
    print("TEST 2: Game State Manager")
    print("="*60)

    try:
        mgr = GameStateManager()
        print(f"✅ State manager initialized")
        print(f"   {mgr}")

        # Test state persistence
        stats = mgr.get_stats()
        print(f"   Stats: {stats}")

        return True
    except Exception as e:
        print(f"❌ State manager test failed: {e}")
        return False


def test_data_updater():
    """Test data updater"""
    print("\n" + "="*60)
    print("TEST 3: Data Updater")
    print("="*60)

    try:
        updater = DataUpdater()
        print(f"✅ Data updater initialized")
        print(f"   Data directory: {updater.DATA_DIR}")
        print(f"   Directory exists: {updater.DATA_DIR.exists()}")

        return True
    except Exception as e:
        print(f"❌ Data updater test failed: {e}")
        return False


def test_finnish_player_cache():
    """Test Finnish player cache"""
    print("\n" + "="*60)
    print("TEST 4: Finnish Player Cache")
    print("="*60)

    cache_path = Path(__file__).parent / "cache" / "finnish-players.json"

    if not cache_path.exists():
        print(f"⚠️  Cache not found at {cache_path}")
        print("   This is OK if cache hasn't been built yet")
        return True

    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache = json.load(f)
            cache_int = {int(k): v for k, v in cache.items()}

        print(f"✅ Cache loaded successfully")
        print(f"   Path: {cache_path}")
        print(f"   Players in cache: {len(cache_int)}")
        print(f"   Cache size: {cache_path.stat().st_size} bytes")

        # Show sample players
        sample_ids = list(cache_int.keys())[:3]
        print(f"   Sample players:")
        for pid in sample_ids:
            name = cache_int[pid].get('name', 'Unknown')
            print(f"     - {pid}: {name}")

        return True
    except Exception as e:
        print(f"❌ Cache test failed: {e}")
        return False


def test_data_file_integration():
    """Test integration with existing data files"""
    print("\n" + "="*60)
    print("TEST 5: Data File Integration")
    print("="*60)

    data_dir = Path(__file__).parent.parent.parent.parent / "data" / "prepopulated" / "games"

    if not data_dir.exists():
        print(f"❌ Data directory not found: {data_dir}")
        return False

    # Find recent data files
    data_files = sorted(data_dir.glob("2025-11-*.json"))
    if not data_files:
        print(f"⚠️  No November data files found")
        return True

    test_file = data_files[0]
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        games_count = len(data.get('games', []))
        players_count = len(data.get('players', []))

        print(f"✅ Data file integration OK")
        print(f"   Test file: {test_file.name}")
        print(f"   Games: {games_count}")
        print(f"   Players: {players_count}")

        return True
    except Exception as e:
        print(f"❌ Data integration test failed: {e}")
        return False


def test_nhl_api_endpoints():
    """Test specific NHL API endpoints"""
    print("\n" + "="*60)
    print("TEST 6: NHL API Endpoints")
    print("="*60)

    import requests

    try:
        # Test schedule endpoint
        today = datetime.now().strftime('%Y-%m-%d')
        schedule_url = f"https://api-web.nhle.com/v1/schedule/{today}"

        response = requests.get(schedule_url, timeout=10)
        schedule_data = response.json()

        # Find a game if available
        game = None
        for date_info in schedule_data.get('gameWeek', []):
            if date_info.get('games'):
                game = date_info['games'][0]
                break

        if not game:
            print(f"✅ Schedule endpoint OK (no games today)")
            return True

        game_id = game['id']
        print(f"✅ Schedule endpoint OK")
        print(f"   Found game: {game_id}")
        print(f"   Teams: {game['awayTeam']['abbrev']} @ {game['homeTeam']['abbrev']}")

        # Test boxscore endpoint if we found a game
        boxscore_url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/boxscore"
        response = requests.get(boxscore_url, timeout=10)
        boxscore_data = response.json()

        home_players = len(boxscore_data.get('homeTeam', {}).get('players', []))
        away_players = len(boxscore_data.get('awayTeam', {}).get('players', []))

        print(f"✅ Boxscore endpoint OK")
        print(f"   Game: {game_id}")
        print(f"   Home players: {home_players}")
        print(f"   Away players: {away_players}")

        return True

    except Exception as e:
        print(f"❌ Endpoint test failed: {e}")
        return False


def test_dependencies():
    """Test required dependencies"""
    print("\n" + "="*60)
    print("TEST 7: Dependencies")
    print("="*60)

    dependencies = [
        ('requests', 'HTTP library'),
        ('json', 'JSON handling'),
        ('pathlib', 'Path handling'),
        ('datetime', 'Date/time utilities'),
        ('threading', 'Threading support')
    ]

    all_ok = True
    for dep_name, description in dependencies:
        try:
            __import__(dep_name)
            print(f"✅ {dep_name}: {description}")
        except ImportError:
            print(f"❌ {dep_name}: {description} - NOT FOUND")
            all_ok = False

    return all_ok


def run_all_tests():
    """Run all integration tests"""
    print("\n" + "="*60)
    print("REAL-TIME NHL MONITOR - INTEGRATION TESTS")
    print("="*60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    tests = [
        ("API Connectivity", test_api_connectivity),
        ("Game State Manager", test_game_state_manager),
        ("Data Updater", test_data_updater),
        ("Finnish Player Cache", test_finnish_player_cache),
        ("Data File Integration", test_data_file_integration),
        ("NHL API Endpoints", test_nhl_api_endpoints),
        ("Dependencies", test_dependencies),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! System is ready for deployment.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
