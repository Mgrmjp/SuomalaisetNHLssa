#!/usr/bin/env python3
"""
Offseason movement collector for Finnish NHL players.

Parses NHL.com trade tracker and free-agent tracker pages,
matches players against the Finnish roster, and writes
validated moves to static/data/offseason-moves.json.

Usage:
    python fetch_offseason_moves.py [--backfill]
"""

import hashlib
import json
import re
import sys
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    DATA_DIR,
    FINNISH_CACHE_FILE,
    NHL_API_BASE,
    API_TIMEOUT,
    JSON_INDENT,
    JSON_ENSURE_ASCII,
)

TRADE_TRACKER_URL = "https://www.nhl.com/news/2026-27-nhl-trades"
FREE_AGENT_TRACKER_URL = (
    "https://www.nhl.com/news/topic/free-agency/free-agency-signings-nhl-2026-27"
)

OUTPUT_FILE = DATA_DIR / "offseason-moves.json"

REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; FinnishNHLBot/1.0; "
        "+https://suomalaisetnhlssa.fi)"
    )
}

TEAM_FULL_TO_ABBREV = {
    "Anaheim Ducks": "ANA", "Boston Bruins": "BOS", "Buffalo Sabres": "BUF",
    "Carolina Hurricanes": "CAR", "Columbus Blue Jackets": "CBJ",
    "Calgary Flames": "CGY", "Chicago Blackhawks": "CHI",
    "Colorado Avalanche": "COL", "Dallas Stars": "DAL",
    "Detroit Red Wings": "DET", "Edmonton Oilers": "EDM",
    "Florida Panthers": "FLA", "Los Angeles Kings": "LAK",
    "Minnesota Wild": "MIN", "Montreal Canadiens": "MTL",
    "New Jersey Devils": "NJD", "Nashville Predators": "NSH",
    "New York Islanders": "NYI", "New York Rangers": "NYR",
    "Ottawa Senators": "OTT", "Philadelphia Flyers": "PHI",
    "Pittsburgh Penguins": "PIT", "Seattle Kraken": "SEA",
    "San Jose Sharks": "SJS", "St. Louis Blues": "STL",
    "Tampa Bay Lightning": "TBL", "Toronto Maple Leafs": "TOR",
    "Utah Mammoth": "UTA", "Utah Hockey Club": "UTA",
    "Vancouver Canucks": "VAN", "Vegas Golden Knights": "VGK",
    "Winnipeg Jets": "WPG", "Washington Capitals": "WSH",
}

VALID_NHL_TEAMS = set(TEAM_FULL_TO_ABBREV.values())

NON_PLAYER_WORDS = {
    "pick", "picks", "round", "conditional", "draft", "consideration",
    "prospect", "prospects", "forward", "forwards", "defenseman",
    "defensemen", "goalie", "goalies", "centre", "center", "winger",
    "each", "and", "the", "from", "for", "to", "a", "an",
}

NON_NHL_KEYWORDS = [
    "sweden", "finland", "czech", "slovakia", "germany", "swiss",
    "austria", "russia", "norway", "denmark", "liiga", "shl",
    "ahl", "echl", "khl", "nl ", "elc", "pwhl",
]

NAME_SUFFIX_RE = re.compile(r"\b(Jr|Sr|II|III|IV)\.?\b", re.IGNORECASE)

MONTHS = {
    "JANUARY": 1, "FEBRUARY": 2, "MARCH": 3, "APRIL": 4,
    "MAY": 5, "JUNE": 6, "JULY": 7, "AUGUST": 8,
    "SEPTEMBER": 9, "OCTOBER": 10, "NOVEMBER": 11, "DECEMBER": 12,
}

WEEKDAYS = {
    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
    "friday": 4, "saturday": 5, "sunday": 6,
}


def strip_diacritics(text):
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def normalize_name_key(name):
    name = strip_diacritics(name.lower().strip())
    name = NAME_SUFFIX_RE.sub("", name).strip()
    name = re.sub(r"[^a-z\s]", "", name)
    return re.sub(r"\s+", " ", name).strip()


