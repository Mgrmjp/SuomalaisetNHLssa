<script>
// @ts-nocheck
import { base } from '$app/paths'
import TeamLogo from '$lib/components/ui/TeamLogo.svelte'
import { formatFinnishDate } from '$lib/utils/dateUtils.js'

const { movesData } = $props()

let _expanded = $state(false)

const COLLAPSED_MOVE_LIMIT = 5

const moves = $derived(movesData?.moves || [])
const totalMoves = $derived(moves.length)
const tradeCount = $derived(moves.filter((m) => m.moveType === 'trade').length)
const faCount = $derived(moves.filter((m) => m.moveType === 'free_agent').length)
const visibleMoves = $derived(_expanded ? moves : moves.slice(0, COLLAPSED_MOVE_LIMIT))
const hasMore = $derived(moves.length > COLLAPSED_MOVE_LIMIT)
const hiddenMoveCount = $derived(_expanded ? 0 : Math.max(0, totalMoves - COLLAPSED_MOVE_LIMIT))
const offseasonYear = $derived(movesData?.offseasonYear || 2026)
const updatedAt = $derived(movesData?.updatedAt || '')
const windowEnd = $derived(movesData?.window?.end || '')

const isStale = $derived.by(() => {
    if (!updatedAt || !windowEnd) return false
    const now = new Date()
    const seasonStart = new Date(`${windowEnd}T00:00:00`)
    if (now > seasonStart) return false
    const lastUpdate = new Date(updatedAt)
    const hoursSince = (now - lastUpdate) / (1000 * 60 * 60)
    return hoursSince > 48
})

const formattedUpdate = $derived.by(() => {
    if (!updatedAt) return ''
    try {
        const d = new Date(updatedAt)
        return formatFinnishDate(d, { showYear: false, showWeekday: false })
    } catch {
        return updatedAt
    }
})

function formatMoveDate(dateStr) {
    if (!dateStr) return ''
    try {
        const d = new Date(`${dateStr}T00:00:00`)
        return formatFinnishDate(d, { showYear: false, showWeekday: false })
    } catch {
        return dateStr
    }
}

function moveTypeLabel(type) {
    return type === 'trade' ? 'Trade' : 'Vapaa agentti'
}

function countLabel(count, singular, partitive) {
    return `${count} ${count === 1 ? singular : partitive}`
}

function toggleExpand() {
    _expanded = !_expanded
}
</script>

