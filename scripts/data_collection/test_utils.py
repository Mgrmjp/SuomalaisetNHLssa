"""Focused tests for the shared atomic JSON writer."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import save_json


class SaveJsonTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_writes_parseable_json_with_defaults(self):
        target = self.base / "nested" / "out.json"
        written = save_json({"name": "Mikko Rantanen", "goals": 2}, target)

        self.assertEqual(written, target)
        self.assertEqual(json.loads(target.read_text(encoding="utf-8")), {"name": "Mikko Rantanen", "goals": 2})

    def test_preserves_unicode_by_default(self):
        target = self.base / "unicode.json"
        save_json({"name": "Artturi Lehkonen"}, target)

        self.assertEqual(target.read_text(encoding="utf-8"), json.dumps({"name": "Artturi Lehkonen"}, indent=2, ensure_ascii=False))

    def test_failed_serialization_preserves_previous_snapshot(self):
        target = self.base / "snapshot.json"
        save_json({"version": "previous"}, target)
        before = target.read_text(encoding="utf-8")

        with self.assertRaises(TypeError):
            save_json({"version": "next", "bad": object()}, target)

        self.assertEqual(target.read_text(encoding="utf-8"), before)
        self.assertEqual(json.loads(target.read_text(encoding="utf-8")), {"version": "previous"})

    def test_failed_serialization_leaves_no_temporary_files(self):
        target = self.base / "snapshot.json"
        save_json({"version": "previous"}, target)

        with self.assertRaises(TypeError):
            save_json({"bad": object()}, target)

        leftovers = sorted(p.name for p in self.base.iterdir())
        self.assertEqual(leftovers, ["snapshot.json"])


if __name__ == "__main__":
    unittest.main()
