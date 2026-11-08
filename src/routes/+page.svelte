<script>
// @ts-nocheck

import {
    CalendarDays,
    CheckCircle,
    CircleDot,
    Database,
    Goal,
    Shield,
    Trophy,
    Users,
} from 'lucide-svelte'
import { onMount } from 'svelte'
import { replaceState } from '$app/navigation'
import { base } from '$app/paths'
import { page } from '$app/stores'
import DateControls from '$lib/components/game/DateControls.svelte'
import PlayerList from '$lib/components/game/PlayerList.svelte'
import AdContainer from '$lib/components/ui/AdContainer.svelte'
import NavTabs from '$lib/components/ui/NavTabs.svelte'
import TeamLogo from '$lib/components/ui/TeamLogo.svelte'
import {
    followsDefaultDate,
    games,
    isLoading,
    players,
    resetToDefault,
    selectedDate,
    setDate,
} from '$lib/stores/gameData.js'
import { didParticipate } from '$lib/utils/dailyPlayers.js'
import { formatFinnishDateWithRelative } from '$lib/utils/dateUtils.js'
import { fiGames } from '$lib/utils/finnishPlural.js'

/** @type {{ data: { initialDate: string, seo: { titleSuffix: string, description: string, summary: string, dateLabel: string, gameCount: number }, playoffStats: { season: string, skaters: Array<{ name: string, team: string, gamesPlayed: number, goals: number, assists: number, points: number }>, goalies: Array<{ name: string, team: string, gamesPlayed: number, wins: number, savePct: number }> } } }} */
const { data } = $props()
// Temporarily disabled; set to true to restore the homepage tracker.
const SHOW_PLAYOFF_TRACKER = false
const playoffStats = $derived(data.playoffStats)

const activeBreak = $derived.by(() => {
    const breaks = data.breaks || []
    const date = $selectedDate || data.initialDate
    if (!date || !breaks.length) return null
    return breaks.find((b) => date >= b.startDate && date <= b.endDate) || null
})

const participatingPlayers = $derived(
    ($players || []).filter((player) => didParticipate(player, $games))
)
const _totalGoals = $derived(
    participatingPlayers.reduce((sum, player) => sum + (Number(player.goals) || 0), 0)
)
const _totalAssists = $derived(
    participatingPlayers.reduce((sum, player) => sum + (Number(player.assists) || 0), 0)
)
const _totalPenaltyMinutes = $derived(
    participatingPlayers.reduce(
        (sum, player) => sum + (Number(player.penalty_minutes ?? player.penaltyMinutes) || 0),
        0
    )
)
const totalPlayers = $derived(participatingPlayers.length)
const _hasScoringPlayers = $derived(totalPlayers > 0)

function buildDateLabel(value) {
    if (!value) {
        return 'valitulle päivälle'
    }

    const { formatted, relative } = formatFinnishDateWithRelative(value, {
        showYear: true,
        showWeekday: true,
        longFormat: false,
    })

    return relative ? `${relative} (${formatted})` : formatted
}

const selectedDateSummary = $derived.by(() => {
    if (!$selectedDate && data.seo) {
        return {
            label: data.seo.dateLabel,
            count: data.seo.gameCount,
            summary: data.seo.summary,
        }
    }

    const gameIds = new Set(participatingPlayers.map((player) => String(player.game_id)))
    const count = gameIds.size
    const label = buildDateLabel($selectedDate)
    const summary = count > 0 ? `${fiGames(count)} ${label}` : `Ei otteluita ${label}`

    return { label, count, summary }
})

const _dynamicTitleSuffix = $derived.by(
    () => selectedDateSummary?.summary || 'suomalaisten NHL-ottelut'
)

const SEO_KEYWORDS =
    'suomi nhl, suomalaiset nhl-pelaajat, suomalaiset jääkiekkoilijat, nhl suomi, pistepörssi, live-tilastot, suomalaiset nhl:ssä'

