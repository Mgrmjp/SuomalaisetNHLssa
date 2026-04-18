import { fetchLocalJSON } from '$lib/utils/apiHelpers.js'
import logger from '$lib/utils/logger.js'
import {
    getTeamConferenceAndDivision,
    initializeStandings,
    updateRankings,
} from '$lib/utils/nhlStructure.js'
import teamMapping from '$lib/utils/teamMapping.js'

/** @typedef {{ r: number, g: number, b: number }} RGB */

/**
 * @typedef {object} GameData
 * @property {string} date
 * @property {object} [error]
 * @property {{ games: Game[] }} [data]
 */

/**
 * @typedef {object} Game
 * @property {string} gameState
 * @property {number} gameType
 * @property {string} homeTeam
 * @property {string} awayTeam
 * @property {number} homeScore
 * @property {number} awayScore
 * @property {number} period
 * @property {boolean} [isOT]
 * @property {boolean} [isSO]
 */

/**
 * @typedef {object} HomeAwayStats
 * @property {number} games
 * @property {number} wins
 * @property {number} losses
 * @property {number} ot
 */

/**
 * @typedef {object} TeamStats
 * @property {string} team
 * @property {number} gamesPlayed
 * @property {number} wins
 * @property {number} losses
 * @property {number} overtimeLosses
 * @property {number} points
 * @property {number} goalsFor
 * @property {number} goalsAgainst
 * @property {number} goalDifferential
 * @property {number} pointsPercentage
 * @property {number} regulationWins
 * @property {number} regulationPlusOTWins
 * @property {string} streak
 * @property {string} last10
 * @property {string[]} last10Results
 * @property {HomeAwayStats} home
 * @property {HomeAwayStats} away
 * @property {boolean} hasSpecialTeamsData
 * @property {number} powerPlayGoals
 * @property {number} powerPlayOpportunities
 * @property {number} penaltyKillGoalsAllowed
 * @property {number} penaltyKillTimesShorthanded
 */

/** @type {string[]} */
let prepopulatedDates = []
/** @type {object|null} */
let gamesManifestCache = null

// Cache for fetched game data to avoid repeated fetches
/** @type {Map<string, object>} */
const gameDataCache = new Map()

/**
 * @param {string} date
 * @returns {Promise<{ games: Game[] } | null>}
 */
async function loadGameDataForDate(date) {
    if (gameDataCache.has(date)) {
        return /** @type {{ games: Game[] } | null} */ (gameDataCache.get(date) || null)
    }
    const data = /** @type {{ games: Game[] } | null} */ (
        await fetchLocalJSON(`/data/prepopulated/games/${date}.json`)
    )
    if (data) {
        gameDataCache.set(date, data)
    }
    return data
}

const EARLIEST_PREPOP_DATE = '2025-09-30'
// 2025-26 NHL regular season starts October 7, 2025
const DEFAULT_SEASON_START = '2025-10-07'

/**
 * Service for calculating and managing NHL standings
 */
export class StandingsService {
    constructor() {
        /** @type {Map<string, { data: object, timestamp: number }>} */
        this.cache = new Map()
        this.cacheTimeout = 5 * 60 * 1000 // 5 minutes
    }

    /**
     * Calculate season standings from existing game data
     * @param {string} [seasonStart=DEFAULT_SEASON_START] - Season start date (YYYY-MM-DD)
     * @returns {Promise<object>} Complete standings data
     */
    async calculateSeasonStandings(seasonStart = DEFAULT_SEASON_START) {
        // Ensure we have the list of available dates
        await this.fetchAvailableDates()

        // Clamp seasonStart to our earliest available prepopulated date
        const effectiveSeasonStart =
            prepopulatedDates.find((d) => d >= seasonStart) || EARLIEST_PREPOP_DATE

        const cacheKey = `standings_${effectiveSeasonStart}`
        const cached = this.cache.get(cacheKey)

        if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
            logger.log('📊 Returning cached standings data')
            return cached.data
        }

        logger.log(
            `📊 Calculating season standings from game data (start=${effectiveSeasonStart}, dates=${prepopulatedDates.length})...`
        )

