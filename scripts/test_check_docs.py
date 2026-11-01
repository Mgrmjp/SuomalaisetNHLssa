import tempfile
import unittest
from pathlib import Path

from check_docs import check_document


class DocumentationChecks(unittest.TestCase):
    def test_accepts_existing_links_anchors_sources_and_commands(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "docs").mkdir()
            (root / "src").mkdir()
            (root / "src/app.js").write_text("")
            (root / "docs/guide.md").write_text("# Setup\n\n## API keys\n")
            readme = root / "README.md"
            readme.write_text(
                "[Guide](docs/guide.md#api-keys)\n`src/app.js`\n```sh\nnpm run check\n```"
            )
            self.assertEqual(check_document(readme, root, {"check": ""}), [])

    def test_reports_broken_links_anchors_commands_and_source_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "guide.md").write_text("# Setup\n")
            readme = root / "README.md"
            readme.write_text(
                "[Missing](gone.md)\n[Anchor](guide.md#wrong)\n`src/missing.js`\nnpm run fake"
            )
            errors = check_document(readme, root, {})
            self.assertEqual(len(errors), 4)
            self.assertEqual([line for line, _ in errors], [1, 2, 3, 4])

    def test_ignores_external_links_and_fenced_markdown_examples(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            readme = root / "README.md"
            readme.write_text(
                "[External](https://example.com/no-request)\n```md\n[Example](not-a-real-file.md)\n```"
            )
            self.assertEqual(check_document(readme, root, {}), [])

    def test_checks_real_command_paths_inside_code_blocks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "scripts").mkdir()
            (root / "scripts/existing.py").write_text("")
            readme = root / "README.md"
            readme.write_text(
                "```bash\n.venv/bin/python3 scripts/existing.py\npython3 scripts/missing.py\n```"
            )
            errors = check_document(readme, root, {})
            self.assertEqual(
                errors, [(3, "Missing command source: scripts/missing.py")]
            )

    def test_rejects_links_outside_the_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            readme = root / "README.md"
            readme.write_text("[Outside](../README.md)")
            self.assertIn("leaves repository", check_document(readme, root, {})[0][1])


if __name__ == "__main__":
    unittest.main()
