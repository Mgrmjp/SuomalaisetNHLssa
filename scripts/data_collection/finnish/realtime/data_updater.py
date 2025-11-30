#!/usr/bin/env python3
"""
Data Updater for Real-Time NHL Monitoring

Merges real-time updates with existing JSON data files.
Preserves batch-collected data, adds real-time fields.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class DataUpdater:
    """Manages data updates for real-time Finnish player tracking"""

    DATA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "prepopulated" / "games"
    CACHE_DIR = Path(__file__).parent / "cache"

    def __init__(self):
        """Initialize the data updater"""
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)

    def update_game_data(self, game_date: str, game_id: int, live_data: dict) -> bool:
        """
        Update a specific game's data with live information

        Args:
            game_date: Date string (YYYY-MM-DD)
            game_id: NHL game ID
            live_data: Live game data from NHL API

        Returns:
            True if update was successful
        """
        data_file = self.DATA_DIR / f"{game_date}.json"

        # Load existing data
        if not data_file.exists():
            print(f"Warning: Data file {data_file} does not exist")
            return False

        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                game_data = json.load(f)
        except Exception as e:
            print(f"Error loading {data_file}: {e}")
            return False

        # Update game record in the games array
        game_found = False
        for game in game_data.get('games', []):
            if game.get('gameId') == game_id:
                game_found = True

                # Update score and state
                if 'homeScore' in live_data:
                    game['homeScore'] = live_data['homeScore']
                if 'awayScore' in live_data:
                    game['awayScore'] = live_data['awayScore']
                if 'gameState' in live_data:
                    game['gameState'] = live_data['gameState']
                if 'startTime' in live_data:
                    game['startTime'] = live_data['startTime']

                # Add real-time fields (V2 fields)
                game['realtime'] = {
                    'last_update': datetime.now().isoformat(),
                    'update_count': game.get('realtime', {}).get('update_count', 0) + 1,
                    'live_period': live_data.get('livePeriod', ''),
                    'live_time_remaining': live_data.get('liveTimeRemaining', ''),
                    'power_play': live_data.get('powerPlay', False),
                }
                break

        if not game_found:
            print(f"Warning: Game {game_id} not found in {data_file}")
            return False

        # Save updated data
        try:
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(game_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving {data_file}: {e}")
            return False

    def update_player_data(self, game_date: str, game_id: int, finnish_players: List[dict]) -> int:
        """
        Update Finnish player statistics in real-time

        Args:
            game_date: Date string (YYYY-MM-DD)
            game_id: NHL game ID
            finnish_players: List of Finnish player data from boxscore

        Returns:
            Number of players updated
        """
        data_file = self.DATA_DIR / f"{game_date}.json"

        if not data_file.exists():
            print(f"Warning: Data file {data_file} does not exist")
            return 0

        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                game_data = json.load(f)
        except Exception as e:
            print(f"Error loading {data_file}: {e}")
            return 0

        updated_count = 0

        # Index players by playerId for quick lookup
        player_updates = {p.get('playerId'): p for p in finnish_players}

        # Update each player in the players array
        for player in game_data.get('players', []):
            player_id = player.get('playerId')
            if player_id in player_updates:
                live_data = player_updates[player_id]

                # Update live stats
                player['live_goals'] = live_data.get('goals', 0)
                player['live_assists'] = live_data.get('assists', 0)
                player['live_points'] = live_data.get('points', 0)
                player['live_shots'] = live_data.get('shots', 0)
                player['live_plus_minus'] = live_data.get('plusMinus', 0)
                player['live_time_on_ice'] = live_data.get('timeOnIce', '')
                player['live_shifts'] = live_data.get('shifts', 0)
                player['live_penalty_minutes'] = live_data.get('penaltyMinutes', 0)
                player['live_hits'] = live_data.get('hits', 0)
                player['live_blocked_shots'] = live_data.get('blockedShots', 0)

                # Add real-time timestamp
                player['last_realtime_update'] = datetime.now().isoformat()

                # If goaltender, add goalie-specific stats
                if player.get('position') == 'G':
                    player['live_saves'] = live_data.get('saves', 0)
                    player['live_shots_against'] = live_data.get('shotsAgainst', 0)
                    player['live_save_percentage'] = live_data.get('savePercentage', 0.0)
                    player['live_goals_against'] = live_data.get('goalsAgainst', 0)

                updated_count += 1

        # Save updated data
        try:
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(game_data, f, indent=2)
            return updated_count
        except Exception as e:
            print(f"Error saving {data_file}: {e}")
            return 0

    def get_live_updates_summary(self, game_date: str, game_id: int) -> Optional[dict]:
        """
        Get a summary of live updates for a game

        Args:
            game_date: Date string (YYYY-MM-DD)
            game_id: NHL game ID

        Returns:
            Summary dictionary or None if game not found
        """
        data_file = self.DATA_DIR / f"{game_date}.json"

        if not data_file.exists():
            return None

        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                game_data = json.load(f)
        except Exception:
            return None

        # Find the game
        for game in game_data.get('games', []):
            if game.get('gameId') == game_id:
                summary = {
                    'game_id': game_id,
                    'game_state': game.get('gameState'),
                    'home_score': game.get('homeScore'),
                    'away_score': game.get('awayScore'),
                    'realtime': game.get('realtime', {}),
                    'finnish_players_updated': 0,
                    'last_player_update': None
                }

                # Count updated players
                for player in game_data.get('players', []):
                    if 'last_realtime_update' in player:
                        summary['finnish_players_updated'] += 1
                        if not summary['last_player_update'] or \
                           player['last_realtime_update'] > summary['last_player_update']:
                            summary['last_player_update'] = player['last_realtime_update']

                return summary

        return None

    def create_realtime_snapshot(self, game_date: str, game_id: int) -> Optional[dict]:
        """
        Create a snapshot of current live data

        Args:
            game_date: Date string (YYYY-MM-DD)
            game_id: NHL game ID

        Returns:
            Snapshot dictionary or None
        """
        data_file = self.DATA_DIR / f"{game_date}.json"

        if not data_file.exists():
            return None

        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                game_data = json.load(f)
        except Exception:
            return None

        # Find the game
        for game in game_data.get('games', []):
            if game.get('gameId') == game_id:
                snapshot = {
                    'game_date': game_date,
                    'game_id': game_id,
                    'snapshot_time': datetime.now().isoformat(),
                    'game': {
                        'home_team': game.get('homeTeam'),
                        'away_team': game.get('awayTeam'),
                        'home_score': game.get('homeScore'),
                        'away_score': game.get('awayScore'),
                        'game_state': game.get('gameState'),
                        'start_time': game.get('startTime'),
                        'realtime': game.get('realtime', {})
                    },
                    'finnish_players': []
                }

                # Add Finnish player snapshots
                for player in game_data.get('players', []):
                    player_snapshot = {
                        'player_id': player.get('playerId'),
                        'name': player.get('name'),
                        'team': player.get('team'),
                        'position': player.get('position'),
                        'goals': player.get('live_goals', player.get('goals', 0)),
                        'assists': player.get('live_assists', player.get('assists', 0)),
                        'points': player.get('live_points', player.get('points', 0)),
                        'shots': player.get('live_shots', player.get('shots', 0)),
                        'time_on_ice': player.get('live_time_on_ice', player.get('time_on_ice', '')),
                        'last_update': player.get('last_realtime_update')
                    }
                    snapshot['finnish_players'].append(player_snapshot)

                return snapshot

        return None

    def save_snapshot(self, snapshot: dict, filename: Optional[str] = None) -> bool:
        """
        Save a snapshot to disk

        Args:
            snapshot: Snapshot dictionary
            filename: Optional filename (auto-generated if None)

        Returns:
            True if saved successfully
        """
        if filename is None:
            # Auto-generate filename
            game_date = snapshot.get('game_date', 'unknown')
            game_id = snapshot.get('game_id', 'unknown')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{game_date}_game{game_id}_snapshot_{timestamp}.json"

        snapshot_dir = Path(__file__).parent / "snapshots"
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        snapshot_file = snapshot_dir / filename

        try:
            with open(snapshot_file, 'w', encoding='utf-8') as f:
                json.dump(snapshot, f, indent=2)
            print(f"📸 Snapshot saved: {snapshot_file}")
            return True
        except Exception as e:
            print(f"Error saving snapshot: {e}")
            return False
