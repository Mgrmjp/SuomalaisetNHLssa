<script>
import TeamLogo from '$lib/components/ui/TeamLogo.svelte'
import ComprehensivePlayerDetails from '$lib/components/game/ComprehensivePlayerDetails.svelte'
import './PlayerCard.css'

export let player

// Reactive variables for player photo
let playerPhotoUrl = null
let photoError = false
let photoLoading = true

// Load player photo when component mounts or player changes
$: if (player && player.playerId) {
    loadPlayerPhoto(player.playerId)
}

/**
 * Load player photo from our API
 */
async function loadPlayerPhoto(playerId) {
    photoLoading = true
    photoError = false
    
    try {
        const response = await fetch(`/api/player-photo?id=${playerId}`)
        if (response.ok) {
            const data = await response.json()
            playerPhotoUrl = data.headshotUrl || data.fallbackUrl
        } else {
            photoError = true
            playerPhotoUrl = null
        }
    } catch (error) {
        console.error('Error loading player photo:', error)
        photoError = true
        playerPhotoUrl = null
    } finally {
        photoLoading = false
    }
}

let showSeasonStats = false
let showComprehensiveDetails = false
let isLogoHovered = false
let isFlipped = false

// Team mapping with full names including cities
const teamMapping = {
  "ANA": "Anaheim Ducks",
  "ARI": "Arizona Coyotes",
  "BOS": "Boston Bruins",
  "BUF": "Buffalo Sabres",
  "CAR": "Carolina Hurricanes",
  "CBJ": "Columbus Blue Jackets",
  "CGY": "Calgary Flames",
  "CHI": "Chicago Blackhawks",
  "COL": "Colorado Avalanche",
  "DAL": "Dallas Stars",
  "DET": "Detroit Red Wings",
  "EDM": "Edmonton Oilers",
  "FLA": "Florida Panthers",
  "LAK": "Los Angeles Kings",
  "MIN": "Minnesota Wild",
  "MTL": "Montreal Canadiens",
  "NJD": "New Jersey Devils",
  "NSH": "Nashville Predators",
  "NYI": "New York Islanders",
  "NYR": "New York Rangers",
  "OTT": "Ottawa Senators",
  "PHI": "Philadelphia Flyers",
  "PIT": "Pittsburgh Penguins",
  "SEA": "Seattle Kraken",
  "SJS": "San Jose Sharks",
  "STL": "St. Louis Blues",
  "TBL": "Tampa Bay Lightning",
  "TOR": "Toronto Maple Leafs",
  "VAN": "Vancouver Canucks",
  "VGK": "Vegas Golden Knights",
  "WPG": "Winnipeg Jets",
  "WSH": "Washington Capitals"
}

function getTeamWithCity(teamAbbrev) {
  if (!teamAbbrev) return 'Unknown Team'
  return teamMapping[teamAbbrev] || teamAbbrev
}

function toggleSeasonStats(event) {
	if (event) {
		event.preventDefault()
		event.stopPropagation()
	}
	showSeasonStats = !showSeasonStats
}

function closeSeasonStats(event) {
	event.preventDefault()
	event.stopPropagation()
	showSeasonStats = false
}

function toggleComprehensiveDetails(event) {
	if (event) {
		event.preventDefault()
		event.stopPropagation()
	}
	showComprehensiveDetails = !showComprehensiveDetails
}

function handleBackdropClick(event) {
	if (event.target === event.currentTarget) {
		showSeasonStats = false
		showComprehensiveDetails = false
	}
}

function toggleFlip() {
	isFlipped = !isFlipped
}

function handleCardClick(event) {
	// Only flip if clicking on the card itself, not on buttons or interactive elements
	if (event.target.closest('button') ||
		event.target.closest('a')) {
		return
	}
	toggleFlip()
}

$: displayName = player.name?.default || player.name || 'Unknown Player'
$: isLive = player.game_status === 'Live' || player.game_status === 'In Progress'
$: teamWithCity = getTeamWithCity(player.team || 'NHL')
$: opponentWithCity = getTeamWithCity(player.opponent || 'NHL')

