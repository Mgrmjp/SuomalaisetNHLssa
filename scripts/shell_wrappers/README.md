# Optional shell helpers

The maintained Finnish fetcher accepts a date or inclusive date range directly; use [Data pipeline](../../docs/DATA_PIPELINE.md) rather than a shell date loop.

- [fetch-finnish-games.sh](fetch-finnish-games.sh) loops over dates using the maintained fetcher. Supply explicit start and end dates; its default start date is historical.
- [view_week_summary.sh](view_week_summary.sh) prints a terminal summary from the last seven days of local snapshots and requires `jq`.

These helpers are not part of the production workflow. Prefer the maintained fetcher's inclusive date-range support for collection.

Do not recreate old aliases that refer to removed scripts or copy results into a second `data/` directory. Current published snapshots belong under `static/data/`.
