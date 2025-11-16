#!/usr/bin/env python3
"""
Fetch Finnish NHL players and save tiny headshot thumbnails.

Requirements:
- Python 3.9+
- requests (standard in this repo)
- Pillow (optional; install with `pip install pillow` for resizing).

Output:
- Thumbs written to static/headshots/thumbs/{playerId}.jpg at 40px.

Usage:
    python3 scripts/data/fetch_finnish_headshot_thumbs.py
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import List, Optional

import requests

try:
    from PIL import Image

    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

NHL_API = "https://api-web.nhle.com"
HEADSHOT_CDN = "https://assets.nhle.com/mugs/nhl"
TEAM_ABBREVS: List[str] = [
    "ANA", "ARI", "BOS", "BUF", "CAR", "CBJ", "CGY", "CHI", "COL", "DAL", "DET", "EDM", "FLA", "LAK", "MIN",
    "MTL", "NJD", "NSH", "NYI", "NYR", "OTT", "PHI", "PIT", "SEA", "SJS", "STL", "TBL", "TOR", "VAN", "VGK", "WPG", "WSH"
]
THUMB_SIZE = 40
OUT_DIR = Path("static/headshots/thumbs")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def is_finnish(player: dict) -> bool:
    country = str(player.get("birthCountry", "")).upper()
    return country in {"FIN", "FINLAND"}


def headshot_url(team: str, player_id: int, season_slug: str = "current") -> str:
    # Try season-specific path first, then fall back to "current"
    return f"{HEADSHOT_CDN}/{season_slug}/{team}/{player_id}.png"


def fetch_json(url: str) -> dict:
    resp = requests.get(url, timeout=8)
    resp.raise_for_status()
    return resp.json()


def fetch_teams_rosters() -> List[dict]:
    finnish_players = []
    for team in TEAM_ABBREVS:
        try:
            roster = fetch_json(f"{NHL_API}/v1/roster/{team}/current")
        except Exception as exc:
            print(f"[WARN] roster failed for {team}: {exc}")
            continue

        players = (roster.get("forwards") or []) + (roster.get("defensemen") or []) + (roster.get("goalies") or [])
        for p in players:
            if is_finnish(p):
                finnish_players.append(
                    {
                        "team": team,
                        "id": p.get("id"),
                        "first": p.get("firstName", {}).get("default") or "",
                        "last": p.get("lastName", {}).get("default") or "",
                    }
                )
    return finnish_players


def get_headshot_for_player(player_id: int, team: str) -> Optional[bytes]:
    """
    Try to fetch a headshot buffer for a player by:
    1) Player landing data -> headshot field
    2) Season-specific mug URL (best guess uses current season year pair if available)
    3) Fallback "current" mug URL
    """
    # 1) Player landing
    try:
        landing = fetch_json(f"{NHL_API}/v1/player/{player_id}/landing")
        headshot = landing.get("headshot")
        if headshot:
            resp = requests.get(headshot, timeout=8)
            resp.raise_for_status()
            return resp.content
    except Exception:
        pass

    # 2) season-specific mug (derive season slug if available)
    season_slug = landing.get("season") if "landing" in locals() and isinstance(landing.get("season"), str) else "current"
    for slug in filter(None, [season_slug, "current"]):
        try:
            url = headshot_url(team, player_id, slug)
            resp = requests.get(url, timeout=8)
            resp.raise_for_status()
            return resp.content
        except Exception:
            continue

    return None


def save_thumb(team: str, player_id: int) -> bool:
    try:
        data = get_headshot_for_player(player_id, team)
        if data is None:
            raise RuntimeError("no headshot found")

        if PIL_AVAILABLE:
            img = Image.open(io.BytesIO(data))
            img = img.convert("RGB")
            img = img.resize((THUMB_SIZE, THUMB_SIZE), Image.LANCZOS)
            out_buf = io.BytesIO()
            img.save(out_buf, format="JPEG", quality=65)
            data = out_buf.getvalue()

        out_path = OUT_DIR / f"{player_id}.jpg"
        out_path.write_bytes(data)
        return True
    except Exception as exc:
        print(f"[WARN] thumb failed for {player_id} ({team}): {exc}")
        return False


def main() -> None:
    finnish_players = fetch_teams_rosters()
    print(f"Finnish players found: {len(finnish_players)}")

    ok = 0
    for player in finnish_players:
        if save_thumb(player["team"], int(player["id"])):
            ok += 1

    print(f"Thumbs saved: {ok} -> {OUT_DIR.resolve()}")
    if not PIL_AVAILABLE:
        print("Note: Pillow not installed, saved original PNGs. Install with `pip install pillow` for resized thumbs.")


if __name__ == "__main__":
    main()
