<script>
    // biome-ignore lint/correctness/noUnusedImports: used in template
    import TeamLogo from "$lib/components/ui/TeamLogo.svelte";
    import { getTeamColorVariables } from "$lib/utils/teamColors.js";
    import teamMapping from "$lib/utils/teamMapping.js";

    const {
        team,
        teamData = {},
        rank,
        showPlayoffIndicator = false,
        isWildCard = false,
        showAdvancedStats = false,
    } = $props();

    // Get team full name
    const teamName = $derived(teamMapping[team] || team);

    // Determine playoff indicator
    const isPlayoffTeam = $derived(rank <= 3 || isWildCard); // Top 3 in division OR Wild Card

    // Use teamData for all team statistics
    const teamStats = $derived(teamData);

    // Team color variables
    let teamColorVars = $state({
        "--team-primary-color": "#000000",
        "--team-secondary-color": "#FFFFFF",
        "--team-accent-color": "#000000",
    });

    // Load team colors when team changes
    $effect(async () => {
        if (team) {
            try {
                teamColorVars = await getTeamColorVariables(team);
            } catch (error) {
                console.warn(`Failed to load team colors for ${team}:`, error);
            }
        }
    });

    // Format streak with enhanced gradient styling
    const streakDisplay = $derived(getEnhancedStreakDisplay(teamData.streak));

    // Format last 10 games
    const last10Display = $derived(teamData.last10 || "0-0-0");

    // Calculate advanced stats
    const advancedStats = $derived(calculateAdvancedStats(teamData));

    // Row classes
    const rowClasses = $derived("border-b border-gray-100 bg-white hover:bg-gray-50");

    // Enhanced streak display with gradients matching PlayerCard style
    function getEnhancedStreakDisplay(streak) {
        if (!streak || streak.length < 2) return null;

        const type = streak[0];

        switch (type) {
            case "W":
                return {
                    text: streak,
                    bg: "bg-gradient-to-br from-green-500 to-green-600",
                    textColor: "text-white",
                    ring: "ring-green-300",
                };
            case "L":
                return {
                    text: streak,
                    bg: "bg-gradient-to-br from-red-500 to-red-600",
                    textColor: "text-white",
                    ring: "ring-red-300",
                };
            case "OT":
                return {
                    text: streak,
                    bg: "bg-gradient-to-br from-amber-500 to-orange-500",
                    textColor: "text-white",
                    ring: "ring-amber-300",
                };
            default:
                return null;
        }
    }

    // Calculate advanced statistics
    function calculateAdvancedStats(stats) {
        const gamesPlayed = stats.gamesPlayed || 1;

        // Power Play Percentage (placeholder - would need real PP data)
        const powerPlayGoals = stats.powerPlayGoals || 0;
        const powerPlayOpportunities = stats.powerPlayOpportunities || 1;
        const powerPlayPercentage = ((powerPlayGoals / powerPlayOpportunities) * 100).toFixed(1);

        // Penalty Kill Percentage (placeholder - would need real PK data)
        const penaltyKillGoalsAllowed = stats.penaltyKillGoalsAllowed || 0;
        const penaltyKillTimesShorthanded = stats.penaltyKillTimesShorthanded || 1;
        const penaltyKillPercentage = (
            ((penaltyKillTimesShorthanded - penaltyKillGoalsAllowed) /
                penaltyKillTimesShorthanded) *
            100
        ).toFixed(1);

        // Goal Differential
        const goalDifferential = stats.goalDifferential || stats.goalsFor - stats.goalsAgainst || 0;

        // Goals For Per Game
        const goalsForPerGame = ((stats.goalsFor || 0) / gamesPlayed).toFixed(2);

        // Goals Against Per Game
        const goalsAgainstPerGame = ((stats.goalsAgainst || 0) / gamesPlayed).toFixed(2);

        return {
            powerPlayPercentage,
            penaltyKillPercentage,
            goalDifferential,
            goalsForPerGame,
            goalsAgainstPerGame,
        };
    }
</script>

<tr
    class={rowClasses}
    style={Object.entries(teamColorVars)
        .map(([key, value]) => `${key}: ${value}`)
        .join("; ")}
