#!/usr/bin/env python3
"""
Validate player data quality in finnish_prospects.json.

Checks:
1. Age consistency - birthDate must be consistent with draft year
2. Stats plausibility - basic sanity checks
3. Headshot ownership - headshot ID matches player ID
4. League consistency - headshot league prefix matches player league

Usage:
    python scripts/data_collection/validate_prospect_data.py
"""

import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_FILE = PROJECT_ROOT / "static" / "data" / "finnish_prospects.json"

LEAGUE_PREFIXES = {
    "liiga": "Liiga",
    "ahl": "AHL",
    "shl": "SHL",
    "mestis": "Mestis",
    "whl": "WHL",
    "ohl": "OHL",
    "qmjhl": "QMJHL",
    "ushl": "USHL",
    "nhl": "NHL",
    "echl": "ECHL",
    "khl": "KHL",
    "nl": "NL",
    "del": "DEL",
    "czech": "Czech",
    "icehl": "ICEHL",
}


def normalize_name(name):
    """Normalize person name for comparison."""
    if not name:
        return ""
    import unicodedata

    return (
        unicodedata.normalize("NFD", name.strip())
        .lower()
        .replace("\u0300", "")
        .replace("\u0301", "")
        .replace("\u0302", "")
        .replace("\u0303", "")
        .replace("\u0308", "")
        .replace("\u030a", "")
        .replace("\u030c", "")
        .replace("\u0327", "")
        .replace("\u0328", "")
    )


def get_draft_year(sources):
    """Extract draft year from sources."""
    for source in sources or []:
        if source.startswith("draft_picks:"):
            try:
                return int(source.split(":")[1])
            except (ValueError, IndexError):
                pass
    return None


def get_league_from_headshot_filename(headshot_url):
    """Extract league from headshot filename prefix."""
    if not headshot_url:
        return None

    filename = (
        headshot_url.replace("/prospect-headshots/", "")
        .replace(".webp", "")
        .replace(".jpg", "")
        .replace(".png", "")
        .lower()
    )

    for prefix, league in LEAGUE_PREFIXES.items():
        if filename.startswith(prefix + "-") or filename.startswith(prefix + "_"):
            return league
    return None


def validate_age_consistency(player):
    """Check if birthDate is consistent with draft year."""
    birth_date = player.get("birthDate")
    draft_year = get_draft_year(player.get("sources", []))

    if not birth_date:
        return True, None

    try:
        birth_year = int(birth_date.split("-")[0])
    except (ValueError, IndexError, AttributeError):
        return True, None  # Can't parse, skip

    if not draft_year:
        return True, None  # No draft year to compare

    age_at_draft = draft_year - birth_year

    if age_at_draft < 17 or age_at_draft > 45:
        return (
            False,
            f"impossible_age: draft_year={draft_year}, birth_year={birth_year}, age={age_at_draft}",
        )

    return True, None


def validate_stats_plausibility(player):
    """Check if stats are plausible."""
    stats = player.get("stats") or {}
    position = player.get("position", "")

    gp = stats.get("gp", 0)
    goals = stats.get("goals", 0)
    assists = stats.get("assists", 0)

    if gp == 0:
        return True, None  # No games played, can't validate

    # If played games but has no goals OR assists, that's unusual but possible
    # We won't flag this as an error

    # Negative values are definitely wrong
    if gp < 0 or goals < 0 or assists < 0:
        return False, f"negative_stats: gp={gp}, goals={goals}, assists={assists}"

    return True, None


def validate_headshot_ownership(player, league_lookups):
    """Check if headshot actually belongs to this player."""
    headshot = player.get("headshot")
    player_name = player.get("name", "")
    player_league = player.get("league", "")

    if not headshot or not headshot.startswith("/prospect-headshots/"):
        return True, None

    filename = (
        headshot.replace("/prospect-headshots/", "")
        .replace(".webp", "")
        .replace(".jpg", "")
        .replace(".png", "")
    )

    # Try to extract ID from filename for different leagues
    extracted_id = None

    if player_league == "Liiga" and filename.startswith("liiga-"):
        extracted_id = filename.replace("liiga-", "")
    elif player_league == "AHL" and filename.startswith("ahl-"):
        extracted_id = filename.replace("ahl-", "")
    elif player_league == "SHL" and filename.startswith("shl-"):
        extracted_id = filename.replace("shl-", "")
    elif player_league == "Mestis" and filename.startswith("mestis-"):
        extracted_id = filename.replace("mestis-", "")
    # Add more leagues as needed

    if not extracted_id:
        return True, None  # Can't extract ID, skip

    # Check if there's a name in the lookup that doesn't match
    lookup = league_lookups.get(player_league, {})
    source_name = lookup.get(extracted_id)

    if source_name:
        # Compare normalized names
        if normalize_name(source_name) != normalize_name(player_name):
            return (
                False,
                f"headshot_belongs_to_other: headshot={filename}, player={player_name}, owner={source_name}",
            )

    return True, None