def team_full_to_abbrev(full_name):
    if not full_name:
        return None
    cleaned = full_name.strip()
    if cleaned in TEAM_FULL_TO_ABBREV:
        return TEAM_FULL_TO_ABBREV[cleaned]
    for team_name, abbrev in TEAM_FULL_TO_ABBREV.items():
        if team_name.lower() == cleaned.lower():
            return abbrev
    return None


def fetch_page_html(url):
    try:
        resp = requests.get(url, headers=REQUEST_HEADERS, timeout=API_TIMEOUT)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as e:
        print(f"  ERROR fetching {url}: {e}")
        return None


def parse_json_ld(html):
    soup = BeautifulSoup(html, "html.parser")
    results = []
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
            if isinstance(data, list):
                results.extend(data)
            else:
                results.append(data)
        except (json.JSONDecodeError, TypeError):
            continue
    return results


def extract_article_date(html, json_ld_blocks):
    for block in json_ld_blocks:
        date_val = block.get("datePublished") or block.get("dateModified")
        if date_val:
            try:
                dt = datetime.fromisoformat(date_val.replace("Z", "+00:00"))
                return dt.strftime("%Y-%m-%d")
            except (ValueError, AttributeError):
                pass
    soup = BeautifulSoup(html, "html.parser")
    time_el = soup.find("time")
    if time_el:
        dt_attr = time_el.get("datetime", "")
        if dt_attr:
            try:
                dt = datetime.fromisoformat(dt_attr.replace("Z", "+00:00"))
                return dt.strftime("%Y-%m-%d")
            except (ValueError, AttributeError):
                pass
    return None


def extract_article_text(html):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(["script", "style", "nav", "header", "footer"]):
        tag.decompose()
    paragraphs = []
    for el in soup.find_all(["p", "div", "h2", "h3", "h5", "a", "li"]):
        text = el.get_text(strip=True)
        if len(text) > 3:
            paragraphs.append(text)
    return paragraphs


def extract_signing_links(html):
    """Map normalized signing headlines to their linked NHL article URL."""
    soup = BeautifulSoup(html, "html.parser")
    links = {}
    for anchor in soup.find_all("a", href=True):
        text = re.sub(r"\s+", " ", anchor.get_text(" ", strip=True)).strip()
        if not text or not re.search(r"\bsigns?\b", text, re.IGNORECASE):
            continue
        links[text.lower()] = urljoin(FREE_AGENT_TRACKER_URL, anchor["href"])
    return links


def find_signing_source_url(source_text, signing_links):
    key = re.sub(r"\s+", " ", (source_text or "").strip()).lower()
    if key in signing_links:
        return signing_links[key]
    for headline, url in signing_links.items():
        if headline in key or key in headline:
            return url
    return None


def parse_calendar_date(text, default_year):
    match = re.search(
        r"\b(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|"
        r"SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)\s+(\d{1,2})(?:,\s*(\d{4}))?\b",
        text,
        re.IGNORECASE,
    )
    if not match:
        return None
    month = MONTHS[match.group(1).upper()]
    day = int(match.group(2))
    year = int(match.group(3) or default_year)
    try:
        return datetime(year, month, day).strftime("%Y-%m-%d")
    except ValueError:
        return None


def date_for_weekday_on_or_before(weekday_name, published_date):
    try:
        published = datetime.strptime(published_date, "%Y-%m-%d")
    except (TypeError, ValueError):
        return None
    target_weekday = WEEKDAYS.get(weekday_name.lower())
    if target_weekday is None:
        return None
    days_back = (published.weekday() - target_weekday) % 7
    return (published - timedelta(days=days_back)).strftime("%Y-%m-%d")


