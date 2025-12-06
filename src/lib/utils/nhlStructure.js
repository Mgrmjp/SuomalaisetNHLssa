/**
 * NHL Structure and Conference/Division Mappings
 */

export const NHL_CONFERENCES = {
	eastern: {
		atlantic: ['BUF', 'BOS', 'DET', 'FLA', 'MTL', 'OTT', 'TBL', 'TOR'],
		metropolitan: ['CAR', 'CBJ', 'NJD', 'NYI', 'NYR', 'PHI', 'PIT', 'WSH']
	},
	western: {
		central: ['CHI', 'COL', 'DAL', 'MIN', 'NSH', 'STL', 'WPG', 'UTA'],
		pacific: ['ANA', 'CGY', 'EDM', 'LAK', 'SJS', 'SEA', 'VAN', 'VGK']
	}
}

export const DIVISION_NAMES = {
	atlantic: 'Atlantic',
	metropolitan: 'Metropolitan',
	central: 'Central',
	pacific: 'Pacific'
}

export const CONFERENCE_NAMES = {
	eastern: 'Eastern',
	western: 'Western'
}

/**
 * Get all teams in a conference
 * @param {string} conference - 'eastern' or 'western'
 * @returns {string[]} Array of team abbreviations
 */
export function getConferenceTeams(conference) {
	const conferenceData = NHL_CONFERENCES[conference]
	if (!conferenceData) return []

	return Object.values(conferenceData).flat()
}

/**
 * Get all teams in a division
 * @param {string} conference - 'eastern' or 'western'
 * @param {string} division - Division name
 * @returns {string[]} Array of team abbreviations
 */
export function getDivisionTeams(conference, division) {
	return NHL_CONFERENCES[conference]?.[division] || []
}

/**
 * Get team's conference and division
 * @param {string} team - Team abbreviation
 * @returns {object} { conference, division }
 */
export function getTeamConferenceAndDivision(team) {
	for (const [conferenceName, conferenceData] of Object.entries(NHL_CONFERENCES)) {
		for (const [divisionName, teams] of Object.entries(conferenceData)) {
			if (teams.includes(team)) {
				return {
					conference: conferenceName,
					division: divisionName
				}
			}
		}
	}
	return null
}

/**
 * Initialize empty standings structure
 * @returns {object} Empty standings object with proper structure
 */
export function initializeStandings() {
	const standings = {}

	for (const [conferenceName, conferenceData] of Object.entries(NHL_CONFERENCES)) {
		standings[conferenceName] = {}

		for (const [divisionName, teams] of Object.entries(conferenceData)) {
			standings[conferenceName][divisionName] = teams.map(team => ({
				team,
				gamesPlayed: 0,
				wins: 0,
				losses: 0,
				overtimeLosses: 0,
				points: 0,
				pointsPercentage: 0,
				regulationWins: 0,
				regulationPlusOTWins: 0,
				goalsFor: 0,
				goalsAgainst: 0,
				goalDifferential: 0,
				divisionRank: 0,
				conferenceRank: 0,
				leagueRank: 0,
				streak: '',
				last10: '0-0-0',
				home: {
					games: 0,
					wins: 0,
					losses: 0,
					ot: 0
				},
				away: {
					games: 0,
					wins: 0,
					losses: 0,
					ot: 0
				}
			}))
		}
	}

	return standings
}

/**
 * Sort teams by NHL standings rules
 * @param {Array} teams - Array of team standings objects
 * @returns {Array} Sorted teams
 */
