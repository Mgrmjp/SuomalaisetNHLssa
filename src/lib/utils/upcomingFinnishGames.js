/**
 * Convert the roster-based schedule to the game format used by the empty state.
 * @param {Array<{gameId: number, startTime: string, finnishPlayers: Array<{name: string}>}>} games
 * @param {string} selectedDate
 * @param {number} now
 */
export function selectUpcomingFinnishGames(games, selectedDate, now) {
    if (!selectedDate) return []
    return games
        .filter(
            (game) =>
                game.startTime?.slice(0, 10) >= selectedDate &&
                new Date(game.startTime).getTime() > now &&
                game.finnishPlayers?.length > 0
        )
        .sort((a, b) => a.startTime.localeCompare(b.startTime))
        .slice(0, 4)
        .map((game) => ({
            ...game,
            gameState: 'FUT',
            finnish_players_count: game.finnishPlayers.length,
            finnishPlayers: game.finnishPlayers.map((player) => player.name),
        }))
}
