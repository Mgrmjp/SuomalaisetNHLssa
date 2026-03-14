"""Base adapter class for league data collection."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any
from .utils.nationality_validator import validator
import requests
import time
import json

HEADSHOT_CANDIDATE_KEYS = (
    'headshot_url', 'headshotUrl', 'headshot',
    'photo_url', 'photoUrl', 'photo',
    'image_url', 'imageUrl', 'image',
    'avatar_url', 'avatarUrl', 'avatar',
    'portrait_url', 'portraitUrl', 'portrait',
)

PROFILE_CANDIDATE_KEYS = (
    'profile_url', 'profileUrl',
    'player_url', 'playerUrl',
    'url', 'link',
)


def _first_non_empty_string(value):
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return None


def _extract_nested_string(data, keys):
    if not isinstance(data, dict):
        return None

    for key in keys:
        value = _first_non_empty_string(data.get(key))
        if value:
            return value

    for nested_key in ('player', 'person', 'athlete', 'media', 'image'):
        nested = data.get(nested_key)
        if isinstance(nested, dict):
            nested_value = _extract_nested_string(nested, keys)
            if nested_value:
                return nested_value

    return None


@dataclass
class PlayerStats:
    """Unified player statistics format."""
    player_id: str
    name: str
    team: str
    league: str
    position: str
    games_played: int = 0
    goals: int = 0
    assists: int = 0
    points: int = 0
    plus_minus: int = 0
    penalty_minutes: int = 0
    
    # Goalie stats
    save_percentage: Optional[float] = None
    goals_against_average: Optional[float] = None
    shutouts: Optional[int] = None
    wins: Optional[int] = None
    
    # Additional info
    birth_date: Optional[str] = None
    height_cm: Optional[int] = None
    weight_kg: Optional[int] = None
    nationality: Optional[str] = None
    headshot_url: Optional[str] = None
    profile_url: Optional[str] = None
    
    # Source tracking
    source_league: Optional[str] = None
    raw_data: Optional[Dict] = None
    last_updated: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        headshot_url = self.headshot_url or _extract_nested_string(self.raw_data, HEADSHOT_CANDIDATE_KEYS)
        profile_url = self.profile_url or _extract_nested_string(self.raw_data, PROFILE_CANDIDATE_KEYS)

        return {
            'player_id': self.player_id,
            'name': self.name,
            'team': self.team,
            'league': self.league,
            'position': self.position,
            'games_played': self.games_played,
            'goals': self.goals,
            'assists': self.assists,
            'points': self.points,
            'plus_minus': self.plus_minus,
            'penalty_minutes': self.penalty_minutes,
            'save_percentage': self.save_percentage,
            'goals_against_average': self.goals_against_average,
            'shutouts': self.shutouts,
            'wins': self.wins,
            'birth_date': self.birth_date,
            'height_cm': self.height_cm,
            'weight_kg': self.weight_kg,
            'nationality': self.nationality,
            'headshot_url': headshot_url,
            'profile_url': profile_url,
            'source_league': self.source_league,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
        }


class BaseLeagueAdapter(ABC):
    """Base class for league data adapters."""
    
    def __init__(self, rate_limit_delay: float = 0.5):
        self.rate_limit_delay = rate_limit_delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; suomalaisetnhlssa-data/1.0)'
        })
        self._last_request_time = 0
    
    def _make_request(self, url: str, params: Optional[Dict] = None, response_format: str = 'json') -> Any:
        """Make rate-limited request."""
        # Rate limiting
        elapsed = time.time() - self._last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            self._last_request_time = time.time()
            
            if response.status_code == 200:
                if response_format == 'text':
                    return response.text
                return response.json()
            else:
                print(f"Error {response.status_code} for {url}")
                return None
        except Exception as e:
            print(f"Request error: {e}")
            return None
    
    def is_finnish_name(self, name: str) -> bool:
        """Public access to name detection."""
        return self._is_likely_finnish_name(name)
    
    @property
    @abstractmethod
    def league_name(self) -> str:
        """Return league name."""
        pass
    
    @property
    @abstractmethod
    def base_url(self) -> str:
        """Return base API URL."""
        pass
    
    @abstractmethod
    def get_all_players(self, season: Optional[str] = None) -> List[PlayerStats]:
        """Fetch all players from the league."""
        pass
    
    @abstractmethod
    def get_player_stats(self, player_id: str, season: Optional[str] = None) -> Optional[PlayerStats]:
        """Fetch individual player stats."""
        pass
    
    @abstractmethod
    def search_players(self, name: str) -> List[PlayerStats]:
        """Search players by name."""
        pass
    
    def filter_finnish_players(self, players: List[PlayerStats]) -> List[PlayerStats]:
        """Filter for Finnish players."""
        finnish_indicators = ['FIN', 'Finland', 'Suomi']
        filtered = []
        for p in players:
            # Check validator first for any explicit REJECTION (overrides everything)
            if not validator.verify(p.name, self.league_name, p.team):
                continue
                
            # If we were rejected, we already continued. 
            # Now check if it's a confirmed Finn or matches heuristic.
            
            # If specifically marked as Finnish in official source, trust it 
            # (unless it was rejected above, which it wasn't)
            if p.nationality in finnish_indicators:
                filtered.append(p)
                continue
                
            # If it's a likely name, we already called validator.verify above 
            # and it returned True (either confirmed, pending, or new).
            if p.name and self._is_likely_finnish_name(p.name):
                filtered.append(p)
                    
        return filtered
    
    def _is_likely_finnish_name(self, name: str) -> bool:
        """Heuristic to detect Finnish names."""
        name_lower = name.lower()
        
        # Very specific Finnish characters
        # 'ä' is very strong for Finland, while 'ö' and 'å' are common in Sweden/Germany/etc.
        if 'ä' in name_lower:
            return True
            
        # Common Finnish surname endings (more precise with regex suggested but let's stick to string ends)
        finnish_endings = (
            'nen', 'lainen', 'tiainen', 'pää', 'järvi', 'mäki', 
            'virta', 'niemi', 'lahti', 'puro', 'ranta', 'koski',
            'salmi', 'vaara', 'harju', 'kari', 'pohja'
        )
        
        # Check if the name ends with any of these accurately
        parts = name_lower.split()
        if not parts:
            return False
        
        surname = parts[-1]
        if surname.endswith(finnish_endings):
            # Exclude some Swedish common names that might clash if we added 'la' etc.
            # But these are quite Finnish-specific.
            return True
            
        # Specific Finnish first names
        finnish_first_names = ('antti', 'matti', 'juha', 'pekka', 'jari', 'mikko', 'teemu', 'vili', 'atte', 'eemeli', 'valteri', 'severi', 'konsta')
        if parts[0] in finnish_first_names:
            return True
            
        return False
