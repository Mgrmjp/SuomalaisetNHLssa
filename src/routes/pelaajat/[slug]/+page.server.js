import { readFileSync } from 'node:fs'
import { join } from 'node:path'
import { error } from '@sveltejs/kit'
import { env } from '$env/dynamic/private'
import { correctFullName, correctFullNameWithLLM } from '$lib/utils/finnishNameUtils.js'
import { sanitizeImageUrl } from '$lib/utils/playerHeadshots.js'

/** @type {import('./$types').PageServerLoad} */
export async function load({ params }) {
    const { slug } = params

    // Helper function to convert player name to URL-friendly slug
    /** @param {string} name */
    function nameToSlug(name) {
        return name
            .toLowerCase()
            .replace(/ä/g, 'a')
            .replace(/ö/g, 'o')
            .replace(/å/g, 'o')
            .replace(/\s+/g, '-')
            .replace(/[^a-z0-9-]/g, '')
    }

    /**
     * @param {any[]} players
     * @param {string} targetSlug
     * @returns {any | null}
     */
    function findPlayerByDeterministicSlug(players, targetSlug) {
        return (
            players.find((p) => {
                const playerName = p.skaterFullName || p.goalieFullName
                const correctedName = correctFullName(playerName)
                const playerSlug = nameToSlug(correctedName)
                return playerSlug === targetSlug
            }) || null
        )
    }

    /**
     * Optional server-side LLM fallback for hard cases that survive deterministic correction.
     *
     * @param {any[]} players
     * @param {string} targetSlug
     * @returns {Promise<any | null>}
     */
    async function findPlayerByLLMSlug(players, targetSlug) {
        for (const player of players) {
            const playerName = player.skaterFullName || player.goalieFullName
            const correctedName = await correctFullNameWithLLM(playerName, env.OPENAI_API_KEY)
            if (nameToSlug(correctedName) === targetSlug) {
                return player
            }
        }
        return null
    }

    try {
        const now = new Date()
        const currentYear = now.getFullYear()
        const currentMonth = now.getMonth()

        const startYear = currentMonth < 9 ? currentYear - 1 : currentYear
        const endYear = startYear + 1
        const seasonId = `${startYear}${endYear}`

        // Try to load from pre-built JSON files first
        const prebuiltDir = join(process.cwd(), 'static/data/player-stats')
        const skatersFile = join(prebuiltDir, `skaters-${seasonId}.json`)
        const goaliesFile = join(prebuiltDir, `goalies-${seasonId}.json`)

        let player = null
        /** @type {any[]} */
        let allPlayers = []

        try {
            const skatersData = JSON.parse(readFileSync(skatersFile, 'utf-8'))
            const goaliesData = JSON.parse(readFileSync(goaliesFile, 'utf-8'))
            allPlayers = [...skatersData, ...goaliesData]

            // Find player by slug (name-based URL)
            player = findPlayerByDeterministicSlug(allPlayers, slug.toLowerCase())

            // Also support numeric IDs for backwards compatibility
            if (!player && !Number.isNaN(parseInt(slug, 10))) {
                player = allPlayers.find((p) => p.playerId === parseInt(slug, 10))
            }

            if (!player && Number.isNaN(parseInt(slug, 10))) {
                player = await findPlayerByLLMSlug(allPlayers, slug.toLowerCase())
            }
        } catch (_fileError) {
            // Fallback to API if pre-built files don't exist
            console.warn('Pre-built data not found, fetching from NHL API...')

            const skaterUrl = `https://api.nhle.com/stats/rest/en/skater/summary?isAggregate=false&isGame=false&sort=%5B%7B%22property%22:%22skaterFullName%22,%22direction%22:%22ASC%22%7D%5D&start=0&limit=500&cayenneExp=nationalityCode%3D%22FIN%22%20and%20gameTypeId%3D2%20and%20seasonId%3D${seasonId}`
            const goalieUrl = `https://api.nhle.com/stats/rest/en/goalie/summary?isAggregate=false&isGame=false&sort=%5B%7B%22property%22:%22goalieFullName%22,%22direction%22:%22ASC%22%7D%5D&start=0&limit=100&cayenneExp=nationalityCode%3D%22FIN%22%20and%20gameTypeId%3D2%20and%20seasonId%3D${seasonId}`

            const [skaterRes, goalieRes] = await Promise.all([fetch(skaterUrl), fetch(goalieUrl)])

            if (skaterRes.ok && goalieRes.ok) {
                const skatersData = await skaterRes.json()
                const goaliesData = await goalieRes.json()
                allPlayers = [...(skatersData.data || []), ...(goaliesData.data || [])]

                player = findPlayerByDeterministicSlug(allPlayers, slug.toLowerCase())

                if (!player && Number.isNaN(parseInt(slug, 10))) {
                    player = await findPlayerByLLMSlug(allPlayers, slug.toLowerCase())
                }
            }
        }

        if (!player) {
            throw error(404, 'Pelaajaa ei löytynyt')
        }

        // Augment with roster data (birthDate, height, weight etc)
        try {
            const rosterFile = join(process.cwd(), 'static/data/players/finnish-roster.json')
            const rosterData = JSON.parse(readFileSync(rosterFile, 'utf-8'))
            const rosterInfo = rosterData[player.playerId.toString()]
            if (rosterInfo) {
                player.birthDate = rosterInfo.birthDate
                if (player.birthDate) {
                    player.age = new Date().getFullYear() - new Date(player.birthDate).getFullYear()
                }
                player.heightInches = rosterInfo.heightInches
                player.weightLbs = rosterInfo.weightLbs
                player.birthplace = rosterInfo.birthplace
                // Sanitize headshot URL to strip malformed transformation parameters
                player.headshot = sanitizeImageUrl(rosterInfo.headshot) || player.headshot
            }
        } catch (rosterError) {
            console.warn('Failed to load roster info for augmentation:', rosterError)
        }

        // Get other players from the same team for related content
        const sameTeamPlayers = allPlayers
            .filter((p) => p.teamAbbrevs === player.teamAbbrevs && p.playerId !== player.playerId)
            .slice(0, 6)

        return {
            player,
            sameTeamPlayers,
            seasonId,
            slug,
            updatedAt: new Date().toISOString(),
        }
    } catch (err) {
        if (err && typeof err === 'object' && 'status' in err) throw err
        console.error('Error fetching player data:', err)
        throw error(500, 'Pelaajatietojen lataus epäonnistui')
    }
}
