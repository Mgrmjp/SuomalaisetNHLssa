# Official NHL standings

The standings view reads `static/data/standings.json`, collected from
`https://api-web.nhle.com/v1/standings/now`. Dashboard date selection does not
change standings. Division, conference, and league order use official ranks.

`npm run data:standings` refreshes once an hour; append `-- --force` to bypass
that interval. The daily workflow forces a refresh. The realtime workflow checks
every ten minutes, refreshes hourly, and forces a refresh after game data changes.
Its existing GitHub Pages build publishes the updated snapshot.

The collector validates 32 teams, consistent seasons/dates, ranks, and records
before atomically replacing the snapshot. Failures preserve the previous file.
The UI shows source date and successful fetch time, warns after three hours, and
keeps last-good rows when a refresh fails. The refresh button reloads the deployed
snapshot with a cache-busting query; browsers do not collect NHL data directly.

Unplayed teams have no percentage or per-game goal rates. Unavailable optional
statistics show a dash. Playoff position highlights are provisional; only
official clinch indicators mean qualification.

Run `npm run test:standings` for collector and adapter tests. Run
`npm run test:browser` against a running dev server for public responsive checks,
card interactions, and standings failure states. Set `TEST_URL` for another
server and `UI_SCREENSHOT_DIR` to save review screenshots.
