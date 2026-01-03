<script>
import { selectedView, setView } from '$lib/stores/gameData.js'

/**
 * Handle view change
 * @param {string} view - 'players', 'standings', or 'roster'
 */
function _handleViewChange(view) {
    setView(view)
}

$: playersActive = $selectedView === 'players'
$: standingsActive = $selectedView === 'standings'
$: rosterActive = $selectedView === 'roster'
</script>

<div class="flex justify-center mb-6">
	<div class="inline-flex rounded-lg border border-gray-200 bg-gray-100 p-1 gap-x-1" role="group">
		<!-- Players Tab -->
		<button
			type="button"
			class="{playersActive
				? 'bg-white text-gray-900 shadow-sm cursor-pointer'
				: 'text-gray-700 hover:bg-white hover:text-gray-900 cursor-pointer'
			} relative inline-flex items-center rounded-md px-4 py-2 text-sm font-medium transition-colors duration-200 focus:z-10 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
			on:click={() => _handleViewChange('players')}
			aria-current={playersActive ? 'page' : 'false'}
		>
			<svg
				class="{playersActive ? 'text-blue-600' : 'text-gray-500'} mr-2 h-4 w-4"
				xmlns="http://www.w3.org/2000/svg"
				viewBox="0 0 24 24"
			>
				<path d="M7.6,3,5.1,4.6l4,6.3,1.8-2.8L7.6,3m8.8,0L7.5,17H2v4H8.5L19,4.6,16.4,3M15,14.6l-1.8,2.8L15.5,21H22V17H16.5Z" />
			</svg>
			Tulokset
		</button>

		<!-- Standings Tab -->
		<button
			type="button"
			class="{standingsActive
				? 'bg-white text-gray-900 shadow-sm cursor-pointer'
				: 'text-gray-700 hover:bg-white hover:text-gray-900 cursor-pointer'
			} relative inline-flex items-center rounded-md px-4 py-2 text-sm font-medium transition-colors duration-200 focus:z-10 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
			on:click={() => _handleViewChange('standings')}
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
				<path d="M3 9L21 9M12 9V20M6.2 20H17.8C18.9201 20 19.4802 20 19.908 19.782C20.2843 19.5903 20.5903 19.2843 20.782 18.908C21 18.4802 21 17.9201 21 16.8V7.2C21 6.0799 21 5.51984 20.782 5.09202C20.5903 4.71569 20.2843 4.40973 19.908 4.21799C19.4802 4 18.9201 4 17.8 4H6.2C5.0799 4 4.51984 4 4.09202 4.21799C3.71569 4.40973 3.40973 4.71569 3.21799 5.09202C3 5.51984 3 6.07989 3 7.2V16.8C3 17.9201 3 18.4802 3.21799 18.908C3.40973 19.2843 3.71569 19.5903 4.09202 19.782C4.51984 20 5.07989 20 6.2 20Z" />
			</svg>
			Sarjataulukko
		</button>

		<!-- Roster Tab -->
		<button
			type="button"
			class="{rosterActive
				? 'bg-white text-gray-900 shadow-sm cursor-pointer'
				: 'text-gray-700 hover:bg-white hover:text-gray-900 cursor-pointer'
			} relative inline-flex items-center rounded-md px-4 py-2 text-sm font-medium transition-colors duration-200 focus:z-10 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
			on:click={() => _handleViewChange('roster')}
			aria-current={rosterActive ? 'page' : 'false'}
		>
			<svg
				class="{rosterActive ? 'text-blue-600' : 'text-gray-500'} mr-2 h-4 w-4"
				xmlns="http://www.w3.org/2000/svg"
				viewBox="0 0 24 24"
				fill="none"
				stroke="currentColor"
				stroke-width="2"
				stroke-linecap="round"
				stroke-linejoin="round"
			>
				<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
				<circle cx="9" cy="7" r="4" />
				<path d="M23 21v-2a4 4 0 0 0-3-3.87" />
				<path d="M16 3.13a4 4 0 0 1 0 7.75" />
			</svg>
			Joukkueet
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