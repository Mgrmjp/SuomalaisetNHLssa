import json
from pathlib import Path
from typing import Dict, Any
import unicodedata
from datetime import datetime

class NationalityValidator:
    """
    Tracks heuristic candidates and manual nationality decisions in a local cache.
    """
    
    def __init__(self, cache_path: str = "scripts/static/data/checks/nationality_cache.json"):
        self.cache_path = Path(cache_path)
        self.cache: Dict[str, Dict[str, Any]] = self._load_cache()

    def _load_cache(self) -> Dict[str, Dict[str, Any]]:
        """Load the nationality cache from disk."""
        if self.cache_path.exists():
            try:
                with open(self.cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading cache: {e}")
        return {}

    def _save_cache(self):
        """Save the nationality cache to disk."""
        try:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_path, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving cache: {e}")

    def _normalize_name(self, name: str) -> str:
        """Normalize name by removing accents, making lowercase and using underscores."""
        nfkd_form = unicodedata.normalize('NFKD', name)
        clean_name = "".join([c for c in nfkd_form if not unicodedata.combining(c)]).lower().strip()
        return clean_name.replace(" ", "_")

    def verify(self, player_name: str, league: str = "", team: str = "") -> bool:
        """
        Return whether a player is a Finnish candidate under the stored decisions.

        Pending candidates remain eligible until manually confirmed or rejected.
        """
        norm_name = self._normalize_name(player_name)
        cache_key = f"{norm_name}_{league.lower()}"
        
        # Also check a generic league key for globally confirmed/rejected players
        global_key = f"{norm_name}_global"
        
        # Check cache for any status
        # Priority: Specific League Status > Global Status
        # However, a 'rejected' status at either level should be respected.
        
        specific = self.cache.get(cache_key, {})
        glob = self.cache.get(global_key, {})
        
        # 1. Any rejection (either league-specific or global) means not Finnish
        if specific.get('status') == 'rejected' or glob.get('status') == 'rejected':
            return False
            
        # 2. Any confirmation (either league-specific or global) means Finnish
        if specific.get('status') == 'confirmed' or glob.get('status') == 'confirmed':
            return True
            
        # 3. If either is already pending, we consider it "likely" for now
        if specific.get('status') == 'pending' or glob.get('status') == 'pending':
            return True

        # If not in cache or unknown, we need to mark as pending for automated/manual check
        print(f"  [Validator] New player detected via heuristic: {player_name} ({league}). Marked for verification.")
        
        # Initial status is 'pending' unless it's a known false positive
        is_known_false = self._is_known_false_positive(player_name)
        
        self.cache[cache_key] = {
            'player_name': player_name,
            'league': league,
            'team': team,
            'status': 'rejected' if is_known_false else 'pending',
            'verified_at': datetime.now().isoformat() if is_known_false else None,
            'method': 'heuristic_discovery'
        }
        self._save_cache()
        
        return not is_known_false

    def _is_known_false_positive(self, player_name: str) -> bool:
        """Heuristic check for common non-Finnish false positives."""
        false_positives = [
            'Matej Stransky', 'Erik Brännström', 'Enzo Corvi', 
            'Nicolai Meyer', 'Nicholas Bailen', 'Nicholas Eric Petersen',
            'Leonhard Pföderl', 'Max Görtz', 'Nicholas B. Jensen', 'Tyler Boland',
            'Aaron Irving', 'Nicholas Jensen', 'Matej Stranský'
        ]
        return any(fp.lower() in player_name.lower() for fp in false_positives)

validator = NationalityValidator()
