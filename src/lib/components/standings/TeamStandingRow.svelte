<script>
	import TeamLogo from '$lib/components/ui/TeamLogo.svelte'
	import teamMapping from '$lib/utils/teamMapping.js'

	export let team
	export let teamData = {}
	export let rank
	export let showPlayoffIndicator = false
	export let isWildCard = false
	export let showAdvancedStats = false

	// Get team full name
	$: teamName = teamMapping[team] || team

	// Determine playoff indicator
	$: isPlayoffTeam = rank <= 3 || isWildCard // Top 3 in division OR Wild Card

	// Use teamData for all team statistics
	$: teamStats = teamData

	// Format streak with color coding
	$: streakDisplay = formatStreak(teamStats.streak)

	function formatStreak(streak) {
		if (!streak || streak.length < 2) return '-'

		const type = streak[0]
		const count = streak.slice(1)

		let colorClass = ''
		let bgColorClass = ''

		if (type === 'W') {
			colorClass = 'text-green-700'
			bgColorClass = 'bg-green-100'
		} else if (type === 'L') {
			colorClass = 'text-red-700'
			bgColorClass = 'bg-red-100'
		} else if (type === 'OT') {
			colorClass = 'text-yellow-700'
			bgColorClass = 'bg-yellow-100'
		}

		return {
			text: streak,
			colorClass,
			bgColorClass
		}
	}

	// Format last 10 games
	$: last10Display = teamStats.last10 || '0-0-0'

	// Calculate advanced stats
	$: advancedStats = calculateAdvancedStats(teamStats)

	// Calculate advanced statistics
	function calculateAdvancedStats(stats) {
		const gamesPlayed = stats.gamesPlayed || 1

		// Power Play Percentage (placeholder - would need real PP data)
		const powerPlayGoals = stats.powerPlayGoals || 0
		const powerPlayOpportunities = stats.powerPlayOpportunities || 1
		const powerPlayPercentage = ((powerPlayGoals / powerPlayOpportunities) * 100).toFixed(1)

		// Penalty Kill Percentage (placeholder - would need real PK data)
		const penaltyKillGoalsAllowed = stats.penaltyKillGoalsAllowed || 0
		const penaltyKillTimesShorthanded = stats.penaltyKillTimesShorthanded || 1
		const penaltyKillPercentage = (((penaltyKillTimesShorthanded - penaltyKillGoalsAllowed) / penaltyKillTimesShorthanded) * 100).toFixed(1)

		// Goal Differential
		const goalDifferential = stats.goalDifferential || (stats.goalsFor - stats.goalsAgainst) || 0

		// Goals For Per Game
		const goalsForPerGame = ((stats.goalsFor || 0) / gamesPlayed).toFixed(2)

		// Goals Against Per Game
		const goalsAgainstPerGame = ((stats.goalsAgainst || 0) / gamesPlayed).toFixed(2)

		return {
			powerPlayPercentage,
			penaltyKillPercentage,
			goalDifferential,
			goalsForPerGame,
			goalsAgainstPerGame
		}
	}

	// Row hover classes
	$: rowClasses = `
		border-b transition-colors duration-150
		${rank <= 3 ? 'bg-blue-50 border-blue-200' :
			isPlayoffTeam ? 'bg-green-50 border-green-200' :
			'bg-white border-gray-200'}
		hover:bg-gray-50
	`
</script>