def extract_move_date_from_article(html, player_name, published_date, offseason_year):
    """Extract the transaction date, which can precede the article publish date."""
    soup = BeautifulSoup(html, "html.parser")
    player_key = normalize_name_key(player_name)
    paragraphs = [
        re.sub(r"\s+", " ", el.get_text(" ", strip=True)).strip()
        for el in soup.find_all(["p", "li"])
    ]

    move_language = re.compile(
        r"\b(announced|transaction|agreed to terms|signed|signing|acquired|traded)\b",
        re.IGNORECASE,
    )
    player_paragraphs = [
        text
        for text in paragraphs
        if player_key in normalize_name_key(text) and move_language.search(text)
    ]
    contextual_paragraphs = [
        text
        for text in paragraphs
        if re.search(
            r"\b(announced today|following roster transactions|agreed to terms)\b",
            text,
            re.IGNORECASE,
        )
    ]
    weekday_paragraphs = [
        text
        for text in paragraphs
        if re.search(r"\bsigned\b", text, re.IGNORECASE)
        and re.search(
            r"\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b",
            text,
            re.IGNORECASE,
        )
    ]

    for text in player_paragraphs + contextual_paragraphs:
        explicit_date = parse_calendar_date(text, offseason_year)
        if explicit_date:
            return explicit_date

    for text in player_paragraphs + contextual_paragraphs + weekday_paragraphs:
        weekday_match = re.search(
            r"\b(?:on\s+)?(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b",
            text,
            re.IGNORECASE,
        )
        if weekday_match:
            weekday_date = date_for_weekday_on_or_before(
                weekday_match.group(1), published_date
            )
            if weekday_date:
                return weekday_date

    return published_date


def enrich_free_agent_dates(moves, tracker_html, offseason_year, fetcher=fetch_page_html):
    signing_links = extract_signing_links(tracker_html)
    article_cache = {}

    for move in moves:
        source_url = find_signing_source_url(move.get("sourceText", ""), signing_links)
        if not source_url:
            continue

        if source_url not in article_cache:
            article_html = fetcher(source_url)
            if article_html:
                article_date = extract_article_date(
                    article_html, parse_json_ld(article_html)
                )
                article_cache[source_url] = (article_html, article_date)
            else:
                article_cache[source_url] = (None, None)

        article_html, published_date = article_cache[source_url]
        if not article_html:
            continue

        move_date = extract_move_date_from_article(
            article_html,
            move["player"].get("name", ""),
            published_date,
            offseason_year,
        )
        if move_date:
            move["date"] = move_date
        move["sourceUrl"] = source_url

    return moves


def parse_date_prefix(text):
    m = re.match(
        r"(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|"
        r"SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)\s+(\d{1,2})",
        text,
        re.IGNORECASE,
    )
    if not m:
        return None, None
    month_str = m.group(1).upper()
    day = int(m.group(2))
    return MONTHS.get(month_str), day


def build_roster_lookup():
    if not FINNISH_CACHE_FILE.exists():
        print(f"  WARNING: Finnish cache not found at {FINNISH_CACHE_FILE}")
        return {}, {}, {}
    with open(FINNISH_CACHE_FILE, "r", encoding="utf-8") as f:
        roster = json.load(f)

    by_id = {}
    by_last_name = {}
    by_full_name = {}

    for pid_str, player in roster.items():
        name = player.get("name", "")
        first_name = ""
        last_name = ""
        if isinstance(player.get("firstName"), dict):
            first_name = player["firstName"].get("default", "")
        if isinstance(player.get("lastName"), dict):
            last_name = player["lastName"].get("default", "")
        if not last_name and name:
            parts = name.split()
            if len(parts) >= 2:
                first_name = parts[0]
                last_name = parts[-1]

        info = {
            "playerId": player.get("playerId", int(pid_str)),
            "name": name,
            "firstName": first_name,
            "lastName": last_name,
            "position": player.get("position", ""),
            "currentTeam": player.get("currentTeam", ""),
            "isActive": player.get("isActive", True),
        }
        by_id[pid_str] = info

        if last_name:
            key = normalize_name_key(last_name)
            if key not in by_last_name:
                by_last_name[key] = []
            by_last_name[key].append(info)

        if name:
            full_key = normalize_name_key(name)
            by_full_name[full_key] = info

    return by_id, by_last_name, by_full_name


def match_player_to_roster(player_name, roster_by_last, roster_by_full):
    if not player_name or not isinstance(player_name, str):
        return None
    cleaned = player_name.strip()
    if not cleaned:
        return None

    full_key = normalize_name_key(cleaned)
    if full_key in roster_by_full:
        return roster_by_full[full_key]

    parts = cleaned.split()
    if not parts:
        return None
    last_name = parts[-1]
    last_key = normalize_name_key(last_name)

    if last_key in NON_PLAYER_WORDS:
        return None

    matches = roster_by_last.get(last_key, [])
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1 and len(parts) >= 2:
        first_key = normalize_name_key(parts[0])
        for m in matches:
            if normalize_name_key(m["firstName"]) == first_key:
                return m
        first_initial = first_key[0] if first_key else ""
        for m in matches:
            if m["firstName"] and normalize_name_key(m["firstName"])[0] == first_initial:
                return m
    return None


