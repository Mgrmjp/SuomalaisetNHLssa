import { error } from '@sveltejs/kit'
import { env } from '$env/dynamic/private'
import { loadOffseasonMovesFromDisk } from '$lib/server/offseasonMoves.js'
import {
    fetchRegularSeasonStats,
    getCurrentSeasonId,
    getRosterPath,
    loadRegularSeasonStatsFromDisk,
    loadRosterLookupFromDisk,
    mergeRosterInfo,
    readJsonFileSync,
} from '$lib/server/playerStats.js'
import { correctFullName, correctFullNameWithLLM } from '$lib/utils/finnishNameUtils.js'
import { sanitizeImageUrl } from '$lib/utils/playerHeadshots.js'

const PLAYER_SLUG_PATTERN = /^[a-z0-9-]{1,100}$/i
const NUMERIC_SLUG_PATTERN = /^\d+$/

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

/** @param {any} player */
function getRosterName(player) {
    const firstName = player.firstName?.default || ''
    const lastName = player.lastName?.fi || player.lastName?.default || ''
    return correctFullName(`${firstName} ${lastName}`.trim() || player.name)
}

/** @param {any} player */
function rosterToPlayer(player) {
    const team = player.currentTeam || player.lastTeam || 'NHL'

    return {
        ...player,
        name: getRosterName(player),
        skaterFullName: player.position === 'G' ? undefined : getRosterName(player),
        goalieFullName: player.position === 'G' ? getRosterName(player) : undefined,
        teamAbbrevs: team,
        positionCode: player.position,
        jerseyNumber: player.sweaterNumber,
        headshot: sanitizeImageUrl(player.headshot),
        age: player.birthDate
            ? new Date().getFullYear() - new Date(player.birthDate).getFullYear()
            : undefined,
        hasSeasonStats: false,
        isRosterProfile: true,
    }
}

/**
 * @param {any[] | undefined} players
 * @param {number | null} numericPlayerId
 * @param {any | null} rosterPlayer
 */
function findPlayerById(players, numericPlayerId, rosterPlayer) {
    const playerId = numericPlayerId ?? rosterPlayer?.playerId
    if (playerId === undefined || playerId === null) return null

    return players?.find((p) => String(p.playerId) === String(playerId)) || null
}

/**
 * @param {any} movesData
 * @param {any} player
 * @param {string} slug
 */
function getLatestPlayerMove(movesData, player, slug) {
    const playerId =
        player?.playerId === undefined || player?.playerId === null ? '' : String(player.playerId)
    const moves = /** @type {any[]} */ (Array.isArray(movesData?.moves) ? movesData.moves : [])

    return (
        moves
            .filter((move) => String(move.playerId) === playerId || move.playerSlug === slug)
            .sort((a, b) => String(b.date).localeCompare(String(a.date)))[0] || null
    )
}

/**
 * @param {any} player
 * @param {any | null} move
 */
function applyLatestMove(player, move) {
    if (!move?.newTeam) return player

    return {
        ...player,
        currentTeam: move.newTeam,
        profileTeamAbbrev: move.newTeam,
        previousTeamAbbrev: move.oldTeam,
        latestMove: move,
    }
}

