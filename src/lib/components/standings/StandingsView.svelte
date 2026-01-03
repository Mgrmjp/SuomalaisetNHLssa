<script>
import { onMount } from 'svelte'
import ConferenceStandings from '$lib/components/standings/ConferenceStandings.svelte'
import { loadStandings, standings, standingsLoading } from '$lib/stores/gameData.js'

let _error = $state(null)
let _activeConference = $state('eastern') // 'eastern' or 'western'
let _showAdvancedStats = $state(false) // Advanced stats toggle

// Subscribe to standings store using Svelte 5 $effect for non-derived reactive state
let _loading = $state($standingsLoading)
let _standingsData = $state($standings || {})

$effect(() => {
    _loading = $standingsLoading
    _standingsData = $standings || {}
    console.log('🔍 $effect fired:', {
        _loading,
        $standingsLoading,
        hasAnyData,
        easternKeys: Object.keys($standings?.eastern || {}).length,
        westernKeys: Object.keys($standings?.western || {}).length
    })
})

// Conference data - using Svelte 5 $derived runes
const easternConference = $derived($standings?.eastern || {})
const westernConference = $derived($standings?.western || {})
const hasEasternData = $derived(Object.keys(easternConference).length > 0)
const hasWesternData = $derived(Object.keys(westernConference).length > 0)
const hasAnyData = $derived(hasEasternData || hasWesternData)

// Debug $derived
$effect(() => {
    console.log('🔍 $derived values:', {
        hasAnyData,
        hasEasternData,
        hasWesternData,
        _loading,
        loadingCondition: _loading && !hasAnyData
    })
})

// Load standings on component mount
onMount(async () => {
    try {
        await loadStandings()
    } catch (err) {
        _error = err.message || 'Failed to load standings'
        console.error('Standings loading error:', err)
    }
})

// Refresh standings
async function _refreshStandingsData() {
    _error = null
    try {
        await loadStandings()
    } catch (err) {
        _error = err.message || 'Failed to refresh standings'
        console.error('Standings refresh error:', err)
    }
}

// Conference switching
function _switchConference(conference) {
    _activeConference = conference
}
</script>

