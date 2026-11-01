# Data collection

Use [Data pipeline](../../docs/DATA_PIPELINE.md) for collection commands and ownership. Shared API paths, timeouts and rate limits live in [config.py](config.py); the atomic JSON writer used by many collectors lives in [utils.py](utils.py).

- [finnish](finnish/README.md): daily Finnish NHL results, roster/cache reconciliation and prospect builders.
- [headshots](headshots/README.md): optional image conversion/download tools.
- [leagues](leagues/README.md): inputs for prospect-cache building.
- [season](season/README.md): all-player research exports, separate from the homepage data path.
- [realtime_poll.py](realtime_poll.py): the active GitHub Actions polling entry point.

See [Player data](../../docs/PLAYER_DATA.md) for record semantics. Do not copy files into a second `data/` directory: published snapshots live under the repository's `static/data/` directory.
