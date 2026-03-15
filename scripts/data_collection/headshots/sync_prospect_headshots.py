#!/usr/bin/env python3
"""
Download prospect headshots to local static files and rewrite data to local paths.

This keeps the frontend from hotlinking third-party league/CDN images on every page load.
"""

from __future__ import annotations

import json
import mimetypes
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

import requests
from crop_profiles import resolve_headshot_crop

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DATA_FILES = (
    PROJECT_ROOT / "static" / "data" / "leagues" / "league_prospects_official.json",
    PROJECT_ROOT / "static" / "data" / "leagues" / "league_prospects_advanced.json",
    PROJECT_ROOT / "static" / "data" / "leagues" / "league_prospects_na.json",
)
OUT_DIR = PROJECT_ROOT / "static" / "prospect-headshots"

USER_AGENT = "suomalaisetnhlssa-headshot-sync/1.0"
TIMEOUT = 20
SHL_SSGT_UUID = "iuzqg7dqk9"
HEADSHOT_SIZE = "320x320>"
WEBP_QUALITY = "82"
OPTIMIZED_EXTENSION = ".webp"

EXTENSION_BY_CONTENT_TYPE = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
    "image/avif": ".avif",
}

MAGIC_HEADERS = {
    b"\x89PNG\r\n\x1a\n": ".png",
    b"\xff\xd8\xff": ".jpg",
    b"RIFF": ".webp",
    b"GIF87a": ".gif",
    b"GIF89a": ".gif",
}


