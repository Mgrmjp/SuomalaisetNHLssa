<script>
import { setDate, isLoading, error, players, displayDate } from '$lib/stores/gameData.js'
import LoadingSpinner from '$lib/components/ui/LoadingSpinner.svelte'
import ErrorBoundary from '$lib/components/ui/ErrorBoundary.svelte'
import PlayerCard from '$lib/components/game/PlayerCard.svelte'
import PlayerCardSkeleton from '$lib/components/game/PlayerCardSkeleton.svelte'

function handleRetry() {
    const currentDate = new Date().toISOString().split('T')[0]
    setDate(currentDate)
}

// Only show goalies who actually played; skaters must have recorded a point
$: filteredPlayers = ($players || []).filter((player) => {
	const position = (player.position || '').toUpperCase()
	const isGoalie = position === 'G' || position === 'GOALIE'
	const hasPoints = (player.points || 0) > 0 || (player.goals || 0) > 0 || (player.assists || 0) > 0

	// Goalie must have logged time or faced shots
	if (isGoalie) {
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
		{#if filteredPlayers.length === 0}
			<div class="text-center py-8 bg-white rounded-lg border border-gray-200 p-8">
				<div class="text-4xl mb-4">🏒</div>
				<h3 class="text-xl font-semibold text-gray-900 mb-2">Ei suomalaisia pelaajia</h3>
				<p class="text-gray-600">Yksikään suomalainen pelaaja ei kerännyt pisteitä päivänä {$displayDate}.</p>
			</div>
		{:else}
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
				{#each filteredPlayers as player (`${player.playerId}-${player.game_id}`)}
					<PlayerCard {player} />
				{/each}
			</div>
		{/if}
		</div>
	</section>
{/if}
