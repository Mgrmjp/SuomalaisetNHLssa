# UI conventions

[Documentation index](README.md)

## Current sources

| Concern | Source |
| --- | --- |
| Global tokens, font and dashboard background | [app.css](../src/app.css) |
| Shared surfaces, controls, tables and focus treatment | [design-system.css](../src/lib/styles/design-system.css) |
| Page shell and headings | [PageShell](../src/lib/components/ui/PageShell.svelte), [PageHeader](../src/lib/components/ui/PageHeader.svelte) |
| Shared controls and state panels | [Button](../src/lib/components/ui/Button.svelte), [ControlGroup](../src/lib/components/ui/ControlGroup.svelte), [ViewState](../src/lib/components/ui/ViewState.svelte), [Notice](../src/lib/components/ui/Notice.svelte) |
| Dashboard layout and totals | [Homepage](../src/routes/+page.svelte) |
| Player grouping and responsive grid | [PlayerList](../src/lib/components/game/PlayerList.svelte) |
| Player-card layout and interactions | [PlayerCard](../src/lib/components/game/PlayerCard.svelte), [PlayerCard.css](../src/lib/components/game/PlayerCard.css) |

Reuse these components and tokens instead of creating a second design system or copying an outdated component signature. The public app forces a light color scheme. The main bundled body font is Onest; see the CSS for fallbacks.

## Layout and content

- Navigation styling belongs to `NavTabs` so its surface, tab dimensions and mobile layout stay consistent across routes.
- Keep navigation and date controls together in the top toolbar; stack them on narrow screens. The calendar opens as an overlaid popover, with a visible close button, Escape/outside dismissal and focus return on explicit close or date selection.
- Keep the dashboard compact and player-card-first. Use the shared rail/page-gutter variables; let wide screens show useful content.
- Use Finnish labels and numeric dates. Preserve visible game/date context when showing yesterday's feature on today's pre-game view.
- Player-card matchups sit at the bottom with team logos flanking the score. Completed wins/losses add a subtle circular green/red glow centered at the bottom edge, with a text result label.
- Team logos identify teams. Keep ordinary text and actions neutral/blue; reserve result colors for semantic states with text or accessible descriptions.
- Position headings use distinct gradient stripes for forwards, defenders and goalies; retain their text labels so color is not the only distinction.
- The underlined player name and window icon open the player-details dialog; keep this action on the name rather than a separate card-footer button.
- Player details use compact stat grids and recent-game rows on the same ice-blue surfaces as the cards. Portalled overlays opt into `.dashboard-theme` to retain dashboard tokens outside the page wrapper. The dialog has an explicit close button, Escape dismissal, focus containment/return and background scroll locking.
- The player list uses a responsive CSS grid. Swiper remains a dependency but is not the current player-list layout.
- Use the game's recorded state to distinguish upcoming, live and completed results. Include scoreless participants and exclude scratches/unused backups.
- Empty states show future Finnish-team games and eligible recent news. News disappears when no verified story qualifies. See [Player data](PLAYER_DATA.md) and [News](DAILY_NEWS.md).

## Accessibility and interaction

Use semantic headings, real buttons/links and visible focus. Supply labels for icon-only controls. Ensure nested card actions do not accidentally flip the card, and keep keyboard flipping and modal close/focus behavior usable. Verify long Finnish names and narrow screens without horizontal page overflow.

Loading, initial failure and background-refresh failure need distinct treatment. Do not erase visible good data while a background request runs. Do not use color as the only indication of win/loss or freshness. Respect reduced-motion preferences when changing animation.

Test responsive behavior and interactions using [Testing](TESTING.md). This guide describes conventions and checks; it does not claim a completed accessibility certification or measured performance score.
