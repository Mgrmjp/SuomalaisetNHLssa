import {
    fetchStats,
    getCurrentSeasonId,
    getStatsUpdatedAt,
    loadSkaterStatsFromDisk,
} from '$lib/server/playerStats.js'

/** @type {import('./$types').PageServerLoad} */
export async function load({ fetch }) {
    const seasonId = getCurrentSeasonId()
    try {
        try {
            const players = loadSkaterStatsFromDisk(seasonId)

            return {
                players,
                seasonId,
                updatedAt: getStatsUpdatedAt(seasonId, ['skaters']),
                source: 'prebuilt',
            }
        } catch (_fileError) {
            // Fallback to API if pre-built file doesn't exist
            console.warn('Pre-built data not found, fetching from NHL API...')

            const players = await fetchStats(fetch, {
                statType: 'skater',
                seasonId,
                gameTypeId: 2,
                sortProperty: 'points',
                sortDirection: 'DESC',
                limit: 100,
            })

            return {
                players,
                seasonId,
                updatedAt: new Date().toISOString(),
                source: 'api',
            }
        }
    } catch (error) {
        console.error('Error fetching leaderboard data:', error)
        return {
            players: [],
            seasonId,
            updatedAt: null,
            error: 'Tilastojen lataus epäonnistui',
        }
    }
}
