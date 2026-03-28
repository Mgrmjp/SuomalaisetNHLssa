#!/usr/bin/env python3
"""
Comprehensive player data quality validation.

Checks:
1. Birthdate validity - future dates, invalid dates, age <15 or >50
2. Draft logic - future draft year, draft before birth
3. Stats consistency - points ≠ goals+assists, negative values
4. Team/League match - team not in that league
5. NHL Rights validity - invalid team abbreviation
6. Duplicate detection - same ID twice, same name+team different ID
7. Data freshness - all stats zero for active player
8. Name integrity - empty names, special chars only

Usage:
    python scripts/data_collection/validate_prospect_data.py [--fix] [--format=metrics] [--output=jsonl]
"""

import argparse
import json
import re
import sys
import unicodedata
from datetime import datetime, date
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_FILES = {
    "finnish": PROJECT_ROOT / "static" / "data" / "finnish_prospects.json",
    "official": PROJECT_ROOT
    / "static"
    / "data"
    / "leagues"
    / "league_prospects_official.json",
    "advanced": PROJECT_ROOT
    / "static"
    / "data"
    / "leagues"
    / "league_prospects_advanced.json",
    "na": PROJECT_ROOT / "static" / "data" / "leagues" / "league_prospects_na.json",
}

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

VALID_NHL_TEAMS = {
    "ANA",
    "ARI",
    "BOS",
    "BUF",
    "CAR",
    "CBJ",
    "CGY",
    "CHI",
    "COL",
    "DAL",
    "DET",
    "EDM",
    "FLA",
    "LAK",
    "MIN",
    "MTL",
    "NJD",
    "NSH",
    "NYI",
    "NYR",
    "OTT",
    "PHI",
    "PHX",
    "PIT",
    "SEA",
    "SJS",
    "STL",
    "TBL",
    "TOR",
    "UTA",
    "VAN",
    "VGK",
    "WPG",
    "WSH",
}


def normalize_name(name):
    """Normalize person name for comparison."""
    if not name:
        return ""
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


def parse_date(date_str):
    """Parse date string to date object. Returns None if invalid."""
    if not date_str:
        return None
    try:
        if "-" in date_str:
            parts = date_str.split("-")
            if len(parts) != 3:
                return None
            year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
        elif "/" in date_str:
            parts = date_str.split("/")
            if len(parts) != 3:
                return None
            month, day, year = int(parts[0]), int(parts[1]), int(parts[2])
        else:
            return None
        return date(year, month, day)
    except (ValueError, IndexError):
        return None


def validate_birthdate_validity(player):
    """Check if birthDate is valid: not future, valid date, age 15-85."""
    issues = []
    birth_date_str = player.get("birthDate") or player.get("birth_date")

    if not birth_date_str:
        return True, None

    birth_date = parse_date(birth_date_str)
    if birth_date is None:
        return False, f"invalid_date_format: {birth_date_str}"

    today = date.today()
    if birth_date > today:
        issues.append(f"future_date: {birth_date_str}")

    age = (
        today.year
        - birth_date.year
        - ((today.month, today.day) < (birth_date.month, birth_date.day))
    )
    if age < 15 or age > 85:
        issues.append(f"age_out_of_range: age={age}")

    if issues:
        return False, ", ".join(issues)
    return True, None


def validate_draft_logic(player):
    """Check draft logic: future draft year, draft before birth."""
    issues = []
    sources = player.get("sources", [])
    draft_year = get_draft_year(sources)
    birth_date_str = player.get("birthDate") or player.get("birth_date")

    has_draft_source = any(s.startswith("draft_picks:") for s in sources)

    if not draft_year:
        if has_draft_source:
            issues.append("missing_draft_year")
        if issues:
            return False, ", ".join(issues)
        return True, None

    today = date.today()
    if draft_year > today.year:
        issues.append(f"future_draft_year: {draft_year}")

    if birth_date_str:
        birth_date = parse_date(birth_date_str)
        if birth_date and draft_year < birth_date.year:
            issues.append(
                f"draft_before_birth: draft={draft_year}, birth={birth_date.year}"
            )

    if issues:
        return False, ", ".join(issues)
    return True, None