def is_re_signing(player_info, new_team_abbrev):
    if not player_info or not new_team_abbrev:
        return False
    current = player_info.get("currentTeam", "")
    return current.upper() == new_team_abbrev.upper()


def is_non_nhl_destination(text):
    lower = text.lower()
    for kw in NON_NHL_KEYWORDS:
        if kw in lower:
            return True
    return False


def generate_move_id(player_id, move_type, old_team, new_team):
    raw = f"{player_id}|{move_type}|{old_team}|{new_team}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def move_identity(move):
    return "|".join([
        str(move.get("playerId", "")),
        str(move.get("moveType", "")),
        str(move.get("oldTeam", "")),
        str(move.get("newTeam", "")),
    ])


def parse_trade_entries(paragraphs, roster_by_last, roster_by_full, page_date):
    moves = []
    current_year = 2026
    current_month = None
    current_day = None

    for text in paragraphs:
        month, day = parse_date_prefix(text)
        if month is not None:
            current_month = month
            current_day = day

        acquire_match = re.search(
            r"([\w\s]+?)\s+acquire\s+(?:forward|defenseman|defenceman|goalie|centre|center|winger)?\s*"
            r"([A-Z][a-záäöåéèêëíïîóöôúüûñčšž]+(?:\s+[A-Z][a-záäöåéèêëíïîóöôúüûñčšž]+)*)"
            r"\s+from\s+(?:the\s+)?([\w\s]+?)(?:\s+for\b|\.\s*$|\s*\|)",
            text,
            re.IGNORECASE,
        )
        if acquire_match:
            new_team_full = acquire_match.group(1).strip()
            player_name = acquire_match.group(2).strip()
            old_team_full = acquire_match.group(3).strip()

            new_team = team_full_to_abbrev(new_team_full)
            old_team = team_full_to_abbrev(old_team_full)

            player = match_player_to_roster(player_name, roster_by_last, roster_by_full)
            if player and new_team and old_team and new_team != old_team:
                date_str = page_date
                if current_month and current_day:
                    date_str = f"{current_year}-{current_month:02d}-{current_day:02d}"
                moves.append({
                    "player": player,
                    "oldTeam": old_team,
                    "newTeam": new_team,
                    "moveType": "trade",
                    "date": date_str,
                })
            continue

        traded_match = re.search(
            r"([A-Z][a-záäöåéèêëíïîóöôúüûñčšž]+(?:\s+[A-Z][a-záäöåéèêëíïîóöôúüûñčšž]+)*)"
            r"\s+traded\s+to\s+([\w\s]+?)\s+by\s+([\w\s]+?)(?:\s*$|\s*\|)",
            text,
            re.IGNORECASE,
        )
        if traded_match:
            player_name = traded_match.group(1).strip()
            new_team_full = traded_match.group(2).strip()
            old_team_full = traded_match.group(3).strip()

            new_team = team_full_to_abbrev(new_team_full)
            old_team = team_full_to_abbrev(old_team_full)

            player = match_player_to_roster(player_name, roster_by_last, roster_by_full)
            if player and new_team and old_team and new_team != old_team:
                date_str = page_date
                if current_month and current_day:
                    date_str = f"{current_year}-{current_month:02d}-{current_day:02d}"
                moves.append({
                    "player": player,
                    "oldTeam": old_team,
                    "newTeam": new_team,
                    "moveType": "trade",
                    "date": date_str,
                })

    return moves


