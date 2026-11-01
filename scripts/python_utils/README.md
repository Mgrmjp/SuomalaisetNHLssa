# Diagnostic and export helpers

- [test_api.py](test_api.py) makes live NHL API requests; it is not a default offline regression suite.
- [check_season.py](check_season.py) inspects source availability for dates/seasons.
- [expand_games.py](expand_games.py) creates optional all-player exports from existing game IDs and can make many requests.

These are supporting tools, not the normal collection pipeline. Use [Data pipeline](../../docs/DATA_PIPELINE.md) for maintained operations and [Testing](../../docs/TESTING.md) for deterministic checks. Review arguments and write destinations before running diagnostics or backfills.
