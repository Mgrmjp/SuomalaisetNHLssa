/**
 * Node.js Compatible Automatic Finnish Player Detection Service
 *
 * This service provides real-time Finnish player detection using the official NHL API
 * to verify player nationality, adapted for Node.js scripts.
 */

import logger from '../node-utils/logger.js'

// Configuration constants (copied from configService.js for Node.js compatibility)
const FINNISH_NATIONALITY_CODES = ['FIN', 'FI']
const NHL_API_BASE = 'https://api-web.nhle.com'
const API_VERSION = 'v1'
const DEFAULT_CACHE_TTL = 21600000 // 6 hours

// In-memory cache for player nationality data
const playerNationalityCache = {
    data: new Map(), // playerId -> player data
    timestamp: null,
    isRefreshing: false,
    lastError: null,
}

// Set-based lookup for O(1) performance
const finnishPlayerIdSet = new Set()

/**
 * @typedef {Object} PlayerData
 * @property {number} id - Player ID
 * @property {string} fullName - Player full name
 * @property {string} nationality - Player nationality
 * @property {boolean} active - Player active status
 * @property {Object} primaryPosition - Player position
 * @property {string} primaryPosition.abbreviation - Position abbreviation
 * @property {Object} currentTeam - Player current team
 * @property {string} currentTeam.abbreviation - Team abbreviation
 */

/**
 * Get configuration for API access
 * @returns {Object} API configuration
 */
function getApiConfig() {
    return {
        baseUrl: NHL_API_BASE,
        version: API_VERSION,
        timeout: 10000,
        retries: 3
    }
}

/**
 * Get configuration for business logic
 * @returns {Object} Business configuration
 */
function getBusinessConfig() {
    return {
        playerCacheTTL: DEFAULT_CACHE_TTL,
        finnishNationalityCodes: FINNISH_NATIONALITY_CODES
    }
}

/**
 * Check if nationality code is Finnish
 * @param {string} nationality - Nationality code
 * @returns {boolean} True if Finnish
 */
export function isFinnishNationalityCode(nationality) {
    if (!nationality) return false
    return FINNISH_NATIONALITY_CODES.includes(nationality.toUpperCase())
}

/**
 * Check if player is Finnish based on nationality or birth country
 * @param {Object} playerData - Player data from API
 * @returns {boolean} True if Finnish
 */
export function isFinnishPlayer(playerData) {
    // Check nationality field first
    if (playerData?.nationality && isFinnishNationalityCode(playerData.nationality)) {
        return true
    }
    
    // Fall back to birthCountry field
    if (playerData?.birthCountry && isFinnishNationalityCode(playerData.birthCountry)) {
        return true
    }
    
    return false
}

/**
 * Build API URL for player landing page
 * @param {number} playerId - Player ID
 * @returns {string} API URL
 */
export function getPlayerApiUrl(playerId) {
    const apiConfig = getApiConfig()
    return `${apiConfig.baseUrl}/${apiConfig.version}/player/${playerId}/landing`
}

/**
 * Fetch data from NHL API with error handling
 * @param {string} url - API URL
 * @param {Object} options - Request options
 * @returns {Promise<Object|null>} API response or null on error
 */
async function fetchFromAPI(url, options = {}) {
    try {
        const response = await fetch(url, {
            timeout: 10000,
            ...options
        })

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }

        return await response.json()
    } catch (error) {
        logger.error(`API call failed for ${url}:`, error.message)
        return null
    }
}

/**
 * Check if player is Finnish by fetching their data from NHL API
 * @param {number} playerId - Player ID
 * @returns {Promise<boolean>} True if player is Finnish
 */
