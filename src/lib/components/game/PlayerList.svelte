<script>
    import LoadingSpinner from "$lib/components/ui/LoadingSpinner.svelte";
    import PlayerCard from "$lib/components/game/PlayerCard.svelte";
    import { displayDate, error, isLoading, players, setDate } from "$lib/stores/gameData.js";
    import {
        getSavePercentage,
        hasPoints,
        isDefense,
        isGoalie,
    } from "$lib/utils/positionHelpers.js";

    function _handleRetry() {
        const currentDate = new Date().toISOString().split("T")[0];
        setDate(currentDate);
    }

    /**
     * Check if a goalie actually played in the game
     * Goalie must have logged time, faced shots, made saves, or allowed goals
     *
     * @param {Object} player - Player object
     * @returns {boolean} True if goalie participated in the game
     */
    function goalieHasPlayed(player) {
        const shotsAgainst = Number(player.shots_against ?? player.shotsAgainst ?? 0);
        const saves = Number(player.saves ?? player.goalie_saves ?? 0);
        const goalsAgainst = Number(player.goals_against ?? player.goalsAgainst ?? 0);
        const toi = player.time_on_ice || player.toi || "";

        return (
            shotsAgainst > 0 ||
            saves > 0 ||
            goalsAgainst > 0 ||
            (toi && toi !== "00:00" && toi !== "0:00")
        );
    }

    /**
     * Filter players based on position and performance
     * - Goalies: must have actually played (faced shots, made saves, etc.)
     * - Skaters: must have recorded at least one point
     *
     * @param {Object[]} players - Array of player objects
     * @returns {Object[]} Filtered array of players
     */
    $: filteredPlayers = ($players || []).filter((player) => {
        if (isGoalie(player)) {
            return goalieHasPlayed(player);
        }
        return hasPoints(player);
    });

    /**
     * Sort skaters by points (primary), then goals, plus/minus, and assists
     *
     * @param {Object[]} list - Array of skater objects
     * @returns {Object[]} Sorted array
     */
    const sortSkatersByPoints = (list) =>
        [...list].sort(
            (a, b) =>
                (b.points || 0) - (a.points || 0) ||
                (b.goals || 0) - (a.goals || 0) ||
                (b.plus_minus ?? -Infinity) - (a.plus_minus ?? -Infinity) ||
                (b.assists || 0) - (a.assists || 0),
        );

    /**
     * Sort goalies by save percentage (best first)
     *
     * @param {Object[]} list - Array of goalie objects
     * @returns {Object[]} Sorted array
     */
    const sortGoalies = (list) =>
        [...list].sort((a, b) => {
            const aPct = getSavePercentage(a);
            const bPct = getSavePercentage(b);

            if (aPct === null && bPct === null) return 0;
            if (aPct === null) return 1;
            if (bPct === null) return -1;

            return bPct - aPct;
        });

    $: forwards = sortSkatersByPoints(filteredPlayers.filter((p) => !isGoalie(p) && !isDefense(p)));
    $: defenders = sortSkatersByPoints(filteredPlayers.filter((p) => !isGoalie(p) && isDefense(p)));
    $: goalies = sortGoalies(filteredPlayers.filter((p) => isGoalie(p)));

    $: hasAnyPlayers = forwards.length + defenders.length + goalies.length > 0;
</script>

