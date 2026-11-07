# Suomalaiset NHL:ssä

A Finnish NHL dashboard for daily player performances, official standings, teams and season scoring leaders. The site is built with Svelte 5, SvelteKit 2 and Tailwind CSS 4, then published as static files to GitHub Pages.

Live site: [suomalaisetnhlssa.fi](https://suomalaisetnhlssa.fi).

## Start locally

Use Linux Node/npm when working in WSL. CI uses Node 25; Python collectors run on Python 3.10 or newer.

```bash
npm ci
npm run dev
```

The dev server uses `http://localhost:3000`. Existing snapshots work without API keys or Python setup. See [Development](docs/DEVELOPMENT.md) before collecting data or running a full production build.

## Common commands

| Task                                       | Command               |
| ------------------------------------------ | --------------------- |
| Develop against existing data              | `npm run dev`         |
| Build without fetching data                | `npm run build:quick` |
| Build with season-stat prebuild collection | `npm run build`       |
| Preview the build on port 4173             | `npm run preview`     |
| Check documentation                        | `npm run docs:check`  |
| Check Svelte types                         | `npm run check`       |
| Run Vitest                                 | `npm test`            |
| Run lint, type checks and tests            | `npm run validate`    |

`package.json` is the command source of truth. `npm run build` automatically runs `prebuild`; `build:quick` skips that network step.

## How updates reach the site

Python collectors save JSON snapshots under `static/data/`. Scheduled GitHub Actions commit data and publish a static build. The browser refreshes published snapshots; it does not collect live results from the NHL API itself. Local data changes are not automatically deployed.

## Documentation

Start at the [documentation index](docs/README.md) for setup, configuration, architecture, data operations, deployment, testing and UI conventions. [AGENTS.md](AGENTS.md) adds repository-specific instructions for coding agents and WSL tooling.

Editorial Markdown under `content/` is website content, not development documentation.
