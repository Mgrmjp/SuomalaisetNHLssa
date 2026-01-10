import { fetchLocalJSON } from '$lib/utils/apiHelpers.js'
import logger from '$lib/utils/logger.js'
import {
    getTeamConferenceAndDivision,
    initializeStandings,
    updateRankings,
} from '$lib/utils/nhlStructure.js'
import teamMapping from '$lib/utils/teamMapping.js'

/** Average power play opportunities per game in NHL */
const AVG_POWER_PLAY_OPPORTUNITIES_PER_GAME = 3.2

/** Average penalty kill times shorthanded per game in NHL */
const AVG_PENALTY_KILL_TIMES_PER_GAME = 3.5

// Prepopulated game dates - all dates we have data for
// Prepopulated game dates - all dates we have data for
// This will be populated from /data/games_manifest.json
let prepopulatedDates = []

// Cache for fetched game data to avoid repeated fetches
const gameDataCache = new Map()

// Cache object for the manifest
let gamesManifestCache = null

async function loadGameDataForDate(date) {
    if (gameDataCache.has(date)) {
        return gameDataCache.get(date)
    }
    const data = await fetchLocalJSON(`/data/prepopulated/games/${date}.json`)
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
        this.cache = new Map()
        this.cacheTimeout = 5 * 60 * 1000 // 5 minutes
    }

    /**
     * Calculate season standings from existing game data
     * @param {string} seasonStart - Season start date (YYYY-MM-DD)
     * @returns {Promise<object>} Complete standings data
     */
    async calculateSeasonStandings(seasonStart = DEFAULT_SEASON_START) {
        // Ensure we have the list of available dates
        await this.fetchAvailableDates()

        // Clamp seasonStart to our earliest available prepopulated date
        const effectiveSeasonStart =
            prepopulatedDates.find((d) => d >= seasonStart) || EARLIEST_PREPOP_DATE

        const cacheKey = `standings_${seasonStart}`
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
            console.log('📊 Initialized standings structure:', Object.keys(standings))

            // Get available game dates from season start to today
            const gameDates = await this.getGameDatesInRange(effectiveSeasonStart)
            console.log(`📊 Processing ${gameDates.length} game dates from ${effectiveSeasonStart}`)

            // Process each game date
            // Parallelize fetching of game data
            const gamesDataPromises = gameDates.map((date) =>
                this.getGamesDataForDate(date)
                    .then((data) => ({ date, data }))
                    .catch((error) => ({ date, error }))
            )

            const results = await Promise.all(gamesDataPromises)

            // Process the fetched data sequentially to ensure data consistency
            for (const result of results) {
                if (result.error) {
                    logger.log(`⚠️ No game data for ${result.date}: ${result.error.message}`)
                    continue
                }

                const gamesData = result.data
                if (!gamesData || !gamesData.games || gamesData.games.length === 0) {
                    continue
                }

                for (const game of gamesData.games) {
                    this.processGame(game, standings)
                }
            }

            console.log('📊 Standings after processing games:', standings)

            // Calculate final rankings
            updateRankings(standings)

            console.log('📊 Final standings structure:', {
                eastern: Object.keys(standings.eastern || {}),
                western: Object.keys(standings.western || {}),
            })

            // Cache the results
            this.cache.set(cacheKey, {
                data: standings,
                timestamp: Date.now(),
            })

            logger.log('✅ Standings calculation complete')
            return standings
        } catch (error) {
            logger.log(`❌ Error calculating standings: ${error.message}`)
            throw error
        }
    }

    /**
     * Get available game dates in a date range
     * @param {string} startDate - Start date (YYYY-MM-DD)
     * @param {string} endDate - End date (YYYY-MM-DD), defaults to today
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

            if (!gamesData || !gamesData.games || gamesData.games.length === 0) {
                return // No games on this date
            }

            for (const game of gamesData.games) {
                this.processGame(game, standings)
            }
        } catch (error) {
            // Log error but continue processing other dates
            logger.log(`⚠️ No game data for ${date}: ${error.message}`)
        }
    }

    /**
     * Get games data for a specific date
     * @param {string} date - Date (YYYY-MM-DD)
     * @returns {Promise<object>} Games data object
     */
    async getGamesDataForDate(date) {
        return await loadGameDataForDate(date)
    }

    /**
     * Process a single game and update standings
     * @param {object} game - Game object
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
     * Get team info and stats objects for both teams in a game
     * @param {string} homeTeam - Home team abbreviation
     * @param {string} awayTeam - Away team abbreviation
     * @param {object} standings - Standings object
     * @returns {object} Object containing team info and stats
     */
    getGameTeamsInfo(homeTeam, awayTeam, standings) {
        const homeInfo = getTeamConferenceAndDivision(homeTeam)
        const awayInfo = getTeamConferenceAndDivision(awayTeam)

        if (!homeInfo || !awayInfo) {
            logger.log(`⚠️ Unknown team in game: ${homeTeam} vs ${awayTeam}`)
            return { homeInfo: null, awayInfo: null, homeTeamStats: null, awayTeamStats: null }
        }

        const homeTeamStats = standings[homeInfo.conference][homeInfo.division].find(
            (team) => team.team === homeTeam
        )
        const awayTeamStats = standings[awayInfo.conference][awayInfo.division].find(
            (team) => team.team === awayTeam
        )

        if (!homeTeamStats || !awayTeamStats) {
            logger.log(`⚠️ Team not found in standings: ${homeTeam} or ${awayTeam}`)
            return { homeInfo, awayInfo, homeTeamStats: null, awayTeamStats: null }
        }

        return { homeInfo, awayInfo, homeTeamStats, awayTeamStats }
    }

    /**
     * Update games played count for both teams
     * @param {object} homeTeamStats - Home team stats
     * @param {object} awayTeamStats - Away team stats
     */
    updateGamesPlayed(homeTeamStats, awayTeamStats) {
        homeTeamStats.gamesPlayed++
        awayTeamStats.gamesPlayed++
    }

    /**
     * Update goals for/after for both teams
     * @param {object} homeTeamStats - Home team stats
     * @param {object} awayTeamStats - Away team stats
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
     * @param {object} homeTeamStats - Home team stats
     * @param {object} awayTeamStats - Away team stats
     */
    updateHomeAwayRecords(homeTeamStats, awayTeamStats) {
        homeTeamStats.home.games++
        awayTeamStats.away.games++
    }

    /**
     * Update win/loss records and points based on game result
     * @param {object} homeTeamStats - Home team stats
     * @param {object} awayTeamStats - Away team stats
     * @param {number} homeScore - Home team score
     * @param {number} awayScore - Away team score
     */
    updateGameResult(homeTeamStats, awayTeamStats, homeScore, awayScore, game) {
        const isOT = game.period > 3 || game.isOT === true || game.isSO === true;

        if (homeScore > awayScore) {
            // Home team wins
            this.applyWin(homeTeamStats, homeTeamStats.home)
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
            this.applyWin(awayTeamStats, awayTeamStats.away)
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
     * @param {object} teamStats - Team stats to update
     * @param {object} locationStats - Home or away stats to update
     */
    applyWin(teamStats, locationStats) {
        teamStats.wins++
        locationStats.wins++
        teamStats.points += 2
        teamStats.regulationWins++
        teamStats.regulationPlusOTWins++
    }

    /**
     * Apply loss statistics to a team
     * @param {object} teamStats - Team stats to update
     * @param {object} locationStats - Home or away stats to update
     */
    applyLoss(teamStats, locationStats) {
        teamStats.losses++
        locationStats.losses++
    }

    /**
     * Apply overtime/shootout loss statistics to a team
     * @param {object} teamStats - Team stats to update
     * @param {object} locationStats - Home or away stats to update
     */
    applyOTLoss(teamStats, locationStats) {
        teamStats.overtimeLosses++
        locationStats.ot = (locationStats.ot || 0) + 1
        teamStats.points += 1
    }

    /**
     * Update derived statistics (goal differential, points percentage)
     * @param {object} homeTeamStats - Home team stats
     * @param {object} awayTeamStats - Away team stats
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
     * @param {object} teamStats - Team stats object
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

        const [, type, countStr] = match
        const count = parseInt(countStr, 10)

        if (type === result) {
            teamStats.streak = `${result}${count + 1}`
        } else {
            teamStats.streak = `${result}1`
        }
    }

    /**
     * Record a game result in the last 10 games tracking
     * @param {object} teamStats - Team stats object
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
     * @param {object} teamStats - Team stats object
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
        return teamMapping[teamAbbrev] || teamAbbrev
    }

    /**
     * Update special teams statistics
     * @param {object} teamStats - Team stats object
     */
    updateSpecialTeamsStats(teamStats) {
        this.initializeSpecialTeamsStats(teamStats)

        if (!teamStats.hasSpecialTeamsData) {
            const gamesPlayed = teamStats.gamesPlayed || 1

            teamStats.powerPlayOpportunities = Math.round(
                gamesPlayed * AVG_POWER_PLAY_OPPORTUNITIES_PER_GAME
            )
            teamStats.powerPlayGoals = Math.round(
                (teamStats.powerPlayOpportunities * (18 + Math.random() * 10)) / 100
            ) // 18-28% PP%

            teamStats.penaltyKillTimesShorthanded = Math.round(
                gamesPlayed * AVG_PENALTY_KILL_TIMES_PER_GAME
            )
            teamStats.penaltyKillGoalsAllowed = Math.round(
                (teamStats.penaltyKillTimesShorthanded * (15 + Math.random() * 8)) / 100
            ) // 15-23% PK%

            teamStats.hasSpecialTeamsData = true
        }
    }

    /**
     * Initialize special teams stats if they don't exist
     * @param {object} teamStats - Team stats object
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
     */
    async fetchAvailableDates() {
        // Return if already populated (and valid)
        if (prepopulatedDates.length > 0 && gamesManifestCache) {
            return prepopulatedDates
        }

        try {
            logger.log('📊 Fetching games manifest...')
            const manifest = await fetchLocalJSON('/data/games_manifest.json')
            
            if (manifest && manifest.games && Array.isArray(manifest.games)) {
                gamesManifestCache = manifest
                prepopulatedDates = manifest.games.sort()
                logger.log(`✅ Loaded ${prepopulatedDates.length} game dates from manifest`)
            } else {
                logger.log('⚠️ Failed to load games manifest or invalid format')
                // Fallback to minimal set or keep empty?
                // If it fails, prepopulatedDates remains empty or whatever it was
            }
        } catch (error) {
            logger.log(`❌ Error fetching games manifest: ${error.message}`)
        }
        
        return prepopulatedDates
    }
}
