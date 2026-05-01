import {
    fetchRegularSeasonStats,
    getCurrentSeasonId,
    loadRegularSeasonStatsFromDisk,
    loadRosterLookupFromDisk,
    mergeRosterInfo,
} from '$lib/server/playerStats.js'

/**
 * @param {any[]} skatersData
 * @param {any[]} goaliesData
 */
function augmentPlayersWithRoster(skatersData, goaliesData) {
    try {
        const rosterData = loadRosterLookupFromDisk()

        return {
            skaters: mergeRosterInfo(skatersData, rosterData),
            goalies: mergeRosterInfo(goaliesData, rosterData),
        }
    } catch (rosterError) {
        console.warn('Failed to load roster info for list augmentation:', rosterError)
        return { skaters: skatersData, goalies: goaliesData }
    }
}

/** @type {import('./$types').PageServerLoad} */
export async function load({ fetch }) {
    try {
        const seasonId = getCurrentSeasonId()

        try {
            const { skaters: skatersData, goalies: goaliesData } =
                loadRegularSeasonStatsFromDisk(seasonId)
            const { skaters, goalies } = augmentPlayersWithRoster(skatersData, goaliesData)

            return {
                skaters,
                goalies,
                seasonId,
                updatedAt: new Date().toISOString(),
                source: 'prebuilt',
            }
        } catch (_fileError) {
            // Fallback to API if pre-built files don't exist
            console.warn('Pre-built data not found, fetching from NHL API...')

            const { skaters: skatersData, goalies: goaliesData } = await fetchRegularSeasonStats(
                fetch,
                seasonId
            )
            const { skaters, goalies } = augmentPlayersWithRoster(skatersData, goaliesData)

            return {
                skaters,
                goalies,
                seasonId,
                updatedAt: new Date().toISOString(),
                source: 'api',
            }
        }
    } catch (error) {
        console.error('Error fetching player data:', error)
        return {
            skaters: [],
            goalies: [],
            error: 'Pelaajaliistan lataus epäonnistui',
        }
    }
}