export async function isFinnishPlayerAutomatic(playerId) {
    try {
        // Check cache first
        if (finnishPlayerIdSet.has(playerId)) {
            return true
        }

        // Check memory cache
        const cachedPlayer = playerNationalityCache.data.get(playerId)
        if (cachedPlayer) {
            const businessConfig = getBusinessConfig()
            const cacheAge = Date.now() - (playerNationalityCache.timestamp || 0)

            if (cacheAge < businessConfig.playerCacheTTL) {
                if (isFinnishNationalityCode(cachedPlayer.nationality)) {
                    finnishPlayerIdSet.add(playerId)
                    return true
                }
                return false
            }
        }

        // Fetch from API
        const apiUrl = getPlayerApiUrl(playerId)
        const playerData = await fetchFromAPI(apiUrl)

        if (!playerData) {
            return false
        }

        // Cache the player data
        playerNationalityCache.data.set(playerId, playerData)
        playerNationalityCache.timestamp = Date.now()

        // Check nationality using the enhanced function
        const isFinnish = isFinnishPlayer(playerData)
        if (isFinnish) {
            finnishPlayerIdSet.add(playerId)
        }

        return isFinnish

    } catch (error) {
        logger.error(`Error checking Finnish nationality for player ${playerId}:`, error)
        return false
    }
}

/**
 * Get Finnish player information from API
 * @param {number} playerId - Player ID
 * @returns {Promise<PlayerData|null>} Player data or null
 */
export async function getFinnishPlayerInfoAutomatic(playerId) {
    try {
        const apiUrl = getPlayerApiUrl(playerId)
        const playerData = await fetchFromAPI(apiUrl)

        if (!playerData || !isFinnishPlayer(playerData)) {
            return null
        }

        return {
            id: playerData.id || playerId,
            fullName: playerData.fullName || playerData.name || '',
            nationality: playerData.nationality,
            active: playerData.active || false,
            primaryPosition: playerData.primaryPosition || {},
            currentTeam: playerData.currentTeam || {}
        }

    } catch (error) {
        logger.error(`Error getting Finnish player info for ${playerId}:`, error)
        return null
    }
}

/**
 * Filter array of players to only Finnish players using automatic detection
 * @param {Array<Object>} players - Array of player objects with id property
 * @returns {Promise<Array<Object>>} Array of Finnish players
 */
export async function filterFinnishPlayersAutomatic(players) {
    if (!Array.isArray(players) || players.length === 0) {
        return []
    }

    const finnishPlayers = []

    // Process players in batches to avoid overwhelming the API
    const batchSize = 5
    for (let i = 0; i < players.length; i += batchSize) {
        const batch = players.slice(i, i + batchSize)

        const batchPromises = batch.map(async (player) => {
            // Handle both id and playerId fields for compatibility
            const playerId = player.playerId || player.id
            if (!player || !playerId) return null

            const isFinnish = await isFinnishPlayerAutomatic(playerId)
            if (isFinnish) {
                return player
            }
            return null
        })

        const batchResults = await Promise.all(batchPromises)
        finnishPlayers.push(...batchResults.filter(Boolean))

        // Add small delay between batches to be respectful to the API
        if (i + batchSize < players.length) {
            await new Promise(resolve => setTimeout(resolve, 1000))
        }
    }

    return finnishPlayers
}

/**
 * Initialize automatic Finnish player detection
 * Pre-warms cache with common Finnish players if needed
 */
export async function initializeAutomaticFinnishPlayerDetection() {
    logger.info('Initializing automatic Finnish player detection for Node.js environment')

    // In Node.js script context, we don't need to pre-populate the cache
    // The fetch script will call APIs as needed

    playerNationalityCache.timestamp = Date.now()
    logger.debug('Automatic Finnish player detection initialized')
}

/**
 * Get statistics about the automatic Finnish player detection
 * @returns {Object} Statistics
 */
export function getAutomaticFinnishPlayerStats() {
    return {
        cachedPlayerCount: finnishPlayerIdSet.size,
        cacheAge: playerNationalityCache.timestamp
            ? Date.now() - playerNationalityCache.timestamp
            : null,
        isRefreshing: playerNationalityCache.isRefreshing,
        lastError: playerNationalityCache.lastError,
    }
}