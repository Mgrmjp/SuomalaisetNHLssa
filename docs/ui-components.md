# Shared public UI

Use the components in `src/lib/components/ui` for public pages. Their visual
rules live in `src/lib/styles/design-system.css` and use the shared app tokens.
Keep feature-specific content and data handling in the consuming view.

- `PageShell`, `PageHeader`, and `Card`: page layout, headings, and surfaces.
- `Button`: native button attributes and handlers; defaults to `type="button"`.
  Use `variant="primary"` for a primary action and `selected={boolean}` for
  toggles. Selected state controls both appearance and `aria-pressed`.
- `ControlGroup`: labelled groups of controls; `scrollable` keeps navigation in
  one horizontally scrollable row. Navigation children remain native links.
- `DataTable`: pass a required `caption` and native `thead`/`tbody` children.
  It provides the hidden caption and labelled, keyboard-focusable scroll region.
  Use native column headers with `scope="col"`. Table contents stay in the view.
- `Notice`: information, warning, or error content. Errors use `role="alert"`;
  other notices use `role="status"`.
- `ViewState`: loading or empty/unavailable content with optional `title`,
  `message`, children, and an `actions` snippet. `busy` uses the shared loader
  with one status announcement.
- `ViewMetadata`: source and update information in a consistent footer.
- `LoadingSpinner`: optional reactive `message`; `announce={false}` allows an
  enclosing status region to handle the announcement.

Keep size, border, radius, color, and focus rules in the shared tokens rather
than copying them into routes. Reserve local styling for feature layout, such
as standings identity columns. Campaign artwork under `/ads` keeps its own
visual rules.

`npm run test:browser` checks public pages at 375, 768, and 1440 pixels, keyboard
controls and scrolling, empty states, and standings loading/retry behavior.

The temporary `PROSPECTS_ENABLED` switch in `src/lib/config/features.js` hides
Lupaukset and its draft/scouting pages from navigation and the sitemap, and
redirects direct routes to the homepage. Set it to `true` and rebuild to restore
the section.
