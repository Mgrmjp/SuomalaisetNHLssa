<script>
// @ts-nocheck

import { AlertCircle, Loader2, TableProperties } from 'lucide-svelte'
import { onMount } from 'svelte'
import { getCurrentSeason } from '$lib/api/nhlApi.js'
import ConferenceStandings from '$lib/components/standings/ConferenceStandings.svelte'
import { loadStandings, standings, standingsLoading } from '$lib/stores/gameData.js'
import { fetchLocalJSON } from '$lib/utils/apiHelpers.js'

let _error = $state(null)
let _activeConference = $state('eastern') // 'eastern' or 'western'
let _showAdvancedStats = $state(false) // Advanced stats toggle
let _lastGameDate = $state('') // Most recent game date in manifest
let _manifestLastUpdated = $state('') // Manifest last updated timestamp

// Get current season
const _currentSeason = getCurrentSeason()

// Subscribe to standings store using Svelte 5 $effect for non-derived reactive state
let _loading = $state($standingsLoading)

$effect(() => {
    _loading = $standingsLoading
})

// Conference data - using Svelte 5 $derived runes
const easternConference = $derived($standings?.eastern || {})
const westernConference = $derived($standings?.western || {})
const hasEasternData = $derived(Object.keys(easternConference).length > 0)
const hasWesternData = $derived(Object.keys(westernConference).length > 0)
const hasAnyData = $derived(hasEasternData || hasWesternData)

// Load standings on component mount
onMount(async () => {
    try {
        // Fetch manifest to get last game date
        const manifest = await fetchLocalJSON('/data/games_manifest.json')
        if (manifest?.games?.length) {
            _lastGameDate = manifest.games[manifest.games.length - 1]
            _manifestLastUpdated = manifest.lastUpdated
        }
        await loadStandings()
    } catch (err) {
        _error = /** @type {Error} */ (err).message || 'Failed to load standings'
        console.error('Standings loading error:', err)
    }
})

// Refresh standings
async function _refreshStandingsData() {
    _error = null
    try {
        await loadStandings()
    } catch (err) {
        _error = /** @type {Error} */ (err).message || 'Failed to refresh standings'
        console.error('Standings refresh error:', err)
    }
}
</script>

<div class="standings-view">
    <!-- Header -->
    <div class="standings-header mb-8 text-center">
        <h1 class="text-3xl md:text-4xl font-bold text-gray-900 mb-2">
            NHL Sarjataulukot {_currentSeason}
        </h1>
        <p class="text-gray-600 mb-6">Konferenssit ja divisioonat</p>

        {#if hasAnyData}
            <!-- Controls -->
            <div class="standings-controls flex flex-wrap justify-center items-center gap-4 mb-6">
                <!-- Conference Toggle -->
                <div class="conference-toggle flex bg-gray-100 rounded-lg p-1 gap-x-1">
                    <button
                        type="button"
                        class="px-4 py-2 rounded-md text-sm font-medium transition-colors cursor-pointer text-gray-600 hover:text-gray-900 hover:bg-white"
                        class:bg-white={_activeConference === "eastern"}
                        class:text-gray-900={_activeConference === "eastern"}
                        class:shadow={_activeConference === "eastern"}
                        onclick={() => (_activeConference = "eastern")}
                    >
                        Itäinen
                    </button>
                    <button
                        type="button"
                        class="px-4 py-2 rounded-md text-sm font-medium transition-colors cursor-pointer text-gray-600 hover:text-gray-900 hover:bg-white"
                        class:bg-white={_activeConference === "western"}
                        class:text-gray-900={_activeConference === "western"}
                        class:shadow={_activeConference === "western"}
                        onclick={() => (_activeConference = "western")}
                    >
                        Läntinen
                    </button>
                </div>

                <!-- Advanced Stats Toggle -->
                <button
                    type="button"
                    class="advanced-stats-toggle px-4 py-2 rounded-md text-sm font-medium border transition-colors cursor-pointer border-gray-300 text-gray-700 hover:bg-gray-50"
                    class:bg-blue-50={_showAdvancedStats}
                    class:border-blue-300={_showAdvancedStats}
                    class:text-blue-700={_showAdvancedStats}
                    onclick={() => (_showAdvancedStats = !_showAdvancedStats)}
                >
                    Lisätilastot
                </button>
            </div>
        {/if}
    </div>

    <!-- Main Content -->
    <div class="standings-main-container max-w-7xl mx-auto">
        {#if _loading && !hasAnyData}
            <!-- Initial Loading State -->
            <div class="standings-loading-state text-center py-16">
                <div
                    class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-100 mb-4"
                >
                    <Loader2 class="animate-spin h-8 w-8 text-blue-600" aria-hidden="true" />
                </div>
                <h2 class="text-xl font-semibold text-gray-900 mb-2">
                    Ladataan sarjataulukoita...
                </h2>
                <p class="text-gray-600">Hetkinen, sarjataulukot ladataan ottelutiedoista.</p>
            </div>
        {:else if _error}
            <!-- Error State -->
            <div class="standings-error-state text-center py-16">
                <div
                    class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-red-100 mb-4"
                >
                    <AlertCircle class="h-8 w-8 text-red-600" aria-hidden="true" />
                </div>
                <h2 class="text-xl font-semibold text-gray-900 mb-2">Virhe ladattaessa</h2>
                <p class="text-gray-600 mb-4">
                    Sarjataulukoiden lataaminen epäonnistui. Yritä uudelleen.
                </p>
                <button
                    type="button"
                    onclick={_refreshStandingsData}
                    class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 cursor-pointer"
                >
                    Yritä uudelleen
                </button>
            </div>
        {:else if !hasAnyData && !_loading}
            <!-- No Data State -->
            <div class="standings-empty-state text-center py-16">
                <div
                    class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-4"
                >
                    <TableProperties class="h-8 w-8 text-gray-400" aria-hidden="true" />
                </div>
                <h2 class="text-xl font-semibold text-gray-900 mb-2">Ei tietoja saatavilla</h2>
                <p class="text-gray-600">Ottelutiedot eivät ole vielä saatavilla tälle kaudelle.</p>
            </div>
        {:else}
            <!-- Active Conference -->
            {#if _activeConference === "eastern"}
                <ConferenceStandings
                    conferenceData={easternConference}
                    conferenceName="eastern"
                    loading={_loading}
                    error={_error}
                    showAdvancedStats={_showAdvancedStats}
                />
            {:else if _activeConference === "western"}
                <ConferenceStandings
                    conferenceData={westernConference}
                    conferenceName="western"
                    loading={_loading}
                    error={_error}
                    showAdvancedStats={_showAdvancedStats}
                />
            {/if}
        {/if}
    </div>

    <!-- Footer -->
    <div class="mt-12 pt-8 border-t border-gray-200 text-center">
        <p class="text-sm text-gray-500">
            Sarjataulukot päivitetään automaattisesti ottelutulosten perusteella.
        </p>
        {#if _lastGameDate}
            <p class="text-xs text-gray-400 mt-2">
                Tiedot {new Date(_lastGameDate + 'T00:00:00').toLocaleDateString("fi-FI")} asti
                {#if _manifestLastUpdated}
                    • Päivitetty {new Date(_manifestLastUpdated).toLocaleDateString("fi-FI")}
                {/if}
            </p>
        {:else}
            <p class="text-xs text-gray-400 mt-2">
                Päivitetty: {new Date().toLocaleString("fi-FI")}
            </p>
        {/if}
    </div>
</div>

<style>
    .standings-view {
        min-height: 400px;
    }
</style>
