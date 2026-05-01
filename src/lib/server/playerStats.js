import { readFileSync } from 'node:fs'
import { readFile } from 'node:fs/promises'
import { join } from 'node:path'

/**
 * @typedef {{ [key: string]: any, playerId?: string | number | undefined, birthDate?: string | undefined, age?: number | undefined, heightInches?: number | undefined, weightLbs?: number | undefined, birthplace?: string | undefined, headshot?: string | undefined }} StatsPlayer
 * @typedef {{ birthDate?: string, heightInches?: number, weightLbs?: number, birthplace?: string, headshot?: string }} RosterPlayer
 * @typedef {Record<string, RosterPlayer>} RosterLookup
 * @typedef {'skater' | 'goalie'} StatType
 * @typedef {'ASC' | 'DESC'} SortDirection
 * @typedef {{ statType: StatType, seasonId: string, gameTypeId?: number, sortProperty: string, sortDirection?: SortDirection, limit?: number }} StatsApiUrlOptions
 */

const NHL_STATS_BASE = 'https://api.nhle.com/stats/rest/en'
const DEFAULT_GAME_TYPE_ID = 2

/**
 * @param {Date} [date]
 * @returns {string}
 */
export function getCurrentSeasonId(date = new Date()) {
    const currentYear = date.getFullYear()
    const currentMonth = date.getMonth()
    const startYear = currentMonth < 9 ? currentYear - 1 : currentYear
    return `${startYear}${startYear + 1}`
}

/**
 * @param {string} seasonId
 * @returns {string}
 */
export function formatSeasonId(seasonId) {
    return `${seasonId.slice(0, 4)}-${seasonId.slice(6, 8)}`
}

/**
 * @returns {string}
 */
export function getPlayerStatsDir() {
    return join(process.cwd(), 'static', 'data', 'player-stats')
}

/**
 * @returns {string}
 */
export function getRosterPath() {
    return join(process.cwd(), 'static', 'data', 'players', 'finnish-roster.json')
}

/**
 * @param {string} type
 * @param {string} seasonId
 * @returns {string}
 */
export function getStatsFilePath(type, seasonId) {
    return join(getPlayerStatsDir(), `${type}-${seasonId}.json`)
}

/**
 * @param {string} filePath
 * @returns {any}
 */
export function readJsonFileSync(filePath) {
    return JSON.parse(readFileSync(filePath, 'utf-8'))
}

/**
 * @param {string} filePath
 * @returns {Promise<any[]>}
 */
export async function readJsonArrayIfExists(filePath) {
    try {
        const parsed = JSON.parse(await readFile(filePath, 'utf-8'))
        return Array.isArray(parsed) ? parsed : []
    } catch (error) {
        const code =
            typeof error === 'object' && error !== null && 'code' in error ? error.code : undefined

        if (code !== 'ENOENT') {
            console.warn(`Could not load ${filePath}:`, error)
        }
        return []
    }
}

/**
 * @param {string} [seasonId]
 * @returns {{ seasonId: string, skaters: StatsPlayer[], goalies: StatsPlayer[] }}
 */
export function loadRegularSeasonStatsFromDisk(seasonId = getCurrentSeasonId()) {
    return {
        seasonId,
        skaters: readJsonFileSync(getStatsFilePath('skaters', seasonId)),
        goalies: readJsonFileSync(getStatsFilePath('goalies', seasonId)),
    }
}

/**
 * @param {string} [seasonId]
 * @returns {StatsPlayer[]}
 */
export function loadSkaterStatsFromDisk(seasonId = getCurrentSeasonId()) {
    return readJsonFileSync(getStatsFilePath('skaters', seasonId))
}

/**
 * @returns {RosterLookup}
 */
export function loadRosterLookupFromDisk() {
    return readJsonFileSync(getRosterPath())
}

/**
 * @param {StatsPlayer[]} players
 * @param {RosterLookup} rosterLookup
 * @param {Date} [asOfDate]
 * @returns {StatsPlayer[]}
 */