        try {
            // Initialize standings structure
            const standings = initializeStandings()
            logger.debug('📊 Initialized standings structure')

            // Get available game dates from season start to today
            const gameDates = await this.getGameDatesInRange(effectiveSeasonStart)
            logger.debug(`📊 Processing ${gameDates.length} game dates`)

            // Process each game date
            // Parallelize fetching of game data
            const gamesDataPromises = gameDates.map((date) =>
                this.getGamesDataForDate(date)
                    .then((/** @type {{ games: Game[] } | null} */ data) => ({
                        date,
                        data: data || undefined,
                    }))
                    .catch((/** @type {unknown} */ error) => ({
                        date,
                        error:
                            typeof error === 'object' && error && 'message' in error
                                ? error
                                : { message: String(error) },
                    }))
            )

            const results = await Promise.all(gamesDataPromises)

            // Process the fetched data sequentially to ensure data consistency
            for (const result of results) {
                if ('error' in result && result.error) {
                    logger.log(`⚠️ No game data for ${result.date}: ${result.error.message}`)
                    continue
                }

                const gamesData =
                    'data' in result ? /** @type {{ games: Game[] }} */ (result.data) : null
                if (!gamesData || !gamesData.games || gamesData.games.length === 0) {
                    continue
                }

                for (const game of gamesData.games) {
                    this.processGame(game, standings)
                }
            }

            // Calculate final rankings
            updateRankings(standings)

            logger.debug('📊 Final standings structure calculated')

            // Cache the results
            this.cache.set(cacheKey, {
                data: standings,
                timestamp: Date.now(),
            })

            logger.log('✅ Standings calculation complete')
            return standings
        } catch (/** @type {unknown} */ error) {
            const msg = error instanceof Error ? error.message : String(error)
            logger.log(`❌ Error calculating standings: ${msg}`)
            throw error
        }
    }

    /**
     * Get available game dates in a date range
     * @param {string} startDate - Start date (YYYY-MM-DD)
     * @param {string|null} [endDate=null] - End date (YYYY-MM-DD), defaults to today
     * @returns {Promise<string[]>} Array of dates with games
     */
    async getGameDatesInRange(startDate, endDate = null) {
        // Ensure dates are loaded
        if (prepopulatedDates.length === 0) {
            await this.fetchAvailableDates()
        }

        return prepopulatedDates
            .filter((date) => (!startDate || date >= startDate) && (!endDate || date <= endDate))
            .sort()
    }

    /**
     * Process all games for a specific date
     * @param {string} date - Date (YYYY-MM-DD)
     * @param {object} standings - Standings object to update
     */
    async processGamesForDate(date, standings) {
        try {
            // Import games data dynamically to avoid bundling issues
            const gamesData = await this.getGamesDataForDate(date)

            if (
                !gamesData ||
                !(/** @type {any} */ (gamesData).games) ||
                /** @type {{ games: Game[] }} */ (gamesData).games.length === 0
            ) {
                return // No games on this date
            }

            for (const game of /** @type {{ games: Game[] }} */ (gamesData).games) {
                this.processGame(game, standings)
            }
        } catch (/** @type {unknown} */ error) {
            // Log error but continue processing other dates
            const msg = error instanceof Error ? error.message : String(error)
            logger.log(`⚠️ No game data for ${date}: ${msg}`)
        }
    }

    /**
     * Get games data for a specific date
     * @param {string} date - Date (YYYY-MM-DD)
     * @returns {Promise<{ games: Game[] } | null>} Games data object
     */
    async getGamesDataForDate(date) {
        return await loadGameDataForDate(date)
    }

    /**
     * Process a single game and update standings
     * @param {Game} game - Game object
     * @param {object} standings - Standings object to update
     */
    processGame(game, standings) {
        // Exclude future games (FUT) - include all completed game states
        if (game.gameState === 'FUT') {
            return
        }

        // Only process regular season games (gameType: 1=preseason, 2=regular season, 3=playoffs)
        if (game.gameType !== 2) {
            return
        }

        const homeTeam = game.homeTeam
        const awayTeam = game.awayTeam
        const homeScore = game.homeScore || 0
        const awayScore = game.awayScore || 0

        const {
            homeInfo: _homeInfo,
            awayInfo: _awayInfo,
            homeTeamStats,
            awayTeamStats,
        } = this.getGameTeamsInfo(homeTeam, awayTeam, standings)

        if (!homeTeamStats || !awayTeamStats) {
            return
        }

        this.updateGamesPlayed(homeTeamStats, awayTeamStats)
        this.updateGoalsStats(homeTeamStats, awayTeamStats, homeScore, awayScore)
        this.updateHomeAwayRecords(homeTeamStats, awayTeamStats)
        this.updateGameResult(homeTeamStats, awayTeamStats, homeScore, awayScore, game)
        this.updateDerivedStats(homeTeamStats, awayTeamStats)
        this.updateSpecialTeamsStats(homeTeamStats)
        this.updateSpecialTeamsStats(awayTeamStats)
    }

    /**
     * @typedef {{ conference: string, division: string }} ConferenceDivisionInfo
     */

    /**
     * Get team info and stats objects for both teams in a game
     * @param {string} homeTeam - Home team abbreviation
     * @param {string} awayTeam - Away team abbreviation
     * @param {any} standings - Standings object
     * @returns {{ homeInfo: ConferenceDivisionInfo|null, awayInfo: ConferenceDivisionInfo|null, homeTeamStats: TeamStats|null, awayTeamStats: TeamStats|null }}
     */
    getGameTeamsInfo(homeTeam, awayTeam, standings) {
        const homeInfo = /** @type {ConferenceDivisionInfo|null} */ (
            getTeamConferenceAndDivision(homeTeam)
        )
        const awayInfo = /** @type {ConferenceDivisionInfo|null} */ (
            getTeamConferenceAndDivision(awayTeam)
        )

        if (!homeInfo || !awayInfo) {
            logger.log(`⚠️ Unknown team in game: ${homeTeam} vs ${awayTeam}`)
            return { homeInfo: null, awayInfo: null, homeTeamStats: null, awayTeamStats: null }
        }

        /** @type {TeamStats|undefined} */
        const homeTeamStats = /** @type {any} */ (standings)[homeInfo.conference][
            homeInfo.division
        ].find((/** @type {TeamStats} */ team) => team.team === homeTeam)
        /** @type {TeamStats|undefined} */
        const awayTeamStats = /** @type {any} */ (standings)[awayInfo.conference][
            awayInfo.division
        ].find((/** @type {TeamStats} */ team) => team.team === awayTeam)

        if (!homeTeamStats || !awayTeamStats) {
            logger.log(`⚠️ Team not found in standings: ${homeTeam} or ${awayTeam}`)
            return { homeInfo, awayInfo, homeTeamStats: null, awayTeamStats: null }
        }

        return { homeInfo, awayInfo, homeTeamStats, awayTeamStats }
    }

    /**
     * Update games played count for both teams
     * @param {TeamStats} homeTeamStats - Home team stats
     * @param {TeamStats} awayTeamStats - Away team stats
     */
    updateGamesPlayed(homeTeamStats, awayTeamStats) {
        homeTeamStats.gamesPlayed++
        awayTeamStats.gamesPlayed++
    }

    /**
     * Update goals for/after for both teams
     * @param {TeamStats} homeTeamStats - Home team stats
     * @param {TeamStats} awayTeamStats - Away team stats
     * @param {number} homeScore - Home team score
     * @param {number} awayScore - Away team score
     */
    updateGoalsStats(homeTeamStats, awayTeamStats, homeScore, awayScore) {
        homeTeamStats.goalsFor += homeScore
        homeTeamStats.goalsAgainst += awayScore
        awayTeamStats.goalsFor += awayScore
        awayTeamStats.goalsAgainst += homeScore
    }

    /**
     * Update home/away records
     * @param {TeamStats} homeTeamStats - Home team stats
     * @param {TeamStats} awayTeamStats - Away team stats
     */
    updateHomeAwayRecords(homeTeamStats, awayTeamStats) {
        homeTeamStats.home.games++
        awayTeamStats.away.games++
    }

    /**
     * Update win/loss records and points based on game result
     * @param {TeamStats} homeTeamStats - Home team stats
     * @param {TeamStats} awayTeamStats - Away team stats
     * @param {number} homeScore - Home team score
     * @param {number} awayScore - Away team score
     * @param {Game} game - Game object
     */
    updateGameResult(homeTeamStats, awayTeamStats, homeScore, awayScore, game) {
        const isOT = game.period > 3 || game.isOT === true || game.isSO === true

        if (homeScore > awayScore) {
            // Home team wins
            this.applyWin(homeTeamStats, homeTeamStats.home, isOT)
            if (isOT) {
                this.applyOTLoss(awayTeamStats, awayTeamStats.away)
                this.updateStreak(homeTeamStats, 'W')
                this.updateStreak(awayTeamStats, 'OT')
                this.recordLast10Result(homeTeamStats, 'W')
                this.recordLast10Result(awayTeamStats, 'OT')
            } else {
                this.applyLoss(awayTeamStats, awayTeamStats.away)
                this.updateStreak(homeTeamStats, 'W')
                this.updateStreak(awayTeamStats, 'L')
                this.recordLast10Result(homeTeamStats, 'W')
                this.recordLast10Result(awayTeamStats, 'L')
            }
        } else if (awayScore > homeScore) {
            // Away team wins
            this.applyWin(awayTeamStats, awayTeamStats.away, isOT)
            if (isOT) {
                this.applyOTLoss(homeTeamStats, homeTeamStats.home)
                this.updateStreak(awayTeamStats, 'W')
                this.updateStreak(homeTeamStats, 'OT')
                this.recordLast10Result(awayTeamStats, 'W')
                this.recordLast10Result(homeTeamStats, 'OT')
            } else {
                this.applyLoss(homeTeamStats, homeTeamStats.home)
                this.updateStreak(awayTeamStats, 'W')
                this.updateStreak(homeTeamStats, 'L')
                this.recordLast10Result(awayTeamStats, 'W')
                this.recordLast10Result(homeTeamStats, 'L')
            }
        } else {
            // Tie (shouldn't happen in modern NHL, but handle just in case)
            homeTeamStats.points += 1
            awayTeamStats.points += 1
            this.updateStreak(homeTeamStats, 'OT')
            this.updateStreak(awayTeamStats, 'OT')
            this.recordLast10Result(homeTeamStats, 'OT')
            this.recordLast10Result(awayTeamStats, 'OT')
        }
    }

    /**
     * Apply win statistics to a team
     * @param {TeamStats} teamStats - Team stats to update
     * @param {HomeAwayStats} locationStats - Home or away stats to update
     * @param {boolean} [isOT=false]
     */
    applyWin(teamStats, locationStats, isOT = false) {
        teamStats.wins++
        locationStats.wins++
        teamStats.points += 2
        if (!isOT) {
            teamStats.regulationWins++
        }
        teamStats.regulationPlusOTWins++
    }

    /**
     * Apply loss statistics to a team
     * @param {TeamStats} teamStats - Team stats to update
     * @param {HomeAwayStats} locationStats - Home or away stats to update
     */
    applyLoss(teamStats, locationStats) {
        teamStats.losses++
        locationStats.losses++
    }

    /**
     * Apply overtime/shootout loss statistics to a team
     * @param {TeamStats} teamStats - Team stats to update
     * @param {HomeAwayStats} locationStats - Home or away stats to update
     */
    applyOTLoss(teamStats, locationStats) {
        teamStats.overtimeLosses++
        locationStats.ot = (locationStats.ot || 0) + 1
        teamStats.points += 1
    }

    /**
     * Update derived statistics (goal differential, points percentage)
     * @param {TeamStats} homeTeamStats - Home team stats
     * @param {TeamStats} awayTeamStats - Away team stats
     */
    updateDerivedStats(homeTeamStats, awayTeamStats) {
        homeTeamStats.goalDifferential = homeTeamStats.goalsFor - homeTeamStats.goalsAgainst
        awayTeamStats.goalDifferential = awayTeamStats.goalsFor - awayTeamStats.goalsAgainst

        homeTeamStats.pointsPercentage = Number(
            (homeTeamStats.points / (homeTeamStats.gamesPlayed * 2)).toFixed(3)
        )
        awayTeamStats.pointsPercentage = Number(
            (awayTeamStats.points / (awayTeamStats.gamesPlayed * 2)).toFixed(3)
        )
    }

    /**
     * Update team streak
     * @param {TeamStats} teamStats - Team stats object
     * @param {string} result - 'W', 'L', or 'OT'
     */
    updateStreak(teamStats, result) {
        const currentStreak = teamStats.streak

        if (!currentStreak || currentStreak.length < 2) {
            teamStats.streak = `${result}1`
            return
        }

        // Use regex to properly parse streak type and count (handles double-digit streaks and OT)
        // Match W#, L#, or OT# where # is any number
        const match = currentStreak.match(/^(W|L|OT)(\d+)$/)
        if (!match) {
            // Corrupted streak format, reset to new streak
            teamStats.streak = `${result}1`
            return
        }

        const type = /** @type {string} */ (match[1])
        const count = parseInt(/** @type {string} */ (match[2]), 10)

        if (type === result) {
            teamStats.streak = `${result}${count + 1}`
        } else {
            teamStats.streak = `${result}1`
        }
    }

    /**
     * Record a game result in the last 10 games tracking
     * @param {TeamStats} teamStats - Team stats object
     * @param {string} result - 'W', 'L', or 'OT'
     */
    recordLast10Result(teamStats, result) {
        teamStats.last10Results.push(result)
        // Keep only the most recent 10 results
        if (teamStats.last10Results.length > 10) {
            teamStats.last10Results.shift()
        }
        this.updateLast10(teamStats)
    }

    /**
     * Update last 10 games record from actual game results
     * @param {TeamStats} teamStats - Team stats object
     */
    updateLast10(teamStats) {
        const results = teamStats.last10Results
        const wins = results.filter((r) => r === 'W').length
        const losses = results.filter((r) => r === 'L').length
        const otLosses = results.filter((r) => r === 'OT').length

        teamStats.last10 = `${wins}-${losses}-${otLosses}`
    }

    /**
     * Get team full name from abbreviation
     * @param {string} teamAbbrev - Team abbreviation
     * @returns {string} Full team name
     */
    getTeamFullName(teamAbbrev) {
        return /** @type {any} */ (teamMapping)[teamAbbrev] || teamAbbrev
    }

    /**
     * Update special teams statistics
     * @param {TeamStats} teamStats - Team stats object
     */
    updateSpecialTeamsStats(teamStats) {
        this.initializeSpecialTeamsStats(teamStats)

        if (!teamStats.hasSpecialTeamsData) {
            teamStats.hasSpecialTeamsData = true
        }
    }

    /**
     * Initialize special teams stats if they don't exist
     * @param {TeamStats} teamStats - Team stats object
     */
    initializeSpecialTeamsStats(teamStats) {
        teamStats.powerPlayGoals ??= 0
        teamStats.powerPlayOpportunities ??= 0
        teamStats.penaltyKillGoalsAllowed ??= 0
        teamStats.penaltyKillTimesShorthanded ??= 0
    }

    /**
     * Clear cache
     */
    clearCache() {
        this.cache.clear()
        gamesManifestCache = null
        prepopulatedDates = []
        logger.log('📊 Standings cache cleared')
    }

    /**
     * Fetch the list of available game dates from the server
     * @returns {Promise<string[]>}
     */
    async fetchAvailableDates() {
        // Return if already populated (and valid)
        if (prepopulatedDates.length > 0 && gamesManifestCache) {
            return prepopulatedDates
        }

        try {
            logger.log('📊 Fetching games manifest...')
            const timestamp = Date.now()
            const manifest = await fetchLocalJSON(`/data/games_manifest.json?t=${timestamp}`)

            if (
                manifest &&
                /** @type {any} */ (manifest).games &&
                Array.isArray(/** @type {any} */ (manifest).games)
            ) {
                gamesManifestCache = manifest
                prepopulatedDates = /** @type {{ games: string[] }} */ (manifest).games.sort()
                logger.log(`✅ Loaded ${prepopulatedDates.length} game dates from manifest`)
            } else {
                logger.log('⚠️ Failed to load games manifest or invalid format')
                // Fallback to minimal set or keep empty?
                // If it fails, prepopulatedDates remains empty or whatever it was
            }
        } catch (/** @type {unknown} */ error) {
            const msg = error instanceof Error ? error.message : String(error)
            logger.log(`❌ Error fetching games manifest: ${msg}`)
        }

        return prepopulatedDates
    }
}
