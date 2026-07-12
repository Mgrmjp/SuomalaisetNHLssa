<script>
// @ts-nocheck

import { AlertCircle, Loader2, TableProperties } from 'lucide-svelte'
import { onMount } from 'svelte'
import ConferenceStandings from '$lib/components/standings/ConferenceStandings.svelte'
import { loadStandings, standings, standingsLoading } from '$lib/stores/gameData.js'
import { fetchLocalJSON } from '$lib/utils/apiHelpers.js'

let _error = $state(null)
let _activeConference = $state('eastern') // 'eastern' or 'western'
let _showAdvancedStats = $state(false) // Advanced stats toggle
let _lastGameDate = $state('') // Most recent game date in manifest
let _manifestLastUpdated = $state('') // Manifest last updated timestamp

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
    {#if hasAnyData}
        <!-- Controls -->
        <div class="standings-controls mb-6 flex flex-wrap items-center justify-center gap-4">
            <!-- Conference Toggle -->
            <div class="conference-toggle flex gap-x-1 border border-gray-200 bg-gray-100 p-1">
                <button
                    type="button"
                    class="cursor-pointer border border-transparent px-4 py-2 text-sm font-medium text-gray-600 transition-colors hover:bg-white hover:text-gray-900"
                    class:bg-white={_activeConference === "eastern"}
                    class:border-gray-300={_activeConference === "eastern"}
                    class:text-gray-900={_activeConference === "eastern"}
                    onclick={() => (_activeConference = "eastern")}
                >
                    Itäinen
                </button>
                <button
                    type="button"
                    class="cursor-pointer border border-transparent px-4 py-2 text-sm font-medium text-gray-600 transition-colors hover:bg-white hover:text-gray-900"
                    class:bg-white={_activeConference === "western"}
                    class:border-gray-300={_activeConference === "western"}
                    class:text-gray-900={_activeConference === "western"}
                    onclick={() => (_activeConference = "western")}
                >
                    Läntinen
                </button>
            </div>

            <!-- Advanced Stats Toggle -->
            <button
                type="button"
                class="advanced-stats-toggle cursor-pointer border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
                class:bg-blue-50={_showAdvancedStats}
                class:border-blue-300={_showAdvancedStats}
                class:text-blue-700={_showAdvancedStats}
                aria-pressed={_showAdvancedStats}
                onclick={() => (_showAdvancedStats = !_showAdvancedStats)}
            >
                Lisätilastot
            </button>
        </div>
    {/if}

    <!-- Main Content -->
    <div class="standings-main-container max-w-7xl mx-auto">
        {#if _loading && !hasAnyData}
            <!-- Initial Loading State -->
            <div class="standings-loading-state text-center py-16">
                <div
                    class="mb-4 inline-flex h-16 w-16 items-center justify-center border border-blue-200 bg-blue-100"
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
                    class="mb-4 inline-flex h-16 w-16 items-center justify-center border border-red-200 bg-red-100"
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
                    class="inline-flex cursor-pointer items-center border border-blue-700 bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none"
                >
                    Yritä uudelleen
                </button>
            </div>
        {:else if !hasAnyData && !_loading}
            <!-- No Data State -->
            <div class="standings-empty-state text-center py-16">
                <div
                    class="mb-4 inline-flex h-16 w-16 items-center justify-center border border-gray-200 bg-gray-100"
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

    .standings-view :global(*) {
        border-radius: 0 !important;
        box-shadow: none !important;
    }

    .standings-view :global(a:focus-visible),
    .standings-view :global(button:focus-visible),
    .standings-view :global(input:focus-visible) {
        outline: 3px solid var(--accent) !important;
        outline-offset: 2px;
    }
</style>
