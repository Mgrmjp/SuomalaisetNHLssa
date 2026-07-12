<script>
// @ts-nocheck

import {
    Activity as ActivityIcon,
    CheckCircle,
    ChevronDown as ChevronDownIcon,
    CircleDot,
    Database,
    Goal,
    HandHeart,
    Menu,
    Trophy,
    Users,
    X,
} from 'lucide-svelte'
import { onMount } from 'svelte'
import { base } from '$app/paths'
import DateControls from '$lib/components/game/DateControls.svelte'
import OffseasonMoves from '$lib/components/game/OffseasonMoves.svelte'
import PlayerList from '$lib/components/game/PlayerList.svelte'
import AdContainer from '$lib/components/ui/AdContainer.svelte'
import MobileAd from '$lib/components/ui/MobileAd.svelte'
import NavTabs from '$lib/components/ui/NavTabs.svelte'
import TeamLogo from '$lib/components/ui/TeamLogo.svelte'
import {
    games,
    isLoading,
    players,
    resetToDefault,
    selectedDate,
    setDate,
} from '$lib/stores/gameData.js'
import { formatFinnishDateWithRelative } from '$lib/utils/dateUtils.js'
import { hasPoints, isGoalie } from '$lib/utils/positionHelpers.js'

/** @type {{ data: { initialDate: string, seo: { titleSuffix: string, description: string, summary: string, dateLabel: string, gameCount: number }, playoffStats: { season: string, skaters: Array<{ name: string, team: string, gamesPlayed: number, goals: number, assists: number, points: number }>, goalies: Array<{ name: string, team: string, gamesPlayed: number, wins: number, savePct: number }> } } }} */
const { data } = $props()
const playoffStats = $derived(data.playoffStats)
const offseasonMoves = $derived(data.offseasonMoves)

const activeBreak = $derived.by(() => {
    const breaks = data.breaks || []
    const date = $selectedDate || data.initialDate
    if (!date || !breaks.length) return null
    return breaks.find((b) => date >= b.startDate && date <= b.endDate) || null
})

const _totalGoals = $derived($players?.reduce((sum, player) => sum + player.goals, 0) || 0)
const _totalAssists = $derived($players?.reduce((sum, player) => sum + player.assists, 0) || 0)
const _totalPoints = $derived($players?.reduce((sum, player) => sum + player.points, 0) || 0)
const _totalPenaltyMinutes = $derived(
    $players?.reduce((sum, player) => sum + (player.penalty_minutes || 0), 0) || 0
)
const totalPlayers = $derived($players?.length || 0)

function _goaliePlayed(player) {
    const shotsAgainst = Number(player.shots_against ?? player.shotsAgainst ?? 0)
    const saves = Number(player.saves ?? player.goalie_saves ?? 0)
    const goalsAgainst = Number(player.goals_against ?? player.goalsAgainst ?? 0)
    const toi = player.time_on_ice || player.toi || ''
    return (
        shotsAgainst > 0 ||
        saves > 0 ||
        goalsAgainst > 0 ||
        (toi && toi !== '00:00' && toi !== '0:00')
    )
}

const _hasScoringPlayers = $derived(
    ($players || []).some((player) =>
        isGoalie(player) ? _goaliePlayed(player) : hasPoints(player)
    )
)

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

    const count = $games?.games?.length || 0
    const label = buildDateLabel($selectedDate)
    const summary = count > 0 ? `${count} ottelua ${label}` : `Ei otteluita ${label}`

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

let _showHeroStats = $state(false)
let _showPlayoffStats = $state(false)
let _hideFloatingHeader = $state(false)

function toggleHeroStats() {
    _showHeroStats = !_showHeroStats
}

function togglePlayoffStats() {
    _showPlayoffStats = !_showPlayoffStats
}

function toggleFloatingHeader() {
    _hideFloatingHeader = !_hideFloatingHeader
}

function formatSavePct(value) {
    if (!Number.isFinite(value)) return '.---'
    return value.toFixed(3).replace(/^0/, '')
}

onMount(() => {
    if ($selectedDate) return
    if (data.initialDate) {
        setDate(data.initialDate)
    }
})
</script>