>
    <!-- Rank -->
    <td
        class="standing-cell standing-cell--rank px-3 py-3 text-sm font-medium text-gray-900 text-center w-12 sticky left-0 z-10 bg-white border-r border-gray-100 shadow-[2px_0_5px_rgba(0,0,0,0.05)]"
    >
        <div class="flex items-center justify-center">
            <span class="text-gray-600">
                {rank}
            </span>
            {#if showPlayoffIndicator && isPlayoffTeam}
                <div class="ml-1 w-2 h-2 bg-gray-800 rounded-full" title="Playoff Position"></div>
            {/if}
        </div>
    </td>

    <!-- Team -->
    <td
        class="standing-cell standing-cell--team px-3 py-3 text-sm sticky left-12 z-10 bg-white border-r border-gray-100 shadow-[2px_0_5px_rgba(0,0,0,0.05)]"
    >
        <div class="flex items-center space-x-3">
            <div class="flex-shrink-0">
                <TeamLogo {team} size="36" />
            </div>
            <div class="min-w-0 flex-1">
                <p class="font-medium text-gray-900 truncate hidden sm:block">
                    {teamName}
                </p>
                <p class="text-xs font-bold sm:font-normal text-gray-700 sm:text-gray-500">
                    {team}
                </p>
            </div>
        </div>
    </td>

    <!-- Games Played -->
    <td class="standing-cell standing-cell--gp px-3 py-3 text-sm text-center text-gray-900 w-12">
        <span class="stat-value">{teamStats.gamesPlayed}</span>
    </td>

    <!-- Wins -->
    <td class="standing-cell standing-cell--wins px-3 py-3 text-sm text-center w-12">
        {teamStats.wins}
    </td>

    <!-- Losses -->
    <td class="standing-cell standing-cell--losses px-3 py-3 text-sm text-center w-12">
        {teamStats.losses}
    </td>

    <!-- Overtime Losses -->
    <td class="standing-cell standing-cell--ot px-3 py-3 text-sm text-center w-12">
        {teamStats.overtimeLosses}
    </td>

    <!-- Points -->
    <td class="standing-cell standing-cell--points px-3 py-3 text-sm font-bold text-center w-12">
        {teamStats.points}
    </td>

    <!-- Points Percentage -->
    <td
        class="standing-cell standing-cell--points-pct px-3 py-3 text-sm text-center text-gray-900 w-14"
    >
        <span class="stat-value">{teamStats.pointsPercentage.toFixed(3)}</span>
    </td>

    <!-- Streak -->
    <td class="standing-cell standing-cell--streak px-3 py-3 text-sm text-center w-14">
        {#if streakDisplay}
            <span class="text-gray-600">{streakDisplay.text}</span>
        {:else}
            <span class="text-gray-400">-</span>
        {/if}
    </td>

    <!-- Last 10 Games -->
    <td class="standing-cell standing-cell--l10 px-3 py-3 text-sm text-center text-gray-600 w-20">
        <span class="stat-value tabular-nums">{last10Display}</span>
    </td>

    {#if showAdvancedStats}
        <!-- Power Play Percentage -->
        <td class="px-3 py-3 text-sm text-center w-14">
            {advancedStats.powerPlayPercentage}%
        </td>

        <!-- Penalty Kill Percentage -->
        <td class="px-3 py-3 text-sm text-center w-14">
            {advancedStats.penaltyKillPercentage}%
        </td>

        <!-- Goal Differential -->
        <td class="px-3 py-3 text-sm text-center w-14">
            <span
                class={advancedStats.goalDifferential > 0
                    ? "text-green-700"
                    : advancedStats.goalDifferential < 0
                      ? "text-red-700"
                      : "text-gray-700"}
            >
                {advancedStats.goalDifferential > 0 ? "+" : ""}{advancedStats.goalDifferential}
            </span>
        </td>

        <!-- Goals For Per Game -->
        <td class="px-3 py-3 text-sm text-center text-gray-900 w-14">
            <span class="stat-value">{advancedStats.goalsForPerGame}</span>
        </td>

        <!-- Goals Against Per Game -->
        <td class="px-3 py-3 text-sm text-center text-gray-900 w-14">
            <span class="stat-value">{advancedStats.goalsAgainstPerGame}</span>
        </td>
    {/if}
</tr>

<style>
    tr {
        position: relative;
    }

    .stat-value {
        font-variant-numeric: tabular-nums;
        font-weight: 600;
        color: #1f2937;
    }

    @media (max-width: 768px) {
        tr {
            font-size: 0.75rem;
        }

        td {
            padding: 0.5rem 0.25rem;
        }
    }
</style>