/** @type {import('./$types').PageServerLoad} */
export async function load({ params, fetch }) {
    const { slug } = params
    const normalizedSlug = slug.toLowerCase()
    const numericPlayerId =
        NUMERIC_SLUG_PATTERN.test(normalizedSlug) && normalizedSlug.length <= 10
            ? parseInt(normalizedSlug, 10)
            : null

    if (!PLAYER_SLUG_PATTERN.test(slug)) {
        throw error(404, 'Pelaajaa ei löytynyt')
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
        const seasonId = getCurrentSeasonId()
        const rosterData = loadRosterLookupFromDisk()
        const rosterPlayers = /** @type {any[]} */ (Object.values(rosterData))
        const rosterPlayer = rosterPlayers.find((p) => {
            if (numericPlayerId !== null && String(p.playerId) === String(numericPlayerId)) {
                return true
            }

            return nameToSlug(getRosterName(p)) === normalizedSlug
        })
        const offseasonMoves = await loadOffseasonMovesFromDisk()

        /** @type {any | null} */
        let player = null
        /** @type {any[]} */
        let allPlayers = []

        try {
            const { skaters: skatersData, goalies: goaliesData } =
                loadRegularSeasonStatsFromDisk(seasonId)
            allPlayers = [...skatersData, ...goaliesData]

            // Find player by slug (name-based URL)
            player = findPlayerByDeterministicSlug(allPlayers, normalizedSlug)

            // Also support numeric IDs for backwards compatibility
            if (!player && numericPlayerId !== null) {
                player = findPlayerById(allPlayers, numericPlayerId, null)
            }

            if (!player) {
                player = findPlayerById(allPlayers, numericPlayerId, rosterPlayer)
            }

            if (!player && numericPlayerId === null) {
                player = await findPlayerByLLMSlug(allPlayers, normalizedSlug)
            }
        } catch (_fileError) {
            // Fallback to API if pre-built files don't exist
            console.warn('Pre-built data not found, fetching from NHL API...')

            const { skaters: skatersData, goalies: goaliesData } = await fetchRegularSeasonStats(
                fetch,
                seasonId
            )
            allPlayers = [...skatersData, ...goaliesData]

            player = findPlayerByDeterministicSlug(allPlayers, normalizedSlug)

            if (!player) {
                player = findPlayerById(allPlayers, numericPlayerId, rosterPlayer)
            }

            if (!player && numericPlayerId === null) {
                player = await findPlayerByLLMSlug(allPlayers, normalizedSlug)
            }
        }

        if (!player) {
            throw error(404, 'Pelaajaa ei löytynyt')
        }

        // Augment with roster data (birthDate, height, weight etc)
        try {
            const [augmentedPlayer] = mergeRosterInfo([player], rosterData)
            player = augmentedPlayer || player

            const rosterInfo = player.playerId
                ? /** @type {any} */ (rosterData[String(player.playerId)])
                : null
            if (rosterInfo) {
                const rosterName = getRosterName(rosterInfo)
                player.name = rosterName
                if ((player.positionCode || rosterInfo.position) === 'G') {
                    player.goalieFullName = rosterName
                } else {
                    player.skaterFullName = rosterName
                }
                player.jerseyNumber = player.jerseyNumber ?? rosterInfo.sweaterNumber
                player.currentTeam = rosterInfo.currentTeam ?? player.currentTeam
            }

            player = applyLatestMove(
                player,
                getLatestPlayerMove(offseasonMoves, player, normalizedSlug)
            )
            player.headshot = sanitizeImageUrl(player.headshot || '') || player.headshot
        } catch (rosterError) {
            console.warn('Failed to load roster info for augmentation:', rosterError)
        }

        if (player) {
            player.hasSeasonStats = true
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
        if (err && typeof err === 'object' && 'status' in err && err.status !== 404) throw err

        try {
            const seasonId = getCurrentSeasonId()
            const rosterData = loadRosterLookupFromDisk()
            const rosterPlayers = /** @type {any[]} */ (Object.values(rosterData))
            const rosterPlayer = rosterPlayers.find((p) => {
                if (numericPlayerId !== null && String(p.playerId) === String(numericPlayerId)) {
                    return true
                }

                return nameToSlug(getRosterName(p)) === normalizedSlug
            })

            if (!rosterPlayer) {
                throw error(404, 'Pelaajaa ei löytynyt')
            }

            const player = rosterToPlayer(rosterPlayer)
            const offseasonMoves = await loadOffseasonMovesFromDisk()

            return {
                player: applyLatestMove(
                    player,
                    getLatestPlayerMove(offseasonMoves, player, normalizedSlug)
                ),
                sameTeamPlayers: [],
                seasonId,
                slug,
                updatedAt: new Date().toISOString(),
            }
        } catch (rosterError) {
            if (rosterError && typeof rosterError === 'object' && 'status' in rosterError) {
                throw rosterError
            }
        }

        console.error('Error fetching player data:', err)
        throw error(500, 'Pelaajatietojen lataus epäonnistui')
    }
}

/** @type {import('./$types').EntryGenerator} */
export function entries() {
    const rosterData = readJsonFileSync(getRosterPath())
    const slugs = new Set(
        Object.values(rosterData).map((player) => nameToSlug(getRosterName(player)))
    )

    return Array.from(slugs).map((slug) => ({ slug }))
}

export const prerender = true