{#if $isLoading}
    <div class="py-8">
        <div class="container mx-auto px-4">
            <div class="text-center">
                <LoadingSpinner message="Ladataan pelaajia..." />
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
    <section id="scoringList" class="scoring-list py-12 bg-gray-50/50">
        <div class="scoring-list__container container mx-auto px-4">
            {#if !hasAnyPlayers && $isLoading === false}
                <div
                    class="scoring-list__grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
                >
                    <div
                        class="scoring-list__empty-state col-span-2 md:col-span-2 lg:col-span-2 lg:col-start-2 xl:col-span-2 xl:col-start-2 bg-white rounded-lg shadow-lg p-6 relative overflow-hidden min-h-[220px] flex items-center justify-center"
                        style="border: 1px solid transparent; background: linear-gradient(white, white) padding-box, linear-gradient(135deg, #1e40af, #3b82f6, #60a5fa) border-box;"
                    >
                        <!-- Subtle background pattern -->
                        <div
                            class="scoring-list__empty-bg absolute inset-0 bg-gradient-to-br from-finnish-blue-50/30 to-transparent opacity-50"
                        ></div>

                        <!-- Content -->
                        <div class="scoring-list__empty-content relative z-10 text-center">
                            <div
                                class="scoring-list__empty-icon w-16 h-16 bg-finnish-blue-100 rounded-lg flex items-center justify-center mb-4 mx-auto"
                            >
                                <svg
                                    viewBox="-0.5 0 25 25"
                                    fill="none"
                                    xmlns="http://www.w3.org/2000/svg"
                                    class="w-8 h-8"
                                >
                                    <path
                                        d="M12 14.5C13.1046 14.5 14 13.6046 14 12.5C14 11.3954 13.1046 10.5 12 10.5C10.8954 10.5 10 11.3954 10 12.5C10 13.6046 10.8954 14.5 12 14.5Z"
                                        stroke="#1e40af"
                                        stroke-miterlimit="10"
                                        fill="none"
                                    ></path>
                                    <path
                                        d="M19.5 14.5C20.6046 14.5 21.5 13.6046 21.5 12.5C21.5 11.3954 20.6046 10.5 19.5 10.5C18.3954 10.5 17.5 11.3954 17.5 12.5C17.5 13.6046 18.3954 14.5 19.5 14.5Z"
                                        stroke="#1e40af"
                                        stroke-miterlimit="10"
                                        fill="none"
                                    ></path>
                                    <path
                                        d="M4.5 14.5C5.60457 14.5 6.5 13.6046 6.5 12.5C6.5 11.3954 5.60457 10.5 4.5 10.5C3.39543 10.5 2.5 11.3954 2.5 12.5C2.5 13.6046 3.39543 14.5 4.5 14.5Z"
                                        stroke="#1e40af"
                                        stroke-miterlimit="10"
                                        fill="none"
                                    ></path>
                                </svg>
                            </div>
                            <h3
                                class="scoring-list__empty-title text-lg font-semibold text-gray-900 mb-2"
                            >
                                Ei suomalaista pisteidentekijää
                            </h3>
                            <p
                                class="scoring-list__empty-text text-sm text-gray-600 leading-relaxed max-w-sm mx-auto"
                            >
                                Yhtään suomalaispelaajaa ei ole merkitty pisteille tai dataa ei ole
                                vielä saatavilla päivälle
                                <span
                                    class="scoring-list__empty-date font-semibold text-finnish-blue-900"
                                    >{$displayDate}</span
                                >.
                            </p>
                        </div>
                    </div>
                </div>
            {:else}
                <div class="scoring-list__sections space-y-10">
                    {#if forwards.length}
                        <div class="scoring-list__section space-y-4">
                            <div
                                class="scoring-list__section-header flex items-baseline gap-3 pb-2 border-b border-gray-200"
                            >
                                <h3
                                    class="scoring-list__section-title text-xl font-bold text-gray-900 tracking-tight"
                                >
                                    Hyökkääjät
                                </h3>
                            </div>
                            <div
                                class="scoring-list__grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
                            >
                                {#each forwards as player (`${player.playerId}-${player.game_id}`)}
                                    <PlayerCard {player} />
                                {/each}
                            </div>
                        </div>
                        <div class="h-8"></div>
                    {/if}

                    {#if defenders.length}
                        <div class="scoring-list__section space-y-4">
                            <div
                                class="scoring-list__section-header flex items-baseline gap-3 pb-2 border-b border-gray-200"
                            >
                                <h3
                                    class="scoring-list__section-title text-xl font-bold text-gray-900 tracking-tight"
                                >
                                    Puolustajat
                                </h3>
                            </div>
                            <div
                                class="scoring-list__grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
                            >
                                {#each defenders as player (`${player.playerId}-${player.game_id}`)}
                                    <PlayerCard {player} />
                                {/each}
                            </div>
                        </div>
                        <div class="h-8"></div>
                    {/if}

                    {#if goalies.length}
                        <div class="scoring-list__section space-y-4">
                            <div
                                class="scoring-list__section-header flex items-baseline gap-3 pb-2 border-b border-gray-200"
                            >
                                <h3
                                    class="scoring-list__section-title text-xl font-bold text-gray-900 tracking-tight"
                                >
                                    Maalivahdit
                                </h3>
                            </div>
                            <div
                                class="scoring-list__grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
                            >
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
