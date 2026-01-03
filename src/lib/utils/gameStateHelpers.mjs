/**
 * Game State Helpers
 *
 * Utilities for determining game status (live, upcoming, complete)
 * based on the gameState field from game data.
 */

/**
 * Game state constants from NHL API
 */
export const GAME_STATE = {
	OFF: 'OFF', // Game is over/final
	FINAL: 'FINAL', // Alternative final state
	PRE: 'PRE', // Pre-game (scheduled, not started)
	FUT: 'FUT', // Future game (scheduled)
	LIVE: 'LIVE', // Game is live/in-progress
	CRIT: 'CRIT', // Critical/late game situation
	IRT: 'IRT' // In review timeout
}

/**
 * Get game state for a player by looking up their game
 * @param {Object} player - Player object with game_id property
 * @param {Object} gamesData - Games data object with findGameById function
 * @returns {string|null} Game state code or null if not found
 */
export function getGameStateForPlayer(player, gamesData) {
	if (!player?.game_id || !gamesData?.findGameById) {
		return null
	}
	const game = gamesData.findGameById(player.game_id)
	return game?.gameState || null
}

/**
 * Check if player's game is currently live/in-progress
 * @param {Object} player - Player object with game_id property
 * @param {Object} gamesData - Games data object with findGameById function
 * @returns {boolean} True if game is live
 */
export function isPlayerGameLive(player, gamesData) {
	const state = getGameStateForPlayer(player, gamesData)
	return state === GAME_STATE.LIVE || state === GAME_STATE.CRIT || state === GAME_STATE.IRT
}

/**
 * Check if game result should be shown (game is complete)
 * @param {Object} player - Player object with game_id property
 * @param {Object} gamesData - Games data object with findGameById function
 * @returns {boolean} True if game is complete and result should be shown
 */
export function shouldShowGameResult(player, gamesData) {
	const state = getGameStateForPlayer(player, gamesData)
	return state === GAME_STATE.OFF || state === GAME_STATE.FINAL
}

/**
 * Check if game is upcoming (not started yet)
 * @param {Object} player - Player object with game_id property
 * @param {Object} gamesData - Games data object with findGameById function
 * @returns {boolean} True if game is upcoming
 */
export function isGameUpcoming(player, gamesData) {
	const state = getGameStateForPlayer(player, gamesData)
	return state === GAME_STATE.PRE || state === GAME_STATE.FUT
}
