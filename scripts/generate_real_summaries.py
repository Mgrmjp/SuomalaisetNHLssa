import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
import subprocess
import random

DATA_DIR = "static/data/prepopulated/games"
OUTPUT_FILE = "static/data/articles.json"
CONTENT_DIR = "content/articles"

TAVILY_CACHE_FILE = "static/data/tavily_news_cache.json"


def get_iso_week(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    year, week, day = dt.isocalendar()
    return year, week


def load_tavily_cache():
    """Load cached Tavily news results"""
    if os.path.exists(TAVILY_CACHE_FILE):
        try:
            with open(TAVILY_CACHE_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_tavily_cache(cache):
    """Save Tavily news cache"""
    with open(TAVILY_CACHE_FILE, "w") as f:
        json.dump(cache, f, ensure_ascii=False)


def fetch_nhl_news_tavily(year, week, week_start, week_end):
    """Fetch real NHL news from Tavily API for a specific week"""
    cache = load_tavily_cache()
    cache_key = f"{year}-W{week:02d}"

    # Return cached results if available
    if cache_key in cache:
        print(f"  Using cached Tavily news for {cache_key}")
        return cache[cache_key]

    try:
        from tavily import TavilyClient

        tavily = TavilyClient()

        # Format date range for the query
        start_str = week_start.strftime("%Y-%m-%d")
        end_str = week_end.strftime("%Y-%m-%d")

        # Search for NHL news from this week
        query = f"NHL hockey news {start_str} to {end_str}"

        results = tavily.search(
            query=query,
            search_depth="basic",
            max_results=5,
            include_answer=True,
            include_raw_content=False,
        )

        news_items = []
        for result in results.get("results", [])[:3]:
            # Clean up the description
            description = result.get("description", "") or result.get("content", "")
            if len(description) > 300:
                description = description[:300] + "..."

            # Extract source from URL domain
            url = result.get("url", "")
            source = result.get("source") or "Unknown"
            if source == "Unknown" and url:
                from urllib.parse import urlparse

                domain = urlparse(url).netloc
                # Clean up common prefixes
                source = domain.replace("www.", "").split(".")[0].capitalize()

            news_items.append(
                {
                    "title": result.get("title", ""),
                    "description": description,
                    "source": source,
                    "url": url,
                }
            )

        # Cache the results
        cache[cache_key] = news_items
        save_tavily_cache(cache)
        print(f"  Fetched {len(news_items)} Tavily news items for {cache_key}")
        return news_items

    except Exception as e:
        print(f"  Error fetching Tavily news for {cache_key}: {e}")
        return []


def fetch_weekly_news(year, week, week_start, week_end, players, games):
    """Generate dynamic news highlights based on weekly statistics"""
    news_items = []

    # 1. Highlight Top Scorer
    skaters = {
        name: stats for name, stats in players.items() if stats.get("position") != "G"
    }
    sorted_players = sorted(
        skaters.items(), key=lambda x: (x[1]["points"], x[1]["goals"]), reverse=True
    )

    if sorted_players:
        top_name, top_stats = sorted_players[0]
        points = top_stats["points"]
        goals = top_stats["goals"]
        assists = top_stats["assists"]

        title = f"{top_name} viikon tehokkain suomalainen"
        desc = (
            f"{top_name} johti suomalaisrintamaa tehoilla {goals}+{assists}={points}."
        )

        # Check for multi-point games
        player_games = [g for g in games if g["name"] == top_name]
        big_games = [g for g in player_games if g.get("points", 0) >= 3]
        if big_games:
            g = big_games[0]
            desc += f" Hän loisti erityisesti ottelussa {g.get('opponent', '???')} vastaan iskemällä tehot {g.get('goals')}+{g.get('assists')}."

        news_items.append(
            {
                "title": title,
                "description": desc,
                "source": "NHL Tilastot",
                "url": "https://www.nhl.com/stats/skaters",
            }
        )

    # 2. Goalie Shutouts or Big Wins
    goalies = {
        name: stats for name, stats in players.items() if stats.get("position") == "G"
    }
    for name, stats in goalies.items():
        player_games = [g for g in games if g["name"] == name]
        for g in player_games:
            if g.get("saves", 0) > 0:
                is_shutout = (g.get("shots_against", 0) == g.get("saves", 0)) and (
                    g.get("shots_against", 0) > 10
                )
                if is_shutout:
                    news_items.append(
                        {
                            "title": f"Nollapeli: {name}",
                            "description": f"{name} torjui kaikki {g.get('saves')} laukausta ottelussa {g.get('opponent', '?')} vastaan ja piti maalinsa puhtaana.",
                            "source": "NHL Tilastot",
                        }
                    )
                elif g.get("saves", 0) >= 40:
                    news_items.append(
                        {
                            "title": f"Muuri: {name}",
                            "description": f"{name} urakoi maalinsuulla ja pysäytti peräti {g.get('saves')} kiekkoa ottelussa {g.get('opponent', '?')} vastaan.",
                            "source": "NHL Tilastot",
                        }
                    )

    # 3. Hat Tricks
    for name, stats in skaters.items():
        player_games = [g for g in games if g["name"] == name]
        for g in player_games:
            if g.get("goals", 0) >= 3:
                news_items.append(
                    {
                        "title": f"Hattutemppu: {name}",
                        "description": f"{name} iski kolme maalia ottelussa {g.get('opponent', '?')} vastaan.",
                        "source": "NHL Tilastot",
                    }
                )

    # 4. Fetch real NHL news from Tavily (limit to 1-2 items)
    tavily_news = fetch_nhl_news_tavily(year, week, week_start, week_end)
    for tavily_item in tavily_news[:2]:
        news_items.append(tavily_item)

    # Fallback if no specific highlights
    if not news_items:
        news_items.append(
            {
                "title": "Tasainen viikko suomalaisittain",
                "description": f"Viikolla {week} nähtiin tasaisia suorituksia, mutta ei yksittäisiä superonnistumisia.",
                "source": "NHL Tilastot",
            }
        )

    return news_items[:4]  # Limit to top 4 news items (stats-based + 1-2 from Tavily)


def load_game_data():
    all_game_performances = []
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".json"):
            try:
                date_str = filename.replace(".json", "")
                datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                continue

            filepath = os.path.join(DATA_DIR, filename)
            with open(filepath, "r") as f:
                try:
                    day_data = json.load(f)
                    if "players" in day_data:
                        for p in day_data["players"]:
                            if "date" not in p:
                                p["date"] = day_data.get("date", date_str)
                            all_game_performances.append(p)
                except json.JSONDecodeError:
                    print(f"Error decoding {filename}")
                    continue

    return all_game_performances


def format_date_finnish(date_str):
    """Format date to Finnish format: 12. tammikuuta 2026"""
    months = [
        "tammikuuta",
        "helmikuuta",
        "maaliskuuta",
        "huhtikuuta",
        "toukokuuta",
        "kesäkuuta",
        "heinäkuuta",
        "elokuuta",
        "syyskuuta",
        "lokakuuta",
        "marraskuuta",
        "joulukuuta",
    ]
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return f"{dt.day}. {months[dt.month - 1]} {dt.year}"


def generate_creative_title(week, year, top_player_name):
    """Generate a more engaging title for the article"""
    # More creative, less formulaic templates
    if top_player_name == "Suomalaiset":
        templates = [
            f"Suomalaisia NHL-tähtiä vauhdissa viikolla {week}",
            f"NHL-viikko {week}: suomalaista voimaa",
            f"Viikko {week}: suomalaispelaajat iskivät",
            f"Leijonat maalittelevät viikolla {week}",
            f"Suomalaisrondo NHL:ssä – viikko {week}",
        ]
    else:
        templates = [
            f"{top_player_name} sytytti suomalaiset viikolla {week}",
            f"Leijonan kynnet: {top_player_name} iski viikolla {week}",
            f"Suomalaisodottaja {top_player_name} rääväisi viikolla {week}",
            f"{top_player_name} johti suomalaiset voittoon viikolla {week}",
            f"NHL-viikko {week}: {top_player_name} ykkönen",
            f"Viikon {week} suomalähti: {top_player_name}",
            f"Suomalaisten tähti {top_player_name} loisti NHL:ssä",
            f"{top_player_name} näytti tietä viikolla {week}",
            f"Leijonat kulkevat – {top_player_name} edellä viikolla {week}",
            f"Viikko {week}: {top_player_name} nostaa tasoa",
            f"{top_player_name} takoi suomalaisille voitot viikolla {week}",
            f"Suomalaisvoittoja – {top_player_name} kärjessä",
            f"{top_player_name} hurjasteli viikolla {week}",
        ]

    # Use week as seed to keep title stable for the same week across regenerations
    random.seed(f"{year}-{week}")
    return random.choice(templates)


def generate_articles(all_games):
    weeks_data = defaultdict(
        lambda: {
            "games": [],
            "players": defaultdict(
                lambda: {
                    "goals": 0,
                    "assists": 0,
                    "points": 0,
                    "games": 0,
                    "teams": set(),
                    "position": "F",
                    "player_id": None,
                }
            ),
        }
    )

    for record in all_games:
        year, week = get_iso_week(record["date"])
        key = (year, week)

        p_stats = weeks_data[key]["players"][record["name"]]
        p_stats["goals"] += record.get("goals", 0)
        p_stats["assists"] += record.get("assists", 0)
        p_stats["points"] += record.get("points", 0)
        p_stats["games"] += 1
        p_stats["teams"].add(record.get("team", "???"))
        if "position" in record:
            p_stats["position"] = record["position"]
        if "playerId" in record:
            p_stats["player_id"] = record["playerId"]

        weeks_data[key]["games"].append(record)

    articles = []
    sorted_weeks = sorted(weeks_data.keys())

    today = datetime.now()
    for year, week in sorted_weeks:
        # Calculate week date range
        try:
            week_start = datetime.fromisocalendar(year, week, 1)
            week_end = datetime.fromisocalendar(year, week, 7)
        except AttributeError:
            # Fallback for older Python versions
            week_start = datetime.strptime(f"{year}-W{week}-1", "%Y-W%W-%w")
            week_end = week_start + timedelta(days=6)

        # Skip weeks that are still in progress
        if week_end > today:
            print(f"Skipping Week {week}/{year} as it is still ongoing.")
            continue

        week_info = weeks_data[(year, week)]
        players = week_info["players"]

        total_goals = sum(p["goals"] for p in players.values())
        total_assists = sum(p["assists"] for p in players.values())
        total_points = sum(p["points"] for p in players.values())
        player_count = len(players)

        # Skaters only for scoring stats
        skaters = {
            name: stats
            for name, stats in players.items()
            if stats.get("position") != "G"
        }
        sorted_players = sorted(
            skaters.items(), key=lambda x: (x[1]["points"], x[1]["goals"]), reverse=True
        )
        top_scorers = sorted_players[:5]

        # Defenders
        defenders = {
            name: stats
            for name, stats in players.items()
            if stats.get("position") == "D"
        }
        sorted_defenders = sorted(
            defenders.items(),
            key=lambda x: (x[1]["points"], x[1]["goals"]),
            reverse=True,
        )

        # Goalies
        goalies = {
            name: stats
            for name, stats in players.items()
            if stats.get("position") == "G"
        }

        date_range = f"{week_start.strftime('%d.%m.')}–{week_end.strftime('%d.%m.%Y')}"

        # Get featured player (top scorer) info
        featured_player_id = None
        top_player_name = "Suomalaiset"
        if top_scorers:
            featured_player_id = top_scorers[0][1].get("player_id")
            top_player_name = top_scorers[0][0]

        # Fetch weekly news
        weekly_news = fetch_weekly_news(
            year, week, week_start, week_end, players, week_info["games"]
        )

        # Build Markdown content
        md = []

        # Opening paragraph
        md.append(
            f"Viikko {week} ({date_range}) oli jälleen aktiivinen suomalaispelaajille NHL:ssä. Yhteensä **{player_count} suomalaista** pääsi jäälle tällä viikolla. Suomalaiset iskivät **{total_goals} maalia** ja keräsivät yhteensä **{total_points} tehopistettä**."
        )
        md.append("")

        # News section
        if weekly_news:
            md.append("## Viikon uutiset")
            md.append("")
            for news in weekly_news:
                md.append(f"### {news['title']}")
                md.append(f"{news['description']}")
                if "source" in news:
                    if "url" in news:
                        md.append(f"*Lähde: [{news['source']}]({news['url']})*")
                    else:
                        md.append(f"*Lähde: {news['source']}*")
                md.append("")

        # Top scorer highlight
        if top_scorers:
            best = top_scorers[0]
            best_name = best[0]
            best_stats = best[1]
            md.append(f"## Viikon tehokkain: {best_name}")
            md.append("")

            # Get best player's individual games
            best_games = [g for g in week_info["games"] if g["name"] == best_name]
            game_details = []
            for g in best_games:
                if g.get("points", 0) > 0:
                    game_details.append(
                        f"{g['opponent']} ({g['goals']}+{g['assists']})"
                    )

            md.append(
                f"**{best_name}** ({', '.join(best_stats['teams'])}) nousi viikon tehokkaimmaksi suomalaiseksi tehoilla **{best_stats['goals']}+{best_stats['assists']}={best_stats['points']}**. Hän pelasi {best_stats['games']} ottelua viikon aikana."
            )
            if game_details:
                md.append(f"- Ottelukohtaiset pisteet: {', '.join(game_details)}")
            md.append("")

        # Notable performances (hat tricks, 4+ point games)
        notable_games = []
        for name, stats in players.items():
            player_daily = [g for g in week_info["games"] if g["name"] == name]
            for g in player_daily:
                if g["goals"] >= 3:
                    game_date = format_date_finnish(g["game_date"])
                    notable_games.append(
                        f"- **{name}** iski hattutempun ({g['goals']} maalia) ottelussa {g['opponent_full']} vastaan ({game_date}). Ottelu päättyi {g['game_score']}."
                    )
                elif g["points"] >= 4:
                    game_date = format_date_finnish(g["game_date"])
                    notable_games.append(
                        f"- **{name}** keräsi neljä tehopistettä ({g['goals']}+{g['assists']}) ottelussa {g['opponent_full']} vastaan ({game_date})."
                    )
                elif (
                    g.get("save_percentage", 0) == 1.0
                    and g.get("saves", 0) > 10
                    and g.get("position") == "G"
                ):
                    game_date = format_date_finnish(g["game_date"])
                    notable_games.append(
                        f"- Maalivahti **{name}** pelasi nollapelin ({g['saves']} torjuntaa) ottelussa {g['opponent_full']} vastaan ({game_date})."
                    )

        if notable_games:
            md.append("## Viikon erikoissuoritukset")
            md.append("")
            md.extend(notable_games)
            md.append("")

        # Top scorers table
        md.append("## Viikon pistepörssi")
        md.append("")
        md.append("| Sija | Pelaaja | Joukkue | Ottelut | Maalit | Syötöt | Pisteet |")
        md.append("|------|---------|---------|---------|--------|--------|---------|")
        for i, (name, stats) in enumerate(top_scorers, 1):
            team = ", ".join(stats["teams"])
            md.append(
                f"| {i}. | {name} | {team} | {stats['games']} | {stats['goals']} | {stats['assists']} | **{stats['points']}** |"
            )
        md.append("")

        # Defenders section
        if sorted_defenders and sorted_defenders[0][1]["points"] >= 1:
            md.append("## Puolustajat")
            md.append("")
            top_d = sorted_defenders[:3]
            for name, stats in top_d:
                if stats["points"] >= 1:
                    team = ", ".join(stats["teams"])
                    md.append(
                        f"- **{name}** ({team}): {stats['goals']}+{stats['assists']}={stats['points']} ({stats['games']} ottelua)"
                    )
            md.append("")

        # Goalies section
        goalie_stats = []
        for name, stats in goalies.items():
            all_records = [g for g in week_info["games"] if g["name"] == name]
            g_daily = [
                g for g in all_records if g.get("time_on_ice", "00:00") != "00:00"
            ]

            if not g_daily:
                continue

            wins = sum(1 for g in g_daily if g.get("game_result") == "W")
            starts = len(g_daily)
            total_saves = sum(g.get("saves", 0) for g in g_daily)
            total_shots = sum(g.get("shots_against", 0) for g in g_daily)
            avg_sv = (total_saves / total_shots * 100) if total_shots > 0 else 0

            goalie_stats.append(
                {
                    "name": name,
                    "team": ", ".join(stats["teams"]),
                    "starts": starts,
                    "wins": wins,
                    "saves": total_saves,
                    "sv_pct": avg_sv,
                }
            )

        if goalie_stats:
            md.append("## Maalivahdit")
            md.append("")
            md.append("| Maalivahti | Joukkue | Ottelut | Voitot | Torjunnat |")
            md.append("|------------|---------|---------|--------|-----------|")
            for g in sorted(goalie_stats, key=lambda x: x["wins"], reverse=True):
                md.append(
                    f"| {g['name']} | {g['team']} | {g['starts']} | {g['wins']} | {g['saves']} |"
                )
            md.append("")

        # Upcoming games
        try:
            d_next = week_start + timedelta(days=7)
            next_year, next_week, _ = d_next.isocalendar()

            if (next_year, next_week) in weeks_data:
                next_week_info = weeks_data[(next_year, next_week)]
                game_finns = defaultdict(list)
                for g in next_week_info["games"]:
                    game_finns[g["game_id"]].append(g)

                interesting_games = sorted(
                    game_finns.items(), key=lambda x: len(x[1]), reverse=True
                )[:3]

                if interesting_games:
                    md.append("## Ensi viikon mielenkiintoisimmat ottelut")
                    md.append("")
                    for gid, game_players in interesting_games:
                        g = game_players[0]
                        finn_count = len(game_players)
                        date_obj = datetime.strptime(g["game_date"], "%Y-%m-%d")
                        date_fmt = date_obj.strftime("%d.%m.")
                        player_names = [p["name"] for p in game_players[:4]]
                        players_str = ", ".join(player_names)
                        if len(game_players) > 4:
                            players_str += f" (+{len(game_players) - 4} muuta)"
                        md.append(
                            f"- **{date_fmt} {g['team_full']} vs {g['opponent_full']}**: {finn_count} suomalaista ({players_str})"
                        )
                    md.append("")
        except Exception as e:
            print(f"Error calculating upcoming games: {e}")

        # Closing
        md.append("---")
        md.append("")
        md.append(f"*Tilastot kattavat viikon {week}/{year} NHL-ottelut.*")

        content = "\n".join(md)

        date_str = week_start.strftime("%Y-%m-%d")
        title = generate_creative_title(week, year, top_player_name)
        excerpt = f"{player_count} suomalaista pelasi, {total_goals} maalia, {total_points} pistettä."
        if top_scorers:
            excerpt = (
                f"{top_scorers[0][0]} johti suomalaisrintamaa {top_scorers[0][1]['points']} pisteellä. "
                + excerpt
            )

        article = {
            "slug": f"{year}-w{week:02d}",
            "title": title,
            "date": date_str,
            "week": week,
            "year": year,
            "excerpt": excerpt,
            "content": content,
        }

        # Add featured player if available
        if featured_player_id:
            article["featured_player_id"] = featured_player_id

        articles.append(article)

    articles.sort(key=lambda x: (x["year"], x["week"]), reverse=True)

    # Write JSON articles
    with open(OUTPUT_FILE, "w") as f:
        json.dump(articles, f, indent=4, ensure_ascii=False)

    # Also write markdown files to content directory
    os.makedirs(CONTENT_DIR, exist_ok=True)
    for article in articles:
        slug = article["slug"]
        md_content = f"""---
title: {article["title"]}
date: {article["date"]}
week: {article["week"]}
year: {article["year"]}
excerpt: {article["excerpt"]}
slug: {article["slug"]}
{f"featured_player_id: {article['featured_player_id']}" if "featured_player_id" in article else ""}
---

{article["content"]}
"""
        md_path = os.path.join(CONTENT_DIR, f"{slug}.md")
        with open(md_path, "w") as f:
            f.write(md_content)


if __name__ == "__main__":
    games = load_game_data()
    generate_articles(games)
    print(f"Generated articles based on {len(games)} game records.")
