/**
 * Merge roster and lineup schedules, keeping only future games with named Finnish players.
 * @param {Array<{gameId: number | string, startTime: string, gameState?: string, finnishPlayers?: Array<{name: string} | string>}>} games
 * @param {string} selectedDate
 * @param {number} now
 */
export function selectUpcomingFinnishGames(games, selectedDate, now) {
    if (!selectedDate) return []
    const seen = new Set()
    return games
        .filter(
            (game) =>
                (!game.gameState || ['FUT', 'PRE'].includes(game.gameState)) &&
                game.startTime?.slice(0, 10) >= selectedDate &&
                new Date(game.startTime).getTime() > now
        )
        .map((game) => ({
            ...game,
            finnishPlayers: [
                ...new Set(
                    (game.finnishPlayers || [])
                        .map((player) =>
                            (typeof player === 'string' ? player : player?.name || '').trim()
                        )
                        .filter(Boolean)
                ),
            ],
        }))
        .filter((game) => {
            const id = String(game.gameId)
            if (!game.finnishPlayers.length || seen.has(id)) return false
            seen.add(id)
            return true
        })
        .sort((a, b) => a.startTime.localeCompare(b.startTime))
        .slice(0, 4)
        .map((game) => ({
            ...game,
            gameState: game.gameState || 'FUT',
            finnish_players_count: game.finnishPlayers.length,
        }))
}
