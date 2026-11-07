"""Check engineering documentation links, source paths and npm script names."""

import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
LINK = re.compile(r"!?\[[^\]]*\]\(<?([^\s)>]+)>?(?:\s+\"[^\"]*\")?\)")
INLINE_PATH = re.compile(r"`((?:src|scripts|static|tests|docs|\.github)/[^`\s]+)`")
NPM_SCRIPT = re.compile(r"\bnpm run ([a-zA-Z0-9][a-zA-Z0-9:._-]*)")
COMMAND_SOURCE = re.compile(r"\b(?:scripts|src)/[\w./\-\[\]]+\.(?:py|cjs|mjs|js|ts|sh)\b")


def documents(root):
    paths = [*root.glob("*.md"), root / "static/data/README.md"]
    for folder in ("docs", "scripts", "tests"):
        paths.extend((root / folder).rglob("*.md"))
    return sorted({path for path in paths if path.is_file()})


def without_fences(text):
    lines = []
    fence = None
    for line in text.splitlines():
        match = re.match(r"^\s*(`{3,}|~{3,})", line)
        if match:
            marker = match[1][0]
            if fence is None:
                fence = marker
            elif marker == fence:
                fence = None
            lines.append("")
        else:
            lines.append("" if fence else line)
    return "\n".join(lines)


def anchors(text):
    seen = Counter()
    found = set()
    for line in without_fences(text).splitlines():
        heading = re.match(r"^#{1,6}\s+(.+?)\s*#*$", line)
        if not heading:
            continue
        label = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", heading[1])
        slug = re.sub(r"[^\w\-\s]", "", label.lower()).replace(" ", "-")
        suffix = f"-{seen[slug]}" if seen[slug] else ""
        found.add(slug + suffix)
        seen[slug] += 1
    return found


def check_document(path, root, npm_scripts):
    text = path.read_text(encoding="utf-8")
    visible = without_fences(text)
    issues = []
    for number, line in enumerate(visible.splitlines(), 1):
        for target in LINK.findall(line):
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc:
                continue
            destination = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
            if not destination.is_relative_to(root.resolve()):
                issues.append((number, f"Link leaves repository: {target}"))
            elif not destination.exists():
                issues.append((number, f"Missing link target: {target}"))
            elif parsed.fragment and destination.suffix == ".md":
                if unquote(parsed.fragment) not in anchors(destination.read_text(encoding="utf-8")):
                    issues.append((number, f"Missing heading anchor: {target}"))
        for source in INLINE_PATH.findall(line):
            # Inline generated/example paths are descriptive, not source references.
            if any(
                marker in source for marker in ("*", "{", "<", ">", "YYYY", "SEASON", "PLAYER_ID")
            ):
                continue
            if not (root / source).exists():
                issues.append((number, f"Missing source path: {source}"))
    for number, line in enumerate(text.splitlines(), 1):
        for command in NPM_SCRIPT.findall(line):
            if command not in npm_scripts:
                issues.append((number, f"Unknown npm script: {command}"))
        if re.search(r"\b(?:python3?|node|bash|vitest)\b", line):
            for source in COMMAND_SOURCE.findall(line):
                if not (root / source).exists():
                    issues.append((number, f"Missing command source: {source}"))
    return issues


def main():
    scripts = json.loads((ROOT / "package.json").read_text())["scripts"]
    files = documents(ROOT)
    failures = 0
    for path in files:
        for line, message in check_document(path, ROOT, scripts):
            print(f"{path.relative_to(ROOT)}:{line}: {message}")
            failures += 1
    print(f"Checked {len(files)} engineering Markdown files; {failures} issue(s).")
    return int(failures > 0)


if __name__ == "__main__":
    sys.exit(main())
