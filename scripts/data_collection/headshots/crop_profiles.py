"""Prospect headshot crop presets resolved during the data pipeline."""

from __future__ import annotations

from copy import deepcopy
from typing import Optional

DEFAULT_CROP = {
    "zoom": 1.12,
    "objectPosition": "50% 18%",
}

LEAGUE_CROP_PRESETS = {
    "mestis": {"zoom": 1.3, "objectPosition": "50% 8%"},
    "liiga": {"zoom": 1.14, "objectPosition": "50% 16%"},
    "shl": {"zoom": 1.12, "objectPosition": "50% 18%"},
    "ahl": {"zoom": 1.1, "objectPosition": "50% 18%"},
    "whl": {"zoom": 1.1, "objectPosition": "50% 18%"},
    "ohl": {"zoom": 1.1, "objectPosition": "50% 18%"},
    "qmjhl": {"zoom": 1.1, "objectPosition": "50% 18%"},
    "ncaa": {"zoom": 1.08, "objectPosition": "50% 18%"},
}

URL_CROP_PRESETS = (
    ("mestis.fi/media/players/", {"zoom": 1.32, "objectPosition": "50% 6%"}),
    ("teamplayer.2cd.io/", {"zoom": 1.18, "objectPosition": "50% 16%"}),
    ("assets.leaguestat.com/", {"zoom": 1.1, "objectPosition": "50% 18%"}),
    ("assets.nhle.com/mugs/", {"zoom": 1.08, "objectPosition": "50% 18%"}),
    ("www.shl.se/imageproxy/", {"zoom": 1.12, "objectPosition": "50% 18%"}),
    ("liiga-backend-prod.s3.eu-north-1.amazonaws.com/", {"zoom": 1.14, "objectPosition": "50% 16%"}),
)

PLAYER_CROP_OVERRIDES = {
    "8480875": {"zoom": 1.22, "objectPosition": "50% 12%"},
}


def _copy_crop(crop: dict) -> dict:
    return deepcopy(crop)


def _normalize_key(value: Optional[str]) -> str:
    return (value or "").strip().lower()


def resolve_headshot_crop(player: dict, source_url: Optional[str]) -> dict:
    """Resolve a deterministic crop preset for a downloaded prospect headshot."""
    player_id = str(player.get("player_id") or player.get("playerId") or "").strip()
    if player_id and player_id in PLAYER_CROP_OVERRIDES:
        return _copy_crop(PLAYER_CROP_OVERRIDES[player_id])

    normalized_url = (source_url or "").strip().lower()
    for token, preset in URL_CROP_PRESETS:
        if token in normalized_url:
            return _copy_crop(preset)

    source_league = _normalize_key(player.get("source_league") or player.get("league"))
    if source_league in LEAGUE_CROP_PRESETS:
        return _copy_crop(LEAGUE_CROP_PRESETS[source_league])

    return _copy_crop(DEFAULT_CROP)
