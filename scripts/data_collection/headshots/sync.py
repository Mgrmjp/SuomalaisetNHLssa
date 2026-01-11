#!/usr/bin/env python3
"""
Headshot sync utilities for Finnish NHL players.

Downloads WebP headshots for players who don't have a local copy.
Called automatically by fetch.py after fetching game data.
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import List, Set, Optional

import requests

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

NHL_API = "https://api-web.nhle.com"
HEADSHOT_CDN = "https://assets.nhle.com/mugs/nhl"
IMAGE_SIZE = 168
WEBP_QUALITY = 80

# Get project root (4 levels up from this file)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
HEADSHOTS_DIR = PROJECT_ROOT / "static" / "headshots"


def get_existing_headshots() -> Set[int]:
    """Get set of player IDs that already have WebP headshots."""
    if not HEADSHOTS_DIR.exists():
        return set()
    return {
        int(f.stem) for f in HEADSHOTS_DIR.glob("*.webp")
        if f.stem.isdigit()
    }


def get_headshot_bytes(player_id: int, team: str, headshot_url: Optional[str] = None) -> Optional[bytes]:
    """
    Fetch headshot bytes for a player.
    
    Args:
        player_id: Player ID
        team: Team abbreviation
        headshot_url: Pre-computed headshot URL (from data)
    
    Returns:
        Image bytes or None
    """
    # Try pre-computed URL first (fastest)
    if headshot_url:
        try:
            resp = requests.get(headshot_url, timeout=10)
            resp.raise_for_status()
            return resp.content
        except Exception:
            pass
    
    # Try player landing page
    try:
        resp = requests.get(f"{NHL_API}/v1/player/{player_id}/landing", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        url = data.get("headshot")
        if url:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            return resp.content
    except Exception:
        pass
    
    # Try CDN URLs
    for season in ["20252026", "current"]:
        try:
            url = f"{HEADSHOT_CDN}/{season}/{team}/{player_id}.png"
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            return resp.content
        except Exception:
            continue
    
    return None


def download_headshot(player_id: int, team: str, headshot_url: Optional[str] = None) -> bool:
    """
    Download and save a player headshot as WebP.
    
    Args:
        player_id: Player ID
        team: Team abbreviation  
        headshot_url: Pre-computed headshot URL
    
    Returns:
        True if successful
    """
    if not PIL_AVAILABLE:
        return False
    
    try:
        data = get_headshot_bytes(player_id, team, headshot_url)
        if data is None:
            return False
        
        img = Image.open(io.BytesIO(data))
        img = img.convert("RGB")
        img = img.resize((IMAGE_SIZE, IMAGE_SIZE), Image.LANCZOS)
        
        HEADSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        out_path = HEADSHOTS_DIR / f"{player_id}.webp"
        img.save(out_path, format="WEBP", quality=WEBP_QUALITY)
        
        return True
    except Exception as e:
        print(f"[WARN] Failed to download headshot for {player_id}: {e}")
        return False


def sync_headshots(players: List[dict], quiet: bool = False) -> int:
    """
    Sync headshots for a list of players.
    Downloads WebP for any player without a local copy.
    
    Args:
        players: List of player dicts with playerId, team, headshot_url
        quiet: If True, suppress output
    
    Returns:
        Number of new headshots downloaded
    """
    if not PIL_AVAILABLE:
        if not quiet:
            print("[WARN] Pillow not available, skipping headshot sync")
        return 0
    
    existing = get_existing_headshots()
    downloaded = 0
    
    for player in players:
        player_id = player.get("playerId")
        if not player_id or player_id in existing:
            continue
        
        team = player.get("team", "")
        headshot_url = player.get("headshot_url")
        
        if download_headshot(player_id, team, headshot_url):
            downloaded += 1
            if not quiet:
                print(f"         📷 Downloaded headshot for {player.get('name', player_id)}")
            existing.add(player_id)  # Avoid duplicate attempts
    
    return downloaded
