# Official standings

[Documentation index](README.md)

The standings view reads [static/data/standings.json](../static/data/standings.json), collected from the NHL standings endpoint. Dashboard date navigation does not change this dataset. Division, conference and league positions use official ranks rather than a client-side points-only sort.

## Refresh

```bash
npm run data:standings
npm run data:standings -- --force
npm run test:standings
```

The first command uses the collector's hourly refresh interval. `--force` bypasses it. The daily workflow forces a refresh; the realtime workflow checks hourly and forces refresh after result updates. See [Deployment](DEPLOYMENT.md) for publication.

The [collector](../scripts/data_collection/fetch_standings.py) validates team coverage, consistent season/date, ranks and records before atomic replacement. Source failures preserve the previous file. The [client adapter](../src/lib/services/standingsService.js) validates the published snapshot again and preserves official ordering.

## UI behavior

The view shows source date and successful fetch time, and warns after three hours. Failed refreshes retain the last good rows. A refresh button reloads the published snapshot; it does not fetch standings directly from the NHL in the browser.

Unplayed teams have no percentage/per-game rate. Missing optional values show a dash. Playoff-position treatment is provisional; only official clinch indicators establish qualification.

Use [Testing](TESTING.md) for responsive/browser checks and failure-state coverage.
