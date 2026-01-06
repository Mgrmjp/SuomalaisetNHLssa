#!/usr/bin/env python3
"""
Fetch full season data for Finnish NHL players.
"""
import sys
import subprocess
import time
from datetime import datetime, timedelta

START_DATE = "2025-10-01"
END_DATE = "2026-01-05"
PER_DATE_TIMEOUT = 300  # 5 minutes per date
RETRY_FAILED = True  # Retry failed dates at the end
RETRY_DELAY = 5  # seconds between retries

def date_range(start, end):
    """Generate list of dates from start to end inclusive."""
    current = datetime.strptime(start, "%Y-%m-%d").date()
    end_date = datetime.strptime(end, "%Y-%m-%d").date()
    while current <= end_date:
        yield current.strftime("%Y-%m-%d")
        current += timedelta(days=1)

def fetch_date(date_str):
    """Fetch data for a single date, return (success, output)."""
    try:
        result = subprocess.run(
            ["python3", "scripts/data_collection/finnish/fetch.py", date_str],
            capture_output=True,
            text=True,
            timeout=PER_DATE_TIMEOUT
        )

        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'Generated data for' in line:
                    return True, line.strip()
            return True, "OK"
        else:
            return False, f"Exit code {result.returncode}"

    except subprocess.TimeoutExpired:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)

def main():
    total = 0
    success = 0
    failed = 0
    failed_dates = []

    # Calculate total days for progress display
    total_days = sum(1 for _ in date_range(START_DATE, END_DATE))

    print("=" * 60)
    print(f"Fetching from {START_DATE} to {END_DATE}")
    print(f"Total: {total_days} days | Timeout: {PER_DATE_TIMEOUT}s per date")
    print("=" * 60)

    for date_str in date_range(START_DATE, END_DATE):
        total += 1
        print(f"\n[{total}/{total_days}] Fetching {date_str}...", flush=True)

        ok, msg = fetch_date(date_str)

        if ok:
            success += 1
            print(f"  ✓ {msg}")
        else:
            failed += 1
            failed_dates.append(date_str)
            print(f"  ✗ {msg}")

        # Brief pause between dates
        time.sleep(1)

    # Retry failed dates
    if RETRY_FAILED and failed_dates:
        print(f"\n{'='*60}")
        print(f"Retrying {len(failed_dates)} failed dates...")
        print(f"{'='*60}")

        for date_str in failed_dates[:]:  # Copy to modify during iteration
            print(f"\n[RETRY] Fetching {date_str}...", flush=True)
            time.sleep(RETRY_DELAY)

            ok, msg = fetch_date(date_str)

            if ok:
                success += 1
                failed -= 1
                failed_dates.remove(date_str)
                print(f"  ✓ {msg}")
            else:
                print(f"  ✗ Still failed: {msg}")

    print(f"\n{'='*60}")
    print(f"Season fetch complete!")
    print(f"Total: {total}, Success: {success}, Failed: {failed}")

    if failed_dates:
        print(f"\nFailed dates ({len(failed_dates)}):")
        for d in failed_dates[:10]:
            print(f"  - {d}")
        if len(failed_dates) > 10:
            print(f"  ... and {len(failed_dates) - 10} more")

    print(f"{'='*60}")

    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
