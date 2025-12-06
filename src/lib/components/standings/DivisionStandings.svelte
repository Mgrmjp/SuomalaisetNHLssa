<script>
	import TeamStandingRow from './TeamStandingRow.svelte'
	import { DIVISION_NAMES } from '$lib/utils/nhlStructure.js'

	export let teams = []
	export let divisionName = ''
	export let conferenceName = ''
	export let showPlayoffIndicator = true
	export let wildCardTeams = [] // Array of team abbreviations that are Wild Cards
	export let showAdvancedStats = false

	// Format division name for display
	$: displayName = DIVISION_NAMES[divisionName] || divisionName
	$: hasTeams = teams && teams.length > 0

	// Table headers
	const baseHeaders = [
		{ key: 'rank', label: 'Sija', center: true, width: 'w-12' },
		{ key: 'team', label: 'Joukkue', center: false, width: '' },
		{ key: 'gamesPlayed', label: 'O', center: true, width: 'w-12' },
		{ key: 'wins', label: 'V', center: true, width: 'w-12' },
		{ key: 'losses', label: 'H', center: true, width: 'w-12' },
		{ key: 'ot', label: 'JA', center: true, width: 'w-12' },
		{ key: 'points', label: 'P', center: true, width: 'w-12' },
		{ key: 'pointsPct', label: 'P%', center: true, width: 'w-14' },
		{ key: 'streak', label: 'Sarja', center: true, width: 'w-14' },
		{ key: 'last10', label: 'V10', center: true, width: 'w-14' }
	]

	const advancedHeaders = [
		{ key: 'powerPlayPercentage', label: 'YV%', center: true, width: 'w-14' },
		{ key: 'penaltyKillPercentage', label: 'AV%', center: true, width: 'w-14' },
		{ key: 'goalDifferential', label: '+/-', center: true, width: 'w-14' },
		{ key: 'goalsForPerGame', label: 'TM/O', center: true, width: 'w-14' },
		{ key: 'goalsAgainstPerGame', label: 'VM/O', center: true, width: 'w-14' }
	]

	$: headers = showAdvancedStats ? [...baseHeaders, ...advancedHeaders] : baseHeaders
</script>

<div class="bg-white rounded-lg shadow-lg overflow-hidden border border-gray-200">
	<!-- Division Header -->
	<div class="px-4 py-3 bg-gradient-to-r from-blue-50 to-blue-100 border-b border-blue-200">
		<h3 class="text-lg font-semibold text-gray-900">
			{displayName}
		</h3>
		<p class="text-xs text-gray-600">
			{hasTeams ? `${teams.length} joukkuetta` : 'Ei tietoja'}
		</p>
	</div>

	{#if hasTeams}
		<div class="overflow-x-auto">
			<table class="w-full text-sm">
				<!-- Table Header -->
				<thead class="bg-gray-50 border-b border-gray-200">
					<tr>
						{#each headers as header}
							<th
								class="px-3 py-2 text-xs font-medium text-gray-700 uppercase tracking-wider {header.width} {header.center ? 'text-center' : 'text-left'}"
							>
								{header.label}
							</th>
						{/each}
					</tr>
				</thead>

				<!-- Table Body -->
				<tbody class="divide-y divide-gray-200">
					{#each teams as team, index}
						<TeamStandingRow
							team={team.team}
							rank={index + 1}
							teamData={team}
							{showPlayoffIndicator}
							isWildCard={wildCardTeams.includes(team.team)}
							{showAdvancedStats}
						/>
					{/each}
				</tbody>
			</table>
		</div>

		<!-- Division Footer with Stats Summary -->
		<div class="px-4 py-2 bg-gray-50 border-t border-gray-200">
			<div class="flex items-center justify-between text-xs text-gray-600">
				<div class="flex items-center space-x-4">
					<!-- Playoff indicator legend -->
					{#if showPlayoffIndicator}
						<div class="flex items-center space-x-2">
							<div class="flex items-center space-x-1">
								<div class="w-2 h-2 bg-green-500 rounded-full"></div>
								<span>Pudotuspelit</span>
							</div>
							<div class="flex items-center space-x-1">
								<div class="w-4 h-1 bg-blue-200 rounded"></div>
								<span>Top 3</span>
							</div>
						</div>
					{/if}
				</div>
				<div>
					Päivitetty: {new Date().toLocaleDateString('fi-FI')}
				</div>
			</div>
		</div>
	{:else}
		<!-- Empty State -->
		<div class="px-6 py-12 text-center">
			<div class="inline-flex items-center justify-center w-12 h-12 rounded-full bg-gray-100 mb-4">
				<svg
					class="w-6 h-6 text-gray-400"
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
			</div>
			<h4 class="text-sm font-medium text-gray-900 mb-1">
				Ei sarjataulukkoa saatavilla
			</h4>
			<p class="text-xs text-gray-500">
				Odottaa ottelutietojen lataamista...
			</p>
		</div>
	{/if}
</div>

<style>
	/* Table responsive design */
	.overflow-x-auto {
		-webkit-overflow-scrolling: touch;
	}

	/* Custom scrollbar for webkit browsers */
	.overflow-x-auto::-webkit-scrollbar {
		height: 6px;
	}

	.overflow-x-auto::-webkit-scrollbar-track {
		background: transparent;
	}

	.overflow-x-auto::-webkit-scrollbar-thumb {
		background-color: rgba(156, 163, 175, 0.5);
		border-radius: 3px;
	}

	.overflow-x-auto::-webkit-scrollbar-thumb:hover {
		background-color: rgba(156, 163, 175, 0.7);
	}

	
	/* Responsive text sizing */
	@media (max-width: 640px) {
		.text-sm {
			font-size: 0.7rem;
		}

		.text-xs {
			font-size: 0.6rem;
		}

		px-3 {
			padding-left: 0.5rem;
			padding-right: 0.5rem;
		}

		py-2 {
			padding-top: 0.25rem;
			padding-bottom: 0.25rem;
		}
	}
</style>