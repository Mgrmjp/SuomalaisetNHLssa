<script>
	import DivisionStandings from './DivisionStandings.svelte'
	import { CONFERENCE_NAMES, calculateWildCardTeams } from '$lib/utils/nhlStructure.js'

	export let conferenceData = {}
	export let conferenceName = ''
	export let loading = false
	export let error = null
	export let showAdvancedStats = false

	// Format conference name for display
	$: displayName = CONFERENCE_NAMES[conferenceName] || conferenceName

	// Check if conference has data
	$: hasData = conferenceData && Object.keys(conferenceData).length > 0
	$: divisions = hasData ? Object.entries(conferenceData) : []
	$: hasDivisions = divisions.length > 0

	// Calculate Wild Card teams for this conference
	$: allConferenceData = hasData ? { [conferenceName]: conferenceData } : {}
	$: wildCardData = hasData ? calculateWildCardTeams(allConferenceData) : {}
	$: wildCardTeams = wildCardData[conferenceName] || []

	// Loading state
	$: isLoading = loading || !hasData

	// Error state
	$: hasError = error !== null
</script>

<div class="conference-standings">
	<!-- Conference Header -->
	{#if hasError}
		<div class="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
			<div class="flex items-center space-x-3">
				<svg
					class="w-5 h-5 text-red-600 flex-shrink-0"
					xmlns="http://www.w3.org/2000/svg"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="2"
					stroke-linecap="round"
					stroke-linejoin="round"
				>
					<circle cx="12" cy="12" r="10" />
					<line x1="12" y1="8" x2="12" y2="12" />
					<line x1="12" y1="16" x2="12.01" y2="16" />
				</svg>
				<div>
					<h3 class="text-sm font-medium text-red-800">
						Virhe ladattaessa sarjataulukkoa
					</h3>
					<p class="text-xs text-red-700 mt-1">
						{error}
					</p>
				</div>
			</div>
		</div>
	{:else if isLoading}
		<div class="mb-6">
			<div class="flex items-center justify-center py-8">
				<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
			</div>
		</div>
	{/if}

	<!-- Conference Title -->
	{#if hasData && !hasError}
		<div class="mb-6">
			<h2 class="text-2xl font-bold text-gray-900 mb-2">
				{displayName}
			</h2>
			<p class="text-gray-600">
				Sarjataulukko ja pudotuspelipaikat
			</p>
		</div>

		<!-- Divisions Grid -->
		<div class="grid gap-6 lg:grid-cols-2 xl:grid-cols-1">
			{#each divisions as [divisionName, teams]}
				<div class="division-container">
					<DivisionStandings
						{teams}
						{divisionName}
						{conferenceName}
						showPlayoffIndicator={true}
						wildCardTeams={wildCardTeams}
						{showAdvancedStats}
					/>
				</div>
			{/each}
		</div>

		<!-- Conference Legend -->
		<div class="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
			<h3 class="text-sm font-medium text-blue-900 mb-3">
				Selitteet
			</h3>
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-xs">
				<div class="flex items-center space-x-2">
					<div class="w-2 h-2 bg-green-500 rounded-full"></div>
					<span class="text-gray-700">Wild Card -pudotuspelipaikka</span>
				</div>
				<div class="flex items-center space-x-2">
					<div class="w-4 h-1 bg-blue-200 rounded"></div>
					<span class="text-gray-700">Divisioonavoitto (Top 3)</span>
				</div>
				<div class="flex items-center space-x-2">
					<span class="font-medium text-gray-700">O=Ottelut</span>
					<span class="text-gray-500">V=Voitot</span>
					<span class="text-gray-500">H=Häviöt</span>
					<span class="text-gray-500">JA=Jälkieisa-häviöt</span>
				</div>
				<div class="flex items-center space-x-2">
					<span class="font-medium text-gray-700">P=Pisteet</span>
					<span class="text-gray-500">P%=Pisteprosentti (järjestys)</span>
				</div>
				<div class="flex items-center space-x-2">
					<span class="font-medium text-gray-700">Sarja=Tulossarja</span>
					<span class="text-gray-500">V10=Viimeiset 10</span>
				</div>
				<div class="flex items-center space-x-2">
					<div class="inline-flex items-center px-2 py-1 rounded-full text-xs bg-green-100 text-green-700">
						W3
					</div>
					<span class="text-gray-700">3 voittoa peräkkäin</span>
				</div>
			</div>
		</div>
	{:else if !isLoading && !hasError}
		<!-- Empty State -->
		<div class="text-center py-12">
			<svg
				class="mx-auto h-12 w-12 text-gray-400 mb-4"
				xmlns="http://www.w3.org/2000/svg"
				viewBox="0 0 24 24"
				fill="none"
				stroke="currentColor"
				stroke-width="2"
				stroke-linecap="round"
				stroke-linejoin="round"
			>
				<path d="M9 9h6v6h-6z" />
				<path d="M3 3h18v18H3z" />
				<path d="M3 9h18" />
				<path d="M9 3v18" />
			</svg>
			<h3 class="text-lg font-medium text-gray-900 mb-2">
				Ei sarjataulukkoa saatavilla
			</h3>
			<p class="text-gray-600 max-w-md mx-auto">
				Sarjataulukko ladataan hetken kuluttua, kun ottelutiedot ovat saatavilla.
			</p>
		</div>
	{/if}
</div>

<style>
	/* Conference grid layout */
	.grid {
		display: grid;
		gap: 1.5rem;
	}

	@media (min-width: 1024px) {
		.lg\:grid-cols-2 {
			grid-template-columns: repeat(2, minmax(0, 1fr));
		}
	}

	@media (min-width: 1280px) {
		.xl\:grid-cols-1 {
			grid-template-columns: repeat(1, minmax(0, 1fr));
		}
	}

	/* Legend grid */
	@media (min-width: 768px) {
		.md\:grid-cols-2 {
			grid-template-columns: repeat(2, minmax(0, 1fr));
		}
	}

	@media (min-width: 1024px) {
		.lg\:grid-cols-3 {
			grid-template-columns: repeat(3, minmax(0, 1fr));
		}
	}

	/* Loading animation */
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

	/* Conference header styling */
	.conference-standings h2 {
		border-bottom: 2px solid theme('colors.blue.600');
		padding-bottom: 0.5rem;
		display: inline-block;
	}

	/* Responsive adjustments */
	@media (max-width: 640px) {
		.text-2xl {
			font-size: 1.5rem;
		}

		.grid {
			gap: 1rem;
		}

		.p-4 {
			padding: 1rem;
		}
	}
</style>