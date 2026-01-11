#!/usr/bin/env python3
"""
Fetch Finnish NHL player headshots and save as optimized WebP.

Requirements:
- Python 3.9+
- requests
- Pillow (pip install pillow)

Output:
- WebP images at 168x168 in static/headshots/{playerId}.webp

Usage:
    python3 scripts/data_collection/headshots/fetch_headshots_webp.py
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import List, Optional

import requests

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("ERROR: Pillow is required. Install with: pip install pillow")
    exit(1)

NHL_API = "https://api-web.nhle.com"
HEADSHOT_CDN = "https://assets.nhle.com/mugs/nhl"
TEAM_ABBREVS: List[str] = [
    "ANA", "BOS", "BUF", "CAR", "CBJ", "CGY", "CHI", "COL", "DAL", "DET",
    "EDM", "FLA", "LAK", "MIN", "MTL", "NJD", "NSH", "NYI", "NYR", "OTT",
    "PHI", "PIT", "SEA", "SJS", "STL", "TBL", "TOR", "UTA", "VAN", "VGK",
    "WPG", "WSH"
]
IMAGE_SIZE = 168  # Display size for player cards
WEBP_QUALITY = 80
OUT_DIR = Path("static/headshots")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def is_finnish(player: dict) -> bool:
    country = str(player.get("birthCountry", "")).upper()
    return country in {"FIN", "FINLAND"}


def fetch_json(url: str) -> dict:
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()


def fetch_finnish_players() -> List[dict]:
    """Fetch all Finnish players from current NHL rosters."""
    finnish_players = []
    for team in TEAM_ABBREVS:
        try:
            roster = fetch_json(f"{NHL_API}/v1/roster/{team}/current")
        except Exception as exc:
            print(f"[WARN] Roster fetch failed for {team}: {exc}")
            continue

        players = (
            roster.get("forwards", []) +
            roster.get("defensemen", []) +
            roster.get("goalies", [])
        )
        for p in players:
            if is_finnish(p):
                finnish_players.append({
                    "team": team,
                    "id": p.get("id"),
                    "first": p.get("firstName", {}).get("default", ""),
                    "last": p.get("lastName", {}).get("default", ""),
                })
    return finnish_players


def get_headshot_bytes(player_id: int, team: str) -> Optional[bytes]:
    """
    Try to fetch headshot bytes:
    1. Player landing page -> headshot field
    2. Season-specific CDN URL
    3. Fallback "current" CDN URL
    """
    # Try player landing first
    try:
        landing = fetch_json(f"{NHL_API}/v1/player/{player_id}/landing")
        headshot_url = landing.get("headshot")
        if headshot_url:
            resp = requests.get(headshot_url, timeout=10)
            resp.raise_for_status()
            return resp.content
    except Exception:
        pass

    # Try CDN URLs
    for season_slug in ["20252026", "current"]:
        try:
            url = f"{HEADSHOT_CDN}/{season_slug}/{team}/{player_id}.png"
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            return resp.content
        except Exception:
            continue

    return None


def save_webp(player_id: int, team: str) -> bool:
    """Download headshot and save as optimized WebP."""
    try:
        data = get_headshot_bytes(player_id, team)
        if data is None:
            raise RuntimeError("No headshot found")

        # Convert to WebP
        img = Image.open(io.BytesIO(data))
        img = img.convert("RGB")
        img = img.resize((IMAGE_SIZE, IMAGE_SIZE), Image.LANCZOS)
        
        out_path = OUT_DIR / f"{player_id}.webp"
        img.save(out_path, format="WEBP", quality=WEBP_QUALITY)
        
        size_kb = out_path.stat().st_size / 1024
        print(f"  ✓ {player_id}.webp ({size_kb:.1f} KB)")
        return True
    except Exception as exc:
        print(f"  ✗ {player_id} ({team}): {exc}")
        return False


def main() -> None:
    print("Fetching Finnish NHL players...")
    players = fetch_finnish_players()
    print(f"Found {len(players)} Finnish players\n")

    print("Downloading and converting headshots to WebP:")
    success = 0
    for p in players:
        if save_webp(int(p["id"]), p["team"]):
            success += 1

    print(f"\n✓ Saved {success}/{len(players)} headshots to {OUT_DIR.resolve()}")
    
    # Calculate total size
    total_bytes = sum(f.stat().st_size for f in OUT_DIR.glob("*.webp"))
    print(f"Total size: {total_bytes / 1024:.1f} KB")


if __name__ == "__main__":
    main()
