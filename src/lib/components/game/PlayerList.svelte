<script>
// @ts-nocheck

import { setDate } from 'globalThis.$lib/stores/gameData.js'
import {
    getSavePercentage,
    hasPoints,
    isDefense,
    isGoalie,
} from 'globalThis.$lib/utils/positionHelpers.js'
import { onMount } from 'svelte'
import Swiper from 'swiper'
import { FreeMode, Mousewheel } from 'swiper/modules'

/** @type {any} */
let forwardsSwiper = null
/** @type {any} */
let defendersSwiper = null
/** @type {any} */
let goaliesSwiper = null
let isMobile = false

/** @typedef {Record<string, any> & { shots_against?: number, shotsAgainst?: number, saves?: number, goalie_saves?: number, goals_against?: number, goalsAgainst?: number, time_on_ice?: string, toi?: string, playerId?: number, game_id?: number, points?: number, goals?: number, plus_minus?: number, assists?: number }} PlayerData */

function checkMobile() {
    isMobile = typeof window !== 'undefined' && window.innerWidth < 768
}

function initSwipers() {
    checkMobile()
    if (!isMobile) return

    const swiperConfig = /** @type {any} */ ({
        modules: [FreeMode, Mousewheel],
        slidesPerView: 'auto',
        spaceBetween: 12,
        freeMode: {
            enabled: true,
            sticky: false,
            momentumRatio: 0.8,
            momentumVelocityRatio: 0.8,
        },
        mousewheel: {
            forceToAxis: true,
        },
        grabCursor: true,
        cssMode: false,
    })

    const forwardsEl = document.querySelector('.swiper-forwards')
    const defendersEl = document.querySelector('.swiper-defenders')
    const goaliesEl = document.querySelector('.swiper-goalies')

    if (forwardsEl && !forwardsSwiper) {
        forwardsSwiper = new Swiper(/** @type {HTMLElement} */ (forwardsEl), swiperConfig)
    }
    if (defendersEl && !defendersSwiper) {
        defendersSwiper = new Swiper(/** @type {HTMLElement} */ (defendersEl), swiperConfig)
    }
    if (goaliesEl && !goaliesSwiper) {
        goaliesSwiper = new Swiper(/** @type {HTMLElement} */ (goaliesEl), swiperConfig)
    }
}

function destroySwipers() {
    if (forwardsSwiper) {
        forwardsSwiper.destroy(true, true)
        forwardsSwiper = null
    }
    if (defendersSwiper) {
        defendersSwiper.destroy(true, true)
        defendersSwiper = null
    }
    if (goaliesSwiper) {
        goaliesSwiper.destroy(true, true)
        goaliesSwiper = null
    }
}

function handleResize() {
    const wasMobile = isMobile
    checkMobile()
    if (wasMobile !== isMobile) {
        destroySwipers()
        if (isMobile) {
            setTimeout(initSwipers, 100)
        }
    }
}

onMount(() => {
    checkMobile()
    setTimeout(initSwipers, 100)
    window.addEventListener('resize', handleResize)
    return () => {
        window.removeEventListener('resize', handleResize)
        destroySwipers()
    }
})

// Re-initialize swipers when players data changes
globalThis.$effect(() => {
    if (globalThis.globalThis.globalThis.$players && isMobile) {
        destroySwipers()
        setTimeout(initSwipers, 100)
    }
})

function _handleRetry() {
    const currentDate = new Date().toISOString().split('T')[0] || ''
    setDate(currentDate)
}

/**
 * Check if a goalie actually played in the game
 * Goalie must have logged time, faced shots, made saves, or allowed goals
 *
 * @param {PlayerData} player - Player object
 * @returns {boolean} True if goalie participated in the game
 */
function goalieHasPlayed(player) {
    const shotsAgainst = Number(player.shots_against ?? player.shotsAgainst ?? 0)
    const saves = Number(player.saves ?? player.goalie_saves ?? 0)
    const goalsAgainst = Number(player.goals_against ?? player.goalsAgainst ?? 0)
    const toi = player.time_on_ice || player.toi || ''

    return (
        shotsAgainst > 0 ||
        saves > 0 ||
        goalsAgainst > 0 ||
        (toi !== '' && toi !== '00:00' && toi !== '0:00')
    )
}

