// Data Service
// Fetches data directly from API without caching

// @ts-nocheck

import { isValidDateFormat } from '$lib/api/nhlApi.js'
import { formatDate } from '$lib/utils/dateHelpers.js'
import playerDetectionService from '$lib/services/playerDetectionService.js'
import logger from '$lib/utils/logger.js'

// API configuration removed - using only prepopulated data


/**
 * Get Finnish player IDs for tracking
 * @returns {Promise<Set<number>>} Set of Finnish player IDs
 */
async function getFinnishPlayerIds() {
    return await playerDetectionService.getFinnishPlayerIds()
}


/**
 * Check if a player ID is Finnish
 * @param {number} playerId - Player ID to check
 * @returns {Promise<boolean>} True if player is Finnish
 */
async function hasFinnishPlayerId(playerId) {
    return await playerDetectionService.isFinnishPlayer(playerId)
}

/**
 * Get Finnish player by ID
 * @param {number} playerId - Player ID
 * @returns {Promise<Object|null>} Finnish player info or null
 */
async function getFinnishPlayerById(playerId) {
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
    try {
        const response = await fetch(`/data/prepopulated/games/${date}.json`)

        if (!response.ok) {
            return null
        }

        const data = await response.json()
        logger.log(`📁 Loaded pre-populated data for ${date}: ${data.total_players} players`)
        return data.players || []
    } catch (error) {
        logger.debug(`No pre-populated data found for ${date}:`, error.message)
        return null
    }
}

/**
 * Get available pre-populated dates
 * @returns {Promise<string[]>} Array of available dates in YYYY-MM-DD format
 */
export async function getAvailablePrepopulatedDates() {
    const availableDates = []

    try {
        // Check for known pre-populated dates
        const datesToCheck = ['2025-11-08', '2025-11-09', '2025-11-13']

        for (const date of datesToCheck) {
            try {
                const response = await fetch(`/data/prepopulated/games/${date}.json`)
                if (response.ok) {
                    availableDates.push(date)
                }
            } catch (error) {
                logger.debug(`No pre-populated data found for ${date}`)
            }
        }

        if (availableDates.length > 0) {
            logger.log(`📅 Available pre-populated dates: ${availableDates.join(', ')}`)
        }

        return availableDates.sort()
    } catch (error) {
        logger.debug('Error checking pre-populated dates:', error.message)
        return []
    }
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
    logger.log(`🏒 Loading Finnish players for ${date}`)

    // Only use pre-populated data - no API fetching
    const prepopulatedData = await loadPrepopulatedData(date)
    if (prepopulatedData) {
        logger.log(`✅ Using pre-populated data for ${date}: ${prepopulatedData.length} players`)
        return prepopulatedData
    }

    // No API fallback - if no prepopulated data exists, return empty array
    logger.log(`📁 No pre-populated data found for ${date}`)
    return []
}

// getGameDataForDate removed - API calls disabled

/**
 * Get Finnish roster data
 * @returns {Promise<any[]>} Array of Finnish players
 */
export async function getFinnishRoster() {
    logger.log(`🏒 Fetching Finnish roster`)
    const players = await playerDetectionService.getAllFinnishPlayers()
    logger.log(`✅ Found ${players.length} Finnish players in roster`)
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