const _metaDescription = $derived.by(() => {
    if (!$selectedDate && data.seo?.description) {
        return data.seo.description
    }

    const playerText =
        totalPlayers > 0
            ? `Seuraa ${totalPlayers} suomalaisen NHL-tilastoja.`
            : 'Seuraa suomalaisten NHL-matkaa.'

    return `${selectedDateSummary?.summary || 'Päivän ottelut'}. ${playerText} ${SEO_KEYWORDS}.`
})

let _showPlayoffStats = $state(false)

function togglePlayoffStats() {
    _showPlayoffStats = !_showPlayoffStats
}

function resetDashboard() {
    const url = new URL(window.location.href)
    url.searchParams.delete('date')
    replaceState(url, $page.state)
    resetToDefault()
}

function formatSavePct(value) {
    if (!Number.isFinite(value)) return '.---'
    return value.toFixed(3).replace(/^0/, '')
}

onMount(() => {
    const requested = new URL(window.location.href).searchParams.get('date')
    const parsed =
        requested && /^\d{4}-\d{2}-\d{2}$/.test(requested)
            ? new Date(`${requested}T00:00:00`)
            : null
    const valid =
        parsed &&
        !Number.isNaN(parsed.getTime()) &&
        `${parsed.getFullYear()}-${String(parsed.getMonth() + 1).padStart(2, '0')}-${String(parsed.getDate()).padStart(2, '0')}` ===
            requested &&
        parsed <= new Date()
    if (valid) setDate(requested)
    else if (!$selectedDate) resetToDefault()
    function syncDateToUrl(date) {
        if (!date) return
        const url = new URL(window.location.href)
        if (followsDefaultDate()) {
            if (!url.searchParams.has('date')) return
            url.searchParams.delete('date')
        } else {
            if (url.searchParams.get('date') === date) return
            url.searchParams.set('date', date)
        }
        replaceState(url, $page.state)
    }
    let ready = false
    let latestDate = ''
    const unsubscribe = selectedDate.subscribe((date) => {
        latestDate = date
        if (ready) syncDateToUrl(date)
    })
    // SvelteKit initializes its client router after the initial mount.
    const timer = setTimeout(() => {
        ready = true
        syncDateToUrl(latestDate)
    }, 0)
    return () => {
        clearTimeout(timer)
        unsubscribe()
    }
})
</script>

<svelte:head>
    <title>Suomi NHL - Suomalaiset NHL-pelaajat | {_dynamicTitleSuffix}</title>
    <meta name="description" content={_metaDescription} />
    <meta
        property="og:title"
        content="Suomi NHL - Suomalaiset NHL-pelaajat | {_dynamicTitleSuffix}"
    />
    <meta property="og:description" content={_metaDescription} />
    <meta name="keywords" content={SEO_KEYWORDS} />
    <meta property="og:url" content="https://suomalaisetnhlssa.fi/" />
    <meta
        name="robots"
        content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1"
    />
</svelte:head>