/**
 * Filter out invalid players that don't have required fields
 * This prevents duplicate key errors in the each blocks
 *
 * @param {PlayerData[]} players - Array of player objects
 * @returns {PlayerData[]} Filtered array of valid players
 */
function getValidPlayers(players) {
    if (!Array.isArray(players)) return []
    return players.filter((player) => {
        return (
            player &&
            typeof player === 'object' &&
            player.playerId != null &&
            player.game_id != null
        )
    })
}

/**
 * Filter players based on position and performance
 * - Goalies: must have actually played (faced shots, made saves, etc.)
 * - Skaters: must have recorded at least one point
 *
 * @param {PlayerData[]} players - Array of player objects
 * @returns {PlayerData[]} Filtered array of players
 */
const filteredPlayers = globalThis.$derived(
    getValidPlayers(globalThis.globalThis.$players || []).filter((player) => {
        if (isGoalie(player)) {
            return goalieHasPlayed(player)
        }
        return hasPoints(player)
    })
)

/**
 * Sort skaters by points (primary), then goals, plus/minus, and assists
 *
 * @param {PlayerData[]} list - Array of skater objects
 * @returns {PlayerData[]} Sorted array
 */
const sortSkatersByPoints = (list) =>
    [...list].sort(
        (a, b) =>
            (b.points || 0) - (a.points || 0) ||
            (b.goals || 0) - (a.goals || 0) ||
            /** @type {number} */ (b.plus_minus ?? -Infinity) -
                /** @type {number} */ (a.plus_minus ?? -Infinity) ||
            (b.assists || 0) - (a.assists || 0)
    )

/**
 * Sort goalies by save percentage (best first)
 *
 * @param {PlayerData[]} list - Array of goalie objects
 * @returns {PlayerData[]} Sorted array
 */
const sortGoalies = (list) =>
    [...list].sort((a, b) => {
        const aPct = getSavePercentage(a)
        const bPct = getSavePercentage(b)

        if (aPct === null && bPct === null) return 0
        if (aPct === null) return 1
        if (bPct === null) return -1

        return /** @type {number} */ (bPct) - /** @type {number} */ (aPct)
    })

const forwards = globalThis.$derived(
    sortSkatersByPoints(filteredPlayers.filter((p) => !isGoalie(p) && !isDefense(p)))
)
const defenders = globalThis.$derived(
    sortSkatersByPoints(filteredPlayers.filter((p) => !isGoalie(p) && isDefense(p)))
)
const goalies = globalThis.$derived(sortGoalies(filteredPlayers.filter((p) => isGoalie(p))))

const _hasAnyPlayers = globalThis.$derived(forwards.length + defenders.length + goalies.length > 0)

// Determine if there are no games today
/** @type {any} */
const gamesData = globalThis.globalThis.$games
const hasNoGames = globalThis.$derived(
    !globalThis.$isLoading && (!gamesData || !gamesData.games || gamesData.games.length === 0)
)

// Determine if we're in a break
const isBreak = globalThis.$derived(globalThis.$currentBreak !== null)

// Determine which empty state to show
const _emptyStateVariant = globalThis.$derived.by(() => {
    if (isBreak) return 'break'
    if (hasNoGames) return 'no-games'
    return 'no-scorers'
})
</script>

