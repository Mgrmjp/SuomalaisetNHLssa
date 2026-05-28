import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

CACHE_FILE = Path("static/data/tavily_news_cache.json")
DAILY_CACHE_FILE = Path("static/data/daily-news-source-cache.json")
OUTPUT_FILE = Path("static/data/daily-news.json")

MONTHS = {
    "january": 1,
    "jan": 1,
    "february": 2,
    "feb": 2,
    "march": 3,
    "mar": 3,
    "april": 4,
    "apr": 4,
    "may": 5,
    "june": 6,
    "jun": 6,
    "july": 7,
    "jul": 7,
    "august": 8,
    "aug": 8,
    "september": 9,
    "sep": 9,
    "sept": 9,
    "october": 10,
    "oct": 10,
    "november": 11,
    "nov": 11,
    "december": 12,
    "dec": 12,
}

DATE_PATTERNS = [
    re.compile(r"\b(20\d{2})-(\d{2})-(\d{2})\b"),
    re.compile(r"\b(20\d{2})/(\d{1,2})/(\d{1,2})\b"),
    re.compile(r"\b([A-Za-z]{3,9})\.?\s+(\d{1,2}),\s*(20\d{2})\b"),
]

GENERIC_TITLE_PATTERNS = [
    re.compile(r"^NHL-lähde julkaisi NHL-uutisen\b", re.IGNORECASE),
]

GENERIC_SUMMARY_PATTERNS = [
    re.compile(r"\bNHL-aiheisen jutun\b", re.IGNORECASE),
    re.compile(r"\bAlkuperäinen kuvaus:", re.IGNORECASE),
    re.compile(r"\bAlkuperäinen otsikko:", re.IGNORECASE),
]

NOISE_TEXT_PATTERNS = [
    re.compile(r"discover a winning edge at vsin", re.IGNORECASE),
    re.compile(r"\bbetting splits\b", re.IGNORECASE),
    re.compile(r"\breal-time odds\b", re.IGNORECASE),
    re.compile(r"\blive broadcasts?\b", re.IGNORECASE),
    re.compile(r"we and our third-party partners may use cookies", re.IGNORECASE),
    re.compile(r"\bpersonalized advertising\b", re.IGNORECASE),
    re.compile(r"\blive scoring leaders?\b", re.IGNORECASE),
    re.compile(r"\bplay fantasy hockey\b", re.IGNORECASE),
    re.compile(r"\bsubscribers only\b", re.IGNORECASE),
    re.compile(r"\bissues by year\b", re.IGNORECASE),
]

NOISE_TITLE_PATTERNS = [
    re.compile(r"^schedule\s*\|", re.IGNORECASE),
    re.compile(r"^nhl scores\b", re.IGNORECASE),
    re.compile(r"\bscores and schedule\b", re.IGNORECASE),
    re.compile(r"\bstandings\b", re.IGNORECASE),
    re.compile(r"\blive updates\b", re.IGNORECASE),
    re.compile(r"\bgame center\b", re.IGNORECASE),
    re.compile(r"\barchive\b", re.IGNORECASE),
    re.compile(r"\bcookies?\b", re.IGNORECASE),
    re.compile(r"\bbetting\b", re.IGNORECASE),
    re.compile(r"\bhighlights?\b", re.IGNORECASE),
    re.compile(r"\bpost game\b", re.IGNORECASE),
    re.compile(r"^review of .* nhl games\b", re.IGNORECASE),
    re.compile(r"^daily nhl recap\b", re.IGNORECASE),
    re.compile(r"\bplayoff board update\b", re.IGNORECASE),
]

NOISE_URL_PATTERNS = [
    re.compile(r"/info/cookies", re.IGNORECASE),
    re.compile(r"/partner/vsin", re.IGNORECASE),
    re.compile(r"/stats/", re.IGNORECASE),
    re.compile(r"/schedule/", re.IGNORECASE),
    re.compile(r"archive\.thehockeynews\.com", re.IGNORECASE),
]

