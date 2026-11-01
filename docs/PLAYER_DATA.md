# Player and game data

[Documentation index](README.md) · [Collection commands](DATA_PIPELINE.md)

## Roster and cache

The master [roster](../static/data/players/finnish-roster.json) and internal [Finnish cache](../scripts/data_collection/finnish/cache/finnish-players.json) are objects keyed by player ID, not arrays. The roster includes active and inactive players; its size is not the number playing on a particular date.

The cache builder and roster sync own these records. Preserve inactive-player `lastTeam` and `gamesPlayed`; the Node last-team prebuild can enrich them from career statistics. Do not replace known history with empty fields from a partial refresh.

## Daily snapshot

The Finnish fetcher writes `static/data/prepopulated/games/YYYY-MM-DD.json`. The top-level contract includes `date`, `games`, `players`, `total_players`, `generated_at` and `source`. The requested date must match the snapshot's date, and games/players must be arrays.

The date is the NHL schedule key. Kickoff times are timestamps; a game on one schedule date can appear after midnight on the following Finnish calendar date. Show the timezone-adjusted date as well as the time when listing future games.

| Record | Relevant fields |
| --- | --- |
| Game | `gameId`, `awayTeam`, `homeTeam`, `awayScore`, `homeScore`, `gameState`, `startTime`, `isOT`, `isSO` |
| Player identity | `playerId`, `game_id`, `name`, `team`, `opponent`, `position`, `jersey_number` |
| Skater performance | `goals`, `assists`, `points`, `time_on_ice`, `shots`, `plus_minus`, `penalty_minutes` |
| Goalie performance | `saves`, `shots_against`, `goals_against`, `save_percentage`, ice time where available |
| Game context on players | `game_status`, `game_result`, `game_score`, `game_venue`, `game_city` |

Some fields are optional or vary between old snapshots. See [fetch.py](../scripts/data_collection/finnish/fetch.py) and [dailyPlayers.js](../src/lib/utils/dailyPlayers.js) before tightening compatibility rules.

`total_players` counts collected records. The UI uses actual-participation rules, so that number need not equal the number of visible cards. Include scoreless skaters who played; exclude scheduled players, scratches and unused backup goalies.

## State and score semantics

- `FUT` and `PRE` mean scheduled/pre-game. A zero score is not a final result.
- `LIVE`, `CRIT` and `IRT` are in-progress states handled by the game-state helpers.
- `OFF` and `FINAL` indicate completion; the collector normalizes final states where appropriate.
- Game `awayScore` and `homeScore` have explicit sides. Player `game_score` and the displayed result badge are player-relative. Do not swap them merely to match the matchup label.

Formatting and state rules live in [gameFormatHelpers.mjs](../src/lib/utils/gameFormatHelpers.mjs) and [gameStateHelpers.mjs](../src/lib/utils/gameStateHelpers.mjs). Participation and scoring fallbacks live in [dailyPlayers.js](../src/lib/utils/dailyPlayers.js).

## Date discovery and previews

The browser's `prepopulatedDates` contains dates backed by snapshot files. Its broader `availableDates` also contains navigation-only break dates. Use the file-backed list for dated JSON requests to avoid missing-file requests.

[YesterdayResult](../src/lib/components/game/YesterdayResult.svelte) uses the exact previous calendar date and a randomly chosen completed game with Finnish participants. Missing or invalid data produces an unavailable state, not a fabricated result or a different day relabeled as yesterday. Today's live/completed results keep the normal player-card path.

Future-game previews use current-roster names and future timestamps; they do not guarantee confirmed lineups. The [upcoming selector](../src/lib/utils/upcomingFinnishGames.js) excludes completed/started games and deduplicates sources.

## Supplemental fields

Venue/city extraction currently uses schedule venue/home-team place data, with boxscore venue/location fallback and optional geocoding. There is no current `VENUE_CITY_MAP` table to maintain.

Empty-net and shorthanded counts are derived in the fetcher, including play-by-play/clip-URL heuristics. Missing media fields are not proof that a special goal did not occur. Existing count detection does not establish a validated event-level video-link feature. Verify a real response/fixture before adding such links.
