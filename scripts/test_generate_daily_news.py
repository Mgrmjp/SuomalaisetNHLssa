import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import generate_daily_news as news


class DailyNewsRefreshTests(unittest.TestCase):
    def test_refresh_keeps_previously_cached_dates(self):
        earlier = {"title": "Earlier NHL news", "url": "https://www.nhl.com/news/earlier"}
        latest = {"title": "Latest NHL news", "url": "https://www.nhl.com/news/latest"}
        daily_cache = {"2026-09-27": [earlier]}

        def fetch_latest(date, cache):
            cache[date] = [latest]
            return cache[date]

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "daily-news.json"
            with (
                patch.object(news.sys, "argv", ["generate_daily_news.py", "2026-10-01"]),
                patch.object(news, "OUTPUT_FILE", output),
                patch.object(news, "load_cache", return_value={}),
                patch.object(news, "load_daily_cache", return_value=daily_cache),
                patch.object(news, "fetch_daily_news_tavily", side_effect=fetch_latest),
            ):
                news.main()
            index = json.loads(output.read_text())

        self.assertEqual(index["byDate"]["2026-09-27"][0]["url"], earlier["url"])
        self.assertEqual(index["byDate"]["2026-10-01"][0]["url"], latest["url"])


class NewsEntryFilterTests(unittest.TestCase):
    def test_homepage_url_is_rejected(self):
        entry = {
            "title": "BakersfieldCondors.com - The Official Website",
            "summary": "Fresh ice, fresh season! Coaching staff extensions and more from the Condors.",
            "url": "https://www.bakersfieldcondors.com",
        }
        self.assertIsNone(news.normalize_news_entry(entry, "2026-10-23"))

    def test_php_var_dump_summary_is_rejected(self):
        entry = {
            "title": "Condors game day",
            "summary": 'string(7) "1029177" ["season_id"]=> string(2) "94" ["quick_score"]=> '
            'string(1) "0"',
            "url": "https://www.nhl.com/news/condors-game-day",
        }
        self.assertIsNone(news.normalize_news_entry(entry, "2026-10-23"))

    def test_untrusted_domain_is_rejected(self):
        entry = {
            "title": "Arena parking information for the 2026 season",
            "summary": "Parking passes and gate times for all events at the arena this season.",
            "url": "https://www.americanairlinescenter.com/events/parking",
        }
        self.assertIsNone(news.normalize_news_entry(entry, "2026-10-23"))

    def test_trusted_article_is_kept(self):
        entry = {
            "title": "Five storylines already dominating the 2026 NHL offseason",
            "summary": "Two-time Vezina winner Sergei Bobrovsky might be priced out of Florida.",
            "url": "https://www.espn.com/nhl/story/_/id/49142380/nhl-2026-offseason",
        }
        result = news.normalize_news_entry(entry, "2026-10-23")
        self.assertIsNotNone(result)
        self.assertEqual(result["source"], "ESPN")

    def test_mangled_hostname_source_is_cleaned(self):
        self.assertEqual(news.infer_source_label("Espn Com"), "ESPN")
        self.assertEqual(news.infer_source_label("Bleacherreport Com"), "Bleacher Report")
        self.assertEqual(news.infer_source_label("Centraloregondaily Com"), "Centraloregondaily")
        self.assertEqual(news.infer_source_label("Yahoo Sports"), "Yahoo Sports")

    def test_source_label_drops_tld(self):
        self.assertEqual(news.format_hostname_label("www.somehockeyblog.com"), "Somehockeyblog")

    def test_trusted_subdomain_matches(self):
        self.assertTrue(news.is_trusted_news_url("https://global.espn.com/nhl/story/x"))
        self.assertFalse(news.is_trusted_news_url("https://example.org/nhl/story/x"))


if __name__ == "__main__":
    unittest.main()
