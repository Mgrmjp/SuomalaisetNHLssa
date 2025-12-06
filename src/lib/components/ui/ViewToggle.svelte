<script>
	import { selectedView, setView } from '$lib/stores/gameData.js'

	/**
	 * Handle view change
	 * @param {string} view - 'players' or 'standings'
	 */
	function handleViewChange(view) {
		setView(view)
	}

	$: playersActive = $selectedView === 'players'
	$: standingsActive = $selectedView === 'standings'
</script>

<div class="flex justify-center mb-6">
	<div class="inline-flex rounded-lg border border-gray-200 bg-gray-100 p-1" role="group">
		<!-- Players Tab -->
		<button
			type="button"
			class="{playersActive
				? 'bg-white text-gray-900 shadow-sm cursor-pointer'
				: 'text-gray-700 hover:bg-white hover:text-gray-900 cursor-pointer'
			} relative inline-flex items-center rounded-md px-4 py-2 text-sm font-medium transition-colors duration-200 focus:z-10 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
			on:click={() => handleViewChange('players')}
			aria-current={playersActive ? 'page' : 'false'}
		>
			<svg
				class="{playersActive ? 'text-blue-600' : 'text-gray-500'} mr-2 h-4 w-4"
				xmlns="http://www.w3.org/2000/svg"
				viewBox="0 0 24 24"
				fill="none"
				stroke="currentColor"
				stroke-width="2"
				stroke-linecap="round"
				stroke-linejoin="round"
			>
				<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
				<circle cx="9" cy="7" r="4" />
				<path d="m22 21-3-3 1-1-3-3 1-1-4-4" />
			</svg>
			Pelaajat
		</button>

		<!-- Standings Tab -->
		<button
			type="button"
			class="{standingsActive
				? 'bg-white text-gray-900 shadow-sm cursor-pointer'
				: 'text-gray-700 hover:bg-white hover:text-gray-900 cursor-pointer'
			} relative inline-flex items-center rounded-md px-4 py-2 text-sm font-medium transition-colors duration-200 focus:z-10 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
			on:click={() => handleViewChange('standings')}
			aria-current={standingsActive ? 'page' : 'false'}
		>
			<svg
				class="{standingsActive ? 'text-blue-600' : 'text-gray-500'} mr-2 h-4 w-4"
				xmlns="http://www.w3.org/2000/svg"
				viewBox="0 0 24 24"
				fill="none"
				stroke="currentColor"
				stroke-width="2"
				stroke-linecap="round"
				stroke-linejoin="round"
			>
				<path d="M3 3h18v18H3zM9 9h6M9 12h6M9 15h4" />
				<path d="M3 9h6v6H3zM15 9h6v6h-6z" />
			</svg>
			Sarjataulukko
		</button>
	</div>
</div>

<style>
	/* Add smooth transitions */
	button {
		transition: all 0.2s ease-in-out;
	}

	/* Focus styles for accessibility */
	button:focus-visible {
		outline: 2px solid #3b82f6;
		outline-offset: 2px;
	}

	</style>