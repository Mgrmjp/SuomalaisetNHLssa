/**
 * Position Helper Utilities
 *
 * Reusable functions for player position handling and filtering
 */

import { POSITION_TYPES } from '$lib/constants/gameConstants.js'

/**
 * Get the position code from a player object
 * Handles different data formats for position information
 *
 * @param {Object} player - Player object containing position data
 * @returns {string} Upper case position code (e.g., 'G', 'D', 'LW', 'C', 'RW')
 */
export function getPositionCode(player) {
    if (!player) return ''
    const pos = player.position?.toUpperCase?.() || player.positionCode?.toUpperCase?.() || ''
    return pos
}

/**
 * Check if player has any of the specified positions
 *
 * @param {Object} player - Player object
 * @param {string[]} positions - Array of position codes to check
 * @returns {boolean} True if player matches any of the positions
 */
export function hasPosition(player, positions) {
    const pos = getPositionCode(player)
    return positions.some((p) => pos === p || pos === p.toUpperCase())
}

/**
 * Check if player is a goalie
 *
 * @param {Object} player - Player object
 * @returns {boolean} True if player is a goalie
 */
export function isGoalie(player) {
    return hasPosition(player, POSITION_TYPES.GOALIE)
}

/**
 * Check if player is a defenseman
 *
 * @param {Object} player - Player object
 * @returns {boolean} True if player is a defenseman
 */
export function isDefense(player) {
    return hasPosition(player, POSITION_TYPES.DEFENSE)
}

/**
 * Check if player is a forward (left wing, right wing, or center)
 *
 * @param {Object} player - Player object
 * @returns {boolean} True if player is a forward
 */
export function isForward(player) {
    return hasPosition(player, POSITION_TYPES.FORWARD)
}

/**
 * Check if player has any points (goals, assists, or points)
 *
 * @param {Object} player - Player object
 * @returns {boolean} True if player has at least one point
 */
export function hasPoints(player) {
    return (player.points || 0) > 0 || (player.goals || 0) > 0 || (player.assists || 0) > 0
}

/**
 * Filter players by position type
 *
 * @param {Object[]} players - Array of player objects
 * @param {string} positionType - One of 'GOALIE', 'DEFENSE', 'FORWARD', or 'ALL'
 * @returns {Object[]} Filtered array of players
 */
export function filterByPosition(players, positionType) {
    if (!players || !Array.isArray(players)) return []
    if (positionType === 'ALL') return players

    switch (positionType) {
        case 'GOALIE':
            return players.filter(isGoalie)
        case 'DEFENSE':
            return players.filter(isDefense)
        case 'FORWARD':
            return players.filter(isForward)
        default:
            return players
    }
}

/**
 * Get save percentage for a goalie
 * Handles different data formats for save percentage
 *
 * @param {Object} goalie - Goalie object
 * @returns {number|undefined} Save percentage as decimal (e.g., 0.912) or undefined
 */
export function getSavePercentage(goalie) {
    if (!goalie) return undefined
    const provided = goalie.save_percentage ?? goalie.savePercentage
    if (provided !== undefined) {
        return provided > 1 ? provided / 100 : provided
    }

    const saves = goalie.saves ?? 0
    const shots = goalie.shotsAgainst ?? goalie.shots_against ?? 0
    if (shots > 0) {
        return saves / shots
    }
    return undefined
}

/**
 * Format save percentage for display
 *
 * @param {Object} goalie - Goalie object
 * @returns {string} Formatted save percentage (e.g., '.912') or '-'
 */
export function formatSavePercentage(goalie) {
    const sv = getSavePercentage(goalie)
    if (sv === undefined) return '-'
    return `.${(sv * 1000).toFixed(0)}`
}