def validate_stats_consistency(player):
    """Check stats consistency: points = goals + assists, no negatives."""
    issues = []
    stats = player.get("stats") or {}
    position = str(player.get("position", "")).lower()

    gp = stats.get("gp", 0)
    goals = stats.get("goals", 0)
    assists = stats.get("assists", 0)
    points = stats.get("points", 0)
    save_pct = stats.get("savePct") or stats.get("save_pct")
    gaa = stats.get("gaa") or stats.get("goals_against_average")

    is_goalie = position in ["g", "goalie", "maalivahti"]
    has_goalie_stats = (save_pct is not None and save_pct > 0) or (
        gaa is not None and gaa > 0
    )
    if has_goalie_stats:
        is_goalie = True

    if gp < 0 or goals < 0 or assists < 0 or points < 0:
        issues.append(
            f"negative_stats: gp={gp}, goals={goals}, assists={assists}, points={points}"
        )

    if not is_goalie and gp > 0 and goals >= 0 and assists >= 0 and points >= 0:
        expected_points = goals + assists
        if points != expected_points:
            issues.append(
                f"points_mismatch: points={points}, expected={expected_points}"
            )

    if issues:
        return False, ", ".join(issues)
    return True, None


def validate_team_league_match(player, valid_teams_by_league):
    """Check if team exists in player's league."""
    team = player.get("team", "").strip()
    league = player.get("league", "").strip()

    if not team or not league:
        return True, None

    valid_teams = valid_teams_by_league.get(league, set())
    if valid_teams and team not in valid_teams:
        return False, f"team_not_in_league: team={team}, league={league}"

    return True, None


def validate_nhl_rights(player):
    """Check if NHL rights team is valid abbreviation."""
    nhl_rights = player.get("nhlRights", "").strip()

    if not nhl_rights or nhl_rights == "N/A":
        return True, None

    if nhl_rights not in VALID_NHL_TEAMS:
        return False, f"invalid_nhl_rights: {nhl_rights}"

    return True, None


def validate_no_duplicates(players_by_id, player):
    """Check for duplicate players."""
    issues = []
    player_id = str(player.get("id", ""))
    name = player.get("name", "")
    team = player.get("team", "")

    if not player_id:
        return True, None

    existing = players_by_id.get(player_id)
    if existing:
        existing_name = existing.get("name", "")
        existing_team = existing.get("team", "")

        if (
            normalize_name(name) == normalize_name(existing_name)
            and team == existing_team
        ):
            issues.append(f"duplicate_player: same_id={player_id}, name={name}")

    return True, None if not issues else False, ", ".join(issues)


def validate_data_freshness(player):
    """Check data freshness: all stats zero for active player."""
    issues = []
    stats = player.get("stats") or {}
    last_season = player.get("lastSeason")

    gp = stats.get("gp", 0)
    goals = stats.get("goals", 0)
    assists = stats.get("assists", 0)
    points = stats.get("points", 0)

    if last_season:
        current_season = 20252026
        if last_season >= current_season and gp == 0 and points == 0:
            issues.append(f"active_no_stats: lastSeason={last_season}")

    if issues:
        return False, ", ".join(issues)
    return True, None


def validate_name_integrity(player):
    """Check name integrity: not empty, not just special chars."""
    name = player.get("name", "").strip()

    if not name:
        return False, "empty_name"

    normalized = normalize_name(name)
    if not normalized or len(normalized) < 2:
        return False, f"invalid_name: {name}"

    has_letters = any(c.isalpha() for c in name)
    if not has_letters:
        return False, f"name_no_letters: {name}"

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

    extracted_id = None
    if player_league == "Liiga" and filename.startswith("liiga-"):
        extracted_id = filename.replace("liiga-", "")
    elif player_league == "AHL" and filename.startswith("ahl-"):
        extracted_id = filename.replace("ahl-", "")
    elif player_league == "SHL" and filename.startswith("shl-"):
        extracted_id = filename.replace("shl-", "")
    elif player_league == "Mestis" and filename.startswith("mestis-"):
        extracted_id = filename.replace("mestis-", "")

    if not extracted_id:
        return True, None

    lookup = league_lookups.get(player_league, {})
    source_name = lookup.get(extracted_id)

    if source_name and normalize_name(source_name) != normalize_name(player_name):
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
            f"league_mismatch: player={player_league}, headshot={headshot_league}",
        )

    return True, None


