#!/usr/bin/env python3
"""
Fetch full season data for Finnish NHL players.
"""
import sys
import subprocess
from datetime import datetime, timedelta

START_DATE = "2025-10-01"
END_DATE = "2026-01-05"

def date_range(start, end):
    """Generate list of dates from start to end inclusive."""
    current = datetime.strptime(start, "%Y-%m-%d").date()
    end_date = datetime.strptime(end, "%Y-%m-%d").date()
    while current <= end_date:
        yield current.strftime("%Y-%m-%d")
        current += timedelta(days=1)

def main():
    total = 0
    success = 0
    failed = 0

    for date_str in date_range(START_DATE, END_DATE):
        total += 1
        print(f"\n[{total}] Fetching {date_str}...", flush=True)

        try:
            result = subprocess.run(
                ["python3", "scripts/data_collection/finnish/fetch.py", date_str],
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                success += 1
                # Extract player count from output
                for line in result.stdout.split('\n'):
                    if 'Generated data for' in line:
                        print(f"  ✓ {line.strip()}")
                        break
            else:
                failed += 1
                print(f"  ✗ Failed")

        except subprocess.TimeoutExpired:
            failed += 1
            print(f"  ✗ Timeout")
        except Exception as e:
            failed += 1
            print(f"  ✗ Error: {e}")

    print(f"\n{'='*60}")
    print(f"Season fetch complete!")
    print(f"Total: {total}, Success: {success}, Failed: {failed}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
