<script>
import { setDate, isLoading, error, players, displayDate } from '$lib/stores/gameData.js'
import LoadingSpinner from '$lib/components/ui/LoadingSpinner.svelte'
import ErrorBoundary from '$lib/components/ui/ErrorBoundary.svelte'
import PlayerCard from '$lib/components/game/PlayerCard.svelte'
import PlayerCardSkeleton from '$lib/components/game/PlayerCardSkeleton.svelte'

const positionCode = (player) => (player.position || '').toUpperCase()
const isGoalie = (player) => {
	const pos = positionCode(player)
	return pos === 'G' || pos === 'GOALIE'
}
const isDefense = (player) => {
	const pos = positionCode(player)
	return pos === 'D' || pos === 'LD' || pos === 'RD' || pos === 'DEFENSE'
}

function getSavePercentage(player) {
	const provided = player.save_percentage ?? player.savePercentage
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

function handleRetry() {
    const currentDate = new Date().toISOString().split('T')[0]
    setDate(currentDate)
}

// Only show goalies who actually played; skaters must have recorded a point
$: filteredPlayers = ($players || []).filter((player) => {
	const position = positionCode(player)
	const goalie = position === 'G' || position === 'GOALIE'
	const hasPoints = (player.points || 0) > 0 || (player.goals || 0) > 0 || (player.assists || 0) > 0

	// Goalie must have logged time or faced shots
	if (goalie) {
		const shotsAgainst = Number(player.shots_against ?? player.shotsAgainst ?? 0)
		const saves = Number(player.saves ?? player.goalie_saves ?? 0)
		const goalsAgainst = Number(player.goals_against ?? player.goalsAgainst ?? 0)
		const toi = player.time_on_ice || player.toi || ''

		const played =
			shotsAgainst > 0 ||
			saves > 0 ||
			goalsAgainst > 0 ||
			(toi && toi !== '00:00' && toi !== '0:00')

		return played
	}

	return hasPoints
})

const sortSkatersByPoints = (list) =>
	[...list].sort(
		(a, b) =>
			(b.points || 0) - (a.points || 0) ||
			(b.goals || 0) - (a.goals || 0) ||
			(b.plus_minus ?? -Infinity) - (a.plus_minus ?? -Infinity) ||
			(b.assists || 0) - (a.assists || 0)
	)

const sortGoalies = (list) =>
	[...list].sort((a, b) => {
		const aPct = getSavePercentage(a)
		const bPct = getSavePercentage(b)

		if (aPct === null && bPct === null) return 0
		if (aPct === null) return 1
		if (bPct === null) return -1

		return bPct - aPct
	})

$: forwards = sortSkatersByPoints(filteredPlayers.filter((p) => !isGoalie(p) && !isDefense(p)))
$: defenders = sortSkatersByPoints(filteredPlayers.filter((p) => !isGoalie(p) && isDefense(p)))
$: goalies = sortGoalies(filteredPlayers.filter((p) => isGoalie(p)))

$: hasAnyPlayers = forwards.length + defenders.length + goalies.length > 0
</script>

{#if $isLoading}
	<div class="py-8">
		<div class="container mx-auto px-4">
			<!-- Loading header -->
			<div class="text-center mb-6">
				<LoadingSpinner message="Ladataan pelaajia..." size="medium" />
			</div>

			<!-- Skeleton cards grid -->
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
				{#each Array(4) as _, i}
					<PlayerCardSkeleton />
				{/each}
			</div>
		</div>
	</div>
{:else if $error}
	<div class="text-center py-8">
		<ErrorBoundary
			error={$error}
			retryAction="Yritä uudelleen"
			onRetry={handleRetry}
			variant="error"
		/>
	</div>
{:else}
	<section id="scoringList" class="py-8">
		<div class="container mx-auto px-4">
		{#if !hasAnyPlayers && $isLoading === false}
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
				<div class="bg-white rounded-lg shadow-lg p-6 border-4 border-finnish-blue-200 relative overflow-hidden min-h-[220px] flex items-center justify-center">
					<!-- Subtle background pattern -->
					<div class="absolute inset-0 bg-gradient-to-br from-finnish-blue-50/30 to-transparent opacity-50"></div>

					<!-- Content -->
					<div class="relative z-10 text-center">
						<div class="w-16 h-16 bg-finnish-blue-100 rounded-lg flex items-center justify-center mb-4 mx-auto">
							<span class="text-3xl">🏒</span>
						</div>
						<h3 class="text-lg font-semibold text-gray-900 mb-2">Ei suomalaista pisteidentekijää</h3>
						<p class="text-sm text-gray-600 leading-relaxed max-w-sm mx-auto">
							Yhtään suomalaispelaajaa ei ole merkitty pisteille tai dataa ei ole vielä saatavilla päivälle
							<span class="font-semibold text-finnish-blue-900">{$displayDate}</span>.
						</p>
					</div>
				</div>
			</div>
		{:else}
			<div class="space-y-10">
				{#if forwards.length}
					<div class="space-y-4">
						<div class="flex items-center gap-3">
							<h3 class="text-lg font-semibold text-gray-900">Hyökkääjät</h3>
							<p class="text-sm text-gray-600">(järjestetty pisteiden mukaan)</p>
						</div>
						<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
							{#each forwards as player (`${player.playerId}-${player.game_id}`)}
								<PlayerCard {player} />
							{/each}
						</div>
					</div>
					<div class="h-px bg-gradient-to-r from-transparent via-gray-200 to-transparent"></div>
				{/if}

				{#if defenders.length}
					<div class="space-y-4">
						<div class="flex items-center gap-3">
							<h3 class="text-lg font-semibold text-gray-900">Puolustajat</h3>
							<p class="text-sm text-gray-600">(järjestetty pisteiden mukaan)</p>
						</div>
						<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
							{#each defenders as player (`${player.playerId}-${player.game_id}`)}
								<PlayerCard {player} />
							{/each}
						</div>
					</div>
					<div class="h-px bg-gradient-to-r from-transparent via-gray-200 to-transparent"></div>
				{/if}

				{#if goalies.length}
					<div class="space-y-4">
						<div class="flex items-center gap-3">
							<h3 class="text-lg font-semibold text-gray-900">Maalivahdit</h3>
							<p class="text-sm text-gray-600">(järjestetty torjuntaprosentin mukaan)</p>
						</div>
						<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
							{#each goalies as player (`${player.playerId}-${player.game_id}`)}
								<PlayerCard {player} />
							{/each}
						</div>
					</div>
				{/if}
			</div>
		{/if}
		</div>
	</section>
{/if}
