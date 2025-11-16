<script>
import TeamLogo from '$lib/components/ui/TeamLogo.svelte'

export let player
export let showComprehensiveDetails = false

function closeComprehensiveDetails(event) {
	event.preventDefault()
	event.stopPropagation()
	showComprehensiveDetails = false
}

function handleBackdropClick(event) {
	if (event.target === event.currentTarget) {
		showComprehensiveDetails = false
	}
}

function toggleSeasonStats(event) {
	if (event) {
		event.preventDefault()
		event.stopPropagation()
	}
	// This will be handled by the parent component
	const seasonStatsEvent = new CustomEvent('toggle-season-stats')
	window.dispatchEvent(seasonStatsEvent)
}

$: displayName = player.name?.default || player.name || 'Unknown Player'
$: isLive = player.game_status === 'Live' || player.game_status === 'In Progress'
</script>

<!-- Comprehensive Details Modal -->
{#if showComprehensiveDetails}
	<div
		class="fixed inset-0 bg-black/30 backdrop-blur-sm flex items-center justify-center z-50"
		role="button"
		tabindex="0"
		on:click={handleBackdropClick}
		on:keydown={(e) => (e.key === 'Escape' || e.key === 'Enter' || e.key === ' ') && handleBackdropClick(e)}
	>
		<div class="bg-white rounded-lg max-w-6xl w-full mx-4 max-h-screen overflow-y-auto">
			<div class="p-6">
				<div class="flex items-center justify-between mb-6">
					<div class="flex items-center space-x-4">
						<div class="relative">
							<TeamLogo team={player.team || 'NHL'} size="48" />
							{#if isLive}
								<div class="absolute -top-2 -right-2">
									<span class="bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-full">
										LIVE
									</span>
								</div>
							{/if}
						</div>
						<div>
							<h2 class="text-2xl font-bold text-gray-900">
								{displayName}
							</h2>
							<div class="text-lg text-gray-600">
								{player.position && player.position !== 'N/A' ? player.position : ''}{player.jersey_number ? ' #' + player.jersey_number : ''} • {player.team_full || player.team || 'Unknown Team'}
							</div>
						</div>
					</div>
					<button
						type="button"
						class="p-2 rounded-lg gradient-button-ghost gradient-button-ghost--sm"
						on:click={closeComprehensiveDetails}
					>
						<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
							<path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
						</svg>
					</button>
				</div>

				<!-- Personal Information Section -->
				{#if player.age || player.birth_date || player.birthplace || player.jersey_number}
					<div class="bg-gray-50 rounded-lg p-4 mb-6">
						<h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
							<svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
								<path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd"/>
							</svg>
							Henkilötiedot
						</h3>
						<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
							{#if player.age}
								<div class="bg-white rounded-lg p-3">
									<div class="text-sm text-gray-600">Ikä</div>
									<div class="text-lg font-semibold text-gray-900">{player.age} vuotta</div>
								</div>
							{/if}
							{#if player.birth_date}
								<div class="bg-white rounded-lg p-3">
									<div class="text-sm text-gray-600">Syntymäpäivä</div>
									<div class="text-lg font-semibold text-gray-900">{new Date(player.birth_date).toLocaleDateString('fi-FI')}</div>
								</div>
							{/if}
							{#if player.birthplace}
								<div class="bg-white rounded-lg p-3">
									<div class="text-sm text-gray-600">Syntymäpaikka</div>
									<div class="text-lg font-semibold text-gray-900">{player.birthplace}</div>
								</div>
							{/if}
							{#if player.jersey_number}
								<div class="bg-white rounded-lg p-3">
									<div class="text-sm text-gray-600">Pelinumero</div>
									<div class="text-lg font-semibold text-gray-900">#{player.jersey_number}</div>
								</div>
							{/if}
						</div>
					</div>
				{/if}

				<!-- Game Statistics -->
				{#if player.goals > 0 || player.assists > 0 || player.points > 0 || (player.penalty_minutes || 0) > 0 || player.plus_minus !== undefined}
					<div class="bg-green-50 rounded-lg p-4 mb-6">
						<h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
							<svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
								<path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z"/>
							</svg>
							Pelin tilastot
						</h3>
						<div class="grid grid-cols-2 md:grid-cols-5 gap-4">
							{#if player.goals > 0}
								<div class="bg-white rounded-lg p-4 text-center">
									<div class="text-2xl font-bold text-gray-900">{player.goals}</div>
									<div class="text-sm text-gray-600">Maalit</div>
								</div>
							{/if}
							{#if player.assists > 0}
								<div class="bg-white rounded-lg p-4 text-center">
									<div class="text-2xl font-bold text-gray-900">{player.assists}</div>
									<div class="text-sm text-gray-600">Syötöt</div>
								</div>
							{/if}
							{#if player.points > 0}
								<div class="bg-white rounded-lg p-4 text-center">
									<div class="text-2xl font-bold text-gray-900">{player.points}</div>
									<div class="text-sm text-gray-600">Pisteet</div>
								</div>
							{/if}
							{#if player.plus_minus !== undefined}
								<div class="bg-white rounded-lg p-4 text-center">
									<div class="text-2xl font-bold text-gray-900">{player.plus_minus > 0 ? '+' : ''}{player.plus_minus}</div>
									<div class="text-sm text-gray-600">+/-</div>
								</div>
							{/if}
							{#if (player.penalty_minutes || 0) > 0}
								<div class="bg-white rounded-lg p-4 text-center">
									<div class="text-2xl font-bold text-gray-900">{player.penalty_minutes}</div>
									<div class="text-sm text-gray-600">Rangaistusminuutit</div>
								</div>
							{/if}
						</div>
					</div>
				{/if}

				<!-- Advanced Skater Statistics -->
				{#if player.position !== 'G' && (player.faceoffs_taken > 0 || player.takeaways > 0 || player.giveaways > 0 || player.blocked_shots > 0 || player.hits > 0 || player.power_play_goals > 0 || player.short_handed_goals > 0 || player.even_strength_goals > 0 || player.power_play_assists > 0 || player.short_handed_assists > 0)}
					<div class="bg-blue-50 rounded-lg p-4 mb-6">
						<h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
							<svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
								<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd"/>
							</svg>
							Kehittyneet pelaajatilastot
						</h3>
						<div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
							{#if player.faceoffs_taken > 0}
								<div class="bg-white rounded-lg p-3 text-center">
									<div class="text-lg font-bold text-gray-900">{player.faceoff_wins || 0}/{player.faceoffs_taken}</div>
									<div class="text-xs text-gray-600">Avo-voitot</div>
									<div class="text-xs text-finnish-blue-600 font-medium">
										{Math.round(((player.faceoff_wins || 0) / player.faceoffs_taken) * 100)}%
									</div>
								</div>
							{/if}
							{#if player.takeaways > 0}
								<div class="bg-white rounded-lg p-3 text-center">
									<div class="text-lg font-bold text-gray-900">{player.takeaways}</div>
									<div class="text-xs text-gray-600">Rystsytykset</div>
								</div>
							{/if}
							{#if player.giveaways > 0}
								<div class="bg-white rounded-lg p-3 text-center">
									<div class="text-lg font-bold text-gray-900">{player.giveaways}</div>
									<div class="text-xs text-gray-600">Menetykset</div>
								</div>
							{/if}
							{#if player.blocked_shots > 0}
								<div class="bg-white rounded-lg p-3 text-center">
									<div class="text-lg font-bold text-gray-900">{player.blocked_shots}</div>
									<div class="text-xs text-gray-600">Estetyt laukaukset</div>
								</div>
							{/if}
							{#if player.hits > 0}
								<div class="bg-white rounded-lg p-3 text-center">
									<div class="text-lg font-bold text-gray-900">{player.hits}</div>
									<div class="text-xs text-gray-600">Taklaukset</div>
								</div>
							{/if}
							{#if player.power_play_goals > 0}
								<div class="bg-white rounded-lg p-3 text-center">
									<div class="text-lg font-bold text-gray-900">{player.power_play_goals}</div>
									<div class="text-xs text-gray-600">Ylivoimamaalit</div>
								</div>
							{/if}
							{#if player.short_handed_goals > 0}
								<div class="bg-white rounded-lg p-3 text-center">
									<div class="text-lg font-bold text-gray-900">{player.short_handed_goals}</div>
									<div class="text-xs text-gray-600">Alivoimamaalit</div>
								</div>
							{/if}
							{#if player.even_strength_goals > 0}
								<div class="bg-white rounded-lg p-3 text-center">
									<div class="text-lg font-bold text-gray-900">{player.even_strength_goals}</div>
									<div class="text-xs text-gray-600">Tasavoimamaalit</div>
								</div>
							{/if}
							{#if player.power_play_assists > 0}
								<div class="bg-white rounded-lg p-3 text-center">
									<div class="text-lg font-bold text-gray-900">{player.power_play_assists}</div>
									<div class="text-xs text-gray-600">Ylivoimasyötöt</div>
								</div>
							{/if}
							{#if player.short_handed_assists > 0}
								<div class="bg-white rounded-lg p-3 text-center">
									<div class="text-lg font-bold text-gray-900">{player.short_handed_assists}</div>
									<div class="text-xs text-gray-600">Alivoimasyötöt</div>
								</div>
							{/if}
						</div>
					</div>
				{/if}

				<!-- Advanced Goalie Statistics -->
				{#if player.position === 'G' && (player.saves > 0 || player.save_percentage > 0 || player.goals_against > 0 || player.shots_against > 0 || player.time_on_ice)}
					<div class="bg-yellow-50 rounded-lg p-4 mb-6">
						<h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
							<svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
								<path fill-rule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clip-rule="evenodd"/>
							</svg>
							Kehittyneet maalivahtitilastot
						</h3>
						<div class="grid grid-cols-2 md:grid-cols-3 gap-4">
							{#if player.saves > 0}
								<div class="bg-white rounded-lg p-4 text-center">
									<div class="text-2xl font-bold text-gray-900">{player.saves}</div>
									<div class="text-sm text-gray-600">Torjunnat</div>
								</div>
							{/if}
							{#if player.save_percentage > 0}
								<div class="bg-white rounded-lg p-4 text-center">
									<div class="text-2xl font-bold text-gray-900">{player.save_percentage}</div>
									<div class="text-sm text-gray-600">Torrjuntaprosentti</div>
								</div>
							{/if}
							{#if player.goals_against > 0}
								<div class="bg-white rounded-lg p-4 text-center">
									<div class="text-2xl font-bold text-gray-900">{player.goals_against}</div>
									<div class="text-sm text-gray-600">Päästetyt maalit</div>
								</div>
							{/if}
							{#if player.shots_against > 0}
								<div class="bg-white rounded-lg p-4 text-center">
									<div class="text-2xl font-bold text-gray-900">{player.shots_against}</div>
									<div class="text-sm text-gray-600">Vastustetut laukaukset</div>
								</div>
							{/if}
							{#if player.time_on_ice}
								<div class="bg-white rounded-lg p-4 text-center">
									<div class="text-2xl font-bold text-gray-900">{player.time_on_ice}</div>
									<div class="text-sm text-gray-600">Pelattu aika</div>
								</div>
							{/if}
						</div>
					</div>
				{/if}

				<!-- Game Context Statistics -->
				{#if player.shifts > 0 || player.average_ice_time || player.blocked_shots > 0}
					<div class="bg-purple-50 rounded-lg p-4 mb-6">
						<h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
							<svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
								<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd"/>
							</svg>
							Pelikontekstitilastot
						</h3>
						<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
							{#if player.shifts > 0}
								<div class="bg-white rounded-lg p-4 text-center">
									<div class="text-2xl font-bold text-gray-900">{player.shifts}</div>
									<div class="text-sm text-gray-600">Vuorot</div>
								</div>
							{/if}
							{#if player.average_ice_time}
								<div class="bg-white rounded-lg p-4 text-center">
									<div class="text-2xl font-bold text-gray-900">{player.average_ice_time}</div>
									<div class="text-sm text-gray-600">Kesk. peliaika</div>
								</div>
							{/if}
							{#if player.blocked_shots > 0 && player.position === 'D'}
								<div class="bg-white rounded-lg p-4 text-center">
									<div class="text-2xl font-bold text-gray-900">{player.blocked_shots}</div>
									<div class="text-sm text-gray-600">Estetyt laukaukset</div>
								</div>
							{/if}
							{#if player.shots > 0}
								<div class="bg-white rounded-lg p-4 text-center">
									<div class="text-2xl font-bold text-gray-900">{player.shots}</div>
									<div class="text-sm text-gray-600">Laukaukset</div>
								</div>
							{/if}
						</div>
					</div>
				{/if}

				</div>
		</div>
	</div>
{/if}
