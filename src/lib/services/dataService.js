// Data Service
// Loads a published results snapshot and checks for finals when updates are delayed.

// @ts-nocheck

import { base } from '$app/paths'
import { isValidDateFormat } from '$lib/api/nhlApi.js'
import { fetchWithTimeout } from '$lib/utils/apiHelpers.js'
import { recoverDelayedResults } from './finalScoreRecovery.js'

/**
 * A pre-populated results snapshot as stored at
 * static/data/prepopulated/games/YYYY-MM-DD.json.
 * @typedef {Object} ResultsSnapshot
 * @property {string} date Date in YYYY-MM-DD format; must match the requested date
 * @property {Array<{gameId: number, gameState?: string, startTime?: string, homeTeam?: any, awayTeam?: any, homeScore?: number, awayScore?: number, [key: string]: any}>} games
 * @property {Array<Record<string, any>>} players Finnish player performances for the date
 * @property {number} [total_players]
 * @property {string} [generated_at]
 */

/** Load the published stats and recover any delayed final scores.
 * @param {string} date Date in YYYY-MM-DD format
 * @returns {Promise<{players: any[], games: {games: any[], findGameById: (id: number) => any}}>}
 * @throws {Error} On an invalid date, failed fetch, or incomplete snapshot
 */
export async function getResultsForDate(date) {
    if (!isValidDateFormat(date)) throw new Error('Invalid results date')
    const response = await fetchWithTimeout(
        `${base}/data/prepopulated/games/${date}.json?t=${Date.now()}`,
        10000,
        { cache: 'no-store' }
    )
    if (!response.ok) throw new Error(`Could not load results: HTTP ${response.status}`)
    const data = await response.json()
    if (data.date !== date || !Array.isArray(data.games) || !Array.isArray(data.players)) {
        throw new Error('Incomplete results snapshot')
    }
    const { games, players } = await recoverDelayedResults(data)
    const gamesById = new Map(games.map((game) => [game.gameId, game]))
    return {
        players,
        games: { games, findGameById: (id) => gamesById.get(id) || null },
    }
}