export function sortTeamsByStandings(teams) {
	return teams.sort((a, b) => {
		// 1. Points Percentage (higher is better) - NHL standard sorting
		const aPointsPct = a.pointsPercentage || 0
		const bPointsPct = b.pointsPercentage || 0
		if (Math.abs(bPointsPct - aPointsPct) > 0.001) {
			return bPointsPct - aPointsPct
		}

		// 2. Points (higher is better) - Secondary sort by total points
		if (b.points !== a.points) {
			return b.points - a.points
		}

		// 3. Regulation Wins (higher is better)
		if (b.regulationWins !== a.regulationWins) {
			return b.regulationWins - a.regulationWins
		}

		// 4. Regulation + Overtime Wins (higher is better)
		if (b.regulationPlusOTWins !== a.regulationPlusOTWins) {
			return b.regulationPlusOTWins - a.regulationPlusOTWins
		}

		// 5. Goal Differential (higher is better)
		if (b.goalDifferential !== a.goalDifferential) {
			return b.goalDifferential - a.goalDifferential
		}

		// 6. Goals For (higher is better)
		if (b.goalsFor !== a.goalsFor) {
			return b.goalsFor - a.goalsFor
		}

		// 7. Team name (alphabetical as final tie-breaker)
		return a.team.localeCompare(b.team)
	})
}

/**
 * Calculate points percentage
 * @param {object} team - Team standings object
 * @returns {number} Points percentage
 */
export function calculatePointsPercentage(team) {
	if (team.gamesPlayed === 0) return 0
	return Number((team.points / (team.gamesPlayed * 2)).toFixed(3))
}

/**
 * Calculate Wild Card teams for each conference
 * @param {object} standings - Full standings object
 * @returns {object} Wild card teams by conference
 */
export function calculateWildCardTeams(standings) {
	const wildCards = { eastern: [], western: [] }

	for (const [conferenceName, conferenceData] of Object.entries(standings)) {
		const allConferenceTeams = []

		// Collect all teams in conference
		for (const [divisionName, teams] of Object.entries(conferenceData)) {
			for (const team of teams) {
				allConferenceTeams.push({
					...team,
					division: divisionName
				})
			}
		}

		// Sort by points percentage
		const sortedTeams = sortTeamsByStandings(allConferenceTeams)

		// Filter out top 3 from each division
		const remainingTeams = sortedTeams.filter(team => team.divisionRank > 3)

		// Take top 2 as Wild Cards
		wildCards[conferenceName] = remainingTeams.slice(0, 2).map(team => team.team)
	}

	return wildCards
}

/**
 * Update team rankings within division and conference
 * @param {object} standings - Full standings object
 */
export function updateRankings(standings) {
	// First, sort teams within each division by points percentage
	for (const [conferenceName, conferenceData] of Object.entries(standings)) {
		for (const [divisionName, teams] of Object.entries(conferenceData)) {
			// Sort teams within the division by points percentage
			const sortedDivisionTeams = sortTeamsByStandings([...teams])

			// Update the division in the standings with sorted teams
			standings[conferenceName][divisionName] = sortedDivisionTeams

			// Set division ranks
			sortedDivisionTeams.forEach((team, index) => {
				team.divisionRank = index + 1
			})
		}
	}

	// Now collect all teams for conference and league rankings
	const allTeams = []

	for (const [conferenceName, conferenceData] of Object.entries(standings)) {
		for (const [divisionName, teams] of Object.entries(conferenceData)) {
			for (const team of teams) {
				allTeams.push({
					...team,
					conference: conferenceName,
					division: divisionName
				})
			}
		}
	}

	// Sort all teams by standings (points percentage first)
	const sortedTeams = sortTeamsByStandings(allTeams)

	// Update conference and league rankings
	const conferenceRankings = { eastern: 1, western: 1 }

	for (const team of sortedTeams) {
		team.leagueRank = sortedTeams.indexOf(team) + 1
		team.conferenceRank = conferenceRankings[team.conference]++

		// Update the original team object in standings
		for (const [conferenceName, conferenceData] of Object.entries(standings)) {
			for (const [divisionName, teams] of Object.entries(conferenceData)) {
				const originalTeam = teams.find(t => t.team === team.team)
				if (originalTeam) {
					originalTeam.conferenceRank = team.conferenceRank
					originalTeam.leagueRank = team.leagueRank
				}
			}
		}
	}
}