<div class="standings-view">
	<!-- Header -->
	<div class="mb-8 text-center">
		<h1 class="text-3xl md:text-4xl font-bold text-gray-900 mb-2">
			NHL Sarjataulukot 2024-25
		</h1>
		<p class="text-gray-600 mb-6">
			Konferenssit ja divisioonat
		</p>

		{#if hasAnyData}
			<!-- Controls -->
			<div class="flex flex-wrap justify-center items-center gap-4 mb-6">
				<!-- Conference Toggle -->
				<div class="flex bg-gray-100 rounded-lg p-1 gap-x-1">
					<button
						type="button"
						class="px-4 py-2 rounded-md text-sm font-medium transition-colors cursor-pointer text-gray-600 hover:text-gray-900 hover:bg-white"
						class:bg-white={_activeConference === 'eastern'}
						class:text-gray-900={_activeConference === 'eastern'}
						class:shadow={_activeConference === 'eastern'}
						on:click={() => _activeConference = 'eastern'}
					>
						Itäinen
					</button>
					<button
						type="button"
						class="px-4 py-2 rounded-md text-sm font-medium transition-colors cursor-pointer text-gray-600 hover:text-gray-900 hover:bg-white"
						class:bg-white={_activeConference === 'western'}
						class:text-gray-900={_activeConference === 'western'}
						class:shadow={_activeConference === 'western'}
						on:click={() => _activeConference = 'western'}
					>
						Läntinen
					</button>
				</div>

				<!-- Advanced Stats Toggle -->
				<button
					type="button"
					class="px-4 py-2 rounded-md text-sm font-medium border transition-colors cursor-pointer border-gray-300 text-gray-700 hover:bg-gray-50"
					class:bg-blue-50={_showAdvancedStats}
					class:border-blue-300={_showAdvancedStats}
					class:text-blue-700={_showAdvancedStats}
					on:click={() => _showAdvancedStats = !_showAdvancedStats}
				>
					Lisätilastot
				</button>
			</div>

			<!-- Refresh Button -->
			<div class="flex justify-center">
				<button
					type="button"
					on:click={_refreshStandingsData}
					disabled={_loading}
					class="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white text-sm font-medium rounded-md transition-colors disabled:cursor-not-allowed cursor-pointer"
				>
					{_loading ? 'Päivitetään...' : 'Päivitä sarjataulukot'}
				</button>
			</div>
		{/if}
	</div>

	<!-- Main Content -->
	<div class="max-w-7xl mx-auto">
		{#if _loading && !hasAnyData}
			<!-- Initial Loading State -->
			<div class="text-center py-16">
				<div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-100 mb-4">
					<svg
						class="animate-spin h-8 w-8 text-blue-600"
						xmlns="http://www.w3.org/2000/svg"
						fill="none"
						viewBox="0 0 24 24"
					>
						<circle
							class="opacity-25"
							cx="12"
							cy="12"
							r="10"
							stroke="currentColor"
							stroke-width="4"
						></circle>
						<path
							class="opacity-75"
							fill="currentColor"
							d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
						></path>
					</svg>
				</div>
				<h2 class="text-xl font-semibold text-gray-900 mb-2">
					Ladataan sarjataulukoita...
				</h2>
				<p class="text-gray-600">
					Hetkinen, sarjataulukot ladataan ottelutiedoista.
				</p>
			</div>
		{:else if _error}
			<!-- Error State -->
			<div class="text-center py-16">
				<div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-red-100 mb-4">
					<svg
						class="h-8 w-8 text-red-600"
						xmlns="http://www.w3.org/2000/svg"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
					>
						<circle cx="12" cy="12" r="10" />
						<line x1="12" y1="8" x2="12" y2="12" />
						<line x1="12" y1="16" x2="12.01" y2="16" />
					</svg>
				</div>
				<h2 class="text-xl font-semibold text-gray-900 mb-2">
					Virhe ladattaessa
				</h2>
				<p class="text-gray-600 mb-4">
					Sarjataulukoiden lataaminen epäonnistui. Yritä uudelleen.
				</p>
				<button
					type="button"
					on:click={_refreshStandingsData}
					class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 cursor-pointer"
				>
					Yritä uudelleen
				</button>
			</div>
		{:else if !hasAnyData && !_loading}
			<!-- No Data State -->
			<div class="text-center py-16">
				<div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-4">
					<svg
						class="h-8 w-8 text-gray-400"
						xmlns="http://www.w3.org/2000/svg"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
					>
						<path d="M9 9h6v6h-6z" />
						<path d="M3 3h18v18H3z" />
						<path d="M3 9h18" />
						<path d="M9 3v18" />
					</svg>
				</div>
				<h2 class="text-xl font-semibold text-gray-900 mb-2">
					Ei tietoja saatavilla
				</h2>
				<p class="text-gray-600">
					Ottelutiedot eivät ole vielä saatavilla tälle kaudelle.
				</p>
			</div>
		{:else}
			<!-- Active Conference -->
			{#if _activeConference === 'eastern'}
				<ConferenceStandings
					conferenceData={easternConference}
					conferenceName="eastern"
					{_loading}
					{_error}
					{_showAdvancedStats}
				/>
			{:else if _activeConference === 'western'}
				<ConferenceStandings
					conferenceData={westernConference}
					conferenceName="western"
					{_loading}
					{_error}
					{_showAdvancedStats}
				/>
			{/if}
		{/if}
	</div>

	<!-- Footer -->
	<div class="mt-12 pt-8 border-t border-gray-200 text-center">
		<p class="text-sm text-gray-500">
			Sarjataulukot päivitetään automaattisesti ottelutulosten perusteella.
		</p>
		<p class="text-xs text-gray-400 mt-2">
			Päivitetty: {new Date().toLocaleString('fi-FI')}
		</p>
	</div>
</div>

<style>
	.standings-view {
		min-height: 400px;
	}
</style>