def parse_signing_line(line, team_abbrev):
    patterns = [
        r"([A-Z][a-záäöåéèêëíïîóöôúüûñčšž]+(?:\s+[A-Z]\.?)?(?:\s+[A-Z][a-záäöåéèêëíïîóöôúüûñčšž]+)+)\s+signs?\b",
        r"([A-Z][a-záäöåéèêëíïîóöôúüûñčšž]+)\s+signs?\b",
    ]
    names = []

    if " each signs " in line.lower() or " each sign " in line.lower():
        prefix_match = re.match(
            r"^(.+?)\s+each\s+signs?\s+",
            line,
            re.IGNORECASE,
        )
        if prefix_match:
            prefix = prefix_match.group(1)
            parts = re.split(r",\s*|\s+and\s+", prefix)
            for part in parts:
                name = part.strip()
                if name and len(name) > 1:
                    names.append(name)
            return names

    for pattern in patterns:
        for m in re.finditer(pattern, line):
            name = m.group(1).strip()
            if name and len(name) > 1 and name.lower() not in NON_PLAYER_WORDS:
                names.append(name)
    return names


def parse_free_agent_entries(paragraphs, roster_by_last, roster_by_full, page_date):
    moves = []
    current_team_abbrev = None
    in_signings_section = False

    team_header_re = re.compile(
        r"^(ANAHEIM\s+DUCKS|BOSTON\s+BRUINS|BUFFALO\s+SABRES|CALGARY\s+FLAMES|"
        r"CAROLINA\s+HURRICANES|CHICAGO\s+BLACKHAWKS|COLORADO\s+AVALANCHE|"
        r"COLUMBUS\s+BLUE\s+JACKETS|DALLAS\s+STARS|DETROIT\s+RED\s+WINGS|"
        r"EDMONTON\s+OILERS|FLORIDA\s+PANTHERS|LOS\s+ANGELES\s+KINGS|"
        r"MINNESOTA\s+WILD|MONTREAL\s+CANADIENS|NASHVILLE\s+PREDATORS|"
        r"NEW\s+JERSEY\s+DEVILS|NEW\s+YORK\s+ISLANDERS|NEW\s+YORK\s+RANGERS|"
        r"OTTAWA\s+SENATORS|PHILADELPHIA\s+FLYERS|PITTSBURGH\s+PENGUINS|"
        r"SEATTLE\s+KRAKEN|SAN\s+JOSE\s+SHARKS|ST\.\s+LOUIS\s+BLUES|"
        r"TAMPA\s+BAY\s+LIGHTNING|TORONTO\s+MAPLE\s+LEAFS|UTAH\s+MAMMOTH|"
        r"UTAH\s+HOCKEY\s+CLUB|VANCOUVER\s+CANUCKS|VEGAS\s+GOLDEN\s+KNIGHTS|"
        r"WINNIPEG\s+JETS|WASHINGTON\s+CAPITALS)\s*$",
        re.IGNORECASE,
    )

    for text in paragraphs:
        normalized = re.sub(r"\s+", " ", text.strip())
        team_match = team_header_re.match(normalized)
        if team_match:
            team_name = re.sub(r"\s+", " ", team_match.group(1))
            current_team_abbrev = team_full_to_abbrev(team_name)
            in_signings_section = False
            continue

        if re.match(r"^Signings\s*$", normalized, re.IGNORECASE):
            in_signings_section = True
            continue

        if re.match(r"^Free\s+agents\s*$", normalized, re.IGNORECASE):
            in_signings_section = False
            continue

        if not in_signings_section or not current_team_abbrev:
            continue

        if "re-signed" in normalized.lower() and "each" not in normalized.lower():
            single_re = re.match(
                r"^([A-Z][a-záäöåéèêëíïîóöôúüûñčšž]+(?:\s+[A-Z][a-záäöåéèêëíïîóöôúüûñčšž]+)*)\s+"
                r"(?:re-signs|signs\s+\d)",
                normalized,
            )
            if single_re:
                pass

        if is_non_nhl_destination(normalized):
            continue

        player_names = parse_signing_line(normalized, current_team_abbrev)
        for player_name in player_names:
            player = match_player_to_roster(player_name, roster_by_last, roster_by_full)
            if not player:
                continue

            if is_re_signing(player, current_team_abbrev):
                continue

            old_team = player.get("currentTeam", "")
            if not old_team or old_team == current_team_abbrev:
                continue

            moves.append({
                "player": player,
                "oldTeam": old_team,
                "newTeam": current_team_abbrev,
                "moveType": "free_agent",
                "date": page_date,
                "sourceText": normalized,
            })

    return moves


