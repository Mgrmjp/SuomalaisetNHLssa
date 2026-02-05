#!/usr/bin/env python3
"""
Validate that games_manifest.json matches actual game files in the directory.
Useful for debugging and CI checks.
"""

import json
import sys
from pathlib import Path

# Add shared utils to path
sys.path.insert(0, str(Path(__file__).parent))

from config import GAMES_DIR, DATA_DIR


def validate_manifest():
    """Check that manifest matches actual game files."""
    manifest_file = DATA_DIR / "games_manifest.json"

    if not manifest_file.exists():
        print("❌ Manifest file does not exist:", manifest_file)
        return False

    # Get actual game files
    actual_files = set()
    for f in GAMES_DIR.glob("*.json"):
        # Check if filename is a date (YYYY-MM-DD.json)
        if len(f.name) == 15 and f.name.count("-") == 2 and f.name.endswith(".json"):
            actual_files.add(f.stem)

    # Get manifest dates
    with open(manifest_file) as fp:
        manifest = json.load(fp)
    manifest_dates = set(manifest["games"])

    # Compare
    missing_in_manifest = actual_files - manifest_dates
    extra_in_manifest = manifest_dates - actual_files

    if missing_in_manifest or extra_in_manifest:
        print("❌ Manifest mismatch detected:")
        if missing_in_manifest:
            print(f"   Missing in manifest ({len(missing_in_manifest)}): {sorted(missing_in_manifest)}")
        if extra_in_manifest:
            print(f"   Extra in manifest ({len(extra_in_manifest)}): {sorted(extra_in_manifest)}")
        return False

    print(f"✅ Manifest valid ({len(actual_files)} dates from {min(actual_files) if actual_files else 'N/A'} to {max(actual_files) if actual_files else 'N/A'})")
    return True


if __name__ == "__main__":
    sys.exit(0 if validate_manifest() else 1)
