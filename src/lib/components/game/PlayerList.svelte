<script>
// @ts-nocheck
import { LayoutGrid, List, Minus, Plus } from 'lucide-svelte'
import { onMount } from 'svelte'
import { base } from '$app/paths'
import Button from '$lib/components/ui/Button.svelte'
import ControlGroup from '$lib/components/ui/ControlGroup.svelte'
import Notice from '$lib/components/ui/Notice.svelte'
import MobileAd from '$lib/components/ui/MobileAd.svelte'
import { getDailyFallbackNews } from '$lib/services/dailyNewsService.js'
import {
    currentBreak,
    currentDate,
    error,
    games,
    isLoading,
    players,
    refreshError,
    refreshSelectedDate,
    selectedDate,
    setDate,
} from '$lib/stores/gameData.js'
import { didParticipate, getDailyHighlights, sortDailyPlayers } from '$lib/utils/dailyPlayers.js'
import { formatDate } from '$lib/utils/dateUtils.js'
import { isDefense, isGoalie } from '$lib/utils/positionHelpers.js'
import { selectUpcomingFinnishGames } from '$lib/utils/upcomingFinnishGames.js'
import { previousCalendarDate, shouldShowYesterdayResult } from '$lib/utils/yesterdayResult.js'
import EmptyState from './EmptyState.svelte'
import PlayerCard from './PlayerCard.svelte'
import SkeletonPlayerCard from './SkeletonPlayerCard.svelte'

const { upcomingGames = [] } = $props()
const loadingResults = $derived($isLoading || !$selectedDate)
let refreshedUpcomingGames = $state(null)
const scheduleRefreshMinute = $derived(Math.floor($currentDate.getTime() / 60000))
const scheduledFinnishGames = $derived(
    selectUpcomingFinnishGames(
        refreshedUpcomingGames ?? upcomingGames,
        $selectedDate,
        $currentDate.getTime()
    )
)

let fallbackNews = $state([])
let newsLookupToken = 0
let viewMode = $state('cards')
const viewModeKey = 'player-view-mode'
onMount(() => {
    try {
        if (window.localStorage.getItem(viewModeKey) === 'compact') viewMode = 'compact'
    } catch {
        // Keep the default view when browser storage is unavailable.
    }
})

function setViewMode(mode) {
    viewMode = mode
    try {
        window.localStorage.setItem(viewModeKey, mode)
    } catch {
        // The selected view still works without persistence.
    }
}

let sortBy = $state('points')
let positionFilter = $state('all')
let expandedGroups = $state({ forwards: false, defenders: false, goalies: false })

function _handleRetry() {
    setDate($selectedDate)
}

const filteredPlayers = $derived(
    ($players || []).filter((player) => didParticipate(player, $games))
)
const highlights = $derived(
    new Map(
        getDailyHighlights(filteredPlayers, $games).map((highlight) => [
            `${highlight.playerId}-${highlight.gameId}`,
            highlight,
        ])
    )
)
const forwards = $derived(
    sortDailyPlayers(
        filteredPlayers.filter((p) => !isGoalie(p) && !isDefense(p)),
        sortBy
    )
)
const defenders = $derived(
    sortDailyPlayers(
        filteredPlayers.filter((p) => !isGoalie(p) && isDefense(p)),
        sortBy
    )
)
const goalies = $derived(
    sortDailyPlayers(filteredPlayers.filter(isGoalie), sortBy === 'name' ? 'name' : 'time')
)
const visibleGroups = $derived(
    [
        { key: 'forwards', title: 'Hyökkääjät', players: forwards },
        { key: 'defenders', title: 'Puolustajat', players: defenders },
        { key: 'goalies', title: 'Maalivahdit', players: goalies },
    ].filter(
        (group) =>
            (positionFilter === 'all' || positionFilter === group.key) && group.players.length
    )
)
const hasAnyPlayers = $derived(filteredPlayers.length > 0)
const yesterdayPreviewDate = $derived(
    !hasAnyPlayers &&
        !$currentBreak &&
        shouldShowYesterdayResult($selectedDate, formatDate($currentDate), $games?.games || [])
        ? previousCalendarDate($selectedDate)
        : ''
)