def _safe_stem(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return normalized or "player"


def _build_filename(player: dict, headshot_url: str, content_type: str = "") -> str:
    player_id = str(player.get("player_id") or "").strip()
    source_league = str(player.get("source_league") or player.get("league") or "unknown").strip().lower()
    stem = _safe_stem(player_id or f"{source_league}-{player.get('name', 'player')}")

    if content_type.startswith("."):
        ext = content_type
    else:
        ext = EXTENSION_BY_CONTENT_TYPE.get((content_type or "").split(";")[0].strip().lower())
    if not ext:
        ext = Path(headshot_url.split("?", 1)[0]).suffix.lower()
    if not ext:
        ext = mimetypes.guess_extension((content_type or "").split(";", 1)[0].strip().lower()) or ".jpg"

    return f"{stem}{ext}"


def _is_remote_headshot(url: Optional[str]) -> bool:
    return isinstance(url, str) and url.startswith(("http://", "https://"))


def _detect_extension_from_bytes(data: bytes) -> Optional[str]:
    for header, extension in MAGIC_HEADERS.items():
        if data.startswith(header):
            if header == b"RIFF" and b"WEBP" not in data[:16]:
                continue
            return extension
    return None


def _build_optimized_filename(player: dict) -> str:
    player_id = str(player.get("player_id") or "").strip()
    source_league = str(player.get("source_league") or player.get("league") or "unknown").strip().lower()
    stem = _safe_stem(player_id or f"{source_league}-{player.get('name', 'player')}")
    return f"{stem}{OPTIMIZED_EXTENSION}"


def _optimize_image_bytes(raw_bytes: bytes, source_extension: str) -> Optional[bytes]:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        input_path = tmp_path / f"input{source_extension or '.img'}"
        output_path = tmp_path / f"output{OPTIMIZED_EXTENSION}"
        input_path.write_bytes(raw_bytes)

        command = [
            "/bin/convert",
            str(input_path),
            "-auto-orient",
            "-strip",
            "-thumbnail",
            HEADSHOT_SIZE,
            "-quality",
            WEBP_QUALITY,
            str(output_path),
        ]

        try:
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            return None

        if not output_path.exists():
            return None

        return output_path.read_bytes()


def _write_optimized_local_headshot(player: dict, raw_bytes: bytes, source_extension: str) -> Optional[str]:
    optimized_bytes = _optimize_image_bytes(raw_bytes, source_extension)
    if not optimized_bytes:
        return None

    filename = _build_optimized_filename(player)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUT_DIR / filename
    output_path.write_bytes(optimized_bytes)
    return f"/prospect-headshots/{filename}"


def _download_to_local(session: requests.Session, player: dict, url: str) -> Optional[str]:
    try:
        response = session.get(url, timeout=TIMEOUT)
        response.raise_for_status()
    except Exception as exc:
        print(f"[WARN] Failed to download {player.get('name', 'player')} from {url}: {exc}")
        return None

    content_type = response.headers.get("content-type", "")
    detected_extension = _detect_extension_from_bytes(response.content)
    is_image = content_type.lower().startswith("image/") or detected_extension is not None

    if not is_image:
        print(f"[WARN] Non-image response for {player.get('name', 'player')}: {url} ({content_type or 'unknown'})")
        return None

    source_extension = _build_filename(player, url, content_type or detected_extension or "")
    source_extension = Path(source_extension).suffix.lower()

    optimized_path = _write_optimized_local_headshot(player, response.content, source_extension)
    if optimized_path:
        return optimized_path

    filename = _build_filename(player, url, content_type or detected_extension or "")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUT_DIR / filename
    output_path.write_bytes(response.content)
    return f"/prospect-headshots/{filename}"


def _resolve_shl_headshot_url(session: requests.Session, player: dict, url: str) -> Optional[str]:
    if "www.shl.se/imageproxy/" not in url:
        return url

    player_id = str(player.get("player_id") or "")
    if not player_id.startswith("shl_"):
        return None

    player_uuid = player_id.removeprefix("shl_")
    if not player_uuid:
        return None

    profile_api_url = "https://www.shl.se/api/statistics-v2/athlete/profile-page"
    headers = {
        "Accept": "application/json",
        "x-s8y-instance-id": "shl1_shl",
        "Referer": f"https://www.shl.se/athlete-profile/{player_uuid}",
    }
    params = {
        "playerUuid": player_uuid,
        "provider": "statnet",
        "ssgtUuid": SHL_SSGT_UUID,
    }

    try:
        response = session.get(profile_api_url, params=params, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
    except Exception as exc:
        print(f"[WARN] Failed to resolve SHL headshot for {player.get('name', 'player')}: {exc}")
        return None

    media = data.get("media") if isinstance(data, dict) else None
    media_url = media.get("url") if isinstance(media, dict) else None
    if isinstance(media_url, str) and media_url.startswith(("http://", "https://")):
        return media_url

    print(f"[WARN] SHL profile API returned no media.url for {player.get('name', 'player')}")
    return None


def _get_players_container(data: object) -> Optional[list[dict]]:
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        players = data.get("players")
        if isinstance(players, list):
            return players
    return None


def _optimize_existing_local_headshot(player: dict, local_url: str) -> Optional[str]:
    if not isinstance(local_url, str) or not local_url.startswith("/prospect-headshots/"):
        return None

    filename = local_url.removeprefix("/prospect-headshots/")
    local_path = OUT_DIR / filename
    if not local_path.exists():
        return None

    source_extension = local_path.suffix.lower() or ".img"
    optimized_url = _write_optimized_local_headshot(player, local_path.read_bytes(), source_extension)
    if not optimized_url:
        return None

    if optimized_url != local_url and local_path.exists():
        local_path.unlink()

    return optimized_url


def _assign_headshot_crop(player: dict, source_url: Optional[str]) -> None:
    player["headshot_crop"] = resolve_headshot_crop(player, source_url)


def _process_data_file(data_file: Path, session: requests.Session) -> tuple[int, int, int]:
    if not data_file.exists():
        print(f"[WARN] Missing data file: {data_file}")
        return 0, 0, 0

    data = json.loads(data_file.read_text(encoding="utf-8"))
    players = _get_players_container(data)
    if players is None:
        print(f"[WARN] Unsupported data shape in {data_file}")
        return 0, 0, 0
    downloaded = 0
    rewritten = 0
    optimized_existing = 0

    for player in players:
        headshot_url = player.get("headshot_url")
        if isinstance(headshot_url, str) and headshot_url.startswith("/prospect-headshots/"):
            optimized_local_url = _optimize_existing_local_headshot(player, headshot_url)
            if optimized_local_url and optimized_local_url != headshot_url:
                player["headshot_url"] = optimized_local_url
                optimized_existing += 1
            _assign_headshot_crop(player, player.get("original_headshot_url") or player.get("resolved_headshot_url") or headshot_url)
            continue

        if not _is_remote_headshot(headshot_url):
            continue

        resolved_headshot_url = headshot_url
        if isinstance(headshot_url, str) and "www.shl.se/imageproxy/" in headshot_url:
            resolved_headshot_url = _resolve_shl_headshot_url(session, player, headshot_url)

        if not _is_remote_headshot(resolved_headshot_url):
            continue

        local_path = _download_to_local(session, player, resolved_headshot_url)
        if not local_path:
            continue

        player["original_headshot_url"] = headshot_url
        if resolved_headshot_url != headshot_url:
            player["resolved_headshot_url"] = resolved_headshot_url
        player["headshot_url"] = local_path
        _assign_headshot_crop(player, resolved_headshot_url)
        downloaded += 1
        rewritten += 1

    data_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Downloaded {downloaded} prospect headshots for {data_file.name}")
    print(f"Rewrote {rewritten} headshot URLs to local paths for {data_file.name}")
    print(f"Optimized {optimized_existing} existing local headshots for {data_file.name}")
    print(f"Saved data to {data_file}")
    return downloaded, rewritten, optimized_existing


def main() -> int:
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    total_downloaded = 0
    total_rewritten = 0
    total_optimized = 0

    for data_file in DATA_FILES:
        downloaded, rewritten, optimized_existing = _process_data_file(data_file, session)
        total_downloaded += downloaded
        total_rewritten += rewritten
        total_optimized += optimized_existing

    print(f"Total downloaded prospect headshots: {total_downloaded}")
    print(f"Total rewritten headshot URLs: {total_rewritten}")
    print(f"Total optimized existing local headshots: {total_optimized}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
