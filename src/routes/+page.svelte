<script>
import FinnishRoster from '$lib/components/game/FinnishRoster.svelte'
import PlayerList from '$lib/components/game/PlayerList.svelte'
import SimpleDateControls from '$lib/components/game/SimpleDateControls.svelte'
import Snowfall from '$lib/components/ui/Snowfall.svelte'
import StandingsView from '$lib/components/standings/StandingsView.svelte'
import ViewToggle from '$lib/components/ui/ViewToggle.svelte'
import { base } from '$app/paths'
import { onMount } from 'svelte'
import { get } from 'svelte/store'
import {
    latestPrepopulatedDate,
    players,
    resetToDefault,
    selectedDate,
    selectedView,
    setDate,
} from '$lib/stores/gameData.js'

const _sparkles = Array.from({ length: 28 }, () => ({
    left: `${Math.random() * 100}%`,
    top: `${Math.random() * 90}%`,
    delay: `${Math.random() * 2}s`,
    duration: `${3.5 + Math.random() * 3}s`,
    size: `${3 + Math.random() * 6}px`,
    blur: `${Math.random() > 0.5 ? 0 : 1}px`,
}))

// Reactive variables
$: totalGoals = $players?.reduce((sum, player) => sum + player.goals, 0) || 0
$: totalAssists = $players?.reduce((sum, player) => sum + player.assists, 0) || 0
$: totalPoints = $players?.reduce((sum, player) => sum + player.points, 0) || 0
$: totalPenaltyMinutes =
    $players?.reduce((sum, player) => sum + (player.penalty_minutes || 0), 0) || 0
$: totalPlayers = $players?.length || 0

// Default to the latest prepopulated date on first load
onMount(() => {
    // Avoid reloading if user already selected a date
    if ($selectedDate) return

    // Use the latest available date - this is the most recent data we have
    // If latestPrepopulatedDate is not yet loaded, it defaults to '2026-01-03'
    const latestDate = get(latestPrepopulatedDate)
    if (latestDate) {
        setDate(latestDate)
    }
})
</script>

<svelte:head>
    <title>Suomalaiset NHL-pelaajat - Reaaliaikaiset tilastot</title>
    <meta
        name="description"
        content="Miten suomalaisilla kulkee NHL:ssä? Tutki päivän ottelut, pisteet ja onnistumiset."
    />
</svelte:head>