const dressedCount = $derived($players?.length || 0)

// Determine if there are no games today
const hasNoGames = $derived(!$isLoading && (!$games || !$games.games || $games.games.length === 0))

// Determine if we're in a break
const isBreak = $derived($currentBreak !== null)

// Determine which empty state to show
const emptyStateVariant = $derived.by(() => {
    if (isBreak && $currentBreak?.type === 'offseason') return 'offseason'
    if (isBreak) return 'break'
    if (
        ($games?.games || []).some((game) => ['FUT', 'PRE'].includes(game.gameState)) ||
        scheduledFinnishGames.some((game) => game.startTime?.slice(0, 10) === $selectedDate)
    )
        return 'upcoming'
    if (hasNoGames) return 'no-games'
    return 'no-scorers'
})

function attachFinnishPlayers(games, allPlayers) {
    return games.map((game) => ({
        ...game,
        finnishPlayers: allPlayers
            .filter((player) => String(player.game_id) === String(game.gameId))
            .map((player) => player.name?.default || player.name || player.fullName || '')
            .filter(Boolean),
    }))
}

const upcomingFinnishGames = $derived(
    selectUpcomingFinnishGames(
        [...attachFinnishPlayers($games?.games || [], $players || []), ...scheduledFinnishGames],
        $selectedDate,
        $currentDate.getTime()
    )
)
const relatedGamesLabel =
    'Tulevat ottelut suomalaispelaajien joukkueille. Kokoonpanot vahvistuvat lähempänä ottelua.'

// Keep the roster-based schedule current even if the page stays open overnight.
$effect(() => {
    const needsSchedule = !hasAnyPlayers && !isBreak
    scheduleRefreshMinute
    if (!needsSchedule) return
    const controller = new AbortController()
    async function refreshSchedule() {
        try {
            const response = await fetch(`${base}/data/upcoming-finnish-games.json`, {
                cache: 'no-store',
                signal: controller.signal,
            })
            if (!response.ok) return
            const snapshot = await response.json()
            if (!controller.signal.aborted && Array.isArray(snapshot?.games)) {
                refreshedUpcomingGames = snapshot.games
            }
        } catch {
            // Keep the last schedule on transient refresh failures.
        }
    }
    refreshSchedule()
    return () => controller.abort()
})

async function loadFallbackNews(selectedDateValue, variant) {
    const token = ++newsLookupToken

    if (!selectedDateValue || variant === 'break') {
        fallbackNews = []
        return
    }

    const newsItems = await getDailyFallbackNews(selectedDateValue)

    if (token !== newsLookupToken) return
    fallbackNews = newsItems
}

$effect(() => {
    scheduleRefreshMinute
    loadFallbackNews($selectedDate, emptyStateVariant)
})
</script>

