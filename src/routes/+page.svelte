<script>
// @ts-nocheck
import { onMount } from 'svelte'
import { base } from '$app/paths'
import DateControls from '$lib/components/game/DateControls.svelte'
import PlayerList from '$lib/components/game/PlayerList.svelte'
import AdContainer from '$lib/components/ui/AdContainer.svelte'
import MobileAd from '$lib/components/ui/MobileAd.svelte'
import NavTabs from '$lib/components/ui/NavTabs.svelte'
import TeamLogo from '$lib/components/ui/TeamLogo.svelte'
import {
    currentBreak,
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

function toggleHeroStats() {
    _showHeroStats = !_showHeroStats
}

function togglePlayoffStats() {
    _showPlayoffStats = !_showPlayoffStats
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

<div class="page-shell dashboard-bg">
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
            {#if $currentBreak}
                <section class="panel panel--break">
                    <div class="panel__inner flex flex-col items-center justify-center text-center">
                        <span class="break-emoji" role="img" aria-label="Break">🏒</span>
                        <h3 class="break-title">{$currentBreak.description}</h3>
                        <p class="break-meta">
                            NHL on tauolla ({formatFinnishDateWithRelative($currentBreak.startDate).formatted} - {formatFinnishDateWithRelative($currentBreak.endDate).formatted})
                        </p>
                    </div>
                </section>
            {/if}
            <DateControls />

            <!-- Mobile ad under date controls -->
            <MobileAd />

            <!-- Navigation: now visually anchored to the dashboard shell -->
            <nav class="dashboard__tabs" aria-label="Päänavigaatio">
                <NavTabs />
            </nav>

            <!-- Ad Container (desktop banner) -->
            <AdContainer />

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
                            <svg
                                class="hero-stats-toggle-icon"
                                class:rotated={_showHeroStats}
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                            >
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                            </svg>
                        </button>

                        <div class="hero-stats-wrapper" class:expanded={_showHeroStats}>
                            <div class="hero-stats">
                                <div class="hero-stat">
                                    <div class="hero-stat__icon-wrap">
                                        <svg class="hero-stat__icon" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
                                            <path fill="currentColor" d="M0 160c0-53 114.6-96 256-96s256 43 256 96s-114.6 96-256 96S0 213 0 160m0 82.2V352c0 53 114.6 96 256 96s256-43 256-96V242.2c-113.4 82.3-398.5 82.4-512 0" />
                                        </svg>
                                    </div>
                                    <div class="hero-stat__value">{_totalGoals}</div>
                                    <div class="hero-stat__label" data-full="Maalit (Goals)">Maalit</div>
                                </div>
                                <div class="hero-stat">
                                    <div class="hero-stat__icon-wrap">
                                        <svg class="hero-stat__icon" viewBox="0 0 640 512" xmlns="http://www.w3.org/2000/svg">
                                            <path fill="currentColor" d="m323.4 85.2l-96.8 78.4c-16.1 13-19.2 36.4-7 53.1c12.9 17.8 38 21.3 55.3 7.8l99.3-77.2c7-5.4 17-4.2 22.5 2.8s4.2 17-2.8 22.5L373 188.8L550.2 352H592c26.5 0 48-21.5 48-48V176c0-26.5-21.5-48-48-48h-80.7l-3.9-2.5L434.8 79c-15.3-9.8-33.2-15-51.4-15c-21.8 0-43 7.5-60 21.2m22.8 124.4l-51.7 40.2c-31.5 24.6-77.2 18.2-100.8-14.2c-22.2-30.5-16.6-73.1 12.7-96.8l83.2-67.3c-11.6-4.9-24.1-7.4-36.8-7.4C234 64 215.7 69.6 200 80l-72 48H48c-26.5 0-48 21.5-48 48v128c0 26.5 21.5 48 48 48h108.2l91.4 83.4c19.6 17.9 49.9 16.5 67.8-3.1c5.5-6.1 9.2-13.2 11.1-20.6l17 15.6c19.5 17.9 49.9 16.6 67.8-2.9c4.5-4.9 7.8-10.6 9.9-16.5c19.4 13 45.8 10.3 62.1-7.5c17.9-19.5 16.6-49.9-2.9-67.8z" />
                                        </svg>
                                    </div>
                                    <div class="hero-stat__value">{_totalAssists}</div>
                                    <div class="hero-stat__label" data-full="Syötöt (Assists)">Syötöt</div>
                                </div>
                                <div class="hero-stat hero-stat--primary">
                                    <div class="hero-stat__icon-wrap">
                                        <svg class="hero-stat__icon hero-stat__icon--lg" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                            <path fill="currentColor" d="M20 12a2 2 0 0 0-.703.133l-2.398-1.963c.059-.214.101-.436.101-.67C17 8.114 15.886 7 14.5 7S12 8.114 12 9.5c0 .396.1.765.262 1.097l-2.909 3.438A2.06 2.06 0 0 0 9 14c-.179 0-.348.03-.512.074l-2.563-2.563C5.97 11.348 6 11.179 6 11c0-1.108-.892-2-2-2s-2 .892-2 2s.892 2 2 2c.179 0 .348-.03.512-.074l2.563 2.563A1.906 1.906 0 0 0 7 16c0 1.108.892 2 2 2s2-.892 2-2c0-.237-.048-.46-.123-.671l2.913-3.442c.227.066.462.113.71.113a2.48 2.48 0 0 0 1.133-.281l2.399 1.963A2.077 2.077 0 0 0 18 14c0 1.108.892 2 2 2s2-.892 2-2s-.892-2-2-2" />
                                        </svg>
                                    </div>
                                    <div class="hero-stat__value hero-stat__value--lg">{_totalPoints}</div>
                                    <div class="hero-stat__label" data-full="Pisteet (Points)">Pisteet</div>
                                </div>
                                <div class="hero-stat">
                                    <div class="hero-stat__icon-wrap">
                                        <svg class="hero-stat__icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                            <g fill="currentColor" fill-rule="evenodd" clip-rule="evenodd">
                                                <path d="M10 5a2 2 0 0 0-2 2v3h2.4A7.48 7.48 0 0 0 8 15.5a7.48 7.48 0 0 0 2.4 5.5H5a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h1V7a4 4 0 1 1 8 0v1.15a7.446 7.446 0 0 0-1.943.685A.999.999 0 0 1 12 8.5V7a2 2 0 0 0-2-2" />
                                                <path d="M10 15.5a5.5 5.5 0 1 1 11 0a5.5 5.5 0 0 1-11 0m6.5-1.5a1 1 0 1 0-2 0v1.5a1 1 0 0 0 .293.707l1 1a1 1 0 0 0 1.414-1.414l-.707-.707z" />
                                            </g>
                                        </svg>
                                    </div>
                                    <div class="hero-stat__value">{_totalPenaltyMinutes}</div>
                                    <div class="hero-stat__label" data-full="Rangaistusmin (PIM)">Rangaistusmin</div>
                                </div>
                                <div class="hero-stat">
                                    <div class="hero-stat__icon-wrap">
                                        <svg class="hero-stat__icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                            <path fill="currentColor" d="M5 6c-1.1 0-2 .9-2 2s.9 2 2 2s2-.89 2-2s-.89-2-2-2m7-2a2 2 0 1 0 2 2c0-1.11-.89-2-2-2m7-2c-1.1 0-2 .9-2 2s.9 2 2 2s2-.89 2-2s-.89-2-2-2M3.5 11c-.83 0-1.5.67-1.5 1.5V17h1v5h4v-5h1v-4.5c0-.83-.67-1.5-1.5-1.5zm7-2C9.67 9 9 9.67 9 10.5V15h1v5h4v-5h1v-4.5c0-.83-.67-1.5-1.5-1.5zm7-2c-.83 0-1.5.67-1.5 1.5V13h1v5h4v-5h1V8.5c0-.83-.67-1.5-1.5-1.5z" />
                                        </svg>
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
            {#if !$currentBreak}
                <PlayerList />
            {/if}

            <!-- Playoff tracker — same card language -->
            <section class="panel panel--playoff">
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
        padding: 2.5rem 1.25rem 4rem;
    }

    .dashboard {
        display: block;
    }

    .dashboard__rail {
        display: grid;
        gap: 1.5rem;
    }

    /* ============================================
       Hero header
       ============================================ */
    .hero-header {
        margin: 0 auto 2rem;
        text-align: center;
    }

    .hero-header__inner {
        max-width: 820px;
        margin: 0 auto;
        padding: 0.5rem 0 0;
    }

    .hero-title {
        max-width: 780px;
        margin: 0.75rem auto 0;
        color: var(--color-ink);
        font-size: clamp(2.2rem, 5.2vw, 3.8rem);
        line-height: 1;
        font-weight: 800;
        letter-spacing: -0.01em;
    }

    .hero-subtitle {
        margin: 0.9rem auto 0;
        max-width: 34rem;
        color: var(--color-muted);
        font-size: clamp(0.98rem, 1.8vw, 1.08rem);
        line-height: 1.6;
    }

    .hero-scroll-to-results {
        margin-top: 1rem;
        border-radius: 999px;
        background: var(--accent);
        color: #fff;
        padding: 0.7rem 1.25rem;
        font-weight: 700;
        box-shadow: 0 10px 22px var(--accent-glow);
        transition: background 0.15s ease, transform 0.15s ease, box-shadow 0.15s ease;
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
        width: 4rem;
        height: 4rem;
        margin: 0 auto;
        transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        filter: drop-shadow(0 8px 14px rgba(16, 24, 40, 0.1));
    }

    .logo-button:hover .logo-img {
        transform: scale(1.05) rotate(-2deg);
    }

    /* ============================================
       Card — one base, four uses (controls, hero,
       playoff, info). All share radius, top accent,
       border, shadow, padding scale.
       ============================================ */
    .panel {
        position: relative;
        overflow: hidden;
        background: var(--card-bg);
        border: var(--card-border);
        border-radius: var(--card-radius);
        box-shadow: var(--card-shadow);
        backdrop-filter: blur(18px);
        max-width: var(--rail-max);
        margin: 0 auto;
        width: 100%;
    }

    .panel::before {
        content: "";
        position: absolute;
        inset: 0 0 auto;
        height: 3px;
        background: var(--card-accent);
        opacity: 0.95;
    }

    .panel__inner {
        padding: var(--card-padding-y) var(--card-padding-x);
    }

    .panel__eyebrow {
        margin-bottom: 0.75rem;
    }

    /* Hero card — the page's "answer" */
    .panel--hero {
        box-shadow:
            0 32px 80px rgba(0, 53, 128, 0.1),
            0 4px 12px rgba(16, 24, 40, 0.05),
            inset 0 1px 0 rgba(255, 255, 255, 0.8);
        background:
            linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(255, 255, 255, 0.86));
    }

    .panel--hero::before {
        height: 4px;
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
        border: 1px solid rgba(0, 53, 128, 0.06);
        min-height: 96px;
    }

    .hero-stat--primary {
        background: linear-gradient(180deg, var(--accent-ice), #ffffff);
        border-color: rgba(0, 53, 128, 0.16);
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8);
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
        border-radius: 0.375rem;
        box-shadow: 0 8px 18px rgba(0, 0, 0, 0.18);
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
        border-radius: 6px;
        background: rgba(0, 53, 128, 0.08);
    }

    .hero-stat-skel__label {
        width: 4rem;
        height: 0.7rem;
        border-radius: 4px;
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
        justify-content: flex-start;
        max-width: var(--rail-max);
        margin: 0 auto;
        padding: 0.5rem 0 0.75rem;
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
        color: var(--accent);
        font-size: 0.82rem;
        font-weight: 700;
        text-decoration: none;
        background: transparent;
        border: 1px solid rgba(0, 53, 128, 0.16);
        border-radius: 999px;
        padding: 0.35rem 0.75rem;
        cursor: pointer;
        transition: background 0.15s ease, color 0.15s ease;
    }

    .playoff-tracker__toggle:hover {
        background: var(--accent-ice);
        color: var(--accent-strong);
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
    .panel--info::before {
        background: linear-gradient(90deg, #003580 0%, #4f7dd8 60%, #b9cdf0 100%);
    }

    .panel__inner--info {
        padding: 1.5rem 1.5rem;
    }

    .info-grid {
        display: grid;
        grid-template-columns: minmax(0, 0.7fr) minmax(0, 1.3fr);
        gap: 1.5rem;
    }

    .info-card__eyebrow {
        margin: 0 0 0.4rem;
        color: var(--accent);
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
            padding: 1.5rem 1rem 3rem;
        }

        .hero-header {
            margin-bottom: 1.5rem;
        }

        .hero-title {
            font-size: clamp(2.1rem, 11vw, 3.4rem);
        }

        .dashboard__rail {
            gap: 1.1rem;
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
</style>