<tr class="{rowClasses}">
	<!-- Rank -->
	<td class="px-3 py-3 text-sm font-medium text-gray-900 text-center w-12">
		<div class="flex items-center justify-center">
			<span class="{rank <= 3 ? 'font-bold text-blue-600' : 'text-gray-600'}">
				{rank}
			</span>
			{#if showPlayoffIndicator && isPlayoffTeam}
				<div class="ml-1 w-2 h-2 bg-green-500 rounded-full" title="Playoff Position"></div>
			{/if}
		</div>
	</td>

	<!-- Team -->
	<td class="px-3 py-3 text-sm">
		<div class="flex items-center space-x-3">
			<div class="flex-shrink-0">
				<TeamLogo team={team} size="24" />
			</div>
			<div class="min-w-0 flex-1">
				<p class="font-medium text-gray-900 truncate">
					{teamName}
				</p>
				<p class="text-xs text-gray-500">
					{team}
				</p>
			</div>
		</div>
	</td>

	<!-- Games Played -->
	<td class="px-3 py-3 text-sm text-center text-gray-900 w-12">
		{teamStats.gamesPlayed}
	</td>

	<!-- Wins -->
	<td class="px-3 py-3 text-sm font-medium text-center text-green-600 w-12">
		{teamStats.wins}
	</td>

	<!-- Losses -->
	<td class="px-3 py-3 text-sm text-center text-red-600 w-12">
		{teamStats.losses}
	</td>

	<!-- Overtime Losses -->
	<td class="px-3 py-3 text-sm text-center text-yellow-600 w-12">
		{teamStats.overtimeLosses}
	</td>

	<!-- Points -->
	<td class="px-3 py-3 text-sm font-bold text-center text-gray-900 w-12">
		{teamStats.points}
	</td>

	<!-- Points Percentage -->
	<td class="px-3 py-3 text-sm text-center text-gray-900 w-14">
		{teamStats.pointsPercentage.toFixed(3)}
	</td>

	<!-- Streak -->
	<td class="px-3 py-3 text-sm text-center w-14">
		{#if streakDisplay.text !== '-'}
			<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium {streakDisplay.colorClass} {streakDisplay.bgColorClass}">
				{streakDisplay.text}
			</span>
		{:else}
			<span class="text-gray-400">-</span>
		{/if}
	</td>

	<!-- Last 10 Games -->
	<td class="px-3 py-3 text-sm text-center text-gray-600 w-14">
		{last10Display}
	</td>

	{#if showAdvancedStats}
		<!-- Power Play Percentage -->
		<td class="px-3 py-3 text-sm text-center text-gray-900 w-14">
			<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-700">
				{advancedStats.powerPlayPercentage}%
			</span>
		</td>

		<!-- Penalty Kill Percentage -->
		<td class="px-3 py-3 text-sm text-center text-gray-900 w-14">
			<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700">
				{advancedStats.penaltyKillPercentage}%
			</span>
		</td>

		<!-- Goal Differential -->
		<td class="px-3 py-3 text-sm text-center w-14">
			<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium {advancedStats.goalDifferential > 0 ? 'bg-green-100 text-green-700' : advancedStats.goalDifferential < 0 ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-700'}">
				{advancedStats.goalDifferential > 0 ? '+' : ''}{advancedStats.goalDifferential}
			</span>
		</td>

		<!-- Goals For Per Game -->
		<td class="px-3 py-3 text-sm text-center text-gray-900 w-14">
			{advancedStats.goalsForPerGame}
		</td>

		<!-- Goals Against Per Game -->
		<td class="px-3 py-3 text-sm text-center text-gray-900 w-14">
			{advancedStats.goalsAgainstPerGame}
		</td>
	{/if}
</tr>

<style>
	/* Ensure proper spacing and alignment */
	tr {
		transition: all 0.15s ease-in-out;
	}

	/* Rank positioning */
	td:first-child {
		position: relative;
	}

	/* Team name styling */
	tr td:nth-child(2) p {
		line-height: 1.2;
	}

	/* Playoff indicator animation */
	@keyframes pulse-green {
		0%, 100% {
			opacity: 1;
		}
		50% {
			opacity: 0.5;
		}
	}

	.bg-green-500 {
		animation: pulse-green 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
	}

	/* Responsive adjustments */
	@media (max-width: 768px) {
		tr {
			font-size: 0.75rem;
		}

		td {
			padding: 0.5rem 0.25rem;
		}
	}
</style>