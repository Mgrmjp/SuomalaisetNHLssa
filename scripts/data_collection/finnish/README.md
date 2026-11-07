# Finnish NHL collectors

[Data pipeline](../../../docs/DATA_PIPELINE.md) owns the command reference. [Player data](../../../docs/PLAYER_DATA.md) describes ID-keyed roster/cache records and dated game snapshots.

The main path is [build_cache.py](build_cache.py) → [fetch.py](fetch.py), with [sync_roster.py](sync_roster.py) publishing roster updates and preserving inactive-player history. A date or inclusive range can be passed directly to the fetcher; no shell date loop is required.

Upcoming-game, move, preseason, rankings and prospect-cache collectors are separate scripts. Their presence does not imply the corresponding public section is enabled; see [Architecture](../../../docs/ARCHITECTURE.md#public-sections).

The active scheduled results poller is [../realtime_poll.py](../realtime_poll.py). See [Deployment](../../../docs/DEPLOYMENT.md) for the GitHub Actions and Pages workflow.
