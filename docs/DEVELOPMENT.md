# Development

[Documentation index](README.md)

## Setup

Use a Linux shell and Linux Node/npm in WSL. The configured dev port is 3000, not Vite's default port. CI currently uses Node 25; Python workflows use Python 3.10.

```bash
npm ci
npm run dev
```

The app serves the checked-in snapshots without credentials. To run Python collectors or Python lint/tests:

```bash
python3 -m venv .venv
.venv/bin/python3 -m pip install -r scripts/data_collection/requirements.txt -r requirements-dev.txt
```

Optional headshot conversion also needs Pillow. Optional background removal has its own dependency in the headshot sync implementation; it is not required to run the dashboard.

For API keys and deliberate overrides, see [Configuration](CONFIGURATION.md). Preserve existing local credentials when updating `.env.local`; do not overwrite it blindly with the template.

## Edit and validate

Follow [Coding standards and structure](CODING_STANDARDS.md) for formatter ownership, naming and file placement. Run `npm run format` before validation; `npm run format:check` checks formatting without changing files.

1. Inspect current behavior and preserve unrelated worktree changes.
2. Make a focused change using the existing components and data boundaries.
3. Run the checks appropriate to that change in [Testing](TESTING.md).
4. Update the relevant guide and run `npm run docs:check`.
5. Review the diff before committing. A local build or local data refresh does not publish the site.

In a pull request, explain the concrete problem, resulting behavior and relevant validation. For data changes, identify the collector and date window.

Use `npm run build:quick` for a production build against existing data. `npm run build` invokes the Node prebuild collectors first and may contact external services or modify data files. `npm run preview` serves the generated build on port 4173.

Use [Data pipeline](DATA_PIPELINE.md) for collection commands rather than old one-off wrappers. Use [UI conventions](UI.md) for layout and component work.

## WSL tooling

The repository's [agent instructions](../AGENTS.md#wsl-file-access) describe UNC atomic-write limitations. Run writes and project commands inside WSL; Windows Node cannot use Linux `node_modules` binaries.

## Where to work

- Pages and build-time loads: [src/routes](../src/routes/).
- Shared components, stores, services and helpers: [src/lib](../src/lib/).
- Vitest suites: [src/lib/tests](../src/lib/tests/).
- Collectors and Python regression tests: [scripts](../scripts/).
- Published data: [static/data](../static/data/README.md).
- Editable articles: [content](../content/); these are website content.
