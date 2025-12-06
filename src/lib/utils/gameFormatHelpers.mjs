/**
 * Helper functions to format game information in "Away @ Home" pattern
 * These functions ensure consistent display regardless of which team the Finnish player is on
 */

/**
 * Format game matchup in "Away @ Home" pattern
 * @param {Object} player - Player data object
 * @param {Object} gamesData - Games data object with findGameById function
 * @returns {string} Formatted matchup string
 */
export function formatGameMatchup(player, gamesData = null) {
	if (!player.team || !player.opponent) return ''

	// If we have games data, use it to determine home/away teams accurately
	if (gamesData && gamesData.findGameById && player.game_id) {
		const game = gamesData.findGameById(player.game_id)
		if (game && game.homeTeam && game.awayTeam) {
			// We have explicit home/away data from the game
			const homeTeam = game.homeTeam
			const awayTeam = game.awayTeam

			// Verify that the teams match the player's team and opponent
			if ((homeTeam === player.team && awayTeam === player.opponent) ||
				(homeTeam === player.opponent && awayTeam === player.team)) {
				// Return proper "Away @ Home" format
				return `${awayTeam} @ ${homeTeam}`
			}
		}
	}

	// Fallback: Can't determine from games data, default to player's team as away
	// This maintains the "Away @ Home" pattern but may not be accurate
	return `${player.team} @ ${player.opponent}`
}

/**
 * Format game score in "Away Score - Home Score" pattern
 * @param {Object} player - Player data object
 * @param {Object} gamesData - Games data object with findGameById function
 * @returns {string} Formatted score string
 */
export function formatGameScore(player, gamesData = null) {
	if (!player.game_score) return ''

	// If we have games data, use it to ensure correct "awayScore-homeScore" format
	if (gamesData && gamesData.findGameById && player.game_id) {
		const game = gamesData.findGameById(player.game_id)
		if (game && game.homeScore !== undefined && game.awayScore !== undefined) {
			// Return scores in consistent "awayScore-homeScore" format
			return `${game.awayScore}-${game.homeScore}`
		}
	}

	// Fallback: Use player.game_score but ensure it's in "awayScore-homeScore" format
	// The current data might be in "homeScore-awayScore" format, so we need to check
	const scoreParts = player.game_score.split('-')
	if (scoreParts.length === 2) {
		const [firstScore, secondScore] = scoreParts.map(Number)

		// If we have games data, we can determine which format is correct
		if (gamesData && gamesData.findGameById && player.game_id) {
			const game = gamesData.findGameById(player.game_id)
			if (game && game.homeScore !== undefined && game.awayScore !== undefined) {
				// Check if player.game_score is in "homeScore-awayScore" format
				if (firstScore === game.homeScore && secondScore === game.awayScore) {
					// It's in wrong format, swap it
					return `${game.awayScore}-${game.homeScore}`
				}
			}
		}
	}

	// Default fallback - return as-is
	return player.game_score
}

/**
 * Format game venue information
 * @param {Object} player - Player data object
 * @returns {string} Formatted venue string
 */
export function formatGameVenue(player) {
	if (!player.game_venue && !player.game_city) return ''
	
	if (player.game_venue && player.game_city) {
		return `${player.game_venue} — ${player.game_city}`
	} else if (player.game_venue) {
		return player.game_venue
	} else if (player.game_city) {
		return player.game_city
	}
	
	return ''
}