SOURCE_LABELS = {
    "archive": "Archive",
    "espnpressroom": "ESPN Press Room",
    "headlinehockey": "Headline Hockey",
    "hockey-reference": "Hockey-Reference",
    "insidetherink": "Inside the Rink",
    "insidetherink com": "Inside the Rink",
    "media": "NHL Media",
    "msn": "MSN",
    "nhl": "NHL.com",
    "nytimes": "The Athletic",
    "plaintextsports": "Plain Text Sports",
    "prohockeynews": "Pro Hockey News",
    "prohockeyrumors": "Pro Hockey Rumors",
    "spectorshockey": "Spectors Hockey",
    "sportsnews-365": "SportsNews 365",
    "thehockeynews": "The Hockey News",
    "thehockeywriters": "The Hockey Writers",
    "youtube": "YouTube",
}

TRUSTED_NEWS_DOMAINS = {
    "nhl.com",
    "media.nhl.com",
    "sportsnet.ca",
    "nytimes.com",
    "theathletic.com",
    "espn.com",
    "thehockeywriters.com",
    "spectorshockey.net",
    "thehockeynews.com",
    "prohockeyrumors.com",
    "insidetherink.com",
}

LOW_VALUE_TITLE_HINTS = [
    "free picks",
    "predictions",
    "dawg of the day",
    "best bets",
    "betting",
    "odds",
    "live stream",
]

LOW_VALUE_SUMMARY_HINTS = [
    "pickdawgz",
    "best bets",
    "betting splits",
    "real-time odds",
    "winning edge",
]

TRACKING_QUERY_KEYS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "fbclid",
    "gclid",
    "igshid",
}

CATEGORY_PATTERNS = [
    (
        "rumors",
        [
            re.compile(r"rumor roundup", re.IGNORECASE),
            re.compile(r"rumor mill", re.IGNORECASE),
            re.compile(r"trade board", re.IGNORECASE),
        ],
    ),
    (
        "recap",
        [
            re.compile(r"morning recap", re.IGNORECASE),
            re.compile(r"preseason roundup", re.IGNORECASE),
            re.compile(r"recap of nhl", re.IGNORECASE),
            re.compile(r"recap of stanley cup playoffs", re.IGNORECASE),
        ],
    ),
    (
        "morning-skate",
        [
            re.compile(r"morning skate", re.IGNORECASE),
        ],
    ),
    (
        "headlines",
        [
            re.compile(r"morning coffee headlines", re.IGNORECASE),
            re.compile(r"\bbuzz\b", re.IGNORECASE),
        ],
    ),
    (
        "key-stories",
        [
            re.compile(r"five key stories", re.IGNORECASE),
        ],
    ),
    (
        "playoffs",
        [
            re.compile(r"playoffs buzz", re.IGNORECASE),
            re.compile(r"stanley cup playoffs buzz", re.IGNORECASE),
        ],
    ),
    (
        "analysis",
        [
            re.compile(r"trade deadline aftermath", re.IGNORECASE),
            re.compile(r"\banalysis\b", re.IGNORECASE),
        ],
    ),
]


def load_cache():
    if not CACHE_FILE.exists():
        return {}
    return json.loads(CACHE_FILE.read_text(encoding="utf-8"))


def load_daily_cache():
    if not DAILY_CACHE_FILE.exists():
        return {}
    return json.loads(DAILY_CACHE_FILE.read_text(encoding="utf-8"))


def save_daily_cache(cache):
    DAILY_CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def to_date_string(year, month, day):
    try:
        return datetime(int(year), int(month), int(day)).strftime("%Y-%m-%d")
    except ValueError:
        return None