def parse_free_agent_old_teams(paragraphs):
    team_abbrevs = {}
    current_team_abbrev = None

    team_header_re = re.compile(
        r"^(ANAHEIM\s+DUCKS|BOSTON\s+BRUINS|BUFFALO\s+SABRES|CALGARY\s+FLAMES|"
        r"CAROLINA\s+HURRICANES|CHICAGO\s+BLACKHAWKS|COLORADO\s+AVALANCHE|"
        r"COLUMBUS\s+BLUE\s+JACKETS|DALLAS\s+STARS|DETROIT\s+RED\s+WINGS|"
        r"EDMONTON\s+OILERS|FLORIDA\s+PANTHERS|LOS\s+ANGELES\s+KINGS|"
        r"MINNESOTA\s+WILD|MONTREAL\s+CANADIENS|NASHVILLE\s+PREDATORS|"
        r"NEW\s+JERSEY\s+DEVILS|NEW\s+YORK\s+ISLANDERS|NEW\s+YORK\s+RANGERS|"
        r"OTTAWA\s+SENATORS|PHILADELPHIA\s+FLYERS|PITTSBURGH\s+PENGUINS|"
        r"SEATTLE\s+KRAKEN|SAN\s+JOSE\s+SHARKS|ST\.\s+LOUIS\s+BLUES|"
        r"TAMPA\s+BAY\s+LIGHTNING|TORONTO\s+MAPLE\s+LEAFS|UTAH\s+MAMMOTH|"
        r"UTAH\s+HOCKEY\s+CLUB|VANCOUVER\s+CANUCKS|VEGAS\s+GOLDEN\s+KNIGHTS|"
        r"WINNIPEG\s+JETS|WASHINGTON\s+CAPITALS)\s*$",
        re.IGNORECASE,
    )

    for text in paragraphs:
        normalized = re.sub(r"\s+", " ", text.strip())
        team_match = team_header_re.match(normalized)
        if team_match:
            team_name = re.sub(r"\s+", " ", team_match.group(1))
            current_team_abbrev = team_full_to_abbrev(team_name)
            continue

        if current_team_abbrev:
            signed_matches = re.finditer(
                r"([A-Z][a-záäöåéèêëíïîóöôúüûñčšž]+(?:\s+[A-Z][a-záäöåéèêëíïîóöôúüûñčšž]+)*)\s+"
                r"\(signed:\s*([A-Z]{2,3})\)",
                normalized,
            )
            for m in signed_matches:
                player_name = m.group(1).strip()
                key = normalize_name_key(player_name)
                team_abbrevs[key] = current_team_abbrev

    return team_abbrevs


def enrich_old_teams(moves, old_team_lookup):
    for move in moves:
        if move.get("oldTeam"):
            continue
        player = move.get("player", {})
        name_key = normalize_name_key(player.get("name", ""))
        if name_key in old_team_lookup:
            move["oldTeam"] = old_team_lookup[name_key]
    return moves


def get_offseason_window(offseason_year=2026):
    start = f"{offseason_year}-06-20"
    end = f"{offseason_year}-10-06"
    try:
        schedule_url = f"{NHL_API_BASE}/v1/schedule/{offseason_year}-{offseason_year + 1}"
        resp = requests.get(schedule_url, headers=REQUEST_HEADERS, timeout=API_TIMEOUT)
        if resp.ok:
            data = resp.json()
            dates = sorted(data.get("dates", []))
            if dates:
                first_game = dates[0].get("date", "")
                if first_game:
                    opener = datetime.strptime(first_game, "%Y-%m-%d")
                    end = (opener - timedelta(days=1)).strftime("%Y-%m-%d")
    except Exception:
        pass
    return {"start": start, "end": end}


def load_existing_moves():
    if OUTPUT_FILE.exists():
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return None


def merge_moves(existing, new_moves_list, offseason_year):
    if existing and existing.get("offseasonYear") == offseason_year:
        existing_moves = {
            move_identity(move): move for move in existing.get("moves", [])
        }
    else:
        existing_moves = {}

    for move in new_moves_list:
        existing_moves[move_identity(move)] = move

    return list(existing_moves.values())


def build_output(offseason_year, moves, source_status):
    window = get_offseason_window(offseason_year)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    sorted_moves = sorted(moves, key=lambda m: m.get("date", ""), reverse=True)

    return {
        "offseasonYear": offseason_year,
        "window": window,
        "updatedAt": now,
        "sourceStatus": source_status,
        "moves": sorted_moves,
    }