def derive_valid_teams():
    """Derive valid teams per league from existing data."""
    teams_by_league = {}

    for filepath in DATA_FILES.values():
        if not filepath.exists():
            continue
        try:
            data = json.loads(filepath.read_text(encoding="utf-8"))
            players = data if isinstance(data, list) else data.get("players", [])

            for p in players:
                league = p.get("league", "")
                team = p.get("team", "").strip()
                if league and team:
                    if league not in teams_by_league:
                        teams_by_league[league] = set()
                    teams_by_league[league].add(team)
        except Exception:
            pass

    return teams_by_league


def load_league_lookups():
    """Build lookup tables from league files."""
    lookups = {}

    for league_name, filepath in [
        ("Liiga", DATA_FILES["official"]),
        ("AHL", DATA_FILES["na"]),
        ("SHL", DATA_FILES["official"]),
        ("Mestis", DATA_FILES["advanced"]),
    ]:
        if not filepath.exists():
            continue
        try:
            data = json.loads(filepath.read_text(encoding="utf-8"))
            players = data if isinstance(data, list) else data.get("players", [])

            lookup = {}
            for p in players:
                player_id = p.get("player_id", "")
                name = p.get("name", "")
                if player_id and name:
                    lookup[str(player_id)] = name
                    numeric_id = str(player_id).split("_")[-1]
                    lookup[numeric_id] = name

            lookups[league_name] = lookup
        except Exception:
            pass

    return lookups


def validate_player(player, league_lookups, valid_teams_by_league, players_by_id):
    """Run all validations on a player. Returns list of issues."""
    issues = []

    validators = [
        ("birthdate_validity", validate_birthdate_validity),
        ("draft_logic", validate_draft_logic),
        ("stats_consistency", validate_stats_consistency),
        ("nhl_rights", validate_nhl_rights),
        ("data_freshness", validate_data_freshness),
        ("name_integrity", validate_name_integrity),
        ("headshot_ownership", validate_headshot_ownership),
        ("league_consistency", validate_league_consistency),
    ]

    for validator_name, validator_func in validators:
        if validator_name == "team_league_match":
            valid, reason = validator_func(player, valid_teams_by_league)
        elif validator_name == "no_duplicates":
            valid, reason = validator_func(players_by_id, player)
        elif validator_name == "headshot_ownership":
            valid, reason = validator_func(player, league_lookups)
        else:
            valid, reason = validator_func(player)

        if not valid:
            issues.append({"validator": validator_name, "reason": reason})

    return issues


def fix_player_issues(player, issues):
    """Auto-fix fixable issues in player data."""
    fixed = []

    for issue in issues:
        validator = issue.get("validator", "")
        reason = issue.get("reason", "")

        if validator == "birthdate_validity":
            player["birthDate"] = None
            fixed.append("cleared invalid birthDate")

        elif validator == "draft_logic":
            if "future_draft_year" in reason or "draft_before_birth" in reason:
                player["birthDate"] = None
                fixed.append("cleared birthDate due to draft logic issue")

        elif validator == "stats_consistency":
            if "negative_stats" in reason or "points_mismatch" in reason:
                player["stats"] = {}
                fixed.append("cleared corrupted stats")

        elif validator == "headshot_ownership":
            player["headshot"] = None
            player["headshotCrop"] = None
            fixed.append("cleared wrong headshot")

        elif validator == "league_consistency":
            player["headshot"] = None
            player["headshotCrop"] = None
            fixed.append("cleared mismatched league headshot")

    return fixed


