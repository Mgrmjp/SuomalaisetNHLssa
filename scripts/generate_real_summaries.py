import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
import subprocess
import random

DATA_DIR = "static/data/prepopulated/games"
OUTPUT_FILE = "static/data/articles.json"
CONTENT_DIR = "content/articles"

def get_iso_week(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    year, week, day = dt.isocalendar()
    return year, week

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
            with open(filepath, 'r') as f:
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

def fetch_weekly_news(year, week, week_start, week_end, players, games):
    """Generate dynamic news highlights based on weekly statistics"""
    news_items = []

    MANUAL_NEWS = {
        (2026, 2): [
            {
                "title": "Juuso Välimäki vahvistamaan Hurricanesia",
                "description": "Carolina Hurricanes hankki suomalaispuolustaja Juuso Välimäen Utah Mammothista. Välimäki on toipunut polvivammastaan ja hakee uutta alkua Carolinassa.",
                "source": "NHL.com",
                "url": "https://www.nhl.com/hurricanes/news/canes-acquire-juuso-valimaki-from-utah/c-347492984"
            },
            {
                "title": "Trade-huhuja: Kotkaniemi mahdollisesti siirtolistalla",
                "description": "Carolina Hurricanesin kerrotaan harkitsevan tarjouksia Jesperi Kotkaniemestä. Suomalaiskeskushyökkääjä on jäänyt vähemmälle peliajalle ja seura saattaa etsiä hänelle uutta osoitetta.",
                "source": "Sportsnet",
                "url": "https://www.sportsnet.ca/nhl/rumors"
            },
            {
                "title": "Rantanen ja Heiskanen lähellä virstanpylväitä",
                "description": "Mikko Rantanen on vain muutaman maalin päässä yhdeksännestä peräkkäisestä 20 maalin kaudestaan. Miro Heiskanen puolestaan lähestyy Janne Niinimaan tehopistemäärää suomalaispuolustajien kaikkien aikojen listalla.",
                "source": "NHL Tilastot",
                "url": "https://www.nhl.com/stats/skaters?reportType=season&seasonFrom=20252026&seasonTo=20252026&gameType=2&sort=points&nationalityCode=FIN"
            }
        ],
        (2026, 1): [
            {
                "title": "Leijonien olympiajoukkue julkaistu – Kapanen korvaa Barkovin",
                "description": "Suomen joukkue Milanon 2026 olympialaisiin on nimetty. Aleksander Barkov jää sivuun loukkaantumisen vuoksi, ja hänen paikkansa ottaa nuori Oliver Kapanen. Joukkueen tähtinä häärivät Rantanen, Aho ja Heiskanen.",
                "source": "Olympics.com",
                "url": "https://www.olympics.com/en/news/finland-men-ice-hockey-roster-milano-cortina-2026"
            },
            {
                "title": "Pikkuleijonille neljäs sija MM-kisoissa",
                "description": "Suomen alle 20-vuotiaiden maajoukkue sijoittui neljänneksi nuorten MM-kisoissa. Julius Miettinen ja Oliver Suvanto olivat joukkueen näkyvimpiä hahmoja.",
                "source": "YLE Urheilu",
                "url": "https://yle.fi/a/74-20138241"
            }
        ],
        (2025, 52): [
            {
                "title": "Eeli Tolvanen hurjassa iskussa joulun alla",
                "description": "Seattle Krakenin Eeli Tolvanen mätti viikkoon tehot 2+4. Joulukuun 20. päivän ottelussa hän merkkautti maalin ja syötön, varmistaen paikkansa viikon tehokkaimpana suomalaisena.",
                "source": "NHL.com",
                "url": "https://www.nhl.com/player/eeli-tolvanen-8480009"
            },
            {
                "title": "Jani Nyman vakuuttaa Seattlessa",
                "description": "Nuori Jani Nyman on saanut vastuuta Seattle Krakenin kokoonpanossa ja osoittanut pystyvänsä pelaamaan NHL-tasolla. Nymanin fyysinen peli ja laukaus ovat herättäneet huomiota.",
                "source": "Times-Colonist",
                "url": "https://www.timescolonist.com/sports"
            }
        ],
        (2025, 51): [
            {
                "title": "Sebastian Aho nöyryytti Bobrovskya läpiajosta",
                "description": "Carolina Hurricanesin Sebastian Aho karkasi läpiajoon Floridaa vastaan ja sijoitti kiekon tyylikkäästi Sergei Bobrovskyn jalkojen välistä maaliin joulukuun 19. päivänä.",
                "source": "NHL Video",
                "url": "https://www.nhl.com/video/aho-scores-on-breakaway-6401928374001"
            },
            {
                "title": "Mikko Rantasen tunteet kuumenivat San Josea vastaan",
                "description": "Dallasin Mikko Rantanen kävi kuumana saatuaan mailasta käsilleen San Josea vastaan. Rantanen vastasi huutoon iskemällä ottelussa kaksi syöttöpistettä.",
                "source": "Dallas Morning News",
                "url": "https://www.dallasnews.com/sports/stars/"
            }
        ],
        (2025, 49): [
            {
                "title": "Aatu Räty vahvassa vireessä Vancouverissa",
                "description": "Vancouver Canucksin Aatu Räty on löytänyt tehorakonsa joulukuun alussa. Räty keräsi viikon kolmeen otteluun tehot 2+3 ja nousi suomalaispörssin kärkeen.",
                "source": "Vancouver Sun",
                "url": "https://vancouversun.com/category/sports/hockey/nhl/vancouver-canucks/"
            }
        ],
        (2025, 48): [
            {
                "title": "Roope Hintzin pisteputki jatkuu",
                "description": "Dallas Starsin Roope Hintz oli viikon tehokkain suomalainen keräten viisi tehopistettä. Hintz on ollut alkukauden yksi Dallasin tasaisimmista suorittajista.",
                "source": "NHL Statistics",
                "url": "https://www.nhl.com/stats/skaters"
            },
            {
                "title": "Ukko-Pekka Luukkoselle kaksi voittoa putkeen",
                "description": "Buffalo Sabresin Ukko-Pekka Luukkonen torjui joukkueelleen kaksi tärkeää voittoa marraskuun lopulla ja vankisti asemaansa ykkösmaalivahtina.",
                "source": "Buffalo News",
                "url": "https://buffalonews.com/sports/sabres/"
            }
        ],
        (2025, 45): [
             {
                "title": "Mikko Rantanen 300 maalin kerhoon",
                "description": "Mikko Rantanen teki historiaa iskemällä kaksi maalia Edmonton Oilersia vastaan 4. marraskuuta. Hänestä tuli vasta neljäs suomalaispelaaja NHL:n historiassa, joka on saavuttanut 300 maalin rajapyykin.",
                "source": "NHL.com",
                "url": "https://www.nhl.com/news/mikko-rantanen-300-career-goals-nhl"
            },
            {
                "title": "Miro Heiskasen neljän syötön ilta",
                "description": "Miro Heiskanen oli pysäyttämätön marraskuun 6. päivän ottelussa merkkauttaen peräti neljä syöttöpistettä. Heiskanen on palannut tasolleen täysin alun loukkaantumishuolien jälkeen.",
                "source": "Dallas Stars",
                "url": "https://www.nhl.com/stars/news/"
            },
            {
                "title": "Anton Lundellille alivoimamaali",
                "description": "Florida Panthersin taitava keskushyökkääjä Anton Lundell iski upean alivoimamaalin marraskuun alussa osoittaen monipuolisuuttaan.",
                "source": "Florida Panthers",
                "url": "https://www.nhl.com/panthers/news/"
            }
        ],
        (2025, 44): [
             {
                "title": "Artturi Lehkoselle 300 tehopistettä täyteen",
                "description": "Colorado Avalanchen Artturi Lehkonen saavutti urallaan 300 tehopisteen rajapyykin syöttöpisteellä 1. marraskuuta pelatussa ottelussa.",
                "source": "Colorado Avalanche",
                "url": "https://www.nhl.com/avalanche/news/"
            },
            {
                 "title": "Brad Lambertin uran avausmaali NHL:ssä",
                 "description": "Winnipeg Jetsin lupaus Brad Lambert iski NHL-uransa ensimmäisen maalin marraskuun alussa. Lambert on yksi seuratuimmista suomalaisnuorukaisista tällä kaudella.",
                 "source": "Winnipeg Jets",
                 "url": "https://www.nhl.com/jets/news/"
            }
        ],
        (2025, 43): [
            {
                "title": "Artturi Lehkonen pelasi 600. NHL-ottelunsa",
                "description": "Artturi Lehkonen rikkoi 600 pelatun NHL-ottelun rajan lokakuun lopulla. Lehkonen on ollut tärkeä palanen Coloradon hyökkäyksessä koko alkukauden.",
                "source": "NHL.com",
                "url": "https://www.nhl.com/player/artturi-lehkonen-8477479"
            },
            {
                 "title": "Patrik Laine pitkään sivussa vatsalihasvamman vuoksi",
                 "description": "Montreal Canadiensin Patrik Laineen paluu kaukaloihin viivästyy vatsalihasvamman vuoksi. Laineen arvioidaan olevan sivussa vielä useita viikkoja.",
                 "source": "NHL.com",
                 "url": "https://www.nhl.com/news/patrik-laine-injury-update"
            }
        ],
        (2025, 40): [
            {
                "title": "Aleksander Barkoville vakava polvivamma harjoitusleirillä",
                "description": "Florida Panthersin kapteeni Aleksander Barkov loukkaantui harjoitusleirillä. Polvivamma vaatii leikkauksen ja pitää tähden sivussa suurimman osan kaudesta.",
                "source": "Miami Herald",
                "url": "https://www.miamiherald.com/sports/nhl/florida-panthers/article292552994.html"
            },
            {
                "title": "Ukko-Pekka Luukkonen loukkaantui harjoitusottelussa",
                "description": "Buffalo Sabresin maalivahti Ukko-Pekka Luukkonen kärsi vammasta harjoituskauden lopulla, mutta paluu tositoimiin on odotettavissa pian.",
                "source": "Buffalo Sabres",
                "url": "https://www.nhl.com/sabres/news/"
            }
        ]
    }


    # Add manual news for the specific week if available
    if (year, week) in MANUAL_NEWS:
        news_items.extend(MANUAL_NEWS[(year, week)])


    # 1. Highlight Top Scorer
    skaters = {name: stats for name, stats in players.items() if stats.get("position") != "G"}
    sorted_players = sorted(skaters.items(), key=lambda x: (x[1]['points'], x[1]['goals']), reverse=True)
    
    if sorted_players:
        top_name, top_stats = sorted_players[0]
        points = top_stats['points']
        goals = top_stats['goals']
        assists = top_stats['assists']
        
        title = f"{top_name} viikon tehokkain suomalainen"
        desc = f"{top_name} johti suomalaisrintamaa tehoilla {goals}+{assists}={points}."
        
        # Check for multi-point games
        player_games = [g for g in games if g['name'] == top_name]
        big_games = [g for g in player_games if g.get('points', 0) >= 3]
        if big_games:
            g = big_games[0]
            desc += f" Hän loisti erityisesti ottelussa {g.get('opponent', '???')} vastaan iskemällä tehot {g.get('goals')}+{g.get('assists')}."

        news_items.append({
            "title": title,
            "description": desc,
            "source": "NHL Tilastot",
            "url": "https://www.nhl.com/stats/skaters"
        })

    # 2. Goalie Shutouts or Big Wins
    goalies = {name: stats for name, stats in players.items() if stats.get("position") == "G"}
    for name, stats in goalies.items():
        player_games = [g for g in games if g['name'] == name]
        for g in player_games:
            if g.get('saves', 0) > 0:
                is_shutout = (g.get('shots_against', 0) == g.get('saves', 0)) and (g.get('shots_against', 0) > 10)
                if is_shutout:
                     news_items.append({
                        "title": f"Nollapeli: {name}",
                        "description": f"{name} torjui kaikki {g.get('saves')} laukausta ottelussa {g.get('opponent', '?')} vastaan ja piti maalinsa puhtaana.",
                        "source": "NHL Tilastot"
                    })
                elif g.get('saves', 0) >= 40:
                     news_items.append({
                        "title": f"Muuri: {name}",
                        "description": f"{name} urakoi maalinsuulla ja pysäytti peräti {g.get('saves')} kiekkoa ottelussa {g.get('opponent', '?')} vastaan.",
                        "source": "NHL Tilastot"
                    })

    # 3. Hat Tricks
    for name, stats in skaters.items():
        player_games = [g for g in games if g['name'] == name]
        for g in player_games:
            if g.get('goals', 0) >= 3:
                news_items.append({
                    "title": f"Hattutemppu: {name}",
                    "description": f"{name} iski kolme maalia ottelussa {g.get('opponent', '?')} vastaan.",
                    "source": "NHL Tilastot"
                })

    # Fallback if no specific highlights
    if not news_items:
        news_items.append({
            "title": "Tasainen viikko suomalaisittain",
            "description": f"Viikolla {week} nähtiin tasaisia suorituksia, mutta ei yksittäisiä superonnistumisia.",
            "source": "NHL Tilastot"
        })

    return news_items[:3]  # Limit to top 3 news items

def format_date_finnish(date_str):
    """Format date to Finnish format: 12. tammikuuta 2026"""
    months = ["tammikuuta", "helmikuuta", "maaliskuuta", "huhtikuuta", "toukokuuta",
              "kesäkuuta", "heinäkuuta", "elokuuta", "syyskuuta", "lokakuuta",
              "marraskuuta", "joulukuuta"]
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return f"{dt.day}. {months[dt.month - 1]} {dt.year}"

def generate_creative_title(week, year, top_player_name):
    """Generate a more engaging title for the article"""
    if top_player_name == "Suomalaiset":
        templates = [
            f"Viikko {week}: suomalaiset iskussa",
            f"Suomalaisilta tasainen viikko {week}",
            f"Viikon {week} suomalaiskatsaus",
            f"Viikko {week}/{year}: suomalaiset vauhdissa",
        ]
    else:
        templates = [
            f"Viikko {week}: {top_player_name} nosti suomalaiset esiin",
            f"{top_player_name} näytti suunnan viikolla {week}",
            f"Viikko {week}/{year}: {top_player_name} piti tahtia",
            f"{top_player_name} loisti viikolla {week}",
            f"Viikon {week} isoin nimi: {top_player_name}",
            f"{top_player_name} sytytti suomalaiset viikolla {week}",
            f"Viikko {week}: {top_player_name} kantoi tehot",
            f"{top_player_name} nappasi viikon {week} otsikot",
            f"Viikko {week} pähkinänkuoressa: {top_player_name} edellä",
        ]
    
    # Use week as seed to keep title stable for the same week across regenerations
    random.seed(f"{year}-{week}")
    return random.choice(templates)

def generate_articles(all_games):
    weeks_data = defaultdict(lambda: {"games": [], "players": defaultdict(lambda: {"goals": 0, "assists": 0, "points": 0, "games": 0, "teams": set(), "position": "F", "player_id": None})})

    for record in all_games:
        year, week = get_iso_week(record['date'])
        key = (year, week)

        p_stats = weeks_data[key]["players"][record['name']]
        p_stats["goals"] += record.get('goals', 0)
        p_stats["assists"] += record.get('assists', 0)
        p_stats["points"] += record.get('points', 0)
        p_stats["games"] += 1
        p_stats["teams"].add(record.get('team', '???'))
        if 'position' in record:
            p_stats["position"] = record['position']
        if 'playerId' in record:
            p_stats["player_id"] = record['playerId']

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
            week_start = datetime.strptime(f'{year}-W{week}-1', "%Y-W%W-%w")
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
        skaters = {name: stats for name, stats in players.items() if stats.get("position") != "G"}
        sorted_players = sorted(skaters.items(), key=lambda x: (x[1]['points'], x[1]['goals']), reverse=True)
        top_scorers = sorted_players[:5]

        # Defenders
        defenders = {name: stats for name, stats in players.items() if stats.get("position") == "D"}
        sorted_defenders = sorted(defenders.items(), key=lambda x: (x[1]['points'], x[1]['goals']), reverse=True)

        # Goalies
        goalies = {name: stats for name, stats in players.items() if stats.get("position") == "G"}

        date_range = f"{week_start.strftime('%d.%m.')}–{week_end.strftime('%d.%m.%Y')}"

        # Get featured player (top scorer) info
        featured_player_id = None
        top_player_name = "Suomalaiset"
        if top_scorers:
            featured_player_id = top_scorers[0][1].get('player_id')
            top_player_name = top_scorers[0][0]

        # Fetch weekly news
        weekly_news = fetch_weekly_news(year, week, week_start, week_end, players, week_info["games"])

        # Build Markdown content
        md = []

        # Opening paragraph
        md.append(f"Viikko {week} ({date_range}) oli jälleen aktiivinen suomalaispelaajille NHL:ssä. Yhteensä **{player_count} suomalaista** pääsi jäälle tällä viikolla. Suomalaiset iskivät **{total_goals} maalia** ja keräsivät yhteensä **{total_points} tehopistettä**.")
        md.append("")

        # News section
        if weekly_news:
            md.append("## Viikon uutiset")
            md.append("")
            for news in weekly_news:
                md.append(f"### {news['title']}")
                md.append(f"{news['description']}")
                if 'source' in news:
                    if 'url' in news:
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
            best_games = [g for g in week_info["games"] if g['name'] == best_name]
            game_details = []
            for g in best_games:
                if g.get('points', 0) > 0:
                    game_details.append(f"{g['opponent']} ({g['goals']}+{g['assists']})")

            md.append(f"**{best_name}** ({', '.join(best_stats['teams'])}) nousi viikon tehokkaimmaksi suomalaiseksi tehoilla **{best_stats['goals']}+{best_stats['assists']}={best_stats['points']}**. Hän pelasi {best_stats['games']} ottelua viikon aikana.")
            if game_details:
                md.append(f"- Ottelukohtaiset pisteet: {', '.join(game_details)}")
            md.append("")

        # Notable performances (hat tricks, 4+ point games)
        notable_games = []
        for name, stats in players.items():
            player_daily = [g for g in week_info["games"] if g['name'] == name]
            for g in player_daily:
                if g['goals'] >= 3:
                    game_date = format_date_finnish(g['game_date'])
                    notable_games.append(f"- **{name}** iski hattutempun ({g['goals']} maalia) ottelussa {g['opponent_full']} vastaan ({game_date}). Ottelu päättyi {g['game_score']}.")
                elif g['points'] >= 4:
                    game_date = format_date_finnish(g['game_date'])
                    notable_games.append(f"- **{name}** keräsi neljä tehopistettä ({g['goals']}+{g['assists']}) ottelussa {g['opponent_full']} vastaan ({game_date}).")
                elif g.get('save_percentage', 0) == 1.0 and g.get('saves', 0) > 10 and g.get('position') == 'G':
                    game_date = format_date_finnish(g['game_date'])
                    notable_games.append(f"- Maalivahti **{name}** pelasi nollapelin ({g['saves']} torjuntaa) ottelussa {g['opponent_full']} vastaan ({game_date}).")

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
            team = ', '.join(stats['teams'])
            md.append(f"| {i}. | {name} | {team} | {stats['games']} | {stats['goals']} | {stats['assists']} | **{stats['points']}** |")
        md.append("")

        # Defenders section
        if sorted_defenders and sorted_defenders[0][1]['points'] >= 1:
            md.append("## Puolustajat")
            md.append("")
            top_d = sorted_defenders[:3]
            for name, stats in top_d:
                if stats['points'] >= 1:
                    team = ', '.join(stats['teams'])
                    md.append(f"- **{name}** ({team}): {stats['goals']}+{stats['assists']}={stats['points']} ({stats['games']} ottelua)")
            md.append("")

        # Goalies section
        goalie_stats = []
        for name, stats in goalies.items():
            all_records = [g for g in week_info["games"] if g['name'] == name]
            g_daily = [g for g in all_records if g.get('time_on_ice', '00:00') != '00:00']

            if not g_daily:
                continue

            wins = sum(1 for g in g_daily if g.get('game_result') == 'W')
            starts = len(g_daily)
            total_saves = sum(g.get('saves', 0) for g in g_daily)
            total_shots = sum(g.get('shots_against', 0) for g in g_daily)
            avg_sv = (total_saves / total_shots * 100) if total_shots > 0 else 0

            goalie_stats.append({
                'name': name,
                'team': ', '.join(stats['teams']),
                'starts': starts,
                'wins': wins,
                'saves': total_saves,
                'sv_pct': avg_sv
            })

        if goalie_stats:
            md.append("## Maalivahdit")
            md.append("")
            md.append("| Maalivahti | Joukkue | Ottelut | Voitot | Torjunnat |")
            md.append("|------------|---------|---------|--------|-----------|")
            for g in sorted(goalie_stats, key=lambda x: x['wins'], reverse=True):
                md.append(f"| {g['name']} | {g['team']} | {g['starts']} | {g['wins']} | {g['saves']} |")
            md.append("")

        # Upcoming games
        try:
            d_next = week_start + timedelta(days=7)
            next_year, next_week, _ = d_next.isocalendar()

            if (next_year, next_week) in weeks_data:
                next_week_info = weeks_data[(next_year, next_week)]
                game_finns = defaultdict(list)
                for g in next_week_info["games"]:
                    game_finns[g['game_id']].append(g)

                interesting_games = sorted(game_finns.items(), key=lambda x: len(x[1]), reverse=True)[:3]

                if interesting_games:
                    md.append("## Ensi viikon mielenkiintoisimmat ottelut")
                    md.append("")
                    for gid, game_players in interesting_games:
                        g = game_players[0]
                        finn_count = len(game_players)
                        date_obj = datetime.strptime(g['game_date'], "%Y-%m-%d")
                        date_fmt = date_obj.strftime("%d.%m.")
                        player_names = [p['name'] for p in game_players[:4]]
                        players_str = ", ".join(player_names)
                        if len(game_players) > 4:
                            players_str += f" (+{len(game_players) - 4} muuta)"
                        md.append(f"- **{date_fmt} {g['team_full']} vs {g['opponent_full']}**: {finn_count} suomalaista ({players_str})")
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
            excerpt = f"{top_scorers[0][0]} johti suomalaisrintamaa {top_scorers[0][1]['points']} pisteellä. " + excerpt

        article = {
            "slug": f"{year}-w{week:02d}",
            "title": title,
            "date": date_str,
            "week": week,
            "year": year,
            "excerpt": excerpt,
            "content": content
        }

        # Add featured player if available
        if featured_player_id:
            article["featured_player_id"] = featured_player_id

        articles.append(article)

    articles.sort(key=lambda x: (x['year'], x['week']), reverse=True)

    # Write JSON articles
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(articles, f, indent=4, ensure_ascii=False)

    # Also write markdown files to content directory
    os.makedirs(CONTENT_DIR, exist_ok=True)
    for article in articles:
        slug = article['slug']
        md_content = f"""---
title: {article['title']}
date: {article['date']}
week: {article['week']}
year: {article['year']}
excerpt: {article['excerpt']}
slug: {article['slug']}
{f"featured_player_id: {article['featured_player_id']}" if 'featured_player_id' in article else ""}
---

{article['content']}
"""
        md_path = os.path.join(CONTENT_DIR, f"{slug}.md")
        with open(md_path, 'w') as f:
            f.write(md_content)

if __name__ == "__main__":
    games = load_game_data()
    generate_articles(games)
    print(f"Generated articles based on {len(games)} game records.")
