# Deployment

[Documentation index](README.md)

## Supported production path

Production is a static SvelteKit build hosted on GitHub Pages. [svelte.config.js](../svelte.config.js) writes pages and assets to `build/`; the workflows upload that directory with GitHub's Pages actions. The custom site URL is `https://suomalaisetnhlssa.fi`.

There is no production Node/Python application server, systemd monitor or server-side API runtime on Pages. Vercel, Netlify and Cloudflare are not configured deployment paths in this repository.

## Workflows

Schedules below are the configured UTC cron expressions, not guaranteed execution times. GitHub can queue scheduled runs.

| Workflow                                                      | Trigger                          | Main responsibility                                                                                                       |
| ------------------------------------------------------------- | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| [Daily update](../.github/workflows/daily-update.yml)         | 06:00 UTC, push to main, manual  | Collect results and supporting data, sync roster, regenerate manifest, commit data, build and publish                     |
| [Realtime update](../.github/workflows/realtime-update.yml)   | Every ten minutes, manual        | Recover live/missing final results, refresh standings and hourly news, commit changes, check whether deployment is needed |
| [Prospects update](../.github/workflows/prospects-update.yml) | 07:00 UTC, manual                | Refresh rankings/prospect cache and commit outputs; no direct Pages deployment step                                       |
| [Data integrity](../.github/workflows/data-integrity.yml)     | 07:00 UTC, push to main, manual  | Validate and optionally fix prospect data; commit successful fixes                                                        |
| [Verify](../.github/workflows/verify.yml)                     | Pull requests and pushes to main | Documentation, frontend and Python checks                                                                                 |

Data-mutating workflows share the `data-updates` concurrency group. Inspect each YAML file for its exact commands and failure handling rather than assuming all collectors run in every workflow.

## Build and artifact checks

```bash
npm run build:quick
npm run preview
```

This builds existing snapshots without prebuild collection and previews them on port 4173. For the workflow-style build, `npm run build` invokes the Node prebuild collectors first.

[scripts/check_deployment.py](../scripts/check_deployment.py) records the artifact's Git revision in `build/data/deployment.json`. The publishing workflows use it to compare the live revision with the checkout and decide whether another deployment is required. Do not rely only on a successful collector log to establish that the live site has new data.

## Publishing a change

1. Validate the code and generated data using [Testing](TESTING.md).
2. Review and commit the complete intended snapshot, including manifest/source-cache changes where applicable.
3. Stage all generated tracked changes before rebasing. A mode change or unstaged generated file can prevent rebase.
4. Push the approved revision and inspect the actual Actions run and Pages deployment.
5. Verify both the published revision and the affected dated JSON on the live site.

A local build is not a deployment. Do not assume that a collector-only commit has published an artifact; use the explicit deployment steps and revision check as evidence.

Credentials are supplied through GitHub repository secrets. Current news collection references `TAVILY_API_KEY` and optional `OPENAI_API_KEY`; see [Configuration](CONFIGURATION.md). The static client must not receive these keys.

## Troubleshooting stale results

Trace the complete path: NHL response → saved dated snapshot → manifest → committed revision → Pages artifact → browser refresh. Check the failed workflow step, not just the overall badge. Preserve valid prior snapshots on source failures.

The browser's retry can reload only published files. It cannot repair a failed collection or deployment. If a published revision is correct but data is stale, inspect the artifact contents and collection timestamps. If data is correct locally but absent in production, inspect the commit/deploy steps.
