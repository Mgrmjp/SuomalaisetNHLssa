import json
import os
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, Mock, patch

import generate_daily_news as news

NOW = datetime(2026, 11, 1, 12, tzinfo=timezone.utc)
ROSTER = {
    "1": {"name": "Aleksander Barkov", "isActive": True},
    "2": {"name": "Sebastian Aho", "isActive": True},
    "3": {"name": "Oliver Kapanen", "isActive": True},
    "4": {"name": "Kasperi Kapanen", "isActive": True},
}
URL = "https://www.nhl.com/panthers/news/barkov-injury-update"


def page(date="2026-11-01T09:00:00Z", title="Aleksander Barkov returns to practice"):
    return f'''<html><head><meta property="article:published_time" content="{date}">
    <meta property="og:title" content="{title}"><meta property="og:description"
    content="Aleksander Barkov returned to Panthers practice after recovering from an injury."></head></html>'''


class FinnishNewsTests(unittest.TestCase):
    def test_main_subject_requires_full_name_or_unambiguous_surname_in_headline(self):
        self.assertEqual(
            news.match_players("Barkov returns to practice", ROSTER),
            ["Aleksander Barkov"],
        )
        self.assertEqual(news.match_players("NHL morning roundup", ROSTER), [])
        self.assertEqual(news.match_players("Kapanen returns", ROSTER), [])
        self.assertEqual(news.match_players("Oliver Kapanen returns", ROSTER), ["Oliver Kapanen"])

    def test_publication_must_come_from_publisher_metadata_not_search_date(self):
        result = news.verify_article(URL, page(), ROSTER, NOW)
        self.assertEqual(result["publishedAt"], "2026-11-01T09:00:00Z")
        self.assertEqual(result["matchedPlayers"], ["Aleksander Barkov"])
        self.assertIsNone(
            news.verify_article(
                URL,
                page().replace("article:published_time", "article:modified_time"),
                ROSTER,
                NOW,
            )
        )
        self.assertIsNone(news.verify_article(URL, page(date="2026-11-01"), ROSTER, NOW))

    def test_rejects_stale_future_unrelated_and_untrusted_articles(self):
        for date in ["2026-10-30T11:59:59Z", "2026-11-01T12:00:01Z", "bad date"]:
            self.assertIsNone(news.verify_article(URL, page(date), ROSTER, NOW))
        self.assertIsNone(
            news.verify_article(URL, page(title="NHL Opening Night Preview"), ROSTER, NOW)
        )
        self.assertIsNone(
            news.verify_article("https://nhl.com.evil.test/news/barkov", page(), ROSTER, NOW)
        )
        self.assertIsNone(news.verify_article("https://nhl.com/", page(), ROSTER, NOW))

    def test_schema_publication_accepts_article_but_ignores_related_articles(self):
        html = """<meta property="og:title" content="Barkov returns"><script type="application/ld+json">{"@graph":[
        {"@type":"NewsArticle","url":"https://www.nhl.com/news/other","headline":"Aho scores","datePublished":"2026-11-01T11:00:00Z"},
        {"@type":"NewsArticle","url":"URL","headline":"Barkov returns","datePublished":"2026-11-01T09:00:00Z"}]}</script>""".replace(
            "URL", URL
        )
        self.assertEqual(
            news.verify_article(URL, html, ROSTER, NOW)["publishedAt"],
            "2026-11-01T09:00:00Z",
        )

    def test_index_discards_legacy_news_and_limits_to_two_real_headlines(self):
        items = [
            news.verify_article(
                URL + str(i), page(title=f"Barkov returns to practice {i}"), ROSTER, NOW
            )
            for i in range(3)
        ]
        items.append({"title": "NHL news", "matchedDate": "2026-11-01"})
        index = news.build_news_index({"2026-11-01": items}, ROSTER, NOW)
        self.assertEqual(len(index["byDate"]["2026-11-01"]), 2)
        self.assertTrue(
            all(
                item["translatedTitle"].startswith("Barkov returns")
                for item in index["byDate"]["2026-11-01"]
            )
        )
        self.assertEqual(
            news.build_news_index({"2026-11-01": [items[-1]]}, ROSTER, NOW)["byDate"],
            {},
        )

    def test_search_refresh_is_hourly_and_failure_preserves_verified_cache(self):
        cache = {"_refresh": {"lastAttemptAt": "2026-11-01T11:30:00Z"}}
        search = Mock()
        self.assertFalse(news.refresh_news(cache, ROSTER, NOW, search=search))
        search.assert_not_called()
        good = news.verify_article(URL, page(), ROSTER, NOW)
        cache = {"2026-11-01": [good]}
        with patch.object(news, "fetch_article", side_effect=RuntimeError("offline")):
            search.side_effect = RuntimeError("offline")
            news.refresh_news(cache, ROSTER, NOW, search=search)
        self.assertEqual(cache["2026-11-01"], [good])
        self.assertEqual(
            news.build_news_index(cache, ROSTER, NOW + timedelta(hours=49))["byDate"],
            {},
        )

    def test_failed_or_generic_translation_uses_the_real_headline(self):
        item = news.verify_article(URL, page(), ROSTER, NOW)
        item.update(
            translatedTitle="NHL:n päivän puheenaiheet 1.11.2026",
            translatedSummary="Kooste päivän uutisista.",
        )
        index = news.build_news_index({"2026-11-01": [item]}, ROSTER, NOW)
        self.assertEqual(index["byDate"]["2026-11-01"][0]["translatedTitle"], item["title"])

    def test_discovery_uses_news_window_and_checks_publisher_content(self):
        cache = {}
        search = Mock(return_value={"results": [{"url": URL, "title": "Barkov returns"}]})
        with (
            patch.object(news, "fetch_article", return_value=(URL, page())),
            patch.object(news, "faithful_translation", side_effect=lambda item: item),
        ):
            news.refresh_news(cache, ROSTER, NOW, search=search)
        self.assertEqual(search.call_count, 2)
        self.assertEqual(search.call_args.kwargs["topic"], "news")
        self.assertEqual(search.call_args.kwargs["days"], 2)
        self.assertEqual(
            news.build_news_index(cache, ROSTER, NOW)["byDate"]["2026-11-01"][0]["url"],
            news.canonicalize_url(URL),
        )

    def test_publisher_unicode_headline_is_decoded_from_html_metadata(self):
        roster = {"1": {"name": "Juuso Välimäki", "isActive": True}}
        html = '<meta charset="utf-8">' + page(title="Juuso Välimäki returns")
        self.assertEqual(
            news.verify_article(URL, html.encode("utf-8"), roster, NOW)["matchedPlayers"],
            ["Juuso Välimäki"],
        )

    def test_index_write_preserves_archive_and_reports_no_changes_on_repeat(self):
        good = news.verify_article(URL, page(), ROSTER, NOW)
        archive = {"2026-01-01": [{"title": "Legacy article"}], "2026-11-01": [good]}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            roster_file, cache_file, output, github_output = [
                root / name for name in ["roster.json", "cache.json", "news.json", "github-output"]
            ]
            roster_file.write_text(json.dumps(ROSTER))
            cache_file.write_text(json.dumps(archive))
            with (
                patch.object(news, "ROSTER_FILE", roster_file),
                patch.object(news, "DAILY_CACHE_FILE", cache_file),
                patch.object(news, "OUTPUT_FILE", output),
                patch.object(news, "refresh_news", return_value=False),
                patch("sys.argv", ["generate_daily_news.py"]),
                patch.object(news, "datetime", wraps=datetime) as clock,
                patch.dict(os.environ, {"GITHUB_OUTPUT": str(github_output)}),
            ):
                clock.now.return_value = NOW
                news.main()
                news.main()
            self.assertEqual(
                json.loads(cache_file.read_text())["2026-01-01"], archive["2026-01-01"]
            )
            self.assertEqual(len(json.loads(output.read_text())["byDate"]["2026-11-01"]), 1)
            self.assertEqual(
                github_output.read_text().splitlines(),
                ["updated=true", "updated=false"],
            )

    def test_article_fetch_does_not_follow_redirect_to_an_untrusted_host(self):
        response = MagicMock(status_code=302, headers={"Location": "http://127.0.0.1/private"})
        response.__enter__.return_value = response
        with patch.object(news.requests, "get", return_value=response) as getter:
            self.assertIsNone(news.fetch_article(URL))
        self.assertEqual(getter.call_count, 1)


if __name__ == "__main__":
    unittest.main()