// Calculate number of stats for responsive grid (skaters)
$: statCount = [
	player.goals > 0,
	player.assists > 0,
	player.points > 0,
	player.plus_minus !== undefined,
	(player.penalty_minutes || 0) > 0
].filter(Boolean).length

// Goalie helpers
$: isGoalie = (player.position || '').toUpperCase() === 'G' || (player.position || '').toUpperCase() === 'GOALIE'
$: goalieSavePct = getSavePercentage(player)

function getSavePercentage(player) {
	const provided = player.save_percentage ?? player.savePercentage
	// Use provided percentage if it's a positive number
	if (typeof provided === 'number' && provided > 0) {
		return Number(provided.toFixed(3))
	}

	const saves = Number(player.saves ?? player.goalie_saves)
	const shotsAgainst = Number(player.shots_against ?? player.shotsAgainst)

	if (Number.isFinite(saves) && Number.isFinite(shotsAgainst) && shotsAgainst > 0) {
		return Number((saves / shotsAgainst).toFixed(3))
	}

	return null
}
</script>

<div class="player-card__container relative w-full min-h-[280px]">
	<!-- Player Card -->
	<div class="player-card" class:flipped={isFlipped}>
		<div class="player-card__inner">
			<!-- Front of Card -->
			<div class="player-card__face player-card__face--front bg-white rounded-lg shadow-lg w-full overflow-hidden relative cursor-pointer" on:click={handleCardClick} role="button" tabindex="0" on:keydown={(e) => e.key === 'Enter' && handleCardClick(e)} aria-label="Click to flip player card">
				<!-- Enhanced Double Border -->
				<div class="player-card__border-outer"></div>
				<div class="player-card__border-middle"></div>
				<div class="player-card__border-inner"></div>
				<div class="player-card__content relative bg-white rounded-lg p-4 h-full flex flex-col">
				<!-- Background Team Logo (static) -->
				<div class="player-card__logo-bg team-logo-bg">
					<TeamLogo team={player.team || 'NHL'} size="100" />
				</div>

					<!-- Top Left Player Info -->
					<div class="player-card__player-info absolute top-4 left-4 z-10">
						<div class="player-card__player-header flex items-center gap-2">
							<h3 class="player-card__player-name text-lg font-semibold text-gray-900">
								{displayName}
							</h3>
						</div>
						<div class="player-card__player-details text-sm text-gray-600">
							{player.position && player.position !== 'N/A' ? player.position : ''}{player.jersey_number ? ' #' + player.jersey_number : ''}{player.position && player.position !== 'N/A' ? ' • ' : ''}{teamWithCity}
						</div>
					</div>

				<!-- Top Right Team Logo -->
				<div class="player-card__team-logo absolute top-4 right-4 z-10">
					<div
						class="player-card__team-logo-container relative team-logo-container"
						role="img"
						aria-label={`Team logo for ${teamWithCity}`}
						on:mouseenter={() => isLogoHovered = true}
						on:mouseleave={() => isLogoHovered = false}
						on:focus={() => isLogoHovered = true}
						on:blur={() => isLogoHovered = false}
						title={teamWithCity}
					>
						<TeamLogo team={player.team || 'NHL'} size="48" />
						{#if isLive}
							<div class="player-card__live-indicator absolute -top-1 -right-1">
								<span class="player-card__live-badge bg-red-500 text-white text-xs font-bold px-2 py-1 rounded">
									LIVE
								</span>
							</div>
						{/if}
					</div>
				</div>

				<!-- Spacer for top content -->
				<div class="h-20 mb-4"></div>

				<!-- Game Stats -->
				{#if isGoalie}
					<div class="player-card__stats mb-4 w-full">
						<div class="player-card__stats-grid grid gap-1 text-left w-full" style="grid-template-columns: repeat(3, 1fr);">
							{#if player.saves !== undefined}
								<div class="player-card__stat-item flex flex-col justify-center min-w-0 text-center">
									<div class="player-card__stat-value text-sm font-bold text-gray-900 truncate">{player.saves}</div>
									<div class="player-card__stat-label text-xs text-gray-600 mt-1 truncate">Torjunnat</div>
								</div>
							{/if}
							{#if player.shots_against !== undefined}
								<div class="player-card__stat-item flex flex-col justify-center min-w-0 text-center">
									<div class="player-card__stat-value text-sm font-bold text-gray-900 truncate">{player.shots_against}</div>
									<div class="player-card__stat-label text-xs text-gray-600 mt-1 truncate">Vastust. laukaukset</div>
								</div>
							{/if}
							{#if goalieSavePct !== null}
								<div class="player-card__stat-item flex flex-col justify-center min-w-0 text-center">
									<div class="player-card__stat-value text-sm font-bold text-gray-900 truncate">{goalieSavePct}</div>
									<div class="player-card__stat-label text-xs text-gray-600 mt-1 truncate">Torj.%</div>
								</div>
							{/if}
						</div>
					</div>
				{:else if player.goals > 0 || player.assists > 0 || player.points > 0 || (player.penalty_minutes || 0) > 0 || player.plus_minus !== undefined}
					<div class="player-card__stats mb-4 w-full">
						<div class="player-card__stats-grid grid gap-1 text-left w-full" style="grid-template-columns: repeat({Math.min(statCount, 5)}, 1fr);">
							{#if player.goals > 0}
								<div class="player-card__stat-item flex flex-col justify-center min-w-0 text-center">
									<div class="player-card__stat-value text-sm font-bold text-gray-900 truncate">{player.goals}</div>
									<div class="player-card__stat-label text-xs text-gray-600 mt-1 truncate">Maalit</div>
								</div>
							{/if}
							{#if player.assists > 0}
								<div class="player-card__stat-item flex flex-col justify-center min-w-0 text-center">
									<div class="player-card__stat-value text-sm font-bold text-gray-900 truncate">{player.assists}</div>
									<div class="player-card__stat-label text-xs text-gray-600 mt-1 truncate">Syötöt</div>
								</div>
							{/if}
							{#if player.points > 0}
								<div class="player-card__stat-item flex flex-col justify-center min-w-0 text-center">
									<div class="player-card__stat-value text-sm font-bold text-finnish-blue-900 truncate">{player.points}</div>
									<div class="player-card__stat-label text-xs text-finnish-blue-600 mt-1 truncate">Pisteet</div>
								</div>
							{/if}
							{#if player.plus_minus !== undefined}
								<div class="player-card__stat-item flex flex-col justify-center min-w-0 text-center">
									<div class="player-card__stat-value text-sm font-bold text-gray-900 truncate">{player.plus_minus > 0 ? '+' : ''}{player.plus_minus}</div>
									<div class="player-card__stat-label text-xs text-gray-600 mt-1 truncate">+/-</div>
								</div>
							{/if}
							{#if (player.penalty_minutes || 0) > 0}
								<div class="player-card__stat-item flex flex-col justify-center min-w-0 text-center">
									<div class="player-card__stat-value text-sm font-bold text-gray-900 truncate">{player.penalty_minutes}</div>
									<div class="player-card__stat-label text-xs text-gray-600 mt-1 truncate">R.min</div>
								</div>
							{/if}
						</div>
					</div>
				{/if}

				<!-- Game Score -->
				{#if player.game_score}
					<div class="player-card__game-score">
						<div class="player-card__game-score-display flex items-center justify-center space-x-3">
							<div class="player-card__team-info flex items-center space-x-2">
								<TeamLogo team={player.team || 'NHL'} size="20" />
								<span class="player-card__team-name text-sm font-medium">{player.team}</span>
							</div>
							<div class="player-card__score text-lg font-bold">{player.game_score}</div>
							{#if player.opponent}
								<div class="player-card__team-info flex items-center space-x-2">
									<span class="player-card__team-name text-sm font-medium">{player.opponent}</span>
									<TeamLogo team={player.opponent || 'NHL'} size="20" />
								</div>
							{/if}
						</div>
							{#if player.game_venue || player.game_city}
								{#if player.game_venue && player.game_city}
									<div class="player-card__game-venue text-xs text-gray-500 mt-2 text-center">📍 {player.game_venue} — {player.game_city}</div>
								{:else if player.game_venue}
									<div class="player-card__game-venue text-xs text-gray-500 mt-2 text-center">📍 {player.game_venue}</div>
								{:else}
									<div class="player-card__game-venue text-xs text-gray-500 mt-2 text-center">📍 {player.game_city}</div>
								{/if}
							{/if}
						</div>
					{/if}
					<div class="player-card__footer mt-auto flex justify-end pt-3 border-t border-gray-100">
						<button
							class="player-card__details-button-inline"
							on:click={toggleComprehensiveDetails}
							on:keydown={(e) => e.key === 'Enter' && toggleComprehensiveDetails()}
							aria-label="Show comprehensive player details for {displayName}"
							title="Näytä kattavat tiedot"
						>
							<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
								<path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
							</svg>
						</button>
					</div>
				</div>
			</div>

			<!-- Back of Card -->
			<div class="player-card__face player-card__face--back bg-white rounded-lg shadow-lg p-[3px] w-full overflow-hidden relative cursor-pointer" on:click={handleCardClick} role="button" tabindex="0" on:keydown={(e) => e.key === 'Enter' && handleCardClick(e)} aria-label="Click to flip player card back">
				<!-- Enhanced Double Border -->
				<div class="player-card__border-outer player-card__border-outer--back"></div>
				<div class="player-card__border-middle player-card__border-middle--back"></div>
				<div class="player-card__border-inner player-card__border-inner--back"></div>
				<div class="player-card__content relative bg-white rounded-lg p-4 h-full flex flex-col">
					<!-- Top Left Player Info -->
					<div class="player-card__player-info absolute top-4 left-4 z-10">
						<div class="player-card__player-header flex items-center gap-2">
							<h3 class="player-card__player-name text-lg font-semibold text-gray-900">
								{displayName}
							</h3>
						</div>
						<div class="player-card__player-details text-sm text-gray-600">
							{player.position && player.position !== 'N/A' ? player.position : ''}{player.jersey_number ? ' #' + player.jersey_number : ''}{player.position && player.position !== 'N/A' ? ' • ' : ''}{teamWithCity}
						</div>
					</div>

				<!-- Top Right Team Logo -->
					<div class="player-card__team-logo absolute top-4 right-4 z-10">
						<TeamLogo team={player.team || 'NHL'} size="48" />
					</div>

					<!-- Spacer for top content -->
					<div class="player-card__spacer h-20 mb-4"></div>

					<!-- Additional Stats -->
					<div class="player-card__advanced-stats mb-4 w-full">
						<div class="player-card__advanced-stats-grid grid gap-1 text-left w-full" style="grid-template-columns: repeat(3, 1fr);">
							{#if player.shots !== undefined && player.shots >= 0}
								<div class="player-card__stat-item flex flex-col justify-center min-w-0 text-center">
									<div class="player-card__stat-value text-sm font-bold text-gray-900 truncate">{player.shots}</div>
									<div class="player-card__stat-label text-xs text-gray-600 mt-1 truncate">Lauk. / Shots</div>
								</div>
							{/if}
							{#if player.hits !== undefined && player.hits >= 0}
								<div class="player-card__stat-item flex flex-col justify-center min-w-0 text-center">
									<div class="player-card__stat-value text-sm font-bold text-gray-900 truncate">{player.hits}</div>
									<div class="player-card__stat-label text-xs text-gray-600 mt-1 truncate">Iskut / Hits</div>
								</div>
							{/if}
							{#if player.blocked_shots !== undefined && player.blocked_shots >= 0}
								<div class="player-card__stat-item flex flex-col justify-center min-w-0 text-center">
									<div class="player-card__stat-value text-sm font-bold text-gray-900 truncate">{player.blocked_shots}</div>
									<div class="player-card__stat-label text-xs text-gray-600 mt-1 truncate">Estot / Blocks</div>
								</div>
							{/if}
							{#if player.takeaways !== undefined && player.takeaways >= 0}
								<div class="player-card__stat-item flex flex-col justify-center min-w-0 text-center">
									<div class="player-card__stat-value text-sm font-bold text-gray-900 truncate">{player.takeaways}</div>
									<div class="player-card__stat-label text-xs text-gray-600 mt-1 truncate">Kappaleet / Takeaways</div>
								</div>
							{/if}
							{#if player.giveaways !== undefined && player.giveaways >= 0}
								<div class="player-card__stat-item flex flex-col justify-center min-w-0 text-center">
									<div class="player-card__stat-value text-sm font-bold text-gray-900 truncate">{player.giveaways}</div>
									<div class="player-card__stat-label text-xs text-gray-600 mt-1 truncate">Menetykset / Giveaways</div>
								</div>
							{/if}
							{#if player.faceoff_wins !== undefined && player.faceoffs_taken !== undefined && player.faceoffs_taken > 0}
								<div class="player-card__stat-item flex flex-col justify-center min-w-0 text-center">
									<div class="player-card__stat-value text-sm font-bold text-gray-900 truncate">{player.faceoff_wins}/{player.faceoffs_taken}</div>
									<div class="player-card__stat-label text-xs text-gray-600 mt-1 truncate">Vahingot / FO</div>
								</div>
							{/if}
						</div>
					</div>

						<!-- Time on Ice -->
						{#if player.time_on_ice}
							<div class="player-card__time-on-ice">
								<div class="player-card__time-on-ice-text text-sm text-gray-700">
									Aika kentällä: <span class="player-card__time-on-ice-value font-semibold">{player.time_on_ice}</span>
								</div>
							</div>
						{/if}
						<div class="player-card__footer mt-auto flex justify-end pt-3 border-t border-gray-100">
							<button
								class="player-card__details-button-inline"
								on:click={toggleComprehensiveDetails}
								on:keydown={(e) => e.key === 'Enter' && toggleComprehensiveDetails()}
								aria-label="Show comprehensive player details for {displayName}"
								title="Näytä kattavat tiedot"
							>
								<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
									<path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
								</svg>
							</button>
						</div>
					</div>
				</div>
			</div>

			</div>

	<!-- Season Stats Modal -->
	{#if showSeasonStats}
		<div
			class="player-card__modal-overlay fixed inset-0 bg-black/30 backdrop-blur-sm flex items-center justify-center z-50"
			role="button"
			tabindex="0"
			on:click={handleBackdropClick}
			on:keydown={(e) => (e.key === 'Escape' || e.key === 'Enter' || e.key === ' ') && handleBackdropClick(e)}
		>
			<div class="player-card__modal-content bg-white rounded-lg max-w-4xl w-full mx-4 max-h-screen overflow-y-auto">
				<div class="player-card__modal-header p-6">
					<div class="player-card__modal-title-row flex items-center justify-between mb-6">
						<h2 class="player-card__modal-title text-2xl font-bold text-gray-900">
							{displayName} - Kauden tilastot
						</h2>
						<button
							type="button"
							class="player-card__modal-close text-gray-400 hover:text-gray-600"
							on:click={closeSeasonStats}
						>
							<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
								<path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
							</svg>
						</button>
					</div>

					<!-- Season Stats Content -->
					<div class="player-card__modal-body text-center text-gray-500">
						<p>Kauden tilastot eivät ole vielä saatavilla</p>
						<p class="text-sm mt-2">Tämä toiminto kehitetään tulevaisuudessa</p>
					</div>

					<div class="player-card__modal-footer mt-6 pt-4 border-t border-gray-200 flex justify-end">
						<button
							type="button"
							class="player-card__modal-close-button bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
							on:click={closeSeasonStats}
						>
							Sulje
						</button>
					</div>
				</div>
			</div>
		</div>
	{/if}

	<!-- Comprehensive Details Modal Component -->
	<ComprehensivePlayerDetails
		{player}
		bind:showComprehensiveDetails
	/>
</div>
