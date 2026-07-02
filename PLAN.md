# Finnish NHL Offseason Movement Tracker

## Summary

Add a homepage module tracking confirmed Finnish NHL team changes. V1 includes trades and free-agent signings between NHL teams, backfilled from the 2026 Stanley Cup Final onward and refreshed daily.

## Implementation Changes

- Build a Python collector using the official [NHL trade tracker](https://www.nhl.com/news/2026-27-nhl-trades), [free-agent tracker](https://www.nhl.com/news/topic/free-agency/free-agency-signings-nhl-2026-27), and pre-July trade-coverage articles.
- Parse NHL pages’ JSON-LD, match players exactly against the Finnish roster, and reject ambiguous matches.
- Include only confirmed `trade` and `free_agent` moves where the NHL team changes. Exclude rumors, re-signings, first NHL contracts, AHL/European moves, and retirements.
- Determine each offseason from the day after the Stanley Cup Final through the day before the next regular-season opener using NHL schedule data.
- Store validated output in `static/data/offseason-moves.json` with:
  - offseason year, window, update timestamp, and source status;
  - player ID/name/slug, position, old and new team;
  - move type, announcement date, and official source URL.
- Merge by a stable movement ID so repeated runs update existing records without duplication or lost history.
- Add the collector to the existing 06:00 UTC daily workflow. On fetch or parsing failure, retain the last valid file and report a workflow warning.

## Homepage

- Add a “Suomalaisten NHL-siirrot 2026” panel below the navigation/advertisement area.
- Show counts for total moves, trades, and free-agent signings.
- Display the five newest moves with player link, date, move-type badge, and old/new team logos joined by an arrow.
- Provide an accessible “Näytä kaikki” expansion for the full list.
- During the offseason, show the latest five by default; after opening day, retain a collapsed summary that users can expand.
- Show the last successful update and a stale-data notice if an active-offseason refresh is over 48 hours old.

## Test Plan

- Fixture-test trade and free-agent JSON-LD parsing, grouped signings, multi-player trades, Finnish diacritics, and source-date fallback.
- Verify exclusion of non-Finns, rumors, re-signings, first contracts, and non-NHL destinations.
- Test stable deduplication, offseason boundaries, malformed-source handling, and preservation of the last valid dataset.
- Test ordering, counts, five-item truncation, expansion behavior, empty state, and post-opening collapsed state.
- Run Vitest, Python collector tests, Svelte checks, linting, and a production build.
- Confirm the 2026 backfill includes known qualifying examples such as Joonas Korpisalo’s trade and Joel Kiviranta’s signing.

## Assumptions

- The homepage remains Finnish-language and no new route or navigation tab is added.
- V1 presents only the active or most recently completed offseason; no multi-year archive UI is included.
- Official NHL pages remain the sole publication source, and source-format changes fail safely rather than publishing uncertain data.
