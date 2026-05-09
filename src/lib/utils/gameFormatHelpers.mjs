// @ts-nocheck
/**
 * @typedef {Object} PlayerData
 * @property {string} [team]
 * @property {string} [opponent]
 * @property {string|number} [game_id]
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
 * @property {function(string|number): GameInfo|null} findGameById
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
    const result = (player?.game_result || player?.gameResult || '').trim().toUpperCase()

    // The card result badge is player-relative, so the displayed score must stay
    // player-relative too. Away-home ordering makes home-player wins look backwards.
    if (!player.game_score && gamesData?.findGameById && player.game_id) {
        const game = gamesData.findGameById(player.game_id)
        if (game && game.homeScore !== undefined && game.awayScore !== undefined) {
            if (player.team === game.awayTeam) {
                return `${game.awayScore}-${game.homeScore}`
            }
            if (player.team === game.homeTeam) {
                return `${game.homeScore}-${game.awayScore}`
            }
        }
    }

    if (!player.game_score) return ''

    const scoreParts = player.game_score.split('-')
    if (scoreParts.length === 2) {
        /** @type {[number, number]} */
        const [firstScore, secondScore] = scoreParts.map(Number)

        if (
            Number.isFinite(firstScore) &&
            Number.isFinite(secondScore) &&
            firstScore === secondScore
        ) {
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
