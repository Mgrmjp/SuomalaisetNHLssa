import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

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


def build_fallback_title(item, matched_date):
    title = normalize_whitespace(item.get("title", ""))
    source = normalize_whitespace(item.get("source", "NHL-lähde"))
    date_label = format_finnish_date(matched_date)
    lower_title = title.lower()

    if "morning skate" in lower_title:
        return f"NHL:n aamukatsaus {date_label}"
    if "morning recap" in lower_title:
        return f"NHL:n aamuyhteenveto {date_label}"
    if "scores" in lower_title:
        return f"NHL-tulokset {date_label}"
    if "buzz" in lower_title:
        return f"NHL:n päivän puheenaiheet {date_label}"
    if "roundup" in lower_title or "recap" in lower_title:
        return f"NHL:n kierroskatsaus {date_label}"

    return f"{source} julkaisi NHL-uutisen {date_label}"


def build_fallback_summary(item, matched_date):
    title = normalize_whitespace(item.get("title", ""))
    description = truncate(item.get("description", ""))
    source = normalize_whitespace(item.get("source", "NHL-lähde"))
    date_label = format_finnish_date(matched_date)

    if description:
        return (
            f"{source} julkaisi {date_label} NHL-aiheisen jutun. "
            f"Alkuperäinen kuvaus: {description}"
        )

    if title:
        return (
            f"{source} julkaisi {date_label} NHL-aiheisen jutun. "
            f"Alkuperäinen otsikko: {title}"
        )

    return f"{source} julkaisi {date_label} NHL-aiheisen jutun englanniksi."


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
Description: {item.get("description", "")}

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
        return daily_cache[date_str]

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
            source = normalize_whitespace(result.get("source", ""))
            url = result.get("url", "")

            if not title and not description:
                continue

            items.append(
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
                }
            )

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

    for week_key, items in cache.items():
        if not isinstance(items, list):
            continue

        for item in items:
            if not isinstance(item, dict):
                continue

            matched_dates = extract_dates(
                item.get("title", ""), item.get("description", ""), item.get("url", "")
            )

            effective_week_key = week_key

            if not matched_dates:
                matched_dates = []

            base_entry = {
                "title": normalize_whitespace(item.get("title", "")),
                "summary": truncate(item.get("description", "")),
                "source": normalize_whitespace(item.get("source", "")),
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
                    by_date[matched_date].append(entry)

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
                    f"{base_entry['source'] or 'NHL-lähde'} julkaisi tällä viikolla NHL-aiheisen jutun. "
                    f"{base_entry['summary'] or base_entry['title']}"
                ),
            }
            by_week[effective_week_key].append(week_entry)

    if explicit_daily_cache:
        for matched_date, items in explicit_daily_cache.items():
            if not isinstance(items, list):
                continue
            by_date[matched_date] = items + by_date[matched_date]

    def dedupe(items):
        seen = set()
        result = []
        for item in items:
            key = item.get("url") or item.get("title")
            if key in seen:
                continue
            seen.add(key)
            result.append(item)
        return result

    return {
        "byDate": {key: dedupe(value) for key, value in sorted(by_date.items())},
        "byWeek": {key: dedupe(value) for key, value in sorted(by_week.items())},
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
            "+00:00", "Z"
        ),
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


if __name__ == "__main__":
    main()
