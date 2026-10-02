"""Exercise the real daily shell pipeline with collectors replaced by local stubs."""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path


class DailyUpdateTests(unittest.TestCase):
    def run_pipeline(self, failure=""):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            scripts = root / "scripts"
            scripts.mkdir()
            script = scripts / "daily_update.sh"
            script.write_text((Path(__file__).parent / "daily_update.sh").read_text())
            python = root / ".venv/bin/python3"
            python.parent.mkdir(parents=True)
            python.write_text('''#!/bin/bash
printf '%s\n' "$*" >> "$UPDATE_TEST_LOG"
case "$1" in
  *finnish/fetch.py) [ "$UPDATE_TEST_FAIL" = "fetch" ] && exit 3 ;;
  *generate_daily_news.py) [ "$UPDATE_TEST_FAIL" = "news" ] && exit 4 ;;
esac
exit 0
''')
            python.chmod(0o755)
            date = root / "date"
            date.write_text('''#!/bin/bash
case "$2" in
  yesterday) echo 2026-10-01 ;;
  '+7 days') echo 2026-10-09 ;;
  *) exit 1 ;;
esac
''')
            date.chmod(0o755)
            log = root / "calls"
            env = {**os.environ, "PATH": f"{root}:{os.environ['PATH']}",
                   "UPDATE_TEST_LOG": str(log), "UPDATE_TEST_FAIL": failure}
            result = subprocess.run(["bash", str(script)], env=env, capture_output=True, text=True)
            return result.returncode, log.read_text()

    def test_default_window_includes_yesterday_and_upcoming_days(self):
        status, calls = self.run_pipeline()
        self.assertEqual(status, 0)
        self.assertIn("finnish/fetch.py 2026-10-01 2026-10-09", calls)

    def test_failed_collection_fails_the_workflow(self):
        status, _calls = self.run_pipeline("fetch")
        self.assertEqual(status, 3)

    def test_failed_news_generation_is_not_reported_as_success(self):
        status, _calls = self.run_pipeline("news")
        self.assertEqual(status, 4)


if __name__ == "__main__":
    unittest.main()
