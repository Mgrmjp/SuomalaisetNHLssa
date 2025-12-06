<script>
	import { onMount } from 'svelte'
	import ConferenceStandings from './ConferenceStandings.svelte'
	import { standings, standingsLoading, loadStandings } from '$lib/stores/gameData.js'

	let standingsData = {}
	let loading = true
	let error = null
	let activeConference = 'eastern' // 'eastern' or 'western'
	let showAdvancedStats = false // Advanced stats toggle

	// Subscribe to standings store
	$: if ($standings) {
		standingsData = $standings
	}

	// Subscribe to loading state
	$: loading = $standingsLoading

	// Load standings on component mount
	onMount(async () => {
		try {
			await loadStandings()
		} catch (err) {
			error = err.message || 'Failed to load standings'
			console.error('Standings loading error:', err)
		}
	})

	// Conference data
	$: easternConference = standingsData.eastern || {}
	$: westernConference = standingsData.western || {}
	$: hasEasternData = Object.keys(easternConference).length > 0
	$: hasWesternData = Object.keys(westernConference).length > 0
	$: hasAnyData = hasEasternData || hasWesternData

	// Refresh standings
	async function refreshStandingsData() {
		error = null
		try {
			await loadStandings()
		} catch (err) {
			error = err.message || 'Failed to refresh standings'
			console.error('Standings refresh error:', err)
		}
	}

	// Conference switching
	function switchConference(conference) {
		activeConference = conference
	}
</script>

<div class="standings-view">
	<!-- Header with title and refresh -->
	<div class="mb-8 text-center">
		<h1 class="text-3xl font-bold text-gray-900 mb-2">
			NHL Sarjataulukot 2024-25
		</h1>
		<p class="text-gray-600 mb-6">
			Konferenssit ja divisioonat reaaliajassa
		</p>

		<!-- Controls Section -->
		{#if hasAnyData}
			<div class="flex flex-col sm:flex-row justify-center items-center gap-4 mb-6">
				<!-- Conference Toggle -->
				<div class="inline-flex rounded-lg border border-gray-200 bg-gray-100 p-1">
					<button
						type="button"
						class="{activeConference === 'eastern'
							? 'bg-white text-gray-900 shadow-sm cursor-pointer'
							: 'text-gray-700 hover:bg-white hover:text-gray-900 cursor-pointer'
						} relative inline-flex items-center rounded-md px-4 py-2 text-sm font-medium transition-colors duration-200 focus:z-10 focus:outline-none focus:ring-2 focus:ring-blue-500"
						on:click={() => switchConference('eastern')}
					>
						Itäinen konferenssi
					</button>
					<button
						type="button"
						class="{activeConference === 'western'
							? 'bg-white text-gray-900 shadow-sm cursor-pointer'
							: 'text-gray-700 hover:bg-white hover:text-gray-900 cursor-pointer'
						} relative inline-flex items-center rounded-md px-4 py-2 text-sm font-medium transition-colors duration-200 focus:z-10 focus:outline-none focus:ring-2 focus:ring-blue-500"
						on:click={() => switchConference('western')}
					>
						Läntinen konferenssi
					</button>
				</div>

				<!-- Advanced Stats Toggle -->
				<div class="flex items-center">
					<button
						type="button"
						on:click={() => showAdvancedStats = !showAdvancedStats}
						class="{showAdvancedStats
							? 'bg-blue-600 text-white cursor-pointer'
							: 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50 cursor-pointer'
						} relative inline-flex items-center rounded-md border px-3 py-2 text-sm font-medium transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
					>
						<svg
							class="{showAdvancedStats ? 'text-white' : 'text-gray-500'} -ml-0.5 mr-2 h-4 w-4"
							xmlns="http://www.w3.org/2000/svg"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
						>
							<path d="M9 19v-6a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v6" />
							<path d="M3 12h4l3 9 4-18 3 9h4" />
						</svg>
						Lisätilastot
					</button>
				</div>
			</div>
		{/if}

		<!-- Refresh Button -->
		<div class="flex justify-center mb-6">
			<button
				type="button"
				on:click={refreshStandingsData}
				disabled={loading}
				class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer transition-colors duration-200"
			>
				{#if loading}
					<svg
						class="animate-spin -ml-1 mr-2 h-4 w-4 text-gray-500"
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
					Päivitetään...
				{:else}
					<svg
						class="-ml-1 mr-2 h-4 w-4 text-gray-500"
						xmlns="http://www.w3.org/2000/svg"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
					>
						<path d="M23 4v6h-6M1 20v-6h6" />
						<path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
					</svg>
				{/if}
				Päivitä sarjataulukot
			</button>
		</div>
	</div>

	<!-- Main Content -->
	<div class="max-w-7xl mx-auto">
		{#if loading && !hasAnyData}
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
		{:else if error}
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
					on:click={refreshStandingsData}
					class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 cursor-pointer"
				>
					Yritä uudelleen
				</button>
			</div>
		{:else if !hasAnyData && !loading}
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
			{#if activeConference === 'eastern'}
				<ConferenceStandings
					conferenceData={easternConference}
					conferenceName="eastern"
					{loading}
					{error}
					{showAdvancedStats}
				/>
			{:else if activeConference === 'western'}
				<ConferenceStandings
					conferenceData={westernConference}
					conferenceName="western"
					{loading}
					{error}
					{showAdvancedStats}
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
	/* Component container */
	.standings-view {
		min-height: 400px;
	}

	/* Animation classes */
	@keyframes spin {
		from {
			transform: rotate(0deg);
		}
		to {
			transform: rotate(360deg);
		}
	}

	.animate-spin {
		animation: spin 1s linear infinite;
	}

	/* Responsive adjustments */
	@media (max-width: 640px) {
		.text-3xl {
			font-size: 1.875rem;
		}

		.text-xl {
			font-size: 1.25rem;
		}

		.px-4 {
			padding-left: 0.75rem;
			padding-right: 0.75rem;
		}

		.py-2 {
			padding-top: 0.5rem;
			padding-bottom: 0.5rem;
		}
	}

	</style>