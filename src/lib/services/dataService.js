// Data Service
// Fetches data directly from API without caching

// @ts-nocheck

import { isValidDateFormat } from '$lib/api/nhlApi.js'
import playerDetectionService from '$lib/services/playerDetectionService.js'
import { fetchLocalJSON } from '$lib/utils/apiHelpers.js'
import { formatDate } from '$lib/utils/dateUtils.js'
import logger from '$lib/utils/logger.js'

// API configuration removed - using only prepopulated data

/**
 * Get Finnish player IDs for tracking
 * @returns {Promise<Set<number>>} Set of Finnish player IDs
 */
async function _getFinnishPlayerIds() {
    return await playerDetectionService.getFinnishPlayerIds()
}

/**
 * Check if a player ID is Finnish
 * @param {number} playerId - Player ID to check
 * @returns {Promise<boolean>} True if player is Finnish
 */
async function _hasFinnishPlayerId(playerId) {
    return await playerDetectionService.isFinnishPlayer(playerId)
}

/**
 * Get Finnish player by ID
 * @param {number} playerId - Player ID
 * @returns {Promise<Object|null>} Finnish player info or null
 */
async function _getFinnishPlayerById(playerId) {
    return await playerDetectionService.getFinnishPlayerById(playerId)
}

// Helper functions removed - only prepopulated data is used

// API fetching functions removed - only prepopulated data is used

// API processing functions removed - only prepopulated data is used

/**
 * Load pre-populated data for a specific date
 * @param {string} date - Date in YYYY-MM-DD format
 * @returns {Promise<any[]>} Array of Finnish player performances from pre-populated data
 */
async function loadPrepopulatedData(date) {
    const data = await fetchLocalJSON(`/data/prepopulated/games/${date}.json`)
    if (data) {
        logger.debug(`📁 Loaded pre-populated data for ${date}: ${data.total_players} players`)
        return data.players || []
    }
    return null
}

/**
 * Load full pre-populated data including games for a specific date
 * @param {string} date - Date in YYYY-MM-DD format
 * @returns {Promise<Object|null>} Full data object including players and games or null
 */
async function loadFullPrepopulatedData(date) {
    const data = await fetchLocalJSON(`/data/prepopulated/games/${date}.json`)
    if (data) {
        logger.debug(
            `📁 Loaded full pre-populated data for ${date}: ${data.total_players} players, ${data.games?.length || 0} games`
        )
        return data
    }
    return null
}

/**
 * Get available pre-populated dates
 * @returns {Promise<string[]>} Array of available dates in YYYY-MM-DD format
 */
export async function getAvailablePrepopulatedDates() {
    const availableDates = []

    // Check for known pre-populated dates
    const datesToCheck = [
        '2025-11-08',
        '2025-11-09',
        '2025-11-13',
        '2026-01-01',
        '2026-01-03',
        '2026-01-06',
    ]

    for (const date of datesToCheck) {
        const data = await fetchLocalJSON(`/data/prepopulated/games/${date}.json`)
        if (data) {
            availableDates.push(date)
        }
    }

    if (availableDates.length > 0) {
        logger.debug(`📅 Available pre-populated dates: ${availableDates.join(', ')}`)
    }

    return availableDates.sort()
}

/**
 * Get Finnish players for a specific date
 * @param {string} date - Date in YYYY-MM-DD format
 * @returns {Promise<any[]>} Array of Finnish player performances
 */
export async function getFinnishPlayersForDate(date) {
    // Input validation
    if (!date || typeof date !== 'string') {
        logger.warn('Invalid or no date provided to getFinnishPlayersForDate:', date)
        return []
    }

    if (!isValidDateFormat(date)) {
        logger.warn(`Invalid date format provided: ${date}. Expected YYYY-MM-DD`)
        return []
    }
    logger.debug(`🏒 Loading Finnish players for ${date}`)

    // Only use pre-populated data - no API fetching
    const prepopulatedData = await loadPrepopulatedData(date)
    if (prepopulatedData) {
        logger.debug(`✅ Using pre-populated data for ${date}: ${prepopulatedData.length} players`)
        return prepopulatedData
    }

    // No API fallback - if no prepopulated data exists, return empty array
    logger.log(`📁 No pre-populated data found for ${date}`)
    return []
}

/**
 * Get games data for a specific date
 * @param {string} date - Date in YYYY-MM-DD format
 * @returns {Promise<Object>} Object with games array and a function to find game by ID
 */
export async function getGamesForDate(date) {
    // Input validation
    if (!date || typeof date !== 'string') {
        logger.warn('Invalid or no date provided to getGamesForDate:', date)
        return { games: [], findGameById: () => null }
    }

    if (!isValidDateFormat(date)) {
        logger.warn(`Invalid date format provided: ${date}. Expected YYYY-MM-DD`)
        return { games: [], findGameById: () => null }
    }

    logger.debug(`🏒 Loading games data for ${date}`)

    // Load full pre-populated data to get games
    const fullData = await loadFullPrepopulatedData(date)
    if (fullData?.games) {
        logger.debug(`✅ Using games data for ${date}: ${fullData.games.length} games`)

        // Create a lookup function to find games by ID
        const gamesMap = new Map(fullData.games.map((game) => [game.gameId, game]))

        return {
            games: fullData.games,
            findGameById: (gameId) => gamesMap.get(gameId) || null,
        }
    }

    logger.debug(`📁 No games data found for ${date}`)
    return { games: [], findGameById: () => null }
}

// getGameDataForDate removed - API calls disabled

/**
 * Get Finnish roster data
 * @returns {Promise<any[]>} Array of Finnish players
 */
export async function getFinnishRoster() {
    logger.debug(`🏒 Fetching Finnish roster`)
    const players = await playerDetectionService.getAllFinnishPlayers()
    logger.success(`Found ${players.length} Finnish players in roster`)
    return players
}

/**
 * Get recent dates that might have data
 * @param {number} days - Number of days to look back
 * @returns {Array<string>} Array of date strings
 */
export function getRecentDates(days = 14) {
    const dates = []
    const today = new Date()

    for (let i = 1; i <= days; i++) {
        const date = new Date(today)
        date.setDate(today.getDate() - i)
        dates.push(formatDate(date))
    }

    return dates
}