def save_output(data):
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=JSON_INDENT, ensure_ascii=JSON_ENSURE_ASCII)
    print(f"  Saved {len(data.get('moves', []))} moves to {OUTPUT_FILE}")


def collect_offseason_moves(offseason_year=2026, backfill=False):
    print(f"Collecting offseason moves for {offseason_year}...")

    roster_by_id, roster_by_last, roster_by_full = build_roster_lookup()
    if not roster_by_id:
        print("  ERROR: Could not load Finnish roster. Aborting.")
        return False

    print(f"  Loaded {len(roster_by_id)} Finnish players from roster")

    source_status = {"tradeTracker": "error", "freeAgentTracker": "error"}
    all_moves = []

    print(f"  Fetching trade tracker: {TRADE_TRACKER_URL}")
    trade_html = fetch_page_html(TRADE_TRACKER_URL)
    if trade_html:
        trade_json_ld = parse_json_ld(trade_html)
        trade_page_date = extract_article_date(trade_html, trade_json_ld)
        trade_paragraphs = extract_article_text(trade_html)
        trade_moves = parse_trade_entries(
            trade_paragraphs, roster_by_last, roster_by_full, trade_page_date
        )
        print(f"  Found {len(trade_moves)} Finnish trade(s)")
        all_moves.extend(trade_moves)
        source_status["tradeTracker"] = "ok"
    else:
        print("  WARNING: Could not fetch trade tracker page")

    print(f"  Fetching free-agent tracker: {FREE_AGENT_TRACKER_URL}")
    fa_html = fetch_page_html(FREE_AGENT_TRACKER_URL)
    if fa_html:
        fa_json_ld = parse_json_ld(fa_html)
        fa_page_date = extract_article_date(fa_html, fa_json_ld)
        fa_paragraphs = extract_article_text(fa_html)

        old_team_lookup = parse_free_agent_old_teams(fa_paragraphs)

        fa_moves = parse_free_agent_entries(
            fa_paragraphs, roster_by_last, roster_by_full, fa_page_date
        )
        fa_moves = enrich_old_teams(fa_moves, old_team_lookup)
        fa_moves = enrich_free_agent_dates(fa_moves, fa_html, offseason_year)
        print(f"  Found {len(fa_moves)} Finnish free-agent signing(s)")
        all_moves.extend(fa_moves)
        source_status["freeAgentTracker"] = "ok"
    else:
        print("  WARNING: Could not fetch free-agent tracker page")

    formatted_moves = []
    for move in all_moves:
        player = move["player"]
        pid = str(player["playerId"])
        name = player["name"]
        first = player.get("firstName", "")
        last = player.get("lastName", "")
        slug = normalize_name_key(name).replace(" ", "-")

        formatted_moves.append({
            "moveId": generate_move_id(
                pid, move["moveType"], move["oldTeam"], move["newTeam"]
            ),
            "playerId": pid,
            "playerName": name,
            "playerSlug": slug,
            "position": player.get("position", ""),
            "oldTeam": move["oldTeam"],
            "newTeam": move["newTeam"],
            "moveType": move["moveType"],
            "date": move["date"],
            "sourceUrl": move.get("sourceUrl") or (
                TRADE_TRACKER_URL if move["moveType"] == "trade"
                else FREE_AGENT_TRACKER_URL
            ),
        })

    seen_ids = set()
    deduped = []
    for m in formatted_moves:
        if m["moveId"] not in seen_ids:
            seen_ids.add(m["moveId"])
            deduped.append(m)

    existing = load_existing_moves()
    merged = merge_moves(existing, deduped, offseason_year)

    output = build_output(offseason_year, merged, source_status)
    save_output(output)

    if any(v == "error" for v in source_status.values()):
        print("  WARNING: One or more sources had errors")
        return False

    print(f"  Done! {len(merged)} total moves recorded")
    return True


if __name__ == "__main__":
    offseason_year = 2026
    backfill = "--backfill" in sys.argv

    success = collect_offseason_moves(offseason_year, backfill)
    sys.exit(0 if success else 1)
