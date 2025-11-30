#!/usr/bin/env python3
"""
Real-Time NHL Game Monitor Daemon

Continuously monitors NHL games and updates Finnish player data every 30 seconds.
Integrates with existing batch collection system.

Usage: python realtime_monitor.py [--daemon] [--config config.json]
"""

import json
import logging
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from threading import Lock, Thread
from typing import Dict, List, Optional
import argparse

# Import our modules
from state_manager import GameStateManager
from data_updater import DataUpdater


class RealtimeMonitor:
    """Main real-time monitoring daemon"""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the monitor

        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        if config_path is None:
            config_path = Path(__file__).parent / "realtime_config.json"

        self.config = self._load_config(config_path)

        # Initialize components
        self.state_manager = GameStateManager()
        self.data_updater = DataUpdater()

        # Setup logging
        self._setup_logging()

        # Thread safety
        self.lock = Lock()

        # Control flags
        self.running = False
        self.threads: List[Thread] = []

        # Statistics
        self.stats = {
            'games_detected': 0,
            'games_updated': 0,
            'players_updated': 0,
            'errors': 0,
            'start_time': datetime.now().isoformat()
        }

    def _load_config(self, config_path: Path) -> dict:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config {config_path}: {e}")
            return self._default_config()

    def _default_config(self) -> dict:
        """Default configuration"""
        return {
            "monitoring": {
                "state_check_interval": 60,
                "live_game_update_interval": 30,
                "max_concurrent_updates": 5
            },
            "api": {
                "base_url": "https://api-web.nhle.com",
                "request_timeout": 10,
                "retry_attempts": 2
            },
            "logging": {
                "level": "INFO",
                "console_output": True
            }
        }

    def _setup_logging(self):
        """Setup logging configuration"""
        log_config = self.config.get('logging', {})
        level = getattr(logging, log_config.get('level', 'INFO'))
        console_output = log_config.get('console_output', True)

        # Create logs directory
        log_file_path = Path(__file__).parent / "logs" / "realtime_monitor.log"
        log_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Configure logging
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file_path),
                logging.StreamHandler(sys.stdout) if console_output else logging.NullHandler()
            ]
        )

        self.logger = logging.getLogger('RealtimeMonitor')
        self.logger.info("Logging initialized")

    def fetch_from_api(self, url: str) -> Optional[dict]:
        """
        Fetch data from NHL API with retry logic

        Args:
            url: API endpoint URL

        Returns:
            JSON data or None if error
        """
        import requests

        api_config = self.config.get('api', {})
        timeout = api_config.get('request_timeout', 10)
        max_retries = api_config.get('retry_attempts', 2)
        retry_delay = api_config.get('retry_delay', 2)

        for attempt in range(max_retries):
            try:
                response = requests.get(url, timeout=timeout)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                self.logger.warning(f"API request failed (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    self.logger.error(f"API request failed after {max_retries} attempts")
                    self.stats['errors'] += 1
                    return None

        return None

    def load_finnish_player_cache(self) -> Dict[int, dict]:
        """Load cached Finnish player information"""
        cache_path = Path(__file__).parent.parent / "cache" / "finnish-players.json"

        if not cache_path.exists():
            self.logger.warning("Finnish player cache not found")
            return {}

        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                str_cache = json.load(f)
                # Convert string keys to integers
                return {int(k): v for k, v in str_cache.items()}
        except Exception as e:
            self.logger.error(f"Error loading cache: {e}")
            return {}

    def get_today_schedule(self) -> List[dict]:
        """
        Get NHL schedule for today

        Returns:
            List of game objects
        """
        today = datetime.now().strftime('%Y-%m-%d')
        url = f"{self.config['api']['base_url']}/v1/schedule/{today}"

        self.logger.debug(f"Fetching schedule for {today}")
        data = self.fetch_from_api(url)

        if not data:
            return []

        games = []
        for date_info in data.get('gameWeek', []):
            games.extend(date_info.get('games', []))

        self.logger.info(f"Found {len(games)} games scheduled for {today}")
        return games

    def get_game_boxscore(self, game_id: int) -> Optional[dict]:
        """
        Get boxscore data for a specific game

        Args:
            game_id: NHL game ID

        Returns:
            Boxscore data or None if error
        """
        url = f"{self.config['api']['base_url']}/v1/gamecenter/{game_id}/boxscore"
        return self.fetch_from_api(url)

    def check_finnish_players_in_game(self, boxscore: dict, finnish_cache: Dict[int, dict]) -> List[dict]:
        """
        Check if Finnish players are in the game

        Args:
            boxscore: Game boxscore data
            finnish_cache: Cache of Finnish players

        Returns:
            List of Finnish player data
        """
        finnish_players = []

        if not boxscore:
            return finnish_players

        # Check both home and away teams
        for team_key in ['homeTeam', 'awayTeam']:
            team = boxscore.get(team_key, {})
            players = team.get('players', [])

            for player in players:
                player_id = player.get('playerId')
                if player_id and player_id in finnish_cache:
                    # Get player details from cache
                    player_info = finnish_cache[player_id].copy()
                    player_info.update({
                        'playerId': player_id,
                        'team': team.get('abbrev', ''),
                        'goals': player.get('goals', 0),
                        'assists': player.get('assists', 0),
                        'points': player.get('points', 0),
                        'shots': player.get('shots', 0),
                        'plusMinus': player.get('plusMinus', 0),
                        'timeOnIce': player.get('timeOnIce', ''),
                        'shifts': player.get('shifts', 0),
                        'penaltyMinutes': player.get('penaltyMinutes', 0),
                        'hits': player.get('hits', 0),
                        'blockedShots': player.get('blockedShots', 0),
                        'position': player.get('position', {}).get('abbrev', ''),
                    })

                    # Add goalie stats if applicable
                    if player_info['position'] == 'G':
                        player_info.update({
                            'saves': player.get('saves', 0),
                            'shotsAgainst': player.get('shotsAgainst', 0),
                            'savePercentage': player.get('savePercentage', 0.0),
                            'goalsAgainst': player.get('goalsAgainst', 0)
                        })

                    finnish_players.append(player_info)

        return finnish_players

    def update_live_game(self, game_data: dict) -> bool:
        """
        Update a live game with latest data

        Args:
            game_data: Game data from state manager

        Returns:
            True if update was successful
        """
        game_id = game_data['game_id']
        home_team = game_data['home_team']
        away_team = game_data['away_team']

        self.logger.debug(f"Updating game {game_id}: {away_team} @ {home_team}")

        # Get boxscore
        boxscore = self.get_game_boxscore(game_id)
        if not boxscore:
            self.logger.warning(f"Could not fetch boxscore for game {game_id}")
            return False

        # Load Finnish player cache
        finnish_cache = self.load_finnish_player_cache()

        # Check for Finnish players
        finnish_players = self.check_finnish_players_in_game(boxscore, finnish_cache)

        if not finnish_players:
            self.logger.debug(f"No Finnish players in game {game_id}")
            return True

        # Get game date
        game_date = datetime.fromisoformat(game_data['start_time']).strftime('%Y-%m-%d')

        # Update game data (score, state, etc.)
        game_live_data = {
            'gameState': boxscore.get('gameState', 'LIVE'),
            'homeScore': boxscore.get('homeTeam', {}).get('score', 0),
            'awayScore': boxscore.get('awayTeam', {}).get('score', 0),
            'startTime': game_data['start_time'],
            'livePeriod': boxscore.get('period', {}).get('ordinalNum', ''),
            'liveTimeRemaining': boxscore.get('period', {}).get('remainingTime', ''),
            'powerPlay': boxscore.get('powerPlay', False)
        }

        if not self.data_updater.update_game_data(game_date, game_id, game_live_data):
            self.logger.error(f"Failed to update game data for {game_id}")
            return False

        # Update Finnish player data
        updated_count = self.data_updater.update_player_data(game_date, game_id, finnish_players)

        if updated_count > 0:
            self.logger.info(f"✅ Updated {updated_count} Finnish players in game {game_id}")
            self.stats['players_updated'] += updated_count
            return True
        else:
            return False

    def state_check_loop(self):
        """Main loop for checking game states"""
        interval = self.config['monitoring']['state_check_interval']

        while self.running:
            try:
                # Get today's schedule
                games = self.get_today_schedule()

                # Update state manager
                with self.lock:
                    transitioned = self.state_manager.update_games(games)
                    self.stats['games_detected'] += len(games)

                    # Start updates for newly live games
                    for game_id in transitioned:
                        self.stats['games_updated'] += 1
                        game_data = self.state_manager.active_games.get(game_id)
                        if game_data:
                            self.update_live_game(game_data)

                # Log statistics periodically
                if int(time.time()) % 300 == 0:  # Every 5 minutes
                    self.log_stats()

            except Exception as e:
                self.logger.error(f"Error in state check loop: {e}", exc_info=True)
                self.stats['errors'] += 1

            time.sleep(interval)

    def live_update_loop(self):
        """Loop for updating live games"""
        interval = self.config['monitoring']['live_game_update_interval']

        while self.running:
            try:
                with self.lock:
                    live_games = self.state_manager.get_live_games()

                if live_games:
                    self.logger.debug(f"Updating {len(live_games)} live games")

                    for game_data in live_games:
                        # Check if game needs update
                        if self.state_manager.should_update_game(game_data['game_id'], interval):
                            with self.lock:
                                self.update_live_game(game_data)
                                self.stats['games_updated'] += 1

            except Exception as e:
                self.logger.error(f"Error in live update loop: {e}", exc_info=True)
                self.stats['errors'] += 1

            time.sleep(interval)

    def log_stats(self):
        """Log current statistics"""
        state_stats = self.state_manager.get_stats()
        self.logger.info(
            f"Stats: {state_stats['live_games']} live games, "
            f"{self.stats['games_updated']} games updated, "
            f"{self.stats['players_updated']} players updated, "
            f"{self.stats['errors']} errors"
        )

    def start(self):
        """Start the monitoring daemon"""
        self.running = True

        # Create threads
        self.threads = [
            Thread(target=self.state_check_loop, name="StateCheck"),
            Thread(target=self.live_update_loop, name="LiveUpdate")
        ]

        # Start threads
        for thread in self.threads:
            thread.start()
            self.logger.info(f"Started thread: {thread.name}")

        self.logger.info("🚀 Real-time monitor started")

    def stop(self):
        """Stop the monitoring daemon"""
        self.logger.info("Stopping real-time monitor...")
        self.running = False

        # Wait for threads to finish
        for thread in self.threads:
            thread.join(timeout=5)
            self.logger.info(f"Stopped thread: {thread.name}")

        self.logger.info("✅ Real-time monitor stopped")

    def run(self):
        """Run the daemon (blocking)"""
        try:
            self.start()
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal")
        finally:
            self.stop()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Real-time NHL Finnish player monitor')
    parser.add_argument('--config', type=Path, help='Path to configuration file')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    args = parser.parse_args()

    monitor = RealtimeMonitor(args.config)

    if args.daemon:
        # Run in background (daemon mode)
        import signal
        signal.signal(signal.SIGTERM, lambda s, f: monitor.stop())
        signal.signal(signal.SIGINT, lambda s, f: monitor.stop())
        monitor.run()
    else:
        # Run in foreground
        print("Starting Real-Time NHL Monitor (Press Ctrl+C to stop)")
        monitor.run()


if __name__ == '__main__':
    main()
