#!/usr/bin/env python3
"""Retry publishing until the live site reports the checked-out source revision."""

import argparse
import json
import os
import subprocess
import time
from pathlib import Path

import requests


def source_revision():
    return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()


def needs_deployment(url, revision):
    try:
        response = requests.get(
            url, params={"t": int(time.time())},
            headers={"Cache-Control": "no-cache"}, timeout=15,
        )
        response.raise_for_status()
        published = response.json()
        return not isinstance(published, dict) or published.get("revision") != revision
    except (requests.RequestException, ValueError) as error:
        print(f"Could not verify the published revision; retrying deployment: {error}")
        return True


def write_deployment_marker(path, revision):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"revision": revision}) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check-url", help="URL of the live data/deployment.json")
    mode.add_argument("--write", help="Write metadata into the built deployment artifact")
    args = parser.parse_args()
    revision = source_revision()
    if args.write:
        write_deployment_marker(args.write, revision)
    else:
        required = needs_deployment(args.check_url, revision)
        print(f"Source revision: {revision}; deployment required: {required}")
        if "GITHUB_OUTPUT" in os.environ:
            with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
                output.write(f"needs_deployment={'true' if required else 'false'}\n")


if __name__ == "__main__":
    main()
