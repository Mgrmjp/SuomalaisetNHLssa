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

# NHL team abbreviation to Finnish name mapping
TEAM_NAMES_FI = {
    "ANA": "Anaheim", "ARI": "Arizona", "BOS": "Boston", "BUF": "Buffalo",
    "CGY": "Calgary", "CAR": "Carolina", "CHI": "Chicago", "COL": "Colorado",
    "CBJ": "Columbus", "DAL": "Dallas", "DET": "Detroit", "EDM": "Edmonton",
    "FLA": "Florida", "LAK": "Los Angeles", "MIN": "Minnesota", "MTL": "Montreal",
    "NJD": "New Jersey", "NYI": "NY Islanders", "NYR": "NY Rangers",
    "NSH": "Nashville", "OTT": "Ottawa", "PHI": "Philadelphia", "PIT": "Pittsburgh",
    "SJS": "San Jose", "SEA": "Seattle", "STL": "St. Louis", "TBL": "Tampa Bay",
    "TOR": "Toronto", "VAN": "Vancouver", "VGK": "Vegas", "WSH": "Washington",
    "WPG": "Winnipeg", "UTA": "Utah", "NHL": "NHL",
}


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

        title = f"{top_name} viikon paras pistemies"
        desc = (
            f"{top_name} keräsi viikon parhaat tehopisteet lukemin {goals}+{assists}={points}."
        )

        # Check for multi-point games
        player_games = [g for g in games if g["name"] == top_name]
        big_games = [g for g in player_games if g.get("points", 0) >= 3]
        if big_games:
            g = big_games[0]
            opp = TEAM_NAMES_FI.get(g.get("opponent", "?"), g.get("opponent", "?"))
            desc += f" Parhaassa ottelussa {opp}a vastaan syntyi tehot {g.get('goals')}+{g.get('assists')}."

        news_items.append(
            {
                "title": title,
                "description": desc,
                "source": "NHL-tilastot",
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
                    opp = TEAM_NAMES_FI.get(g.get("opponent", "?"), g.get("opponent", "?"))
                    news_items.append(
                        {
                            "title": f"{name} torjui nollapelin",
                            "description": f"{name} piti maalinsa puhtaana {opp}a vastaan. Torjuntoja kertyi {g.get('saves')}.",
                            "source": "NHL-tilastot",
                        }
                    )
                elif g.get("saves", 0) >= 40:
                    opp = TEAM_NAMES_FI.get(g.get("opponent", "?"), g.get("opponent", "?"))
                    news_items.append(
                        {
                            "title": f"{name} venyi suurtorjuntaan",
                            "description": f"{name} torjui peräti {g.get('saves')} kertaa {opp}a vastaan.",
                            "source": "NHL-tilastot",
                        }
                    )

    # 3. Hat Tricks
    for name, stats in skaters.items():
        player_games = [g for g in games if g["name"] == name]
        for g in player_games:
            if g.get("goals", 0) >= 3:
                opp = TEAM_NAMES_FI.get(g.get("opponent", "?"), g.get("opponent", "?"))
                news_items.append(
                    {
                        "title": f"Hattutemppu: {name}",
                        "description": f"{name} teki kolme maalia {opp}a vastaan.",
                        "source": "NHL-tilastot",
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
                "description": f"Viikolla {week} nähtiin tasaisia esityksiä suomalaisilta, mutta ei yksittäisiä kohokohtia.",
                "source": "NHL-tilastot",
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


def generate_creative_title(week, year, top_player_name, top_points, has_hat_trick=False, has_shutout=False):
    """Generate an engaging title in natural Finnish sports journalism style"""
    random.seed(f"{year}-{week}")

    if top_player_name == "Suomalaiset":
        templates = [
            f"Suomalaispelaajat NHL:ssä: viikon {week} yhteenveto",
            f"NHL-viikko {week}: suomalaisten katsaus",
            f"Viikko {week}: suomalaispelaajien kierros",
            f"Suomalaisittain tasainen NHL-viikko {week}",
            f"Leijona-pelaajat NHL:ssä – viikko {week}",
        ]
    elif has_hat_trick:
        templates = [
            f"{top_player_name} iski hattutempun – viikon {week} suomalaiskatsaus",
            f"Hattutemppuviikko: {top_player_name} juhli NHL:ssä",
            f"{top_player_name} kolmen maalin ilta – NHL-viikko {week}",
        ]
    elif top_points >= 5:
        templates = [
            f"{top_player_name} loisti tehopisteillä {top_points} – viikko {week}",
            f"{top_player_name} repi {top_points} tehopistettä – NHL-viikko {week}",
            f"{top_player_name} ylivoimainen ykkönen viikolla {week} – {top_points} pistettä",
            f"Tehoviikko: {top_player_name} keräsi {top_points} pistettä",
        ]
    elif top_points >= 3:
        templates = [
            f"{top_player_name} viikon tehokkain suomalaisessa NHL:ssä",
            f"{top_player_name} johti suomalaisia viikolla {week}",
            f"Viikon {week} suomalainen: {top_player_name}",
            f"{top_player_name} nousi viikon tehomieheksi",
            f"{top_player_name} näytti osaamistaan viikolla {week}",
            f"{top_player_name} paras suomalainen viikolla {week}",
            f"Viikko {week}: {top_player_name} suomalaiskärjessä",
        ]
    else:
        templates = [
            f"Viikko {week}: suomalaisten NHL-katsaus",
            f"NHL-viikko {week}: suomalaispelaajat yhdessä",
            f"Suomalaiset NHL:ssä – viikon {week} katsaus",
            f"Viikon {week} suomalaiset NHL-jäillä",
            f"{top_player_name} paras suomalainen viikolla {week}",
        ]

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

        # Opening paragraph - varied based on performance level
        if total_points >= 25:
            openings = [
                f"Viikko {week} ({date_range}) oli tehokas suomalaisille NHL:ssä. Kaikkiaan **{player_count} suomalaista** pelasi, ja yhteispisteiksi tuli **{total_points} ({total_goals}+{total_assists})**.",
                f"Suomalaisittain pistejuhlaa viikolla {week} ({date_range}): **{player_count} pelaajaa** keräsi yhteensä **{total_points} tehopistettä**, joista **{total_goals}** maaleja.",
            ]
        elif total_points >= 15:
            openings = [
                f"Viikolla {week} ({date_range}) nähtiin **{player_count} suomalaista** NHL-jäällä. Kokonaispisteiksi kirjattiin **{total_points} ({total_goals}+{total_assists})**.",
                f"**{player_count} suomalaista** pelasi viikolla {week} ({date_range}). Yhteispisteet **{total_points}**, maaleja syntyi **{total_goals}**.",
            ]
        else:
            openings = [
                f"Viikko {week} ({date_range}) toi **{player_count} suomalaiselle** peliaikaa NHL:ssä. Maaleja kirjattiin **{total_goals}**, pisteitä yhteensä **{total_points}**.",
                f"**{player_count} suomalaista** NHL-kaukaloissa viikolla {week} ({date_range}). Kokonaissaldoksi jäi **{total_points} tehopistettä** ja **{total_goals} maalia**.",
            ]
        random.seed(f"opening-{year}-{week}")
        md.append(random.choice(openings))
        md.append("")

        # Top scorer highlight (replaces news section for the top player)
        if top_scorers:
            best = top_scorers[0]
            best_name = best[0]
            best_stats = best[1]
            md.append(f"## Viikon paras pistemies: {best_name}")
            md.append("")

            # Get best player's individual games with full team names
            best_games = [g for g in week_info["games"] if g["name"] == best_name]
            game_details = []
            for g in sorted(best_games, key=lambda x: x.get("points", 0), reverse=True):
                if g.get("points", 0) > 0:
                    opp = TEAM_NAMES_FI.get(g.get("opponent", "?"), g.get("opponent", "?"))
                    game_details.append(
                        f"{opp} {g.get('game_date', '')}: {g['goals']}+{g['assists']}={g['points']}"
                    )

            team_names = [TEAM_NAMES_FI.get(t, t) for t in best_stats["teams"]]
            team_display = ", ".join(team_names)
            md.append(
                f"**{best_name}** ({team_display}) keräsi viikon suomalaispelaajista eniten tehopisteitä: **{best_stats['goals']}+{best_stats['assists']}={best_stats['points']}**."
            )
            md.append(f"Pelejä viikon aikana: {best_stats['games']}.")
            if game_details:
                md.append("")
                md.append("**Pistepelit:**")
                for gd in game_details:
                    md.append(f"- {gd}")
            md.append("")

        # News section (external + goalie/hat trick highlights, skip top scorer since it's covered above)
        if weekly_news:
            # Filter out the top-scorer news item since we have a dedicated section
            filtered_news = []
            top_name = top_scorers[0][0] if top_scorers else None
            for news in weekly_news:
                # Skip if it's the same top-scorer summary (we have dedicated section)
                if top_name and news.get("title", "").startswith(f"{top_name} viikon paras"):
                    continue
                filtered_news.append(news)

            if filtered_news:
                md.append("## Viikon uutiset")
                md.append("")
                for news in filtered_news:
                    md.append(f"### {news['title']}")
                    md.append(f"{news['description']}")
                    if "source" in news:
                        if "url" in news:
                            md.append(f"*Lähde: [{news['source']}]({news['url']})*")
                        else:
                            md.append(f"*Lähde: {news['source']}*")
                    md.append("")

        # Notable performances (hat tricks, 4+ point games, shutouts)
        notable_games = []
        for name, stats in players.items():
            player_daily = [g for g in week_info["games"] if g["name"] == name]
            for g in player_daily:
                opp_short = TEAM_NAMES_FI.get(g.get("opponent", "?"), g.get("opponent", "?"))
                if g["goals"] >= 3:
                    game_date = format_date_finnish(g["game_date"])
                    notable_games.append(
                        f"- **{name}** teki hattutempun ({g['goals']} maalia) ottelussa {opp_short}a vastaan ({game_date}). Loppulukemat {g['game_score']}."
                    )
                elif g["points"] >= 4:
                    game_date = format_date_finnish(g["game_date"])
                    notable_games.append(
                        f"- **{name}** kirjautti neljä tehopistettä ({g['goals']}+{g['assists']}) ottelussa {opp_short}a vastaan ({game_date})."
                    )
                elif (
                    g.get("save_percentage", 0) == 1.0
                    and g.get("saves", 0) > 10
                    and g.get("position") == "G"
                ):
                    game_date = format_date_finnish(g["game_date"])
                    notable_games.append(
                        f"- Maalivahti **{name}** torjui nollapelin ({g['saves']} torjuntaa) ottelussa {opp_short}a vastaan ({game_date})."
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
            team_names = [TEAM_NAMES_FI.get(t, t) for t in stats["teams"]]
            team = ", ".join(team_names)
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
                    team_names = [TEAM_NAMES_FI.get(t, t) for t in stats["teams"]]
                    team = ", ".join(team_names)
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

            team_names = [TEAM_NAMES_FI.get(t, t) for t in stats["teams"]]
            goalie_stats.append(
                {
                    "name": name,
                    "team": ", ".join(team_names),
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

        # Detect hat tricks and shutouts for title generation
        has_hat_trick = any(
            g.get("goals", 0) >= 3
            for g in week_info["games"]
        )
        has_shutout = any(
            g.get("saves", 0) > 10
            and g.get("shots_against", 0) == g.get("saves", 0)
            and g.get("position") == "G"
            for g in week_info["games"]
        )

        top_points = top_scorers[0][1]["points"] if top_scorers else 0
        title = generate_creative_title(week, year, top_player_name, top_points, has_hat_trick, has_shutout)

        excerpt = f"{player_count} suomalaista pelasi, {total_goals} maalia, {total_points} pistettä."
        if top_scorers:
            excerpt = (
                f"{top_scorers[0][0]} keräsi {top_scorers[0][1]['points']} tehopistettä. "
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
