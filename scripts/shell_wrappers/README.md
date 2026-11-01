# Older shell wrappers

The maintained Finnish fetcher accepts a date or inclusive date range directly; use [Data pipeline](../../docs/DATA_PIPELINE.md) rather than a shell date loop.

The wrappers in this directory include dated defaults and one-off historical backfills. They are not part of the production workflow. If deliberately reusing one, inspect its arguments, paths and write behavior first, and supply explicit dates.

Do not recreate old aliases that refer to removed scripts or copy results into a second `data/` directory. Current published snapshots belong under `static/data/`.
