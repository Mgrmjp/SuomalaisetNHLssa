<script>
    // biome-ignore lint/correctness/noUnusedImports: used in template
    import TeamStandingRow from "$lib/components/standings/TeamStandingRow.svelte";
    import { DIVISION_NAMES } from "$lib/utils/nhlStructure.js";
    import { getTeamColorVariables } from "$lib/utils/teamColors.js";

    const {
        teams = [],
        divisionName = "",
        showPlayoffIndicator = true,
        wildCardTeams = [],
        showAdvancedStats = false,
    } = $props();

    // Format division name for display
    const displayName = $derived(DIVISION_NAMES[divisionName] || divisionName);
    const hasTeams = $derived(teams && teams.length > 0);

    // Load division-leading team colors for container styling
    let divisionLeaderColors = $state({
        "--team-primary-color": "#003580",
        "--team-secondary-color": "#6366f1",
        "--team-accent-color": "#8b5cf6",
    });

    // Load team colors when teams change
    $effect(() => {
        (async () => {
            if (teams && teams.length > 0) {
                const leaderTeam = teams[0].team;
                try {
                    divisionLeaderColors = await getTeamColorVariables(leaderTeam);
                } catch (error) {
                    console.warn(`Failed to load colors for division leader ${leaderTeam}:`, error);
                }
            }
        })();
    });

    // Table headers
    const baseHeaders = [
        { key: "rank", label: "Sija", center: true, width: "w-12" },
        { key: "team", label: "Joukkue", center: false, width: "" },
        { key: "gamesPlayed", label: "O", center: true, width: "w-12" },
        { key: "wins", label: "V", center: true, width: "w-12" },
        { key: "losses", label: "H", center: true, width: "w-12" },
        { key: "ot", label: "JA", center: true, width: "w-12" },
        { key: "points", label: "P", center: true, width: "w-12" },
        { key: "pointsPct", label: "P%", center: true, width: "w-14" },
        { key: "streak", label: "Sarja", center: true, width: "w-14" },
        { key: "last10", label: "V10", center: true, width: "w-20" },
    ];

    const advancedHeaders = [
        { key: "powerPlayPercentage", label: "YV%", center: true, width: "w-14" },
        { key: "penaltyKillPercentage", label: "AV%", center: true, width: "w-14" },
        { key: "goalDifferential", label: "+/-", center: true, width: "w-14" },
        { key: "goalsForPerGame", label: "TM/O", center: true, width: "w-14" },
        { key: "goalsAgainstPerGame", label: "VM/O", center: true, width: "w-14" },
    ];

    // biome-ignore lint/correctness/noUnusedVariables: used in template
    const headers = $derived(
        showAdvancedStats ? [...baseHeaders, ...advancedHeaders] : baseHeaders,
    );
</script>

<div
    class="division-container bg-white rounded-lg shadow-lg overflow-hidden relative"
    style={Object.entries(divisionLeaderColors)
        .map(([key, value]) => `${key}: ${value}`)
        .join("; ")}
>
    <!-- Division Header -->
    <div class="division-header px-4 py-4 text-white relative overflow-hidden">
        <h3 class="division-title text-xl font-bold relative z-10 text-shadow">
            {displayName}
        </h3>
    </div>

    {#if hasTeams}
        <div class="overflow-x-auto">
            <table class="w-full text-sm">
                <!-- Table Header -->
                <thead class="bg-gray-100 border-b border-gray-200">
                    <tr>
                        {#each headers as header}
                            <th
                                class="px-3 py-2 text-xs font-medium text-gray-600 uppercase tracking-wider {header.width} {header.center
                                    ? 'text-center'
                                    : 'text-left'}"
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

        <!-- Division Footer -->
        <div class="px-4 py-3 bg-gray-50 border-t border-gray-200">
            <div class="flex items-center justify-between text-xs text-gray-600">
                <div>
                    <p>Päivitetty: {new Date().toLocaleDateString("fi-FI")}</p>
                </div>
            </div>
        </div>
    {:else}
        <!-- Empty State -->
        <div class="px-6 py-12 text-center">
            <div
                class="inline-flex items-center justify-center w-12 h-12 rounded-full bg-gray-100 mb-4"
            >
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
            <h4 class="text-sm font-medium text-gray-900 mb-1">Ei sarjataulukkoa saatavilla</h4>
            <p class="text-xs text-gray-500">Odottaa ottelutietojen lataamista...</p>
        </div>
    {/if}
</div>

<style>
    .division-container {
        border-radius: 8px;
        overflow: hidden;
        background: white;
        border: 1px solid #e5e7eb;
    }

    .division-header {
        background: #1e40af;
        color: white;
        padding: 0.75rem 1rem;
    }

    .division-title {
        font-weight: 600;
    }

    table {
        border-collapse: collapse;
        width: 100%;
    }

    thead th {
        background: #f9fafb;
        border-bottom: 1px solid #e5e7eb;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.75rem;
        padding: 0.5rem;
    }
</style>
