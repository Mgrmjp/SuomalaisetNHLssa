#!/usr/bin/env python3
"""Check the published revision and wait for new GitHub Pages artifacts."""

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
            url,
            params={"t": int(time.time())},
            headers={"Cache-Control": "no-cache"},
            timeout=15,
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


def wait_for_artifact(url, token):
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "Cache-Control": "no-cache",
    }
    for delay in (2, 4, 8, 8):
        time.sleep(delay)
        try:
            response = requests.get(url, headers=headers, timeout=5)
        except (requests.ConnectionError, requests.Timeout) as error:
            print(f"Artifact metadata request failed: {error}")
            continue

        if response.status_code == 200:
            print("Pages artifact metadata is available.")
            return
        if response.status_code not in (404, 429) and response.status_code < 500:
            response.raise_for_status()
        print(f"Pages artifact metadata is unavailable (HTTP {response.status_code}).")

    raise RuntimeError("Pages artifact metadata did not become visible after four attempts.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check-url", help="URL of the live data/deployment.json")
    mode.add_argument("--write", help="Write metadata into the built deployment artifact")
    mode.add_argument("--wait-for-artifact", type=int, help="Wait for the uploaded artifact ID")
    args = parser.parse_args()
    if args.wait_for_artifact is not None:
        api_url = os.environ["GITHUB_API_URL"]
        repo = os.environ["GITHUB_REPOSITORY"]
        url = f"{api_url}/repos/{repo}/actions/artifacts/{args.wait_for_artifact}"
        wait_for_artifact(url, os.environ["GITHUB_TOKEN"])
        return

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
