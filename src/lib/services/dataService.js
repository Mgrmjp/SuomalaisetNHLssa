// Data Service
// Loads the single pre-populated results snapshot for a date.
// Scores and players always come from the same snapshot.

// @ts-nocheck

import { base } from '$app/paths'
import { isValidDateFormat } from '$lib/api/nhlApi.js'
import { fetchWithTimeout } from '$lib/utils/apiHelpers.js'

/**
 * A pre-populated results snapshot as stored at
 * static/data/prepopulated/games/YYYY-MM-DD.json.
 * @typedef {Object} ResultsSnapshot
 * @property {string} date Date in YYYY-MM-DD format; must match the requested date
 * @property {Array<{gameId: number, gameState?: string, startTime?: string, homeTeam?: any, awayTeam?: any, homeScore?: number, awayScore?: number, [key: string]: any}>} games
 * @property {Array<Record<string, any>>} players Finnish player performances for the date
 * @property {number} [total_players]
 */

/** Load one fresh snapshot so scores and players update together.
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
    const gamesById = new Map(data.games.map((game) => [game.gameId, game]))
    return {
        players: data.players,
        games: { games: data.games, findGameById: (id) => gamesById.get(id) || null },
    }
}