{#if globalThis.$isLoading}
    <div class="py-12">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 2xl:grid-cols-4 gap-7">
            {#each [1,2,3,4,5,6] as _}
                <SkeletonPlayerCard />
            {/each}
        </div>
    </div>
{:else if globalThis.$error}
    <div class="text-center py-8">
        <ErrorBoundary
            error={globalThis.$error}
            retryAction="Yritä uudelleen"
            onRetry={handleRetry}
            variant="error"
        />
    </div>
{:else if !hasAnyPlayers}
    <EmptyState variant={emptyStateVariant} />
{:else}
    <section id="scoringList" class="scoring-list py-12 bg-gray-50/50">
        <div class="scoring-list__container w-full">
            <div class="scoring-list__sections space-y-10">
                {#if forwards.length}
                    <div class="scoring-list__section space-y-4">
                        <div
                            class="scoring-list__section-header flex items-baseline gap-3 pb-2 border-b border-gray-200"
                        >
                            <h2
                                class="scoring-list__section-title text-xl font-bold text-gray-900 tracking-tight"
                            >
                                Hyökkääjät
                            </h2>
                        </div>
                        <!-- Desktop Grid -->
                        <div
                            class="scoring-list__grid hidden md:grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 2xl:grid-cols-4 gap-7"
                        >
                            {#each forwards as player, index (`${player.playerId}-${index}`)}
                                <PlayerCard {player} />
                            {/each}
                        </div>
                        <!-- Mobile Swiper -->
                        <div class="swiper swiper-forwards md:hidden">
                            <div class="swiper-wrapper">
                                {#each forwards as player, index (`${player.playerId}-${index}-mobile`)}
                                    <div class="swiper-slide mobile-card-slide">
                                        <PlayerCard {player} />
                                    </div>
                                {/each}
                            </div>
                        </div>
                    </div>
                {/if}

                {#if defenders.length}
                    <div class="scoring-list__section space-y-4">
                        <div
                            class="scoring-list__section-header flex items-baseline gap-3 pb-2 border-b border-gray-200"
                        >
                            <h2
                                class="scoring-list__section-title text-xl font-bold text-gray-900 tracking-tight"
                            >
                                Puolustajat
                            </h2>
                        </div>
                        <!-- Desktop Grid -->
                        <div
                            class="scoring-list__grid hidden md:grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 2xl:grid-cols-4 gap-7"
                        >
                            {#each defenders as player, index (`${player.playerId}-${index}`)}
                                <PlayerCard {player} />
                            {/each}
                        </div>
                        <!-- Mobile Swiper -->
                        <div class="swiper swiper-defenders md:hidden">
                            <div class="swiper-wrapper">
                                {#each defenders as player, index (`${player.playerId}-${index}-mobile`)}
                                    <div class="swiper-slide mobile-card-slide">
                                        <PlayerCard {player} />
                                    </div>
                                {/each}
                            </div>
                        </div>
                    </div>
                {/if}

                {#if goalies.length}
                    <div class="scoring-list__section space-y-4">
                        <div
                            class="scoring-list__section-header flex items-baseline gap-3 pb-2 border-b border-gray-200"
                        >
                            <h2
                                class="scoring-list__section-title text-xl font-bold text-gray-900 tracking-tight"
                            >
                                Maalivahdit
                            </h2>
                        </div>
                        <!-- Desktop Grid -->
                        <div
                            class="scoring-list__grid hidden md:grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 2xl:grid-cols-4 gap-7"
                        >
                            {#each goalies as player, index (`${player.playerId}-${index}`)}
                                <PlayerCard {player} />
                            {/each}
                        </div>
                        <!-- Mobile Swiper -->
                        <div class="swiper swiper-goalies md:hidden">
                            <div class="swiper-wrapper">
                                {#each goalies as player, index (`${player.playerId}-${index}-mobile`)}
                                    <div class="swiper-slide mobile-card-slide">
                                        <PlayerCard {player} />
                                    </div>
                                {/each}
                            </div>
                        </div>
                    </div>
                {/if}
            </div>
        </div>
    </section>
{/if}

<style>
    /* Mobile-only styles for swiper - prevents affecting desktop layout */
    @media (max-width: 767px) {
        /* Essential Swiper styles - only applied on mobile */
        .swiper {
            overflow: visible;
            position: relative;
            margin-left: -1rem;
            margin-right: -1rem;
            padding: 0.5rem 1rem 1.5rem;
        }

        .swiper-wrapper {
            display: flex;
            align-items: stretch;
            box-sizing: content-box;
            transition-property: transform;
            transition-timing-function: ease-out;
        }

        .swiper-slide {
            flex-shrink: 0;
            position: relative;
        }

        /* Mobile swiper card slides - narrower for more breathing room, taller spacer to prevent cutoff */
        .mobile-card-slide {
            width: min(17rem, calc(100vw - 6.5rem)) !important;
            flex-shrink: 0;
        }

        .mobile-card-slide :global(.player-card__spacer) {
            min-height: 320px;
        }
    }
</style>
