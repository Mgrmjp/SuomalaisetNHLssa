# All-player season exports

[fetch_season_games.py](fetch_season_games.py) collects all-player game data for research/export use. It is separate from the Finnish-only daily snapshot path consumed by the homepage.

Use explicit dates when invoking older export tools; do not assume their no-argument season defaults track the current season. These exports can make many external requests and are not needed for normal frontend work.

Use [Data pipeline](../../../docs/DATA_PIPELINE.md) for maintained daily results and roster operations. The application season-stat prebuild is another distinct path under [scripts/prebuild](../../prebuild/).
