import { didParticipate, sortDailyPlayers } from './dailyPlayers.js'

/** Previous calendar date, independent of timezone and daylight-saving changes.
 * @param {string} date
 */
export function previousCalendarDate(date) {
    const day = new Date(`${date}T12:00:00Z`)
    if (Number.isNaN(day.getTime())) return ''
    day.setUTCDate(day.getUTCDate() - 1)
    return day.toISOString().slice(0, 10)
}

/** Keep live and completed results in the normal player-card view.
 * @param {string} selectedDate
 * @param {string} today
 * @param {Array<{gameState?: string}>} games
 */
export function shouldShowYesterdayResult(selectedDate, today, games = []) {
    return (
        selectedDate === today &&
        !games.some((game) =>
            ['LIVE', 'CRIT', 'IRT', 'OFF', 'FINAL'].includes(game.gameState || '')
        )
    )
}

/** Choose a completed game from exactly the requested day, with Finnish participants.
 * @param {{date?: string, games?: any[], players?: any[]} | null} snapshot
 * @param {string} date
 */
export function selectYesterdayResult(snapshot, date, random = Math.random()) {
    if (
        !snapshot ||
        snapshot.date !== date ||
        !Array.isArray(snapshot.games) ||
        !Array.isArray(snapshot.players)
    ) {
        return null
    }
    const games = snapshot.games.filter((game) => game?.gameId != null)
    const lookup = new Map(games.map((game) => [String(game.gameId), game]))
    const gamesData = {
        /** @param {string | number} id */
        findGameById: (id) => lookup.get(String(id)),
    }
    const participants = snapshot.players.filter((player) => didParticipate(player, gamesData))
    const results = games.flatMap((game) => {
        if (
            !['OFF', 'FINAL'].includes(game.gameState) ||
            !game.awayTeam ||
            !game.homeTeam ||
            ![game.awayScore, game.homeScore].every(
                (score) => Number.isInteger(score) && score >= 0
            )
        ) {
            return []
        }
        const players = participants.filter(
            (player) => String(player.game_id) === String(game.gameId)
        )
        return players.length ? [{ date, game, players: sortDailyPlayers(players) }] : []
    })
    return results[Math.min(Math.floor(random * results.length), results.length - 1)] || null
}