export function mergeRosterInfo(players, rosterLookup, asOfDate = new Date()) {
    return players.map((player) => {
        const rosterInfo =
            player.playerId === undefined || player.playerId === null
                ? null
                : rosterLookup[String(player.playerId)]

        if (!rosterInfo) {
            return { ...player }
        }

        /** @type {StatsPlayer} */
        const mergedPlayer = { ...player }
        const birthDate = rosterInfo.birthDate ?? player.birthDate

        if (birthDate !== undefined) {
            mergedPlayer.birthDate = birthDate
            mergedPlayer.age = asOfDate.getFullYear() - new Date(birthDate).getFullYear()
        }

        if (rosterInfo.heightInches !== undefined) {
            mergedPlayer.heightInches = rosterInfo.heightInches
        }

        if (rosterInfo.weightLbs !== undefined) {
            mergedPlayer.weightLbs = rosterInfo.weightLbs
        }

        if (rosterInfo.birthplace !== undefined) {
            mergedPlayer.birthplace = rosterInfo.birthplace
        }

        if (rosterInfo.headshot !== undefined) {
            mergedPlayer.headshot = rosterInfo.headshot
        }

        return mergedPlayer
    })
}

/**
 * @param {StatsApiUrlOptions} options
 * @returns {string}
 */
export function buildStatsApiUrl({
    statType,
    seasonId,
    gameTypeId = DEFAULT_GAME_TYPE_ID,
    sortProperty,
    sortDirection = 'ASC',
    limit,
}) {
    const resolvedLimit = limit ?? (statType === 'goalie' ? 100 : 500)
    const sort = encodeURIComponent(
        JSON.stringify([{ property: sortProperty, direction: sortDirection }])
    )
    const cayenneExp = encodeURIComponent(
        `nationalityCode="FIN" and gameTypeId=${gameTypeId} and seasonId=${seasonId}`
    )

    return `${NHL_STATS_BASE}/${statType}/summary?isAggregate=false&isGame=false&sort=${sort}&start=0&limit=${resolvedLimit}&cayenneExp=${cayenneExp}`
}

/**
 * @param {(input: string) => Promise<Response>} fetchFn
 * @param {StatsApiUrlOptions} options
 * @returns {Promise<StatsPlayer[]>}
 */
export async function fetchStats(fetchFn, options) {
    const response = await fetchFn(buildStatsApiUrl(options))

    if (!response.ok) {
        throw new Error(`Failed to fetch ${options.statType} stats: ${response.status}`)
    }

    const data = await response.json()
    return Array.isArray(data?.data) ? data.data : []
}

/**
 * @param {(input: string) => Promise<Response>} fetchFn
 * @param {string} [seasonId]
 * @param {SortDirection} [sortDirection]
 * @returns {Promise<{ seasonId: string, skaters: StatsPlayer[], goalies: StatsPlayer[] }>}
 */
export async function fetchRegularSeasonStats(
    fetchFn,
    seasonId = getCurrentSeasonId(),
    sortDirection = 'ASC'
) {
    const [skaters, goalies] = await Promise.all([
        fetchStats(fetchFn, {
            statType: 'skater',
            seasonId,
            gameTypeId: 2,
            sortProperty: sortDirection === 'DESC' ? 'points' : 'skaterFullName',
            sortDirection,
            limit: 500,
        }),
        fetchStats(fetchFn, {
            statType: 'goalie',
            seasonId,
            gameTypeId: 2,
            sortProperty: sortDirection === 'DESC' ? 'wins' : 'goalieFullName',
            sortDirection,
            limit: 100,
        }),
    ])

    return { seasonId, skaters, goalies }
}

/**
 * @param {string} [seasonId]
 * @returns {Promise<{ seasonId: string, season: string, skaters: any[], goalies: any[] }>}
 */
export async function loadPlayoffStatsFromDisk(seasonId = getCurrentSeasonId()) {
    const [skaters, goalies] = await Promise.all([
        readJsonArrayIfExists(getStatsFilePath('playoff-skaters', seasonId)),
        readJsonArrayIfExists(getStatsFilePath('playoff-goalies', seasonId)),
    ])

    return {
        seasonId,
        season: formatSeasonId(seasonId),
        skaters: skaters.map((player) => ({
            playerId: player.playerId,
            name: player.skaterFullName,
            team: player.teamAbbrevs,
            gamesPlayed: player.gamesPlayed,
            goals: player.goals,
            assists: player.assists,
            points: player.points,
        })),
        goalies: goalies.map((goalie) => ({
            playerId: goalie.playerId,
            name: goalie.goalieFullName,
            team: goalie.teamAbbrevs,
            gamesPlayed: goalie.gamesPlayed,
            wins: goalie.wins,
            savePct: goalie.savePct,
        })),
    }
}