def validate_league_consistency(player):
    """Check if headshot league prefix matches player league."""
    headshot = player.get("headshot")
    player_league = player.get("league", "")

    if not headshot or not headshot.startswith("/prospect-headshots/"):
        return True, None

    headshot_league = get_league_from_headshot_filename(headshot)

    if headshot_league and headshot_league != player_league:
        return (
            False,
            f"league_mismatch: player_league={player_league}, headshot_league={headshot_league}",
        )

    return True, None


def load_league_lookups():
    """Build lookup tables from league files."""
    import json

    lookups = {}
    league_files = [
        (
            "Liiga",
            PROJECT_ROOT
            / "static"
            / "data"
            / "leagues"
            / "league_prospects_official.json",
        ),
        (
            "AHL",
            PROJECT_ROOT / "static" / "data" / "leagues" / "league_prospects_na.json",
        ),
        (
            "SHL",
            PROJECT_ROOT
            / "static"
            / "data"
            / "leagues"
            / "league_prospects_official.json",
        ),
        (
            "Mestis",
            PROJECT_ROOT
            / "static"
            / "data"
            / "leagues"
            / "league_prospects_advanced.json",
        ),
    ]

    for league_name, filepath in league_files:
        if not filepath.exists():
            continue

        try:
            data = json.loads(filepath.read_text(encoding="utf-8"))
            players = data.get("players", []) if isinstance(data, dict) else data

            lookup = {}
            for p in players:
                player_id = p.get("player_id", "")
                name = p.get("name", "")
                if player_id and name:
                    # Store both full ID and numeric part
                    lookup[str(player_id)] = name
                    numeric_id = str(player_id).split("_")[-1]
                    lookup[numeric_id] = name

            lookups[league_name] = lookup
        except Exception as e:
            print(f"Error loading {filepath}: {e}", file=sys.stderr)

    return lookups


def main():
    if not DATA_FILE.exists():
        print(f"ERROR: Data file not found: {DATA_FILE}")
        return 1

    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    players = data if isinstance(data, list) else data.get("players", [])

    league_lookups = load_league_lookups()

    total = len(players)
    issues = {
        "age_impossible": [],
        "negative_stats": [],
        "headshot_wrong_player": [],
        "league_mismatch": [],
    }
    passed = 0

    for player in players:
        name = player.get("name", "Unknown")
        player_id = player.get("id", "?")

        has_issue = False

        # Check age consistency
        valid, reason = validate_age_consistency(player)
        if not valid:
            issues["age_impossible"].append(
                {"name": name, "id": player_id, "reason": reason}
            )
            has_issue = True

        # Check stats plausibility
        valid, reason = validate_stats_plausibility(player)
        if not valid:
            issues["negative_stats"].append(
                {"name": name, "id": player_id, "reason": reason}
            )
            has_issue = True

        # Check headshot ownership
        valid, reason = validate_headshot_ownership(player, league_lookups)
        if not valid:
            issues["headshot_wrong_player"].append(
                {"name": name, "id": player_id, "reason": reason}
            )
            has_issue = True

        # Check league consistency
        valid, reason = validate_league_consistency(player)
        if not valid:
            issues["league_mismatch"].append(
                {"name": name, "id": player_id, "reason": reason}
            )
            has_issue = True

        if not has_issue:
            passed += 1

    quality_score = (passed / total * 100) if total > 0 else 0

    print("=" * 60)
    print("PLAYER DATA QUALITY REPORT")
    print("=" * 60)
    print(f"Total players: {total}")
    print(f"Passed validation: {passed} ({quality_score:.1f}%)")
    print()

    for issue_type, items in issues.items():
        count = len(items)
        print(f"{issue_type}: {count}")
        if count > 0 and count <= 20:
            for item in items:
                print(f"  - {item['name']} (ID: {item['id']}): {item['reason']}")
        elif count > 20:
            for item in items[:10]:
                print(f"  - {item['name']} (ID: {item['id']}): {item['reason']}")
            print(f"  ... and {count - 10} more")
        print()

    print("METRIC data_quality_score={:.2f}".format(quality_score))
    print("METRIC total_players={}".format(total))
    print("METRIC players_passed={}".format(passed))
    print("METRIC issue_count_age_impossible={}".format(len(issues["age_impossible"])))
    print("METRIC issue_count_negative_stats={}".format(len(issues["negative_stats"])))
    print(
        "METRIC issue_count_headshot_wrong_player={}".format(
            len(issues["headshot_wrong_player"])
        )
    )
    print(
        "METRIC issue_count_league_mismatch={}".format(len(issues["league_mismatch"]))
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
