# Testing

[Documentation index](README.md)

## Normal checks

| Command                | Scope                                                                       |
| ---------------------- | --------------------------------------------------------------------------- |
| `npm run docs:check`   | Engineering-doc links, anchors, source paths and npm commands               |
| `npm run lint`         | Biome for frontend and JavaScript scripts                                   |
| `npm run lint:python`  | Ruff for Python scripts; install development requirements                   |
| `npm run format:check` | Prettier for web/docs/shell files and Ruff formatting for Python; no writes |
| `npm run check`        | SvelteKit sync and Svelte type checking                                     |
| `npm test`             | Vitest suites under `src/`                                                  |
| `npm run validate`     | Documentation, formatting, JS/Python lint, Svelte checks and Vitest         |
| `npm run build:quick`  | Production build from existing data                                         |

Vitest's actual include pattern and mocks are in [vitest.config.js](../vitest.config.js). Current suites live in [src/lib/tests](../src/lib/tests/), including API handlers, snapshot validation, store recovery and news expiry. Files in the top-level `tests/` directory are not automatically included by that configuration.

Do not add a fixed test-count promise or coverage threshold to docs. Check actual runner output. A green unit suite does not prove the live APIs or current production revision are healthy.

## Focused frontend tests

```bash
npx vitest run src/lib/tests/dailyNews.test.js src/lib/tests/dailyNewsService.test.js
npx vitest run src/lib/tests/gameData-refresh.test.js src/lib/tests/gameData-dates.test.js
npm run test:roster
npm run test:standings
```

Snapshot-integrity tests validate repository data, so a failure can be a data regression rather than a code-test regression. CI separates the snapshot suite from its other Vitest tests.

## Focused Python tests

Use the virtual environment; these tests do not require live provider credentials:

```bash
.venv/bin/python3 scripts/test_check_docs.py
.venv/bin/python3 scripts/test_generate_daily_news.py
.venv/bin/python3 scripts/test_daily_update.py
.venv/bin/python3 scripts/test_check_deployment.py
.venv/bin/python3 scripts/data_collection/finnish/test_fetch_results.py
.venv/bin/python3 scripts/data_collection/test_realtime_poll.py
.venv/bin/python3 scripts/data_collection/finnish/test_sync_roster.py
.venv/bin/python3 scripts/data_collection/finnish/test_prospects_cache.py
```

The [Verify workflow](../.github/workflows/verify.yml) and collection workflows list their required guard suites. `npm run validate` runs Python lint but does not run every Python regression suite; invoke the affected ones explicitly.

## Browser verification

With a development server already running, `npm run test:browser` invokes [scripts/test-pages.js](../scripts/test-pages.js) with Puppeteer. This is a real browser check, separate from the default unit suite. It checks responsive pages and interactions. Surface geometry follows the active `--card-radius` token; player-card checks use the grid, flip control and name button. Recovery checks cover retained results/standings and keyboard retry through the shared `Notice` variant. Use `TEST_URL` to target another server and `UI_SCREENSHOT_DIR` to save screenshots.

Browser work should cover desktop/mobile layout, focus, card flipping/details, date navigation, and failed refresh states. Follow the current session's browser-access constraints when working with an agent.

Run `npm run test:ads:browser` against a running development server to check campaign expiry and image/link consistency across Finnish midnight, including pages loaded after the cutoff. Use `TEST_URL` to target a production preview. The check covers both mobile ad components and desktop slots at narrow and wide widths.

## Documentation validation

[scripts/check_docs.py](../scripts/check_docs.py) checks the engineering-documentation set; editorial content and font licensing files are excluded. It validates literal npm script names against [package.json](../package.json) without executing network collectors. Its behavior is covered by [scripts/test_check_docs.py](../scripts/test_check_docs.py).

Review prose against implementation when changing data formats or workflows. Link checking cannot establish that a provider's response, a roster membership or a screenshot is current.