<svelte:head>
    <title>Suomi NHL - Suomalaiset NHL-pelaajat | {_dynamicTitleSuffix}</title>
    <meta name="description" content={_metaDescription} />
    <meta property="og:title" content="Suomi NHL - Suomalaiset NHL-pelaajat | {_dynamicTitleSuffix}" />
    <meta property="og:description" content={_metaDescription} />
    <meta name="keywords" content={SEO_KEYWORDS} />
    <meta property="og:url" content="https://suomalaisetnhlssa.fi/" />
    <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1" />
</svelte:head>

<div class="page-shell dashboard-bg" class:page-shell--compact-header={_hideFloatingHeader}>
    <div class="dashboard__floating-header" class:dashboard__floating-header--hidden={_hideFloatingHeader} aria-label="Päivämäärä ja päänavigaatio">
        {#if !_hideFloatingHeader}
            <div id="floating-header-content" class="dashboard__floating-content">
                <div class="dashboard__floating-topline">
                    <div class="dashboard__floating-date">
                        <DateControls />
                        <button
                            type="button"
                            class="dashboard__floating-toggle dashboard__floating-toggle--close"
                            onclick={toggleFloatingHeader}
                            aria-expanded={!_hideFloatingHeader}
                            aria-controls="floating-header-content"
                            aria-label="Piilota valikko"
                            title="Piilota valikko"
                        >
                            <X class="dashboard__floating-toggle-icon" aria-hidden="true" />
                        </button>
                    </div>
                </div>
                <div class="dashboard__tabs" aria-label="Päänavigaatio">
                    <NavTabs />
                </div>
            </div>
        {:else}
            <button
                type="button"
                class="dashboard__floating-toggle dashboard__floating-toggle--open"
                onclick={toggleFloatingHeader}
                aria-expanded={!_hideFloatingHeader}
                aria-controls="floating-header-content"
                aria-label="Näytä valikko"
                title="Näytä valikko"
            >
                <Menu class="dashboard__floating-toggle-icon dashboard__floating-toggle-icon--left" aria-hidden="true" />
                <span class="dashboard__floating-toggle-label">Näytä valikko</span>
            </button>
        {/if}
    </div>

    <header class="hero-header">
        <div class="hero-header__inner">
            <button
                onclick={resetToDefault}
                class="logo-button"
                aria-label="Palaa etusivulle ja nollaa valinnat"
            >
                <img
                    src={base + "/logo.svg"}
                    alt="Suomalaiset NHL-pelaajat"
                    class="logo-img"
                />
            </button>
            <h1 class="hero-title">
                Miten suomalaisilla kulkee NHL:ssä?
            </h1>
            <p class="hero-subtitle">Tutki päivän ottelut, pisteet ja onnistumiset</p>
            <button
                onclick={() => document.getElementById('scoringList')?.scrollIntoView({ behavior: 'smooth' })}
                class="hero-scroll-to-results md:hidden"
            >
                Tuloksiin
            </button>
        </div>
    </header>

    <div class="dashboard">
        <div class="dashboard__rail">
            <!-- Controls (date picker) -->
            {#if activeBreak}
                <div class="dashboard__notice">
                    <section class="panel panel--break">
                        <div class="panel__inner flex flex-col items-center justify-center text-center">
                            {#if activeBreak.type === 'offseason'}
                                <span class="break-emoji" role="img" aria-label="Offseason">☀️</span>
                                <h3 class="break-title">Nähdään ensi kaudella!</h3>
                                <p class="break-meta">
                                    NHL-kausi on päättynyt. Uusi kausi alkaa lokakuussa.
                                </p>
                            {:else}
                                <span class="break-emoji" role="img" aria-label="Break">🏒</span>
                                <h3 class="break-title">{activeBreak.description}</h3>
                                <p class="break-meta">
                                    NHL on tauolla ({formatFinnishDateWithRelative(activeBreak.startDate).formatted} - {formatFinnishDateWithRelative(activeBreak.endDate).formatted})
                                </p>
                            {/if}
                        </div>
                    </section>
                </div>
            {/if}

            <!-- Offseason moves tracker -->
            {#if offseasonMoves}
                <div class="dashboard__moves">
                    <OffseasonMoves movesData={offseasonMoves} />
                </div>
            {/if}

            <!-- Navigation and its active content form one section. -->
            <section class="dashboard__results" aria-label="Tulokset ja tilastot">
                <div class="dashboard__active-stack">

            <!-- Hero Stats — the "answer" of the page -->
            {#if $isLoading}
                <section class="panel panel--hero" aria-busy="true">
                    <div class="panel__inner">
                        <div class="panel__eyebrow rink-divider">Päivän yhteistilastot</div>
                        <div class="hero-stats-skeleton">
                            {#each [1,2,3,4,5] as _}
                                <div class="hero-stat-skel">
                                    <div class="hero-stat-skel__icon"></div>
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
                        <div class="panel__eyebrow rink-divider">Päivän yhteistilastot</div>
                        <h2 id="hero-stats-title" class="panel__hero-heading">
                            {selectedDateSummary?.label || 'Valittu päivä'}
                        </h2>
                        <p class="panel__hero-sub">{selectedDateSummary?.summary || ''}</p>

                        <!-- Mobile toggle -->
                        <button
                            class="hero-stats-toggle md:hidden"
                            onclick={toggleHeroStats}
                            aria-label="Näytä tilastot"
                            aria-expanded={_showHeroStats}
                        >
                            <span class="hero-stats-toggle-text">Päivän tilastot</span>
                            <ChevronDown class="hero-stats-toggle-icon" aria-hidden="true" />
                        </button>

                        <div class="hero-stats-wrapper" class:expanded={_showHeroStats}>
                            <div class="hero-stats">
                                <div class="hero-stat">
                                    <div class="hero-stat__icon-wrap">
                                        <ActivityIcon class="hero-stat__icon" aria-hidden="true" />
                                    </div>
                                    <div class="hero-stat__value">{_totalGoals}</div>
                                    <div class="hero-stat__label" data-full="Maalit (Goals)">Maalit</div>
                                </div>
                                <div class="hero-stat">
                                    <div class="hero-stat__icon-wrap">
                                        <HandHeart class="hero-stat__icon" aria-hidden="true" />
                                    </div>
                                    <div class="hero-stat__value">{_totalAssists}</div>
                                    <div class="hero-stat__label" data-full="Syötöt (Assists)">Syötöt</div>
                                </div>
                                <div class="hero-stat hero-stat--primary">
                                    <div class="hero-stat__icon-wrap">
                                        <CircleDot class="hero-stat__icon hero-stat__icon--lg" aria-hidden="true" />
                                    </div>
                                    <div class="hero-stat__value hero-stat__value--lg">{_totalPoints}</div>
                                    <div class="hero-stat__label" data-full="Pisteet (Points)">Pisteet</div>
                                </div>
                                <div class="hero-stat">
                                    <div class="hero-stat__icon-wrap">
                                        <Goal class="hero-stat__icon" aria-hidden="true" />
                                    </div>
                                    <div class="hero-stat__value">{_totalPenaltyMinutes}</div>
                                    <div class="hero-stat__label" data-full="Rangaistusmin (PIM)">Rangaistusmin</div>
                                </div>
                                <div class="hero-stat">
                                    <div class="hero-stat__icon-wrap">
                                        <Users class="hero-stat__icon" aria-hidden="true" />
                                    </div>
                                    <div class="hero-stat__value">{totalPlayers}</div>
                                    <div class="hero-stat__label" data-full="Pelaajaa kokoonpanossa">Kokoonpanossa</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>
            {/if}

            <!-- Player List -->
            {#if !activeBreak}
                <PlayerList />
            {/if}

            <!-- Playoff tracker — same card language -->
            <section class="panel panel--playoff" class:panel--active={activeBreak}>
                <div class="panel__inner">
                    <div class="panel__eyebrow rink-divider">Pudotuspelit</div>
                    <div class="playoff-tracker__head">
                        <div class="min-w-0">
                            <h2 class="playoff-tracker__title">Pudotuspelien suomalaiset</h2>
                            <p class="playoff-tracker__sub">NHL {playoffStats.season}</p>
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
                                                <div class="playoff-row__rank">{index + 1}</div>
                                                <div class="playoff-row__player min-w-0">
                                                    <div class="playoff-row__player-line">
                                                        <TeamLogo team={player.team} size="24" />
                                                        <span class="playoff-row__name">{player.name}</span>
                                                    </div>
                                                    <div class="playoff-row__meta">
                                                        {player.gamesPlayed} ott. · {player.goals}+{player.assists}
                                                    </div>
                                                </div>
                                                <div class="playoff-row__stat">{player.points} P</div>
                                            </div>
                                        {/each}
                                    {/if}

                                    {#if playoffStats.goalies.length > 0}
                                        {#each playoffStats.goalies as goalie}
                                            <div class="playoff-row">
                                                <div class="playoff-row__rank">MV</div>
                                                <div class="playoff-row__player min-w-0">
                                                    <div class="playoff-row__player-line">
                                                        <TeamLogo team={goalie.team} size="24" />
                                                        <span class="playoff-row__name">{goalie.name}</span>
                                                    </div>
                                                </div>
                                                <div class="playoff-row__stat playoff-row__stat--muted">
                                                    {goalie.wins} W · {formatSavePct(goalie.savePct)} SV%
                                                </div>
                                            </div>
                                        {/each}
                                    {/if}
                                </div>
                            {:else}
                                <div class="playoff-tracker__empty">
                                    Pudotuspelitilastot päivittyvät tähän, kun suomalaispelaajille kertyy pelejä.
                                </div>
                            {/if}
                        </div>
                    {/if}
                </div>
            </section>
                </div>
            </section>

            <!-- Info card — same card language as the rest -->
            <section class="panel panel--info" aria-labelledby="data-source-title">
                <div class="panel__inner panel__inner--info">
                    <div class="info-grid">
                        <div class="info-heading">
                            <p class="info-card__eyebrow">Suomi NHL</p>
                            <h2 id="data-source-title" class="info-card__title">Tietoa datasta</h2>
                        </div>
                        <div class="info-card__copy">
                            <p>
                                Sivusto kokoaa NHL:ssä pelaavien suomalaisten ottelukohtaiset tilastot yhteen näkymään: maalit, syötöt, pisteet, peliajan ja maalivahtien keskeiset luvut.
                            </p>
                            <p>
                                Mukana ovat suomalaispelaajat läpi kauden, ja tiedot päivittyvät myös otteluiden aikana.
                            </p>
                            <p>
                                Tilastot perustuvat NHL:n virallisiin lähteisiin.
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Ads follow the product content so navigation stays attached to its section. -->
            <div class="dashboard__ads">
                <MobileAd />
                <AdContainer />
            </div>
        </div>
    </div>

    <footer class="page-footer">
        <a href={base + "/tietoa"} class="page-footer__link">Tietoa sivustosta</a>
    </footer>
</div>

<style>
    /* ============================================
       Dashboard shell — single centered product
       ============================================ */
    .page-shell {
        position: relative;
        z-index: 1;
        width: 100%;
        max-width: var(--rail-max);
        margin: 0 auto;
        padding: 7.75rem 1.25rem 4rem;
    }

    .page-shell--compact-header {
        padding-top: 3.75rem;
    }

    .dashboard__floating-header {
        position: fixed;
        top: 0.75rem;
        left: 50%;
        z-index: 100;
        width: min(calc(100% - 2rem), var(--rail-max));
        transform: translateX(-50%);
        --floating-header-gap: 0.35rem;
        --floating-header-control: 4.5rem;
    }

    .dashboard__floating-header--hidden {
        width: auto;
        display: flex;
        justify-content: center;
    }

    .dashboard__floating-content {
        display: grid;
        grid-template-columns: 1fr;
        grid-template-rows: auto auto;
        width: 100%;
        gap: var(--floating-header-gap);
        position: relative;
    }

    .dashboard__floating-topline {
        display: contents;
    }

    .dashboard__floating-toggle {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 0 0.5rem;
        border: 1px solid rgba(16, 24, 40, 0.14);
        background: rgba(255, 255, 255, 0.92);
        color: #475467;
        font-size: 0.66rem;
        font-weight: 800;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        cursor: pointer;
    }

    .dashboard__floating-toggle:hover {
        background: #ffffff;
        color: var(--color-ink);
    }

    .dashboard__floating-header--hidden .dashboard__floating-toggle {
        margin: 0;
        min-height: 2.35rem;
        padding: 0.55rem 1rem;
        border-radius: 0;
        background: rgba(0, 53, 128, 0.94);
        color: #ffffff;
    }

    .dashboard__floating-date {
        grid-column: 1;
        grid-row: 1;
        width: 100%;
        min-width: 0;
        position: relative;
    }

    .dashboard__floating-content > .dashboard__tabs {
        grid-column: 1;
        grid-row: 2;
        display: block;
        width: 100%;
        max-width: none;
        margin: 0;
        min-width: 0;
    }

    .dashboard__floating-date > .dashboard__floating-toggle {
        position: absolute;
        top: 50%;
        right: 0;
        width: 3rem;
        height: var(--floating-row-control-height);
        padding: 0;
        border: 0;
        border-radius: 0;
        background: transparent;
        color: #475467;
        box-shadow: none;
        z-index: 20;
        transform: translateY(-50%);
    }

    .dashboard__floating-toggle-icon {
        width: 1.1rem;
        height: 1.1rem;
        flex: 0 0 auto;
    }

    .dashboard__floating-toggle--open {
        gap: 0.5rem;
    }

    .dashboard__floating-toggle--open .dashboard__floating-toggle-label {
        font-size: var(--floating-row-font-size);
        font-weight: 800;
        letter-spacing: 0.02em;
    }

    .dashboard__floating-date > .dashboard__floating-toggle:hover {
        background: rgba(16, 24, 40, 0.04);
        color: var(--color-ink);
    }

    :global(.dashboard__floating-header) {
        --floating-row-font-size: 0.86rem;
        --floating-row-line-height: 1.2;
        --floating-row-inner-padding-y: 0.3rem;
        --floating-row-inner-padding-x: 0.5rem;
        --floating-row-control-height: 2.35rem;
        font-family:
            var(--font-sans, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif);
        -webkit-font-smoothing: antialiased;
        text-rendering: optimizeLegibility;
    }

    :global(.dashboard__floating-header .date-controls) {
        max-width: none;
    }

    :global(.dashboard__floating-header .date-controls__card) {
        width: 100%;
        box-sizing: border-box;
        padding: 0.25rem 3rem 0.25rem 0.25rem;
        background: rgba(255, 255, 255, 0.92);
        border-color: rgba(16, 24, 40, 0.14);
    }

    :global(.dashboard__floating-header .date-controls__navigation-row) {
        height: 100%;
        align-items: center;
    }

    :global(.dashboard__floating-header .date-controls__label) {
        display: none;
    }

    :global(.dashboard__floating-header .date-controls__navigation-row) {
        grid-template-columns: var(--floating-row-control-height) minmax(0, 1fr) auto var(--floating-row-control-height);
        gap: 0.25rem;
    }

    :global(.dashboard__floating-header .date-controls__nav-btn),
    :global(.dashboard__floating-header .date-controls__picker-input),
    :global(.dashboard__floating-header .date-controls__today-btn) {
        min-height: var(--floating-row-control-height);
        font-size: var(--floating-row-font-size);
        line-height: var(--floating-row-line-height);
        font-variant-numeric: tabular-nums;
    }

    :global(.dashboard__floating-header .date-controls__nav-btn) {
        width: var(--floating-row-control-height);
        height: var(--floating-row-control-height);
    }

    :global(.dashboard__floating-header .date-controls__picker-input) {
        padding: var(--floating-row-inner-padding-y) var(--floating-row-inner-padding-x);
    }

    :global(.dashboard__floating-header .date-controls__today-btn) {
        padding: var(--floating-row-inner-padding-y) 0.65rem;
    }

    :global(.dashboard__floating-header .nav-tabs-list) {
        box-sizing: border-box;
        padding: 0.25rem;
        background: rgba(255, 255, 255, 0.92);
        border-color: rgba(16, 24, 40, 0.14);
        font-size: var(--floating-row-font-size);
        line-height: var(--floating-row-line-height);
    }

    :global(.dashboard__floating-header .nav-tab-item) {
        min-height: var(--floating-row-control-height);
        padding: var(--floating-row-inner-padding-y) 0.65rem;
        font-size: var(--floating-row-font-size);
        line-height: var(--floating-row-line-height);
    }

    :global(.dashboard__floating-header .nav-tab-icon) {
        width: 1rem;
        height: 1rem;
        flex: 0 0 auto;
    }

    .dashboard {
        display: block;
    }

    .dashboard__rail {
        display: flex;
        flex-direction: column;
    }

    .dashboard__notice,
    .dashboard__moves {
        margin-bottom: 1.5rem;
    }

    .dashboard__results {
        display: grid;
        gap: 1.5rem;
        margin-bottom: 1.5rem;
        min-width: 0;
    }

    .dashboard__active-stack {
        display: grid;
        gap: 1.5rem;
        min-width: 0;
    }

    .dashboard__ads {
        display: grid;
        gap: 1.5rem;
        margin-top: 1.5rem;
    }

    /* ============================================
       Hero header
       ============================================ */
    .hero-header {
        margin: 0 auto 1rem;
        text-align: center;
    }

    .hero-header__inner {
        max-width: 620px;
        margin: 0 auto;
        padding: 0;
    }

    .hero-title {
        max-width: 580px;
        margin: 0.4rem auto 0;
        color: var(--color-ink);
        font-size: clamp(1.55rem, 3.2vw, 2.15rem);
        line-height: 1.1;
        font-weight: 800;
        letter-spacing: -0.01em;
    }

    .hero-subtitle {
        margin: 0.45rem auto 0;
        max-width: 32rem;
        color: var(--color-muted);
        font-size: clamp(0.9rem, 1.3vw, 1rem);
        line-height: 1.5;
    }

    .hero-scroll-to-results {
        margin-top: 0.6rem;
        border-radius: 0;
        background: var(--accent);
        color: #fff;
        padding: 0.45rem 0.9rem;
        font-size: 0.85rem;
        font-weight: 700;
        transition: background 0.15s ease, transform 0.15s ease;
    }

    .hero-scroll-to-results:hover {
        background: var(--accent-strong);
        transform: translateY(-1px);
    }

    .logo-button {
        background: transparent;
        border: none;
        padding: 0;
        cursor: pointer;
        display: block;
        margin: 0 auto;
    }

    .logo-img {
        width: 2.25rem;
        height: 2.25rem;
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
        content: "";
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

    /* Hero card — the page's "answer" */
    .panel--hero {
        background: var(--card-bg);
    }

    .panel--hero::before {
        display: block;
    }

    .panel__hero-heading {
        margin: 0 0 0.25rem;
        color: var(--color-ink);
        font-size: clamp(1.4rem, 2.6vw, 1.75rem);
        line-height: 1.2;
        font-weight: 800;
        letter-spacing: -0.01em;
    }

    .panel__hero-sub {
        margin: 0 0 1.25rem;
        color: var(--color-muted);
        font-size: 0.95rem;
        line-height: 1.5;
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

    /* ============================================
       Hero stats — the central "answer"
       ============================================ */
    .hero-stats-wrapper {
        margin-top: 0.5rem;
    }

    .hero-stats {
        display: grid;
        grid-template-columns: repeat(5, minmax(0, 1fr));
        gap: 0.5rem;
        align-items: stretch;
    }

    .hero-stat {
        position: relative;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 0.35rem;
        padding: 1rem 0.5rem;
        border-radius: var(--card-radius-sm);
        background: rgba(248, 250, 255, 0.6);
        border: 1px solid rgba(16, 24, 40, 0.08);
        min-height: 96px;
    }

    .hero-stat--primary {
        background: linear-gradient(180deg, var(--accent-ice), #ffffff);
        border-color: rgba(16, 24, 40, 0.12);
    }

    .hero-stat__icon-wrap {
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 1.75rem;
    }

    .hero-stat__icon {
        width: 1.5rem;
        height: 1.5rem;
        color: var(--accent-soft);
    }

    .hero-stat--primary .hero-stat__icon {
        color: var(--accent);
    }

    .hero-stat__icon--lg {
        width: 1.85rem;
        height: 1.85rem;
    }

    .hero-stat__value {
        color: var(--color-ink);
        font-size: 1.4rem;
        font-weight: 800;
        line-height: 1;
        font-variant-numeric: tabular-nums;
    }

    .hero-stat__value--lg {
        font-size: 2rem;
        color: var(--accent);
    }

    .hero-stat__label {
        color: var(--color-muted);
        font-size: 0.78rem;
        font-weight: 600;
        line-height: 1.1;
        text-align: center;
    }

    .hero-stat__label::after {
        content: attr(data-full);
        position: absolute;
        left: 50%;
        top: 100%;
        transform: translateX(-50%);
        padding: 0.35rem 0.5rem;
        background: rgba(17, 24, 39, 0.92);
        color: #e5e7eb;
        font-size: 0.75rem;
        border-radius: 0;
        white-space: nowrap;
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.12s ease;
        z-index: 10;
    }

    .hero-stat:hover .hero-stat__label::after {
        opacity: 1;
        transition-delay: 0.25s;
    }

    .hero-stats-skeleton {
        display: grid;
        grid-template-columns: repeat(5, minmax(0, 1fr));
        gap: 0.5rem;
        margin-top: 0.5rem;
    }

    .hero-stat-skel {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.5rem;
        padding: 1rem 0.5rem;
        min-height: 96px;
        border-radius: var(--card-radius-sm);
        background: rgba(248, 250, 255, 0.6);
    }

    .hero-stat-skel__icon {
        width: 1.5rem;
        height: 1.5rem;
        border-radius: 50%;
        background: rgba(0, 53, 128, 0.08);
    }

    .hero-stat-skel__value {
        width: 3rem;
        height: 1.4rem;
        border-radius: 0;
        background: rgba(0, 53, 128, 0.08);
    }

    .hero-stat-skel__label {
        width: 4rem;
        height: 0.7rem;
        border-radius: 0;
        background: rgba(0, 53, 128, 0.06);
    }

    .hero-stat-skel__icon,
    .hero-stat-skel__value,
    .hero-stat-skel__label {
        animation: pulse 1.4s ease-in-out infinite;
    }

    @keyframes pulse {
        0%, 100% { opacity: 0.55; }
        50% { opacity: 1; }
    }

    /* Mobile toggle (compact) */
    .hero-stats-toggle {
        width: 100%;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.6rem 0.85rem;
        margin-top: 0.25rem;
        background: var(--card-bg);
        border: var(--card-border);
        border-radius: var(--card-radius-sm);
        color: var(--color-ink);
        cursor: pointer;
        font-size: 0.9rem;
        font-weight: 700;
    }

    .hero-stats-toggle-icon {
        width: 1.1rem;
        height: 1.1rem;
        transition: transform 0.2s ease;
    }

    .hero-stats-toggle-icon.rotated {
        transform: rotate(180deg);
    }

    .hero-stats-wrapper.expanded {
        margin-top: 0.5rem;
    }

    /* ============================================
       Dashboard tabs — anchored to the rail
       ============================================ */
    .dashboard__tabs {
        display: flex;
        justify-content: center;
        max-width: var(--rail-max);
        margin: 0 auto;
        padding: 0;
        width: 100%;
        min-width: 0;
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
        transition: background 0.15s ease, color 0.15s ease;
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
       Info card — same card language
       ============================================ */
    .panel__inner--info {
        padding: var(--card-padding-y) var(--card-padding-x);
    }

    .info-grid {
        display: grid;
        grid-template-columns: minmax(0, 0.7fr) minmax(0, 1.3fr);
        gap: 1.5rem;
    }

    .info-card__eyebrow {
        margin: 0 0 0.4rem;
        color: var(--eyebrow-color);
        font-size: var(--eyebrow-size);
        font-weight: var(--eyebrow-weight);
        letter-spacing: var(--eyebrow-track);
        text-transform: uppercase;
    }

    .info-card__title {
        margin: 0;
        color: var(--color-ink);
        font-size: clamp(1.2rem, 2.2vw, 1.5rem);
        line-height: 1.2;
        font-weight: 800;
    }

    .info-card__copy {
        display: grid;
        gap: 0.6rem;
        color: #475467;
        font-size: 0.95rem;
        line-height: 1.65;
    }

    .info-card__copy p {
        margin: 0;
    }

    /* ============================================
       Footer
       ============================================ */
    .page-footer {
        margin-top: 2.5rem;
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
            padding: 6rem 1rem 3rem;
        }

        .page-shell--compact-header {
            padding-top: 3.25rem;
        }

        .dashboard__floating-header {
            top: 0.35rem;
            width: calc(100% - 0.75rem);
            --floating-header-gap: 0.2rem;
            --floating-header-control: 2rem;
            --floating-row-font-size: 0.78rem;
            --floating-row-control-height: 2rem;
            --floating-row-inner-padding-y: 0.28rem;
        }

        .dashboard__floating-header--hidden {
            width: auto;
        }

        .dashboard__floating-content {
            gap: var(--floating-header-gap);
        }

        .dashboard__floating-date > .dashboard__floating-toggle {
            width: 2.5rem;
            height: var(--floating-row-control-height);
            padding: 0;
        }

        .dashboard__floating-toggle-icon {
            width: 0.95rem;
            height: 0.95rem;
        }

        .dashboard__floating-header--hidden .dashboard__floating-toggle {
            position: static;
            height: auto;
            width: auto;
            min-height: 2.35rem;
            padding: 0.55rem 1rem;
            gap: 0.4rem;
            border-radius: 0;
            background: rgba(0, 53, 128, 0.94);
            color: #ffffff;
        }

        .dashboard__floating-header--hidden .dashboard__floating-toggle-label {
            font-size: 0.78rem;
            font-weight: 800;
            letter-spacing: 0.04em;
        }

        :global(.dashboard__floating-header .date-controls__card) {
            padding: 0.25rem 2.5rem 0.25rem 0.25rem;
        }

        :global(.dashboard__floating-header .date-controls__navigation-row) {
            height: 100%;
        }

        :global(.dashboard__floating-header .date-controls__navigation-row) {
            grid-template-columns: 2rem minmax(0, 1fr) 2rem;
            gap: 0.2rem;
        }

        :global(.dashboard__floating-header .date-controls__today-btn) {
            display: none !important;
        }

        :global(.dashboard__floating-header .date-controls__nav-btn) {
            width: 2rem;
            height: 2rem;
        }

        :global(.dashboard__floating-header .date-controls__nav-btn),
        :global(.dashboard__floating-header .date-controls__picker-input),
        :global(.dashboard__floating-header .date-controls__today-btn) {
            min-height: 2rem;
        }

        :global(.dashboard__floating-header .date-controls__picker-input) {
            justify-content: center;
            padding-inline: 0.35rem;
            font-size: var(--floating-row-font-size);
            text-align: center;
        }

        :global(.dashboard__floating-header .date-controls__picker-input svg) {
            display: none;
        }

        :global(.dashboard__floating-header .nav-tabs-list) {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.12rem;
            padding: 0.12rem;
            overflow: visible;
        }

        :global(.dashboard__floating-header .nav-tab-item) {
            flex: none;
            min-width: 0;
            min-height: var(--floating-row-control-height);
            padding: 0.3rem 0.25rem;
            font-size: var(--floating-row-font-size);
            line-height: 1.1;
            white-space: normal;
        }

        :global(.dashboard__floating-header .nav-tab-icon) {
            display: none;
        }

        .hero-header {
            margin-bottom: 0.85rem;
        }

        .hero-header__inner {
            max-width: 22rem;
        }

        .logo-img {
            width: 1.75rem;
            height: 1.75rem;
        }

        .hero-title {
            margin-top: 0.35rem;
            font-size: clamp(1.3rem, 6.4vw, 1.65rem);
            line-height: 1.1;
        }

        .hero-subtitle {
            margin-top: 0.35rem;
            font-size: 0.82rem;
            line-height: 1.4;
        }

        .hero-scroll-to-results {
            margin-top: 0.5rem;
            padding: 0.4rem 0.8rem;
            font-size: 0.8rem;
        }

        .panel__inner {
            padding: 0.9rem;
        }

        .hero-stats,
        .hero-stats-skeleton {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }

        .hero-stats-wrapper {
            display: none;
        }

        .hero-stats-wrapper.expanded {
            display: block;
        }

        .info-grid {
            grid-template-columns: 1fr;
            gap: 0.85rem;
        }
    }

    @media (max-width: 380px) {
        .page-shell {
            padding-inline: 0.75rem;
        }
    }
</style>
