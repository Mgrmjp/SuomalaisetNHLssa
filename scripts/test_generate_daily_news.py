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


if __name__ == "__main__":
    unittest.main()
