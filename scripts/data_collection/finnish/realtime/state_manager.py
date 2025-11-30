#!/usr/bin/env python3
"""
Game State Manager for Real-Time NHL Monitoring

Tracks active games and their states (FUT → LIVE → OFF)
Manages state transitions and scheduling for real-time updates.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Set, Optional, List


class GameStateManager:
    """Manages game states and transitions for real-time monitoring"""

    STATE_FILE = Path(__file__).parent / "state" / "active_games.json"
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Game state constants
    STATE_FUTURE = "FUT"      # Scheduled/Future
    STATE_LIVE = "LIVE"       # Currently playing
    STATE_OFF = "OFF"         # Final/Finished
    STATE_CRIT = "CRIT"       # Critical situation (overtime/shootout)

    def __init__(self):
        """Initialize the state manager"""
        self.active_games: Dict[int, dict] = {}
        self.load_state()

    def load_state(self) -> None:
        """Load existing game states from disk"""
        if self.STATE_FILE.exists():
            try:
                with open(self.STATE_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Convert keys back to integers
                    self.active_games = {
                        int(k): v for k, v in data.get('active_games', {}).items()
                    }
                    self._cleanup_old_states()
            except Exception as e:
                print(f"Warning: Could not load state file: {e}")
                self.active_games = {}

    def save_state(self) -> None:
        """Persist current game states to disk"""
        try:
            state_data = {
                'active_games': self.active_games,
                'last_update': datetime.now().isoformat()
            }
            with open(self.STATE_FILE, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=2)
        except Exception as e:
            print(f"Error saving state: {e}")

    def _cleanup_old_states(self) -> None:
        """Remove games that are too old (probably finished)"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        to_remove = []

        for game_id, game_data in self.active_games.items():
            try:
                last_update = datetime.fromisoformat(game_data.get('last_update', ''))
                if last_update < cutoff_time:
                    to_remove.append(game_id)
            except Exception:
                # If we can't parse the date, check if state is final
                if game_data.get('game_state') in [self.STATE_OFF]:
                    to_remove.append(game_id)

        for game_id in to_remove:
            del self.active_games[game_id]

    def update_games(self, schedule_data: List[dict]) -> Set[int]:
        """
        Update game states from NHL schedule data

        Args:
            schedule_data: List of game objects from NHL API schedule endpoint

        Returns:
            Set of game IDs that transitioned to LIVE state
        """
        transitioned_to_live = set()
        current_time = datetime.now()

        for game in schedule_data:
            game_id = game.get('id')
            if not game_id:
                continue

            game_state = game.get('gameState', self.STATE_FUTURE)
            start_time = game.get('startTimeUTC', '')

            # Get existing state if available
            existing = self.active_games.get(game_id, {})

            # Update game data
            game_data = {
                'game_id': game_id,
                'game_state': game_state,
                'start_time': start_time,
                'home_team': game.get('homeTeam', {}).get('abbrev', ''),
                'away_team': game.get('awayTeam', {}).get('abbrev', ''),
                'home_score': game.get('homeTeam', {}).get('score', 0),
                'away_score': game.get('awayTeam', {}).get('score', 0),
                'last_update': current_time.isoformat(),
                'update_count': existing.get('update_count', 0) + 1 if existing else 1,
            }

            # Check for state transition to LIVE
            previous_state = existing.get('game_state', self.STATE_FUTURE)
            if previous_state != self.STATE_LIVE and game_state in [self.STATE_LIVE, self.STATE_CRIT]:
                transitioned_to_live.add(game_id)
                print(f"🎮 Game {game_id} ({game_data['away_team']} @ {game_data['home_team']}) is now LIVE!")

            self.active_games[game_id] = game_data

        # Remove games that are no longer in schedule or are final
        self._cleanup_old_states()

        # Save state
        self.save_state()

        return transitioned_to_live

    def get_live_games(self) -> List[dict]:
        """
        Get list of currently live games

        Returns:
            List of game data for live games
        """
        live_games = []
        for game_data in self.active_games.values():
            if game_data.get('game_state') in [self.STATE_LIVE, self.STATE_CRIT]:
                live_games.append(game_data)
        return live_games

    def get_all_tracked_games(self) -> List[dict]:
        """
        Get list of all tracked games (including recent)

        Returns:
            List of all game data
        """
        return list(self.active_games.values())

    def mark_game_final(self, game_id: int) -> bool:
        """
        Mark a game as final

        Args:
            game_id: NHL game ID

        Returns:
            True if game was marked as final
        """
        if game_id in self.active_games:
            self.active_games[game_id]['game_state'] = self.STATE_OFF
            self.active_games[game_id]['last_update'] = datetime.now().isoformat()
            self.save_state()
            print(f"🏁 Game {game_id} marked as FINAL")
            return True
        return False

    def should_update_game(self, game_id: int, update_interval: int = 30) -> bool:
        """
        Check if a game should be updated based on interval

        Args:
            game_id: NHL game ID
            update_interval: Minimum seconds between updates

        Returns:
            True if game should be updated
        """
        if game_id not in self.active_games:
            return False

        game_data = self.active_games[game_id]
        last_update_str = game_data.get('last_update', '')

        try:
            last_update = datetime.fromisoformat(last_update_str)
            time_since_update = (datetime.now() - last_update).total_seconds()
            return time_since_update >= update_interval
        except Exception:
            return True

    def get_stats(self) -> dict:
        """
        Get statistics about tracked games

        Returns:
            Dictionary with statistics
        """
        live_count = len(self.get_live_games())
        total_tracked = len(self.active_games)

        state_counts = {}
        for game_data in self.active_games.values():
            state = game_data.get('game_state', 'UNKNOWN')
            state_counts[state] = state_counts.get(state, 0) + 1

        return {
            'live_games': live_count,
            'total_tracked': total_tracked,
            'state_breakdown': state_counts,
            'last_state_update': datetime.now().isoformat()
        }

    def __str__(self) -> str:
        """String representation of current state"""
        stats = self.get_stats()
        return (
            f"GameStateManager: {stats['live_games']} live, "
            f"{stats['total_tracked']} total tracked"
        )