<section class="panel panel--moves" aria-labelledby="moves-title">
    <div class="panel__inner">
        <div class="panel__eyebrow rink-divider">Siirrot</div>
        <div class="moves-header">
            <div class="moves-header__copy">
                <h2 id="moves-title" class="moves-header__title">
                    Suomalaisten NHL-siirrot {offseasonYear}
                </h2>
                <p class="moves-header__sub">
                    {countLabel(totalMoves, 'siirto', 'siirtoa')} ·
                    {countLabel(tradeCount, 'pelaajakauppa', 'pelaajakauppaa')} ·
                    {countLabel(faCount, 'vapaan agentin siirto', 'vapaan agentin siirtoa')}
                </p>
            </div>
            {#if hasMore && _expanded}
                <button
                    type="button"
                    class="moves-header__toggle"
                    onclick={toggleExpand}
                    aria-expanded={_expanded}
                    aria-controls="moves-list"
                >
                    {_expanded ? 'Piilota' : 'Näytä kaikki'}
                </button>
            {/if}
        </div>

        {#if isStale}
            <div class="moves-stale" role="alert">
                Tiedot voivat olla vanhentuneet (päivitetty {formattedUpdate})
            </div>
        {/if}

        {#if totalMoves === 0}
            <div class="moves-empty">
                Ei vahvistettuja siirtoja vielä. Tiedot päivittyvät offseason-kauden aikana.
            </div>
        {:else}
            <div id="moves-list" class="moves-list">
                {#each visibleMoves as move (move.moveId)}
                    <div class="move-row">
                        <div class="move-row__date">{formatMoveDate(move.date)}</div>
                        <div class="move-row__body">
                            <div class="move-row__player-line">
                                <a
                                    href="{base}/pelaajat/{move.playerSlug}/"
                                    class="move-row__name"
                                >
                                    {move.playerName}
                                </a>
                                <span class="move-row__badge" class:move-row__badge--trade={move.moveType === 'trade'}>
                                    {moveTypeLabel(move.moveType)}
                                </span>
                            </div>
                            <div class="move-row__teams">
                                <div class="move-row__team">
                                    <TeamLogo team={move.oldTeam} size="28" />
                                    <span class="move-row__abbrev">{move.oldTeam}</span>
                                </div>
                                <svg class="move-row__arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M5 12h14M12 5l7 7-7 7" stroke-linecap="round" stroke-linejoin="round" />
                                </svg>
                                <div class="move-row__team">
                                    <TeamLogo team={move.newTeam} size="28" />
                                    <span class="move-row__abbrev">{move.newTeam}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                {/each}
                {#if hiddenMoveCount > 0}
                    <button
                        type="button"
                        class="moves-more"
                        onclick={toggleExpand}
                        aria-expanded={_expanded}
                        aria-controls="moves-list"
                    >
                        ja {hiddenMoveCount} lisää
                    </button>
                {/if}
            </div>
        {/if}

        {#if updatedAt}
            <div class="moves-footer">
                Päivitetty {formattedUpdate}
            </div>
        {/if}
    </div>
</section>

<style>
    .panel--moves {
        position: relative;
        overflow: hidden;
        background: var(--card-bg);
        border: var(--card-border);
        border-radius: var(--card-radius);
        box-shadow: none;
        backdrop-filter: none;
        width: 100%;
        max-width: var(--rail-max);
        margin: 0 auto;
    }

    .panel__inner {
        padding: var(--card-padding-y, 1.25rem) var(--card-padding-x, 1.5rem);
        text-align: center;
    }

    .panel__eyebrow {
        margin-bottom: 0.75rem;
    }

    .moves-header {
        display: grid;
        justify-items: center;
        gap: 0.6rem;
    }

    .moves-header__copy {
        min-width: 0;
        max-width: 34rem;
    }

    .moves-header__title {
        margin: 0;
        color: var(--color-ink);
        font-size: 1.05rem;
        font-weight: 800;
        line-height: 1.25;
    }

    .moves-header__sub {
        margin: 0.15rem 0 0;
        color: var(--color-muted);
        font-size: 0.82rem;
    }

    .moves-header__toggle {
        color: #475467;
        font-size: 0.78rem;
        font-weight: 700;
        background: transparent;
        border: 1px solid rgba(16, 24, 40, 0.12);
        border-radius: 0;
        padding: 0.3rem 0.7rem;
        cursor: pointer;
        transition: background 0.15s ease, color 0.15s ease;
    }

    .moves-header__toggle:hover {
        background: #f7f8fa;
        color: var(--accent);
    }

    .moves-stale {
        margin-top: 0.5rem;
        padding: 0.5rem 0.75rem;
        background: rgba(234, 179, 8, 0.1);
        border: 1px solid rgba(234, 179, 8, 0.3);
        border-radius: 0;
        color: #92400e;
        font-size: 0.82rem;
    }

    .moves-empty {
        margin-top: 0.75rem;
        color: var(--color-muted);
        font-size: 0.9rem;
    }

    .moves-list {
        margin-top: 0.75rem;
        margin-inline: auto;
        width: min(100%, 34rem);
        display: flex;
        flex-direction: column;
        gap: 0;
    }

    .move-row {
        display: grid;
        grid-template-columns: 4.5rem 1fr;
        gap: 0.75rem;
        align-items: center;
        padding: 0.65rem 0.25rem;
        border-bottom: 1px solid rgba(16, 24, 40, 0.05);
    }

    .move-row:last-child {
        border-bottom: none;
    }

    .moves-more {
        appearance: none;
        border: 0;
        background: transparent;
        padding: 0.6rem 0.25rem 0.15rem;
        color: var(--color-muted);
        font-size: 0.82rem;
        font-weight: 700;
        cursor: pointer;
    }

    .moves-more:hover {
        color: var(--accent);
    }

    .move-row__date {
        color: var(--color-muted);
        font-size: 0.78rem;
        font-variant-numeric: tabular-nums;
    }

    .move-row__body {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.3rem;
        min-width: 0;
    }

    .move-row__player-line {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        min-width: 0;
    }

    .move-row__name {
        color: var(--color-ink);
        font-size: 0.92rem;
        font-weight: 700;
        text-decoration: none;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .move-row__name:hover {
        color: var(--accent);
        text-decoration: underline;
    }

    .move-row__badge {
        flex-shrink: 0;
        display: inline-flex;
        align-items: center;
        padding: 0.15rem 0.5rem;
        border-radius: 0;
        font-size: 0.7rem;
        font-weight: 700;
        background: rgba(16, 185, 129, 0.12);
        color: #065f46;
    }

    .move-row__badge--trade {
        background: rgba(71, 84, 103, 0.1);
        color: #344054;
    }

    .move-row__teams {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
    }

    .move-row__team {
        display: flex;
        align-items: center;
        gap: 0.3rem;
    }

    .move-row__abbrev {
        color: var(--color-muted);
        font-size: 0.78rem;
        font-weight: 600;
    }

    .move-row__arrow {
        width: 1rem;
        height: 1rem;
        color: var(--color-muted);
        flex-shrink: 0;
    }

    .moves-footer {
        margin-top: 0.75rem;
        padding-top: 0.5rem;
        border-top: 1px solid rgba(16, 24, 40, 0.06);
        color: var(--color-muted);
        font-size: 0.78rem;
    }

    @media (max-width: 767px) {
        .panel__inner {
            padding: 0.9rem;
        }

        .move-row {
            grid-template-columns: 3.5rem 1fr;
            gap: 0.5rem;
        }
    }

    @media (max-width: 420px) {
        .move-row {
            grid-template-columns: 1fr;
            justify-items: center;
            padding: 0.75rem 0.25rem;
        }

        .move-row__date {
            font-size: 0.72rem;
        }

        .move-row__player-line,
        .move-row__teams {
            max-width: 100%;
        }

        .move-row__name {
            max-width: 13rem;
        }
    }
</style>