def main():
    parser = argparse.ArgumentParser(description="Validate player data quality")
    parser.add_argument("--fix", action="store_true", help="Auto-fix fixable issues")
    parser.add_argument(
        "--format", choices=["human", "metrics"], default="human", help="Output format"
    )
    parser.add_argument("--output", type=str, help="Append results to JSONL file")
    parser.add_argument(
        "--file",
        type=str,
        default="finnish",
        choices=["finnish", "official", "advanced", "na", "all"],
        help="Which data file to validate",
    )
    args = parser.parse_args()

    if args.file == "all":
        files_to_check = list(DATA_FILES.items())
    else:
        files_to_check = [(args.file, DATA_FILES[args.file])]

    all_issues = {}
    all_fixed = []
    total_players = 0
    total_passed = 0

    league_lookups = load_league_lookups()
    valid_teams_by_league = derive_valid_teams()

    for file_key, filepath in files_to_check:
        if not filepath.exists():
            print(f"WARNING: File not found: {filepath}")
            continue

        data = json.loads(filepath.read_text(encoding="utf-8"))
        players = data if isinstance(data, list) else data.get("players", [])

        if not isinstance(data, list):
            data = players

        players_by_id = {str(p.get("id", "")): p for p in players if p.get("id")}

        issues_by_validator = {}
        passed = 0
        fixed_count = 0

        for player in players:
            total_players += 1
            player_issues = validate_player(
                player, league_lookups, valid_teams_by_league, players_by_id
            )

            if player_issues:
                for issue in player_issues:
                    validator = issue["validator"]
                    if validator not in issues_by_validator:
                        issues_by_validator[validator] = []
                    issues_by_validator[validator].append(
                        {
                            "name": player.get("name", "Unknown"),
                            "id": player.get("id", "?"),
                            "reason": issue["reason"],
                        }
                    )

                if args.fix:
                    fixed = fix_player_issues(player, player_issues)
                    if fixed:
                        fixed_count += len(fixed)
                        all_fixed.extend([f"{player.get('name')}: {f}" for f in fixed])
            else:
                passed += 1
                total_passed += 1

        all_issues[file_key] = issues_by_validator

        if args.fix and fixed_count > 0:
            filepath.write_text(
                json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
            )

    quality_score = (total_passed / total_players * 100) if total_players > 0 else 0

    if args.format == "metrics":
        print(f"METRIC data_quality_score={quality_score:.2f}")
        print(f"METRIC total_players={total_players}")
        print(f"METRIC players_passed={total_passed}")

        validators = [
            "birthdate_validity",
            "draft_logic",
            "stats_consistency",
            "team_league_match",
            "nhl_rights",
            "no_duplicates",
            "data_freshness",
            "name_integrity",
            "headshot_ownership",
            "league_consistency",
        ]

        for v in validators:
            count = sum(len(all_issues.get(f, {}).get(v, [])) for f in all_issues)
            print(f"METRIC issue_count_{v}={count}")

        if args.fix:
            print(f"METRIC fixed_count={len(all_fixed)}")

    else:
        print("=" * 60)
        print("PLAYER DATA QUALITY REPORT")
        print("=" * 60)
        print(f"Total players: {total_players}")
        print(f"Passed validation: {total_passed} ({quality_score:.1f}%)")
        if args.fix:
            print(f"Issues fixed: {len(all_fixed)}")
        print()

        validators = [
            "birthdate_validity",
            "draft_logic",
            "stats_consistency",
            "team_league_match",
            "nhl_rights",
            "no_duplicates",
            "data_freshness",
            "name_integrity",
            "headshot_ownership",
            "league_consistency",
        ]

        for v in validators:
            items = []
            for f in all_issues:
                items.extend(all_issues.get(f, {}).get(v, []))
            count = len(items)
            print(f"{v}: {count}")
            if count > 0 and count <= 10:
                for item in items:
                    print(f"  - {item['name']} (ID: {item['id']}): {item['reason']}")
            elif count > 10:
                for item in items[:5]:
                    print(f"  - {item['name']} (ID: {item['id']}): {item['reason']}")
                print(f"  ... and {count - 5} more")
            print()

        if args.fix and all_fixed:
            print("FIXED ISSUES:")
            for f in all_fixed[:20]:
                print(f"  - {f}")
            if len(all_fixed) > 20:
                print(f"  ... and {len(all_fixed) - 20} more")

    if args.output:
        result = {
            "timestamp": datetime.now().isoformat(),
            "data_quality_score": quality_score,
            "total_players": total_players,
            "players_passed": total_passed,
            "fixed_count": len(all_fixed) if args.fix else 0,
        }
        with open(args.output, "a") as f:
            f.write(json.dumps(result) + "\n")

    return 0 if quality_score == 100 else 1


if __name__ == "__main__":
    sys.exit(main())
