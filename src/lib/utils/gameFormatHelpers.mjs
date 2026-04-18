// @ts-nocheck
/**
 * @typedef {Object} PlayerData
 * @property {string} [team]
 * @property {string} [opponent]
 * @property {string} [game_id]
 * @property {string} [game_score]
 * @property {string} [game_result]
 * @property {string} [gameResult]
 * @property {string} [game_venue]
 * @property {string} [game_city]
 * @property {string} [headshot_url]
 * @property {string} [team_full]
 * @property {string} [opponent_full]
 */

/**
 * @typedef {Object} GameData
 * @property {function(string): GameInfo} findGameById
 */

/**
 * @typedef {Object} GameInfo
 * @property {string} homeTeam
 * @property {string} awayTeam
 * @property {number} homeScore
 * @property {number} awayScore
 * @property {boolean} isOT
 * @property {boolean} isSO
 */

/**
 * Helper functions to format game information in "Away @ Home" pattern
 * These functions ensure consistent display regardless of which team the Finnish player is on
 */

/**
 * Format game matchup in "Away @ Home" pattern
 * @param {PlayerData} player - Player data object
 * @param {GameData | null} [gamesData] - Games data object with findGameById function
 * @returns {string} Formatted matchup string
 */
export function formatGameMatchup(player, gamesData = null) {
    if (!player.team || !player.opponent) return ''

    // If we have games data, use it to determine home/away teams accurately
    if (gamesData?.findGameById && player.game_id) {
        const game = gamesData.findGameById(player.game_id)
        if (game?.homeTeam && game.awayTeam) {
            // We have explicit home/away data from the game
            const homeTeam = game.homeTeam
            const awayTeam = game.awayTeam

            // Verify that the teams match the player's team and opponent
            if (
                (homeTeam === player.team && awayTeam === player.opponent) ||
                (homeTeam === player.opponent && awayTeam === player.team)
            ) {
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
 * @param {PlayerData} player - Player data object
 * @param {GameData | null} [gamesData] - Games data object with findGameById function
 * @returns {string} Formatted score string
 */
export function formatGameScore(player, gamesData = null) {
    if (!player.game_score) return ''

    // If we have games data, use it to ensure correct "awayScore-homeScore" format
    if (gamesData?.findGameById && player.game_id) {
        const game = gamesData.findGameById(player.game_id)
        if (game && game.homeScore !== undefined && game.awayScore !== undefined) {
            if (game.isSO && game.awayScore === game.homeScore) {
                const result = (player?.game_result || player?.gameResult || '')
                    .trim()
                    .toUpperCase()
                const playerTeam = player?.team
                const opponentTeam = player?.opponent
                let winningTeam = null

                if (result === 'W') winningTeam = playerTeam
                if (result === 'L') winningTeam = opponentTeam

                if (winningTeam === game.awayTeam) {
                    return `${game.awayScore + 1}-${game.homeScore}`
                }

                if (winningTeam === game.homeTeam) {
                    return `${game.awayScore}-${game.homeScore + 1}`
                }
            }

            // Return scores in consistent "awayScore-homeScore" format
            return `${game.awayScore}-${game.homeScore}`
        }
    }

    // Fallback: Use player.game_score but ensure it's in "awayScore-homeScore" format
    // The current data might be in "homeScore-awayScore" format, so we need to check
    const scoreParts = player.game_score.split('-')
    if (scoreParts.length === 2) {
        /** @type {[number, number]} */
        const [firstScore, secondScore] = scoreParts.map(Number)

        // If we have games data, we can determine which format is correct
        if (gamesData?.findGameById && player.game_id) {
            const game = gamesData.findGameById(player.game_id)
            if (game && game.homeScore !== undefined && game.awayScore !== undefined) {
                // Check if player.game_score is in "homeScore-awayScore" format
                if (firstScore === game.homeScore && secondScore === game.awayScore) {
                    // It's in wrong format, swap it
                    return `${game.awayScore}-${game.homeScore}`
                }
            }
        }

        if (
            Number.isFinite(firstScore) &&
            Number.isFinite(secondScore) &&
            firstScore === secondScore
        ) {
            const result = (player?.game_result || player?.gameResult || '').trim().toUpperCase()
            if (result === 'W') {
                return `${firstScore + 1}-${secondScore}`
            }
            if (result === 'L') {
                return `${firstScore}-${secondScore + 1}`
            }
        }
    }

    // Default fallback - return as-is
    return player.game_score
}

/**
 * Format game venue information
 * @param {PlayerData} player - Player data object
 * @returns {string} Formatted venue string
 */
export function formatGameVenue(player) {
    if (!player.game_venue && !player.game_city) return ''

    if (player.game_venue && player.game_city) {
        return `${player.game_venue}, ${player.game_city}`
    }
    if (player.game_venue) {
        return player.game_venue
    }
    if (player.game_city) {
        return player.game_city
    }

    return ''
}
