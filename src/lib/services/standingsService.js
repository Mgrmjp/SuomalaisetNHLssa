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
const prepopulatedDates = [
    '2025-09-30',
    '2025-10-01',
    '2025-10-02',
    '2025-10-03',
    '2025-10-04',
    '2025-10-05',
    '2025-10-06',
    '2025-10-07',
    '2025-10-08',
    '2025-10-09',
    '2025-10-10',
    '2025-10-11',
    '2025-10-12',
    '2025-10-13',
    '2025-10-14',
    '2025-10-15',
    '2025-10-16',
    '2025-10-17',
    '2025-10-18',
    '2025-10-19',
    '2025-10-20',
    '2025-10-21',
    '2025-10-22',
    '2025-10-23',
    '2025-10-24',
    '2025-10-25',
    '2025-10-26',
    '2025-10-27',
    '2025-10-28',
    '2025-10-29',
    '2025-10-30',
    '2025-10-31',
    '2025-11-01',
    '2025-11-02',
    '2025-11-03',
    '2025-11-04',
    '2025-11-05',
    '2025-11-06',
    '2025-11-07',
    '2025-11-08',
    '2025-11-09',
    '2025-11-10',
    '2025-11-11',
    '2025-11-12',
    '2025-11-13',
    '2025-11-14',
    '2025-11-15',
    '2025-11-16',
    '2025-11-17',
    '2025-11-18',
    '2025-11-19',
    '2025-11-20',
    '2025-11-21',
    '2025-11-22',
    '2025-11-23',
    '2025-11-24',
    '2025-11-25',
    '2025-11-26',
    '2025-11-27',
    '2025-11-28',
    '2025-11-29',
    '2025-11-30',
    '2025-12-01',
    '2025-12-02',
    '2025-12-03',
    '2025-12-04',
    '2025-12-05',
    '2025-12-06',
    '2025-12-07',
    '2025-12-08',
    '2025-12-09',
    '2025-12-10',
    '2025-12-11',
    '2025-12-12',
    '2025-12-13',
    '2025-12-14',
    '2025-12-15',
    '2025-12-16',
    '2025-12-17',
    '2025-12-18',
    '2025-12-19',
    '2025-12-20',
    '2025-12-21',
    '2025-12-22',
    '2025-12-23',
    '2025-12-24',
    '2025-12-25',
    '2025-12-26',
    '2025-12-27',
    '2025-12-28',
    '2025-12-29',
    '2025-12-30',
    '2025-12-31',
]

// Cache for fetched game data to avoid repeated fetches
const gameDataCache = new Map()

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

const EARLIEST_PREPOP_DATE = prepopulatedDates[0] || '2025-09-30'
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
            for (const date of gameDates) {
                await this.processGamesForDate(date, standings)
            }

            console.log('📊 Standings after processing games:', standings)

            // Calculate final rankings
            updateRankings(standings)

            console.log('📊 Final standings structure:', {
                eastern: Object.keys(standings.eastern || {}),
                western: Object.keys(standings.western || {})
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
        // Only process completed games
        if (game.gameState !== 'OFF' && game.gameState !== 'FINAL') {
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
        this.updateGameResult(homeTeamStats, awayTeamStats, homeScore, awayScore)
        this.updateDerivedStats(homeTeamStats, awayTeamStats)
        this.updateLast10(homeTeamStats)
        this.updateLast10(awayTeamStats)
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
    updateGameResult(homeTeamStats, awayTeamStats, homeScore, awayScore) {
        if (homeScore > awayScore) {
            // Home team wins
            this.applyWin(homeTeamStats, homeTeamStats.home)
            this.applyLoss(awayTeamStats, awayTeamStats.away)
            this.updateStreak(homeTeamStats, 'W')
            this.updateStreak(awayTeamStats, 'L')
        } else if (awayScore > homeScore) {
            // Away team wins
            this.applyWin(awayTeamStats, awayTeamStats.away)
            this.applyLoss(homeTeamStats, homeTeamStats.home)
            this.updateStreak(awayTeamStats, 'W')
            this.updateStreak(homeTeamStats, 'L')
        } else {
            // Tie (shouldn't happen in modern NHL)
            homeTeamStats.points += 1
            awayTeamStats.points += 1
            this.updateStreak(homeTeamStats, 'OT')
            this.updateStreak(awayTeamStats, 'OT')
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

        if (!currentStreak) {
            teamStats.streak = `${result}1`
            return
        }

        const [type, count] = currentStreak.split('')

        if (type === result) {
            teamStats.streak = `${result}${parseInt(count, 10) + 1}`
        } else {
            teamStats.streak = `${result}1`
        }
    }

    /**
     * Update last 10 games record (simplified implementation)
     * @param {object} teamStats - Team stats object
     */
    updateLast10(teamStats) {
        // This is a simplified version
        // In a full implementation, you'd track the actual last 10 games
        const winPercentage = teamStats.wins / Math.max(teamStats.gamesPlayed, 1)
        const wins10 = Math.min(10, Math.round(winPercentage * 10))
        const losses10 = Math.min(10 - wins10, teamStats.losses)
        const ot10 = Math.min(10 - wins10 - losses10, teamStats.overtimeLosses)

        teamStats.last10 = `${wins10}-${losses10}-${ot10}`
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
        logger.log('📊 Standings cache cleared')
    }
}
