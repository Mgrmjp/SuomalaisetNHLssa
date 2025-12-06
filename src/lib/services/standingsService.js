import { initializeStandings, updateRankings, getTeamConferenceAndDivision } from '$lib/utils/nhlStructure.js'
import teamMapping from '$lib/utils/teamMapping.js'
import logger from '$lib/utils/logger.js'

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
	async calculateSeasonStandings(seasonStart = '2025-10-01') {
		const cacheKey = `standings_${seasonStart}`
		const cached = this.cache.get(cacheKey)

		if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
			logger.log('📊 Returning cached standings data')
			return cached.data
		}

		logger.log('📊 Calculating season standings from game data...')

		try {
			// Initialize standings structure
			const standings = initializeStandings()

			// Get available game dates from season start to today
			const gameDates = await this.getGameDatesInRange(seasonStart)

			// Process each game date
			for (const date of gameDates) {
				await this.processGamesForDate(date, standings)
			}

			// Calculate final rankings
			updateRankings(standings)

			// Cache the results
			this.cache.set(cacheKey, {
				data: standings,
				timestamp: Date.now()
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
		const dates = []
		const start = new Date(startDate)
		const end = endDate ? new Date(endDate) : new Date()

		// If we're in a development environment without API access,
		// we'll generate expected dates
		const today = new Date()
		let current = new Date(start)

		while (current <= today) {
			const dateStr = current.toISOString().split('T')[0]
			dates.push(dateStr)
			current.setDate(current.getDate() + 1)
		}

		return dates
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
		try {
			// Try to fetch the game data file
			const response = await fetch(`/data/prepopulated/games/${date}.json`)
			if (!response.ok) {
				return null
			}
			return await response.json()
		} catch (error) {
			return null
		}
	}

	/**
	 * Process a single game and update standings
	 * @param {object} game - Game object
	 * @param {object} standings - Standings object to update
	 */
	processGame(game, standings) {
		// Only process completed games
		if (game.gameState !== 'OFF') {
			return
		}

		const homeTeam = game.homeTeam
		const awayTeam = game.awayTeam
		const homeScore = game.homeScore || 0
		const awayScore = game.awayScore || 0

		// Get team info for both teams
		const homeInfo = getTeamConferenceAndDivision(homeTeam)
		const awayInfo = getTeamConferenceAndDivision(awayTeam)

		if (!homeInfo || !awayInfo) {
			logger.log(`⚠️ Unknown team in game: ${homeTeam} vs ${awayTeam}`)
			return
		}

		// Update home team stats
		const homeTeamStats = standings[homeInfo.conference][homeInfo.division]
			.find(team => team.team === homeTeam)

		// Update away team stats
		const awayTeamStats = standings[awayInfo.conference][awayInfo.division]
			.find(team => team.team === awayTeam)

		if (!homeTeamStats || !awayTeamStats) {
			logger.log(`⚠️ Team not found in standings: ${homeTeam} or ${awayTeam}`)
			return
		}

		// Update games played
		homeTeamStats.gamesPlayed++
		awayTeamStats.gamesPlayed++

		// Update goals for/against
		homeTeamStats.goalsFor += homeScore
		homeTeamStats.goalsAgainst += awayScore
		awayTeamStats.goalsFor += awayScore
		awayTeamStats.goalsAgainst += homeScore

		// Update home/away records
		homeTeamStats.home.games++
		awayTeamStats.away.games++

		// Determine winner and update points
		if (homeScore > awayScore) {
			// Home team wins
			homeTeamStats.wins++
			homeTeamStats.home.wins++
			homeTeamStats.points += 2
			homeTeamStats.regulationWins++
			homeTeamStats.regulationPlusOTWins++

			awayTeamStats.losses++
			awayTeamStats.away.losses++

			// Update streaks
			this.updateStreak(homeTeamStats, 'W')
			this.updateStreak(awayTeamStats, 'L')

		} else if (awayScore > homeScore) {
			// Away team wins
			awayTeamStats.wins++
			awayTeamStats.away.wins++
			awayTeamStats.points += 2
			awayTeamStats.regulationWins++
			awayTeamStats.regulationPlusOTWins++

			homeTeamStats.losses++
			homeTeamStats.home.losses++

			// Update streaks
			this.updateStreak(awayTeamStats, 'W')
			this.updateStreak(homeTeamStats, 'L')

		} else {
			// Tie (shouldn't happen in modern NHL, but handle just in case)
			homeTeamStats.points += 1
			awayTeamStats.points += 1

			this.updateStreak(homeTeamStats, 'OT')
			this.updateStreak(awayTeamStats, 'OT')
		}

		// Update goal differential
		homeTeamStats.goalDifferential = homeTeamStats.goalsFor - homeTeamStats.goalsAgainst
		awayTeamStats.goalDifferential = awayTeamStats.goalsFor - awayTeamStats.goalsAgainst

		// Update points percentage
		homeTeamStats.pointsPercentage = Number(
			(homeTeamStats.points / (homeTeamStats.gamesPlayed * 2)).toFixed(3)
		)
		awayTeamStats.pointsPercentage = Number(
			(awayTeamStats.points / (awayTeamStats.gamesPlayed * 2)).toFixed(3)
		)

		// Update last 10 games (simplified version)
		this.updateLast10(homeTeamStats)
		this.updateLast10(awayTeamStats)

		// Update special teams stats (simplified simulation for demonstration)
		this.updateSpecialTeamsStats(homeTeamStats)
		this.updateSpecialTeamsStats(awayTeamStats)
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
			teamStats.streak = `${result}${parseInt(count) + 1}`
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
		// Initialize special teams stats if they don't exist
		if (!teamStats.powerPlayGoals) {
			teamStats.powerPlayGoals = 0
		}
		if (!teamStats.powerPlayOpportunities) {
			teamStats.powerPlayOpportunities = 0
		}
		if (!teamStats.penaltyKillGoalsAllowed) {
			teamStats.penaltyKillGoalsAllowed = 0
		}
		if (!teamStats.penaltyKillTimesShorthanded) {
			teamStats.penaltyKillTimesShorthanded = 0
		}

		// Simulate special teams data for demonstration
		// In a real implementation, this would come from actual game data
		const gamesPlayed = teamStats.gamesPlayed || 1
		const avgPPOPerGame = 3.2 // NHL average
		const avgPKTPerGame = 3.5 // NHL average

		// Generate some realistic-looking power play data
		if (!teamStats.hasSpecialTeamsData) {
			teamStats.powerPlayOpportunities = Math.round(gamesPlayed * avgPPOPerGame)
			teamStats.powerPlayGoals = Math.round(teamStats.powerPlayOpportunities * (18 + Math.random() * 10) / 100) // 18-28% PP%

			teamStats.penaltyKillTimesShorthanded = Math.round(gamesPlayed * avgPKTPerGame)
			teamStats.penaltyKillGoalsAllowed = Math.round(teamStats.penaltyKillTimesShorthanded * (15 + Math.random() * 8) / 100) // 15-23% PK%

			teamStats.hasSpecialTeamsData = true
		}
	}

	/**
	 * Clear cache
	 */
	clearCache() {
		this.cache.clear()
		logger.log('📊 Standings cache cleared')
	}
}