{#if $refreshError && !$isLoading && !$error}
    <Notice variant="recovery">
        <span>Päivitys epäonnistui. Näytetään viimeisimmät tulokset.</span>
        {#snippet actions()}
            <Button onclick={refreshSelectedDate}>Yritä uudelleen</Button>
        {/snippet}
    </Notice>
{/if}

{#if loadingResults}
    <div class="scoring-list" aria-busy="true">
        <p class="scoring-list__loading-label" role="status">Ladataan pelaajien ottelutilastoja…</p>
        <div
            class="scoring-list__grid scoring-list__grid--loading"
            class:scoring-list__grid--compact={viewMode === 'compact'}
        >
            {#each [1, 2, 3, 4] as _}
                <SkeletonPlayerCard compact={viewMode === 'compact'} />
            {/each}
        </div>
    </div>
{:else if $error}
    <Notice variant="error">
        <span>{$error}</span>
        <Button onclick={_handleRetry}>Yritä uudelleen</Button>
    </Notice>
{:else if !hasAnyPlayers}
    <EmptyState
        variant={emptyStateVariant}
        relatedGames={upcomingFinnishGames}
        {relatedGamesLabel}
        newsItems={fallbackNews}
        lineupCount={dressedCount}
        yesterdayDate={yesterdayPreviewDate}
    />
{:else}
    <section
        id="scoringList"
        class="scoring-list"
        aria-label="Pelaajien ottelutilastot"
        data-view-mode={viewMode}
    >
        <div class="scoring-list__controls">
            <ControlGroup label="Pelaajanäkymä" class="scoring-list__view">
                <Button selected={viewMode === 'cards'} onclick={() => setViewMode('cards')}>
                    <LayoutGrid size={16} aria-hidden="true" /> Kortit
                </Button>
                <Button selected={viewMode === 'compact'} onclick={() => setViewMode('compact')}>
                    <List size={16} aria-hidden="true" /> Tiivis
                </Button>
            </ControlGroup>
            {#if filteredPlayers.length > 1}
                <label
                    >Pelipaikka
                    <select bind:value={positionFilter}>
                        <option value="all">Kaikki pelaajat</option>
                        <option value="forwards">Hyökkääjät</option>
                        <option value="defenders">Puolustajat</option>
                        <option value="goalies">Maalivahdit</option>
                    </select>
                </label>
                <label
                    >Järjestä
                    <select bind:value={sortBy}>
                        <option value="points">Pisteet</option>
                        <option value="goals">Maalit</option>
                        <option value="assists">Syötöt</option>
                        <option value="time">Peliaika</option>
                        <option value="name">Nimi</option>
                    </select>
                </label>
            {/if}
        </div>
        {#each visibleGroups as group, groupIndex (group.key)}
            <div class="scoring-list__section">
                {#if groupIndex > 0}
                    <MobileAd spot={`mobile-before-${group.key}`} betweenGroups />
                {/if}
                <h2 class="scoring-list__section-title" data-position={group.key}>
                    {group.title}
                </h2>
                <div
                    id={`players-${group.key}`}
                    class="scoring-list__grid"
                    class:scoring-list__grid--compact={viewMode === 'compact'}
                    class:scoring-list__grid--collapsed={viewMode === 'cards' &&
                        positionFilter === 'all' &&
                        !expandedGroups[group.key]}
                >
                    {#each group.players.slice(0, viewMode === 'cards' && positionFilter === 'all' && !expandedGroups[group.key] ? 8 : undefined) as player (`${player.playerId}-${player.game_id}`)}
                        <PlayerCard
                            {player}
                            compact={viewMode === 'compact'}
                            highlight={highlights.get(`${player.playerId}-${player.game_id}`)}
                        />
                    {/each}
                </div>
                {#if viewMode === 'cards' && positionFilter === 'all' && group.players.length > 2}
                    <button
                        type="button"
                        class="scoring-list__more"
                        class:scoring-list__more--mobile-only={group.players.length <= 8}
                        aria-expanded={expandedGroups[group.key]}
                        aria-controls={`players-${group.key}`}
                        onclick={() => {
                            expandedGroups[group.key] = !expandedGroups[group.key]
                        }}
                    >
                        {#if expandedGroups[group.key]}<Minus
                                size={16}
                                aria-hidden="true"
                            />{:else}<Plus size={16} aria-hidden="true" />{/if}
                        {expandedGroups[group.key]
                            ? 'Näytä vähemmän'
                            : `Näytä kaikki ${group.players.length} pelaajaa`}
                    </button>
                {/if}
            </div>
        {/each}
        {#if positionFilter !== 'all' && ((positionFilter === 'forwards' && !forwards.length) || (positionFilter === 'defenders' && !defenders.length) || (positionFilter === 'goalies' && !goalies.length))}
            <p class="scoring-list__empty">Ei pelaajia tällä pelipaikalla valittuna päivänä.</p>
        {/if}
    </section>
{/if}

<style>
.scoring-list {
    min-width: 0;
}
.scoring-list__loading-label {
    margin: 0 0 0.75rem;
    color: var(--color-muted);
    font-size: 0.8rem;
    font-weight: 600;
}
.scoring-list__controls {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    justify-content: flex-end;
    margin-bottom: 0.75rem;
}
.scoring-list__controls :global(.scoring-list__view) {
    margin-right: auto;
    align-self: flex-end;
}
.scoring-list__controls label {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    color: var(--color-muted);
    font-size: 0.75rem;
    font-weight: 600;
}
.scoring-list__controls select {
    min-height: 2.5rem;
    max-width: 100%;
    padding: 0.4rem 1.6rem 0.4rem 0.6rem;
    border: var(--card-border);
    border-radius: var(--card-radius-sm);
    background: var(--card-bg);
    color: var(--color-ink);
}
.scoring-list__section + .scoring-list__section {
    margin-top: 2.25rem;
}
.scoring-list__section-title {
    margin: 0 0 0.75rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #d5dce6;
    font-family: var(--font-display);
    font-size: 1.35rem;
    font-weight: 800;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}
.scoring-list__section-title[data-position='forwards'] {
    --position-stripe: linear-gradient(#1275ff, #9563ff);
}
.scoring-list__section-title[data-position='defenders'] {
    --position-stripe: linear-gradient(#0d9488, #38bdf8);
}
.scoring-list__section-title[data-position='goalies'] {
    --position-stripe: linear-gradient(#fbbf24, #f97316);
}
.scoring-list__section-title::before {
    content: '';
    width: 0.3rem;
    height: 1.1rem;
    border-radius: 3px;
    transform: skew(-18deg);
    background: var(--position-stripe);
}
.scoring-list__grid {
    display: grid;
    grid-template-columns: minmax(0, 1fr);
    gap: 1rem;
    align-items: stretch;
}
.scoring-list__grid.scoring-list__grid--compact {
    grid-template-columns: minmax(0, 1fr);
    gap: 0.5rem;
}
.scoring-list__empty {
    padding: 1rem;
    color: var(--color-muted);
}
.scoring-list__more {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.4rem;
    width: fit-content;
    max-width: 100%;
    min-height: 2.5rem;
    margin: 1.5rem auto 1rem;
    padding: 0.5rem 1rem;
    border: var(--card-border);
    border-radius: var(--card-radius-sm);
    background: var(--card-bg);
    color: var(--color-ink);
    font-size: 0.8rem;
    font-weight: 600;
    cursor: pointer;
}
.scoring-list__more:hover {
    background: var(--color-table-hover);
}
.scoring-list__more:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
}
@media (max-width: 767px) {
    .scoring-list__grid--loading:not(.scoring-list__grid--compact)
        :global(.card--skeleton:nth-child(n + 3)) {
        display: none;
    }
    .scoring-list__grid--collapsed :global(.game-player-card__container:nth-child(n + 3)) {
        display: none;
    }
    .scoring-list__controls :global(.scoring-list__view) {
        width: 100%;
    }
    .scoring-list__controls :global(.scoring-list__view .ui-control) {
        flex: 1;
        justify-content: center;
    }
    .scoring-list__controls label {
        flex: 1 1 0;
        min-width: 0;
        flex-direction: column;
        align-items: stretch;
    }
    .scoring-list__controls select {
        width: 100%;
    }
}
@media (min-width: 768px) {
    .scoring-list__more--mobile-only {
        display: none;
    }
}
@media (min-width: 768px) {
    .scoring-list__grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}
@media (min-width: 1024px) {
    .scoring-list__grid {
        grid-template-columns: repeat(3, minmax(0, 1fr));
    }
}
@media (min-width: 1280px) {
    .scoring-list__grid {
        grid-template-columns: repeat(4, minmax(0, 1fr));
    }
}
</style>
