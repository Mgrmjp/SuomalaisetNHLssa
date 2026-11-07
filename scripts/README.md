# Scripts

The maintained command reference is [Data pipeline](../docs/DATA_PIPELINE.md). Use [Development](../docs/DEVELOPMENT.md) for dependencies and [Testing](../docs/TESTING.md) for validation.

| Directory or entry | Role |
| --- | --- |
| [data_collection](data_collection/README.md) | Python sources, shared configuration, validation and snapshot writers |
| [prebuild](prebuild/) | Node season-stat and inactive-player enrichment |
| [daily_update.sh](daily_update.sh) | Cache refresh, dated results and news collection; not the complete deployment workflow |
| [realtime_poll.py](data_collection/realtime_poll.py) | Active GitHub Actions results polling and final-result recovery |
| [update_prospects.sh](update_prospects.sh) | Rankings and prospect-cache refresh |
| [check_deployment.py](check_deployment.py) | Published/artifact revision checks |
| [python_utils](python_utils/README.md) | Live API diagnostics and optional research exports |
| [shell_wrappers](shell_wrappers/README.md) | Optional date-range and terminal-summary helpers; prefer the maintained collector entry point |

Run from the repository root. Collectors can write tracked data and contact external services; a file named `test_api.py` is a live diagnostic, not automatically a deterministic unit test.