<div class="page-shell dashboard-bg">
    <div class="dashboard__toolbar">
        <div class="dashboard__nav"><NavTabs /></div>
        <div class="dashboard__date"><DateControls /></div>
    </div>

    <header class="hero-header">
        <div class="hero-header__inner">
            <button
                onclick={resetDashboard}
                class="logo-button"
                aria-label="Palaa etusivulle ja nollaa valinnat"
            >
                <img src={base + '/logo.svg'} alt="Suomalaiset NHL-pelaajat" class="logo-img" />
            </button>
            <h1 class="hero-title">Miten suomalaisilla kulkee NHL:ssä?</h1>
        </div>
        <p class="hero-subtitle">Tutki päivän ottelut, pisteet ja onnistumiset</p>
    </header>

    <div class="dashboard">
        <div class="dashboard__rail">
            <!-- Controls (date picker) -->
            {#if activeBreak && !$isLoading && totalPlayers === 0}
                <div class="dashboard__notice">
                    <section class="panel panel--break">
                        <div
                            class="panel__inner flex flex-col items-center justify-center text-center"
                        >
                            {#if activeBreak.type === 'offseason'}
                                <span class="break-emoji" role="img" aria-label="Offseason">☀️</span
                                >
                                <h2 class="break-title">Runkosarja alkaa pian!</h2>
                                <p class="break-meta">
                                    NHL on tauolla ({formatFinnishDateWithRelative(
                                        activeBreak.startDate
                                    ).formatted} - {formatFinnishDateWithRelative(
                                        activeBreak.endDate
                                    ).formatted})
                                </p>
                            {:else}
                                <span class="break-emoji" role="img" aria-label="Break">🏒</span>
                                <h3 class="break-title">{activeBreak.description}</h3>
                                <p class="break-meta">
                                    NHL on tauolla ({formatFinnishDateWithRelative(
                                        activeBreak.startDate
                                    ).formatted} - {formatFinnishDateWithRelative(
                                        activeBreak.endDate
                                    ).formatted})
                                </p>
                            {/if}
                        </div>
                    </section>
                </div>
            {/if}

            <!-- Navigation and its active content form one section. -->
            <section class="dashboard__results" aria-label="Tulokset ja tilastot">
                <div class="dashboard__active-stack">
                    <!-- Compact daily totals -->
                    {#if $isLoading}
                        <section
                            class="panel panel--hero"
                            aria-busy="true"
                            aria-label="Päivän yhteistilastot"
                        >
                            <div class="panel__inner">
                                <div class="hero-stats-header">
                                    <h2 class="panel__hero-heading">Päivän yhteistilastot</h2>
                                </div>
                                <div class="hero-stats-skeleton" aria-hidden="true">
                                    {#each [1, 2, 3, 4] as _}
                                        <div class="hero-stat-skel">
                                            <div class="hero-stat-skel__value"></div>
                                            <div class="hero-stat-skel__label"></div>
                                        </div>
                                    {/each}
                                </div>
                            </div>
                        </section>
                    {:else if _hasScoringPlayers}
                        <section class="panel panel--hero" aria-labelledby="hero-stats-title">
                            <div class="panel__inner">
                                <div class="hero-stats-header">
                                    <CalendarDays
                                        class="hero-stats-header__icon"
                                        aria-hidden="true"
                                    />
                                    <h2 id="hero-stats-title" class="panel__hero-heading">
                                        Päivän yhteistilastot
                                    </h2>
                                    <p class="panel__hero-sub">
                                        <span
                                            >{formatFinnishDateWithRelative(
                                                $selectedDate || data.initialDate
                                            ).formatted}</span
                                        >
                                        <span class="hero-game-count"
                                            >{fiGames(selectedDateSummary?.count || 0)}</span
                                        >
                                    </p>
                                </div>
                                <dl class="hero-stats">
                                    <div class="hero-stat">
                                        <dt class="hero-stat__label">Maalit</dt>
                                        <dd class="hero-stat__value">
                                            <Goal aria-hidden="true" />{_totalGoals}
                                        </dd>
                                    </div>
                                    <div class="hero-stat">
                                        <dt class="hero-stat__label">Syötöt</dt>
                                        <dd class="hero-stat__value">
                                            <CircleDot aria-hidden="true" />{_totalAssists}
                                        </dd>
                                    </div>
                                    <div class="hero-stat">
                                        <dt class="hero-stat__label">Jäähymin</dt>
                                        <dd class="hero-stat__value">
                                            <Shield aria-hidden="true" />{_totalPenaltyMinutes}
                                        </dd>
                                    </div>
                                    <div class="hero-stat">
                                        <dt class="hero-stat__label">Pelaajaa</dt>
                                        <dd class="hero-stat__value">
                                            <Users aria-hidden="true" />{totalPlayers}
                                        </dd>
                                    </div>
                                </dl>
                            </div>
                        </section>
                    {/if}

                    <!-- Player List -->
                    {#if !activeBreak || $isLoading || totalPlayers > 0}
                        <PlayerList upcomingGames={data.upcomingGames} />
                    {/if}

                    <!-- Playoff tracker — same card language -->
                    {#if SHOW_PLAYOFF_TRACKER}
                        <section class="panel panel--playoff" class:panel--active={activeBreak}>
                            <div class="panel__inner">
                                <div class="panel__eyebrow rink-divider">Pudotuspelit</div>
                                <div class="playoff-tracker__head">
                                    <div class="min-w-0">
                                        <h2 class="playoff-tracker__title">
                                            Pudotuspelien suomalaiset
                                        </h2>
                                        <p class="playoff-tracker__sub">
                                            NHL {playoffStats.season}
                                        </p>
                                    </div>
                                    <button
                                        type="button"
                                        class="playoff-tracker__toggle"
                                        onclick={togglePlayoffStats}
                                        aria-expanded={_showPlayoffStats}
                                        aria-controls="playoff-stats-panel"
                                    >
                                        {_showPlayoffStats ? 'Piilota' : 'Näytä'}
                                    </button>
                                </div>

                                {#if _showPlayoffStats}
                                    <div id="playoff-stats-panel" class="playoff-tracker__panel">
                                        {#if playoffStats.skaters.length > 0 || playoffStats.goalies.length > 0}
                                            <div class="playoff-tracker__list">
                                                {#if playoffStats.skaters.length > 0}
                                                    {#each playoffStats.skaters as player, index}
                                                        <div class="playoff-row">
                                                            <div class="playoff-row__rank">
                                                                {index + 1}
                                                            </div>
                                                            <div
                                                                class="playoff-row__player min-w-0"
                                                            >
                                                                <div
                                                                    class="playoff-row__player-line"
                                                                >
                                                                    <TeamLogo
                                                                        team={player.team}
                                                                        size="24"
                                                                    />
                                                                    <span class="playoff-row__name"
                                                                        >{player.name}</span
                                                                    >
                                                                </div>
                                                                <div class="playoff-row__meta">
                                                                    {player.gamesPlayed} ott. · {player.goals}+{player.assists}
                                                                </div>
                                                            </div>
                                                            <div class="playoff-row__stat">
                                                                {player.points} P
                                                            </div>
                                                        </div>
                                                    {/each}
                                                {/if}

                                                {#if playoffStats.goalies.length > 0}
                                                    {#each playoffStats.goalies as goalie}
                                                        <div class="playoff-row">
                                                            <div class="playoff-row__rank">MV</div>
                                                            <div
                                                                class="playoff-row__player min-w-0"
                                                            >
                                                                <div
                                                                    class="playoff-row__player-line"
                                                                >
                                                                    <TeamLogo
                                                                        team={goalie.team}
                                                                        size="24"
                                                                    />
                                                                    <span class="playoff-row__name"
                                                                        >{goalie.name}</span
                                                                    >
                                                                </div>
                                                            </div>
                                                            <div
                                                                class="playoff-row__stat playoff-row__stat--muted"
                                                            >
                                                                {goalie.wins} W · {formatSavePct(
                                                                    goalie.savePct
                                                                )} SV%
                                                            </div>
                                                        </div>
                                                    {/each}
                                                {/if}
                                            </div>
                                        {:else}
                                            <div class="playoff-tracker__empty">
                                                Pudotuspelitilastot päivittyvät tähän, kun
                                                suomalaispelaajille kertyy pelejä.
                                            </div>
                                        {/if}
                                    </div>
                                {/if}
                            </div>
                        </section>
                    {/if}
                </div>
            </section>

            <p class="dashboard__source">
                Tilastot: NHL:n viralliset lähteet · mukana myös pisteittä jääneet pelaajat. <a
                    href={base + '/tietoa'}>Tietoa datasta</a
                >
            </p>

            <!-- Ads follow the product content so navigation stays attached to its section. -->
            <div class="dashboard__ads">
                <AdContainer />
            </div>
        </div>
    </div>

    <footer class="page-footer">
        <a href={base + '/tietoa'} class="page-footer__link">Tietoa ja tietolähteet</a>
        <a href={base + '/tietoa#mainosilmoitus'} class="page-footer__link">Mainonta</a>
    </footer>
</div>

<style>
/* ============================================
       Dashboard shell — single centered product
       ============================================ */
.page-shell {
    position: relative;
    z-index: 1;
    width: min(calc(100% - 2 * var(--page-gutter)), var(--rail-max));
    max-width: var(--rail-max);
    margin: 0 auto;
    padding: 0.75rem 0 2rem;
}

.dashboard__toolbar {
    --toolbar-control-height: 2.5rem;
    --toolbar-radius: 14px;
    --toolbar-padding: 0.25rem;
    --card-radius-sm: calc(var(--toolbar-radius) - var(--toolbar-padding) - 1px);
    display: flex;
    flex-wrap: wrap;
    align-items: flex-start;
    justify-content: center;
    gap: 0.75rem 1rem;
    margin-bottom: 1.25rem;
}
.dashboard__nav {
    width: max-content;
    max-width: 100%;
    min-width: 0;
}
.dashboard__toolbar .dashboard__date :global(.date-controls__card) {
    padding: var(--toolbar-padding);
    border: 1px solid white;
    border-radius: var(--toolbar-radius);
    background: rgba(245, 250, 255, 0.96);
    box-shadow:
        0 5px 18px rgba(31, 83, 141, 0.2),
        0 0 0 1px #bdd9f7;
}
.dashboard__date {
    flex: 0 1 360px;
    width: min(100%, 360px);
    min-width: 0;
    margin: 0;
}
.dashboard__date :global(.date-controls__label) {
    display: none;
}
.dashboard__date :global(.date-controls__navigation-row) {
    grid-template-columns: 2.5rem minmax(0, 1fr) auto 2.5rem;
    gap: 0.25rem;
}
.dashboard__toolbar :global(.date-controls__nav-btn),
.dashboard__toolbar :global(.date-controls__picker-input),
.dashboard__toolbar :global(.date-controls__today-btn) {
    height: var(--toolbar-control-height);
    min-height: var(--toolbar-control-height);
    padding-block: 0;
    line-height: 1;
}
.dashboard__date :global(.date-controls__nav-btn) {
    width: 2.5rem;
}
.dashboard__date :global(.date-controls__today-btn) {
    padding-inline: 0.65rem;
}
.dashboard__source {
    margin: 0;
    text-align: center;
    color: var(--color-muted);
    font-size: 0.8rem;
    line-height: 1.5;
}
.dashboard__source a {
    color: var(--accent);
}

.dashboard {
    display: block;
}

.dashboard__rail {
    display: flex;
    flex-direction: column;
}

.dashboard__notice {
    margin-bottom: 2.25rem;
}

.dashboard__results {
    display: grid;
    gap: 1.5rem;
    margin-bottom: 2.25rem;
    min-width: 0;
}

.dashboard__active-stack {
    display: grid;
    gap: 1.25rem;
    min-width: 0;
}

.dashboard__ads {
    display: grid;
    gap: 2.25rem;
    margin-top: 2.25rem;
}

@media (max-width: 767px) {
    .dashboard__ads {
        display: none;
    }
}

/* ============================================
       Hero header
       ============================================ */
.hero-header {
    margin: 0 auto 1rem;
    text-align: center;
}

.hero-subtitle {
    margin: 0.3rem 0 0;
    color: var(--color-muted);
    font-size: 1rem;
    font-weight: 500;
}

.hero-header__inner {
    display: grid;
    justify-items: center;
    gap: 0.25rem;
    max-width: 100%;
    margin: 0 auto;
    padding: 0;
}

.hero-title {
    max-width: 100%;
    margin: 0;
    color: var(--color-ink);
    font-size: clamp(1.3rem, 2.6vw, 2rem);
    line-height: 1.15;
    font-weight: 800;
    letter-spacing: -0.01em;
    white-space: normal;
}

.logo-button {
    align-self: center;
    background: transparent;
    border: none;
    padding: 0;
    cursor: pointer;
    display: block;
    margin: 0 auto;
}

.logo-img {
    width: 2.5rem;
    height: 2.5rem;
    margin: 0 auto;
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.logo-button:hover .logo-img {
    transform: scale(1.05) rotate(-2deg);
}

/* ============================================
       Card — one base, four uses (controls, hero,
       playoff, info). Flat sections with shared border,
       radius, top accent, and padding scale.
       ============================================ */
.panel {
    position: relative;
    overflow: hidden;
    background: var(--card-bg);
    border: var(--card-border);
    border-radius: var(--card-radius);
    box-shadow: none;
    backdrop-filter: none;
    max-width: var(--rail-max);
    margin: 0 auto;
    width: 100%;
}

.panel::before {
    content: '';
    position: absolute;
    inset: 0 0 auto;
    height: 3px;
    display: none;
    background: var(--accent);
    opacity: 1;
}

.panel__inner {
    padding: var(--card-padding-y) var(--card-padding-x);
}

.panel__eyebrow {
    margin-bottom: 0.75rem;
}

/* Daily totals: compact header and a single row at every width. */
.panel--hero .panel__inner {
    display: grid;
    grid-template-columns: minmax(240px, 1.5fr) 4fr;
    align-items: center;
    padding: 0.5rem;
}

.hero-stats-header {
    position: relative;
    padding: 0.5rem 0.75rem 0.5rem 3.25rem;
}
.hero-stats-header :global(.hero-stats-header__icon) {
    position: absolute;
    left: 0.75rem;
    top: 50%;
    transform: translateY(-50%);
    width: 1.5rem;
    height: 1.5rem;
    color: var(--accent);
}

.panel__hero-heading {
    margin: 0;
    color: var(--color-ink);
    font-size: 0.95rem;
    line-height: 1.4;
    font-weight: 700;
}

.panel__hero-sub {
    display: flex;
    flex-wrap: wrap;
    gap: 0.25rem 0.75rem;
    margin: 0.25rem 0 0;
    color: var(--color-muted);
    font-size: 0.8rem;
    line-height: 1.4;
}

.hero-game-count {
    white-space: nowrap;
}

/* Break card — same family, just compact */
.panel--break {
    text-align: center;
}

.break-emoji {
    font-size: 1.75rem;
    line-height: 1;
}

.break-title {
    margin: 0.5rem 0 0.25rem;
    color: var(--color-ink);
    font-size: 1.1rem;
    font-weight: 800;
}

.break-meta {
    margin: 0;
    color: var(--color-muted);
    font-size: 0.9rem;
}

.hero-stats,
.hero-stats-skeleton {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    margin: 0;
    padding: 0;
}

.hero-stat,
.hero-stat-skel {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.25rem;
    min-width: 0;
    padding: 0.5rem 0.25rem;
    text-align: center;
}

.hero-stat__value :global(svg) {
    width: 1.5rem;
    height: 1.5rem;
    color: #52739d;
}

.hero-stat + .hero-stat,
.hero-stat-skel + .hero-stat-skel {
    border-left: var(--card-border);
}

.hero-stat__value {
    order: -1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.6rem;
    margin: 0;
    color: var(--color-ink);
    font-size: 1.65rem;
    font-weight: 800;
    line-height: 1.2;
    font-variant-numeric: tabular-nums;
}

.hero-stat__label {
    color: var(--color-muted);
    font-size: 0.75rem;
    font-weight: 600;
    line-height: 1.4;
}

.hero-stat-skel__value {
    width: 1.75rem;
    height: 1.75rem;
    background: var(--accent-ice);
}

.hero-stat-skel__label {
    width: 75%;
    max-width: 3rem;
    height: 0.75rem;
    background: var(--accent-ice);
}

.hero-stat-skel__value,
.hero-stat-skel__label {
    animation: pulse 1.4s ease-in-out infinite;
}

@keyframes pulse {
    0%,
    100% {
        opacity: 0.55;
    }
    50% {
        opacity: 1;
    }
}

@media (prefers-reduced-motion: reduce) {
    .hero-stat-skel__value,
    .hero-stat-skel__label {
        animation: none;
    }
}

/* ============================================
       Playoff tracker — same card language
       ============================================ */
.playoff-tracker__head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
}

.playoff-tracker__title {
    margin: 0;
    color: var(--color-ink);
    font-size: 1.05rem;
    font-weight: 800;
    line-height: 1.25;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.playoff-tracker__sub {
    margin: 0.15rem 0 0;
    color: var(--color-muted);
    font-size: 0.82rem;
}

.playoff-tracker__toggle {
    flex-shrink: 0;
    color: #475467;
    font-size: 0.82rem;
    font-weight: 700;
    text-decoration: none;
    background: transparent;
    border: 1px solid rgba(16, 24, 40, 0.12);
    border-radius: 0;
    padding: 0.35rem 0.75rem;
    cursor: pointer;
    transition:
        background 0.15s ease,
        color 0.15s ease;
}

.playoff-tracker__toggle:hover {
    background: #f7f8fa;
    color: var(--accent);
}

.playoff-tracker__panel {
    margin-top: 0.85rem;
    border-top: 1px solid rgba(16, 24, 40, 0.06);
    padding-top: 0.5rem;
}

.playoff-tracker__list {
    display: flex;
    flex-direction: column;
}

.playoff-row {
    display: grid;
    grid-template-columns: 1.25rem minmax(0, 1fr) auto;
    align-items: center;
    gap: 0.5rem;
    padding: 0.55rem 0.25rem;
    border-bottom: 1px solid rgba(16, 24, 40, 0.05);
}

.playoff-row:last-child {
    border-bottom: none;
}

.playoff-row__rank {
    color: var(--color-muted);
    font-size: 0.78rem;
    font-variant-numeric: tabular-nums;
    text-align: center;
}

.playoff-row__player-line {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    min-width: 0;
}

.playoff-row__name {
    color: var(--color-ink);
    font-size: 0.92rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.playoff-row__meta {
    margin-top: 0.15rem;
    color: var(--color-muted);
    font-size: 0.78rem;
}

.playoff-row__stat {
    color: var(--color-ink);
    font-size: 0.95rem;
    font-weight: 800;
    font-variant-numeric: tabular-nums;
}

.playoff-row__stat--muted {
    color: var(--color-muted);
    font-weight: 700;
    font-size: 0.82rem;
}

.playoff-tracker__empty {
    margin-top: 0.5rem;
    color: var(--color-muted);
    font-size: 0.9rem;
}

/* ============================================
       Footer
       ============================================ */
.page-footer {
    margin-top: 1.5rem;
    display: flex;
    justify-content: center;
    gap: 1rem;
    text-align: center;
    font-size: 0.85rem;
    color: var(--color-muted);
}

.page-footer__link {
    color: inherit;
    text-decoration: none;
    transition: color 0.15s ease;
}

.page-footer__link:hover {
    color: var(--accent);
}

/* ============================================
       Mobile / narrow
       ============================================ */
@media (max-width: 767px) {
    .page-shell {
        padding: 0.75rem 0 2rem;
    }

    .dashboard__toolbar {
        --toolbar-control-height: 2.75rem;
        flex-direction: column;
        align-items: stretch;
    }
    .dashboard__nav {
        width: 100%;
    }
    .dashboard__date {
        flex: none;
        align-self: center;
    }
    .dashboard__date :global(.date-controls__navigation-row) {
        grid-template-columns: 2.25rem minmax(0, 1fr) auto 2.25rem;
    }
    .dashboard__date :global(.date-controls__nav-btn) {
        width: 2.25rem;
    }
    .dashboard__date :global(.date-controls__today-btn) {
        padding-inline: 0.45rem;
    }
    .hero-header {
        margin-bottom: 1rem;
    }

    .logo-img {
        width: 1.75rem;
        height: 1.75rem;
    }

    .hero-title {
        margin-top: 0;
        font-size: clamp(1.2rem, 4vw, 1.6rem);
        line-height: 1.15;
    }

    .panel__inner {
        padding: 0.9rem;
    }

    .panel--hero .panel__inner {
        grid-template-columns: minmax(0, 1fr);
        padding: 0.5rem;
    }
    .hero-stats-header {
        margin-bottom: 0.5rem;
    }
    .hero-subtitle {
        font-size: 0.8rem;
    }
    .hero-stat__value {
        gap: 0.25rem;
        font-size: 1.25rem;
    }
    .hero-stat__value :global(svg) {
        width: 1rem;
        height: 1rem;
    }

    .hero-stat__label {
        font-size: 0.7rem;
        letter-spacing: -0.02em;
    }
}
</style>