def extract_dates_from_text(text):
    matches = []

    if not text:
        return matches

    for pattern in DATE_PATTERNS:
        for groups in pattern.findall(text):
            if len(groups) != 3:
                continue

            if groups[0].isalpha():
                month_name, day, year = groups
                month = MONTHS.get(month_name.lower().rstrip("."))
                if not month:
                    continue
                date_str = to_date_string(year, month, day)
            else:
                year, month, day = groups
                date_str = to_date_string(year, month, day)

            if date_str:
                matches.append(date_str)

    # Preserve order, drop duplicates
    return list(dict.fromkeys(matches))


def extract_dates(title, description, url):
    title_matches = extract_dates_from_text(title)
    url_matches = extract_dates_from_text(url)

    if title_matches or url_matches:
        return list(dict.fromkeys(title_matches + url_matches))

    description_matches = extract_dates_from_text(description)
    if len(description_matches) > 2:
        return []

    return description_matches


def format_finnish_date(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.strftime("%-d.%-m.%Y")


def iso_week_key(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    year, week, _ = dt.isocalendar()
    return f"{year}-W{week:02d}"


def normalize_whitespace(text):
    return re.sub(r"\s+", " ", (text or "")).strip()


def truncate(text, limit=220):
    text = normalize_whitespace(text)
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def matches_any_pattern(text, patterns):
    normalized = normalize_whitespace(text)
    return bool(normalized) and any(pattern.search(normalized) for pattern in patterns)


def is_generic_fallback_title(title):
    return matches_any_pattern(title, GENERIC_TITLE_PATTERNS)


def is_generic_fallback_summary(summary):
    return matches_any_pattern(summary, GENERIC_SUMMARY_PATTERNS)


def infer_source_label(source, url=""):
    normalized_source = normalize_whitespace(source)
    source_key = normalized_source.lower()

    if source_key in SOURCE_LABELS:
        return SOURCE_LABELS[source_key]

    if normalized_source:
        return normalized_source

    try:
        hostname = (urlparse(url).hostname or "").lower().removeprefix("www.")
    except ValueError:
        hostname = ""

    if not hostname:
        return ""

    if hostname in SOURCE_LABELS:
        return SOURCE_LABELS[hostname]

    primary = hostname.split(".")[0]
    if primary in SOURCE_LABELS:
        return SOURCE_LABELS[primary]

    label = " ".join(hostname.split(".")[:2]).strip()
    return label.title()


def infer_category(*parts):
    combined = " ".join(normalize_whitespace(part).lower() for part in parts if part)
    if not combined:
        return None

    for category, patterns in CATEGORY_PATTERNS:
        if any(pattern.search(combined) for pattern in patterns):
            return category

    return None


def infer_keyword_category(title, summary):
    combined = f"{normalize_whitespace(title).lower()} {normalize_whitespace(summary).lower()}"
    if "playoff" in combined or "stanley cup" in combined:
        return "playoffs"
    if "rumor" in combined or "rumour" in combined or "trade" in combined:
        return "rumors"
    if "recap" in combined:
        return "recap"
    if "ufa" in combined or "free agent" in combined:
        return "analysis"
    return None


def canonicalize_url(url):
    normalized_url = normalize_whitespace(url)
    if not normalized_url:
        return ""

    try:
        parsed = urlparse(normalized_url)
    except ValueError:
        return normalized_url

    host = (parsed.hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]

    path = parsed.path or ""
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")

    query_parts = []
    for key, value in parse_qsl(parsed.query, keep_blank_values=False):
        lowered_key = key.lower()
        if lowered_key in TRACKING_QUERY_KEYS:
            continue
        query_parts.append((key, value))

    query_parts.sort(key=lambda pair: (pair[0].lower(), pair[1]))
    normalized_query = urlencode(query_parts, doseq=True)

    return urlunparse((parsed.scheme.lower() or "https", host, path, "", normalized_query, ""))


def semantic_title_key(title):
    text = normalize_whitespace(title).lower()
    if not text:
        return ""

    cleaned = []
    previous_space = False
    for char in text:
        if char.isalnum():
            cleaned.append(char)
            previous_space = False
            continue
        if not previous_space:
            cleaned.append(" ")
            previous_space = True

    words = [word for word in "".join(cleaned).split(" ") if len(word) > 2]
    return " ".join(words[:10])


def _hostname(url):
    try:
        host = (urlparse(url).hostname or "").lower()
    except ValueError:
        return ""

    if host.startswith("www."):
        return host[4:]
    return host


def score_news_item(item):
    title = normalize_whitespace(item.get("title", "")).lower()
    summary = normalize_whitespace(item.get("summary") or item.get("description", "")).lower()
    url = item.get("url", "")
    host = _hostname(url)
    source = normalize_whitespace(item.get("source", "")).lower()

    score = 0
    reasons = []

    if host in TRUSTED_NEWS_DOMAINS:
        score += 3
        reasons.append("trusted_domain")
    elif source in SOURCE_LABELS:
        score += 1
        reasons.append("mapped_source")

    if "nhl" in title or "stanley cup" in title:
        score += 1
        reasons.append("relevant_title")

    if len(summary) >= 80:
        score += 1
        reasons.append("descriptive_summary")

    combined = f"{title} {summary}"
    if any(hint in combined for hint in LOW_VALUE_TITLE_HINTS):
        score -= 4
        reasons.append("promo_title")
    if any(hint in combined for hint in LOW_VALUE_SUMMARY_HINTS):
        score -= 3
        reasons.append("promo_summary")
    if "youtube.com" in host and "nhl media" not in source:
        score -= 2
        reasons.append("low_value_video")

    if is_noise_news_item(
        item.get("title", ""),
        item.get("summary") or item.get("description", ""),
        item.get("translatedTitle", ""),
        item.get("translatedSummary", ""),
        item.get("url", ""),
    ):
        score -= 6
        reasons.append("noise_pattern")

    return score, reasons


def rank_and_limit(items, limit, diagnostics=None, bucket_name="unknown"):
    enriched = []
    for item in items:
        score, reasons = score_news_item(item)
        if score < 0:
            if diagnostics is not None:
                diagnostics["low_quality_filtered"] += 1
            continue
        enriched.append((score, reasons, item))

    enriched.sort(
        key=lambda row: (
            row[0],
            len(normalize_whitespace(row[2].get("translatedSummary") or row[2].get("summary", ""))),
        ),
        reverse=True,
    )

    limited = [row[2] for row in enriched[:limit]]
    if diagnostics is not None:
        diagnostics[f"{bucket_name}_accepted"] += len(limited)
    return limited


def format_category_title(category, matched_date=None):
    date_label = format_finnish_date(matched_date) if matched_date else ""

    titles = {
        "rumors": "NHL:n huhukatsaus",
        "recap": "NHL:n kierroskatsaus",
        "morning-skate": "NHL:n aamukatsaus",
        "headlines": "NHL:n päivän puheenaiheet",
        "key-stories": "NHL:n viikon puheenaiheet",
        "playoffs": "NHL:n pudotuspeliseuranta",
        "analysis": "NHL-analyysi",
    }

    base_title = titles.get(category, "")
    if not base_title:
        return ""

    return f"{base_title} {date_label}".strip()


def format_category_summary(category):
    summaries = {
        "rumors": "Kooste päivän siirtohuhuista ja puheenaiheista NHL:ssä.",
        "recap": "Yhteenveto päivän NHL-otteluista ja käännekohdista.",
        "morning-skate": "Kooste päivän tärkeimmistä NHL-uutisista ja ottelunostoista.",
        "headlines": "Kooste päivän tärkeimmistä NHL-uutisista ja puheenaiheista.",
        "key-stories": "Kooste viikon tärkeimmistä NHL-uutisista ja puheenaiheista.",
        "playoffs": "Tilannekatsaus pudotuspeleihin ja sarjojen tärkeimpiin puheenaiheisiin.",
        "analysis": "Taustoittava katsaus päivän NHL-aiheeseen.",
    }
    return summaries.get(category, "")


def is_noise_news_item(title="", summary="", translated_title="", translated_summary="", url=""):
    title_text = normalize_whitespace(title)
    summary_text = normalize_whitespace(summary)
    translated_title_text = normalize_whitespace(translated_title)
    translated_summary_text = normalize_whitespace(translated_summary)
    combined_text = " ".join(
        text
        for text in [title_text, summary_text, translated_title_text, translated_summary_text]
        if text
    )

    if matches_any_pattern(combined_text, NOISE_TEXT_PATTERNS):
        return True

    if matches_any_pattern(title_text, NOISE_TITLE_PATTERNS):
        return True

    return matches_any_pattern(url, NOISE_URL_PATTERNS)


def build_fallback_title(item, matched_date):
    title = normalize_whitespace(item.get("title", ""))
    summary = normalize_whitespace(item.get("summary") or item.get("description", ""))
    translated_title = normalize_whitespace(item.get("translatedTitle", ""))
    translated_summary = normalize_whitespace(item.get("translatedSummary", ""))
    category = infer_category(title, summary, translated_title, translated_summary)
    if not category:
        category = infer_keyword_category(title, summary)

    if category:
        return format_category_title(category, matched_date)

    return title


def build_fallback_summary(item, matched_date):
    title = normalize_whitespace(item.get("title", ""))
    summary = normalize_whitespace(item.get("summary") or item.get("description", ""))
    translated_title = normalize_whitespace(item.get("translatedTitle", ""))
    translated_summary = normalize_whitespace(item.get("translatedSummary", ""))
    category = infer_category(title, summary, translated_title, translated_summary)
    if not category:
        category = infer_keyword_category(title, summary)

    if category:
        return format_category_summary(category)

    if summary:
        return truncate(summary)

    if title:
        return "Lyhyt nosto päivän NHL-aiheesta englanninkielisestä lähteestä."

    return ""


def normalize_news_entry(item, matched_date=None):
    if not isinstance(item, dict):
        return None

    title = normalize_whitespace(item.get("title", ""))
    summary = normalize_whitespace(item.get("summary") or item.get("description", ""))
    translated_title = normalize_whitespace(item.get("translatedTitle", ""))
    translated_summary = normalize_whitespace(item.get("translatedSummary", ""))
    url = item.get("url", "")
    source = infer_source_label(item.get("source", ""), url)
    effective_date = matched_date or item.get("matchedDate")

    if is_noise_news_item(title, summary, translated_title, translated_summary, url):
        return None

    normalized_title = (
        build_fallback_title(
            {
                "title": title,
                "summary": summary,
                "translatedTitle": translated_title,
                "translatedSummary": translated_summary,
            },
            effective_date,
        )
        if not translated_title or is_generic_fallback_title(translated_title)
        else translated_title
    )

    normalized_summary = (
        build_fallback_summary(
            {
                "title": title,
                "summary": summary,
                "translatedTitle": translated_title,
                "translatedSummary": translated_summary,
            },
            effective_date,
        )
        if not translated_summary or is_generic_fallback_summary(translated_summary)
        else translated_summary
    )

    if is_noise_news_item(normalized_title, normalized_summary, url=url):
        return None

    normalized_entry = {
        **item,
        "title": title,
        "summary": truncate(summary),
        "source": source,
        "url": url,
        "matchedDate": effective_date,
        "translatedTitle": normalize_whitespace(normalized_title),
        "translatedSummary": truncate(normalized_summary),
    }

    normalized_entry.pop("description", None)
    return normalized_entry


def translate_with_openai(item, matched_date):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        prompt = f"""
Translate this NHL news item into concise Finnish for a website fallback card.

Date: {matched_date}
Source: {item.get("source", "")}
Title: {item.get("title", "")}
Description: {item.get("summary") or item.get("description", "")}

Return strict JSON with keys:
- translatedTitle
- translatedSummary

Rules:
- Keep it short and natural Finnish.
- Do not invent details not present in the source text.
- If the source text is vague, say so briefly.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.2,
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}],
        )
        content = response.choices[0].message.content or ""
        parsed = json.loads(content)
        return {
            "translatedTitle": normalize_whitespace(parsed.get("translatedTitle", "")),
            "translatedSummary": normalize_whitespace(parsed.get("translatedSummary", "")),
        }
    except Exception:
        return None


def fetch_daily_news_tavily(date_str, daily_cache):
    if date_str in daily_cache:
        cached_items = [
            normalized
            for item in daily_cache[date_str]
            if (normalized := normalize_news_entry(item, date_str))
        ]
        if cached_items != daily_cache[date_str]:
            daily_cache[date_str] = cached_items
            save_daily_cache(daily_cache)
        return cached_items

    try:
        from tavily import TavilyClient

        tavily = TavilyClient()
        query = f"NHL news {date_str}"
        results = tavily.search(
            query=query,
            search_depth="basic",
            max_results=5,
            include_answer=False,
            include_raw_content=False,
        )

        items = []
        for result in results.get("results", [])[:3]:
            title = normalize_whitespace(result.get("title", ""))
            description = truncate(result.get("description", "") or result.get("content", ""))
            source = infer_source_label(result.get("source", ""), result.get("url", ""))
            url = result.get("url", "")

            if not title and not description:
                continue

            normalized_item = normalize_news_entry(
                {
                    "title": title,
                    "summary": description,
                    "source": source,
                    "url": url,
                    "matchedDate": date_str,
                    "translatedTitle": build_fallback_title(result, date_str),
                    "translatedSummary": build_fallback_summary(
                        {"source": source, "title": title, "description": description},
                        date_str,
                    ),
                },
                date_str,
            )
            if normalized_item:
                items.append(normalized_item)

        daily_cache[date_str] = items
        save_daily_cache(daily_cache)
        return items
    except Exception:
        return daily_cache.get(date_str, [])


def enumerate_dates(start_date=None, end_date=None):
    if not start_date and not end_date:
        return []

    start = datetime.strptime(start_date or end_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date or start_date, "%Y-%m-%d").date()
    if end < start:
        start, end = end, start

    current = start
    dates = []
    while current <= end:
        dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)
    return dates


def build_news_index(cache, explicit_daily_cache=None):
    by_date = defaultdict(list)
    by_week = defaultdict(list)
    translation_cache = {}
    diagnostics = {
        "total_candidates": 0,
        "noise_filtered": 0,
        "low_quality_filtered": 0,
        "date_deduped": 0,
        "week_deduped": 0,
        "by_date_accepted": 0,
        "by_week_accepted": 0,
    }

    for week_key, items in cache.items():
        if not isinstance(items, list):
            continue

        for item in items:
            if not isinstance(item, dict):
                continue
            diagnostics["total_candidates"] += 1

            if is_noise_news_item(
                item.get("title", ""),
                item.get("summary") or item.get("description", ""),
                url=item.get("url", ""),
            ):
                diagnostics["noise_filtered"] += 1
                continue

            matched_dates = extract_dates(
                item.get("title", ""), item.get("description", ""), item.get("url", "")
            )

            effective_week_key = week_key

            if not matched_dates:
                matched_dates = []

            base_entry = {
                "title": normalize_whitespace(item.get("title", "")),
                "summary": truncate(item.get("summary") or item.get("description", "")),
                "source": infer_source_label(item.get("source", ""), item.get("url", "")),
                "url": item.get("url", ""),
                "weekKey": effective_week_key,
            }

            if matched_dates:
                for matched_date in matched_dates:
                    translation_key = f"{matched_date}|{base_entry['url']}|{base_entry['title']}"
                    translated = translation_cache.get(translation_key)
                    if translated is None:
                        translated = translate_with_openai(item, matched_date) or {}
                        translation_cache[translation_key] = translated

                    entry = {
                        **base_entry,
                        "matchedDate": matched_date,
                        "translatedTitle": translated.get("translatedTitle")
                        or build_fallback_title(item, matched_date),
                        "translatedSummary": translated.get("translatedSummary")
                        or build_fallback_summary(item, matched_date),
                    }
                    normalized_entry = normalize_news_entry(entry, matched_date)
                    if normalized_entry:
                        by_date[matched_date].append(normalized_entry)

            week_fallback_date = matched_dates[0] if matched_dates else None
            week_entry = {
                **base_entry,
                "matchedDate": week_fallback_date,
                "translatedTitle": build_fallback_title(item, week_fallback_date or week_key[:4] + "-01-01")
                if week_fallback_date
                else normalize_whitespace(item.get("title", "")),
                "translatedSummary": build_fallback_summary(item, week_fallback_date)
                if week_fallback_date
                else (
                    base_entry["summary"]
                    or "Kooste viikon NHL-aiheisesta jutusta englanniksi."
                ),
            }
            normalized_week_entry = normalize_news_entry(week_entry, week_fallback_date)
            if normalized_week_entry:
                by_week[effective_week_key].append(normalized_week_entry)

    if explicit_daily_cache:
        for matched_date, items in explicit_daily_cache.items():
            if not isinstance(items, list):
                continue
            normalized_items = [
                normalized
                for item in items
                if (normalized := normalize_news_entry(item, matched_date))
            ]
            by_date[matched_date] = normalized_items + by_date[matched_date]

    def dedupe(items, bucket_name):
        seen = set()
        result = []
        for item in items:
            url_key = canonicalize_url(item.get("url", ""))
            title_key = semantic_title_key(item.get("translatedTitle") or item.get("title", ""))
            key = url_key or title_key or item.get("url") or item.get("title")
            if key in seen:
                if bucket_name == "date":
                    diagnostics["date_deduped"] += 1
                else:
                    diagnostics["week_deduped"] += 1
                continue
            seen.add(key)
            result.append(item)
        return result

    ranked_by_date = {}
    for key, value in sorted(by_date.items()):
        deduped = dedupe(value, "date")
        ranked_by_date[key] = rank_and_limit(deduped, 3, diagnostics, "by_date")

    ranked_by_week = {}
    for key, value in sorted(by_week.items()):
        deduped = dedupe(value, "week")
        ranked_by_week[key] = rank_and_limit(deduped, 5, diagnostics, "by_week")

    return {
        "byDate": ranked_by_date,
        "byWeek": ranked_by_week,
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
            "+00:00", "Z"
        ),
        "_diagnostics": diagnostics,
    }


def main():
    start_date = sys.argv[1] if len(sys.argv) > 1 else None
    end_date = sys.argv[2] if len(sys.argv) > 2 else start_date

    cache = load_cache()
    daily_cache = load_daily_cache()

    requested_dates = enumerate_dates(start_date, end_date)
    fetched_daily = {}

    for date_str in requested_dates:
        items = fetch_daily_news_tavily(date_str, daily_cache)
        if items:
            fetched_daily[date_str] = items

    index = build_news_index(cache, fetched_daily)
    OUTPUT_FILE.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT_FILE}")
    print(f"Daily dates: {len(index['byDate'])}")
    print(f"Weeks: {len(index['byWeek'])}")
    diagnostics = index.get("_diagnostics", {})
    if diagnostics:
        print(
            "Quality diagnostics: "
            f"candidates={diagnostics.get('total_candidates', 0)}, "
            f"noise_filtered={diagnostics.get('noise_filtered', 0)}, "
            f"low_quality_filtered={diagnostics.get('low_quality_filtered', 0)}, "
            f"date_deduped={diagnostics.get('date_deduped', 0)}, "
            f"week_deduped={diagnostics.get('week_deduped', 0)}, "
            f"accepted_date={diagnostics.get('by_date_accepted', 0)}, "
            f"accepted_week={diagnostics.get('by_week_accepted', 0)}"
        )


if __name__ == "__main__":
    main()