<div class="w-full max-w-6xl mx-auto px-4 py-8 relative" style="z-index: 1; position: relative;">
    <div class="text-center mb-8 hero-header space-y-3 relative overflow-hidden">
        <Snowfall />
        <div class="sparkles pointer-events-none" aria-hidden="true">
            {#each _sparkles as sparkle, idx}
                <span
                    class="sparkle"
                    style={`--spark-left:${sparkle.left};--spark-top:${sparkle.top};--spark-delay:${sparkle.delay};--spark-duration:${sparkle.duration};--spark-size:${sparkle.size};--spark-blur:${sparkle.blur};`}
                ></span>
            {/each}
        </div>
        <div class="relative space-y-3 p-6">
            <button
                onclick={resetToDefault}
                class="logo-button focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2 rounded-xl transition-all duration-300"
                aria-label="Palaa etusivulle ja nollaa valinnat"
            >
                <img
                    src={base + "/logo.svg"}
                    alt="Suomalaiset NHL-pelaajat"
                    class="w-16 h-16 mx-auto mb-4 logo-img"
                />
            </button>
            <h1 class="text-3xl font-bold text-gray-900 hero-title">
                Miten suomalaisilla kulkee NHL:ssä?
            </h1>
            <p class="text-gray-700 hero-subtitle">Tutki päivän ottelut, pisteet ja onnistumiset</p>
        </div>
    </div>

    <div class="space-y-8">
        <!-- Controls Section -->
        <div>
            <SimpleDateControls />
        </div>

        <!-- View Toggle -->
        <ViewToggle />

        <!-- Hero Stats - Only show on Players view -->
        {#if $selectedView === "players" && $players && $players.length > 0}
            <div class="text-center mb-4">
                <p class="text-sm text-gray-600">Valitun päivän yhteistilastot</p>
            </div>
            <div class="flex flex-wrap justify-center gap-8 hero-stats">
                <div class="text-center hero-stat hero-stat--goals">
                    <div class="flex justify-center mb-1 hero-stat__icon-wrap">
                        <svg
                            class="text-gray-600 hero-stat__icon hero-stat__icon--goals"
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 512 512"
                        >
                            <path
                                fill="currentColor"
                                d="M0 160c0-53 114.6-96 256-96s256 43 256 96s-114.6 96-256 96S0 213 0 160m0 82.2V352c0 53 114.6 96 256 96s256-43 256-96V242.2c-113.4 82.3-398.5 82.4-512 0"
                            />
                        </svg>
                    </div>
                    <div class="text-xl font-bold text-gray-800">{totalGoals}</div>
                    <div class="text-xs text-gray-600 hero-stat__label" data-full="Maalit (Goals)">
                        Maalit
                    </div>
                </div>
                <div class="text-center hero-stat hero-stat--assists">
                    <div class="flex justify-center mb-1 hero-stat__icon-wrap">
                        <svg
                            class="text-gray-600 hero-stat__icon"
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 640 512"
                        >
                            <path
                                fill="currentColor"
                                d="m323.4 85.2l-96.8 78.4c-16.1 13-19.2 36.4-7 53.1c12.9 17.8 38 21.3 55.3 7.8l99.3-77.2c7-5.4 17-4.2 22.5 2.8s4.2 17-2.8 22.5L373 188.8L550.2 352H592c26.5 0 48-21.5 48-48V176c0-26.5-21.5-48-48-48h-80.7l-3.9-2.5L434.8 79c-15.3-9.8-33.2-15-51.4-15c-21.8 0-43 7.5-60 21.2m22.8 124.4l-51.7 40.2c-31.5 24.6-77.2 18.2-100.8-14.2c-22.2-30.5-16.6-73.1 12.7-96.8l83.2-67.3c-11.6-4.9-24.1-7.4-36.8-7.4C234 64 215.7 69.6 200 80l-72 48H48c-26.5 0-48 21.5-48 48v128c0 26.5 21.5 48 48 48h108.2l91.4 83.4c19.6 17.9 49.9 16.5 67.8-3.1c5.5-6.1 9.2-13.2 11.1-20.6l17 15.6c19.5 17.9 49.9 16.6 67.8-2.9c4.5-4.9 7.8-10.6 9.9-16.5c19.4 13 45.8 10.3 62.1-7.5c17.9-19.5 16.6-49.9-2.9-67.8z"
                            />
                        </svg>
                    </div>
                    <div class="text-xl font-bold text-gray-800">{totalAssists}</div>
                    <div
                        class="text-xs text-gray-600 hero-stat__label"
                        data-full="Syötöt (Assists)"
                    >
                        Syötöt
                    </div>
                </div>
                <div class="text-center hero-stat hero-stat--points">
                    <div class="flex justify-center mb-1 hero-stat__icon-wrap">
                        <svg
                            class="text-gray-600 hero-stat__icon hero-stat__icon--points"
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 24 24"
                        >
                            <path
                                fill="currentColor"
                                d="M20 12a2 2 0 0 0-.703.133l-2.398-1.963c.059-.214.101-.436.101-.67C17 8.114 15.886 7 14.5 7S12 8.114 12 9.5c0 .396.1.765.262 1.097l-2.909 3.438A2.06 2.06 0 0 0 9 14c-.179 0-.348.03-.512.074l-2.563-2.563C5.97 11.348 6 11.179 6 11c0-1.108-.892-2-2-2s-2 .892-2 2s.892 2 2 2c.179 0 .348-.03.512-.074l2.563 2.563A1.906 1.906 0 0 0 7 16c0 1.108.892 2 2 2s2-.892 2-2c0-.237-.048-.46-.123-.671l2.913-3.442c.227.066.462.113.71.113a2.48 2.48 0 0 0 1.133-.281l2.399 1.963A2.077 2.077 0 0 0 18 14c0 1.108.892 2 2 2s2-.892 2-2s-.892-2-2-2"
                            />
                        </svg>
                    </div>
                    <div class="text-xl font-bold text-gray-900">{totalPoints}</div>
                    <div
                        class="text-xs text-gray-600 hero-stat__label"
                        data-full="Pisteet (Points)"
                    >
                        Pisteet
                    </div>
                </div>
                <div class="text-center hero-stat hero-stat--pims">
                    <div class="flex justify-center mb-1 hero-stat__icon-wrap">
                        <svg
                            class="text-gray-600 hero-stat__icon"
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 24 24"
                        >
                            <g fill="currentColor" fill-rule="evenodd" clip-rule="evenodd">
                                <path
                                    d="M10 5a2 2 0 0 0-2 2v3h2.4A7.48 7.48 0 0 0 8 15.5a7.48 7.48 0 0 0 2.4 5.5H5a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h1V7a4 4 0 1 1 8 0v1.15a7.446 7.446 0 0 0-1.943.685A.999.999 0 0 1 12 8.5V7a2 2 0 0 0-2-2"
                                />
                                <path
                                    d="M10 15.5a5.5 5.5 0 1 1 11 0a5.5 5.5 0 0 1-11 0m6.5-1.5a1 1 0 1 0-2 0v1.5a1 1 0 0 0 .293.707l1 1a1 1 0 0 0 1.414-1.414l-.707-.707z"
                                />
                            </g>
                        </svg>
                    </div>
                    <div class="text-xl font-bold text-gray-700">{totalPenaltyMinutes}</div>
                    <div
                        class="text-xs text-gray-600 hero-stat__label"
                        data-full="Rangaistusmin (PIM)"
                    >
                        Rangaistusmin
                    </div>
                </div>
                <div class="text-center hero-stat hero-stat--onboard">
                    <div class="flex justify-center mb-1 hero-stat__icon-wrap">
                        <svg
                            class="text-gray-600 hero-stat__icon"
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 24 24"
                        >
                            <path
                                fill="currentColor"
                                d="M5 6c-1.1 0-2 .9-2 2s.9 2 2 2s2-.89 2-2s-.89-2-2-2m7-2a2 2 0 1 0 2 2c0-1.11-.89-2-2-2m7-2c-1.1 0-2 .9-2 2s.9 2 2 2s2-.89 2-2s-.89-2-2-2M3.5 11c-.83 0-1.5.67-1.5 1.5V17h1v5h4v-5h1v-4.5c0-.83-.67-1.5-1.5-1.5zm7-2C9.67 9 9 9.67 9 10.5V15h1v5h4v-5h1v-4.5c0-.83-.67-1.5-1.5-1.5zm7-2c-.83 0-1.5.67-1.5 1.5V13h1v5h4v-5h1V8.5c0-.83-.67-1.5-1.5-1.5z"
                            />
                        </svg>
                    </div>
                    <div class="text-xl font-bold text-gray-800">{totalPlayers}</div>
                    <div
                        class="text-xs text-gray-600 hero-stat__label"
                        data-full="Pelaajaa kokoonpanossa (Players in lineup)"
                    >
                        Kokoonpanossa
                    </div>
                </div>
            </div>
        {/if}

        <!-- Content based on selected view -->
        {#if $selectedView === "players"}
            <!-- Player List -->
            <PlayerList />
        {:else if $selectedView === "standings"}
            <!-- Standings View -->
            <StandingsView />
        {:else if $selectedView === "roster"}
            <!-- Finnish Roster View -->
            <FinnishRoster />
        {/if}
    </div>

    <!-- Footer link -->
    <footer class="text-center py-4 text-sm text-gray-500">
        <a href={base + "/tietoa"} class="hover:text-gray-700 transition-colors"
            >Tietoa sivustosta</a
        >
    </footer>
</div>

<style>
    .sparkles {
        position: absolute;
        inset: 0;
        overflow: hidden;
    }

    .sparkle {
        position: absolute;
        left: var(--spark-left);
        top: var(--spark-top);
        width: var(--spark-size);
        height: var(--spark-size);
        border-radius: 9999px;
        background: radial-gradient(circle, #e5e7eb 0%, #e5e7eb 50%, transparent 100%);
        opacity: 0.8;
        filter: blur(var(--spark-blur));
        animation: sparkle-float var(--spark-duration) ease-in-out infinite;
        animation-delay: var(--spark-delay);
    }

    @keyframes sparkle-float {
        0% {
            transform: translate3d(0, 0, 0) scale(0.6);
            opacity: 0;
        }
        20% {
            opacity: 0.8;
            transform: translate3d(4px, -6px, 0) scale(1);
        }
        60% {
            opacity: 0.6;
            transform: translate3d(-4px, 6px, 0) scale(0.9);
        }
        100% {
            opacity: 0;
            transform: translate3d(0, 12px, 0) scale(0.5);
        }
    }

    .hero-stat {
        position: relative;
        min-width: 110px;
    }

    .hero-stat__icon {
        width: 1.5rem;
        height: 1.5rem;
    }

    .hero-stat__icon-wrap {
        min-height: 1.75rem;
        align-items: center;
    }

    .hero-stat__icon--goals {
        width: 1.25rem;
        height: 1.25rem;
    }

    .hero-stat__icon--points {
        width: 1.75rem;
        height: 1.75rem;
    }

    .hero-stat__label {
        max-width: 80px;
        margin: 0.25rem auto 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
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
        transition-delay: 0s;
    }

    .hero-stat:hover .hero-stat__label::after {
        opacity: 1;
        transition-delay: 0.25s;
    }

    .logo-button {
        background: transparent;
        border: none;
        padding: 0;
        cursor: pointer;
        display: block;
        margin: 0 auto;
    }

    .logo-button:hover .logo-img {
        transform: scale(1.05) rotate(-2deg);
        filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.1));
    }

    .logo-img {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
</style>
