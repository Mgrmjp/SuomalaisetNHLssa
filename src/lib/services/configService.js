const DEFAULT_CONFIG = {
    api: {
        baseUrl: 'https://api-web.nhle.com',
        version: 'v1',
        userAgent: 'Finnish-NHL-Tracker/4.0-Automatic',
        requestTimeout: 10000,
        maxRetries: 3,
        retryDelay: 2000,
        batchSize: 10,
        apiDelay: 500,
    },
    business: {
        finnishNationalityCodes: ['FIN', 'FINLAND'],
        earliestNhlDate: '2010-10-01',
        defaultSeasonStartDate: '2025-10-01',
        playerCacheTtl: 6 * 60 * 60 * 1000,
    },
    ui: {
        teamLogoCdnBaseUrl: 'https://cdn.nhl.com/images/logos/teams-current-primary-light',
    },
}

/**
 * @typedef {typeof DEFAULT_CONFIG} AppConfig
 * @typedef {AppConfig['api']} ApiConfig
 * @typedef {AppConfig['business']} BusinessConfig
 * @typedef {AppConfig['ui']} UiConfig
 * @typedef {{
 *     isHealthy: boolean
 *     isInitialized: boolean
 *     hasConfigCache: boolean
 *     lastValidation: string | null
 *     errors: string[]
 *     warnings: string[]
 * }} ConfigHealth
 */

/** @type {AppConfig | null} */
let configCache = null
/** @type {string | null} */
let lastValidation = null
/** @type {string[]} */
let errors = []
/** @type {string[]} */
let warnings = []

/**
 * @returns {AppConfig}
 */
function cloneConfig() {
    return structuredClone(DEFAULT_CONFIG)
}

/**
 * @returns {Promise<AppConfig>}
 */
export async function initializeConfig() {
    if (!configCache) {
        configCache = cloneConfig()
        lastValidation = new Date().toISOString()
        errors = []
        warnings = []
    }

    return configCache
}

/**
 * @returns {Promise<AppConfig>}
 */
export async function reloadConfig() {
    configCache = cloneConfig()
    lastValidation = new Date().toISOString()
    errors = []
    warnings = []
    return configCache
}

/**
 * @returns {AppConfig}
 */
export function getConfig() {
    if (!configCache) {
        configCache = cloneConfig()
        lastValidation = new Date().toISOString()
    }

    return configCache
}

/**
 * @returns {ApiConfig}
 */
export function getApiConfig() {
    return getConfig().api
}

/**
 * @returns {BusinessConfig}
 */
export function getBusinessConfig() {
    return getConfig().business
}

/**
 * @returns {UiConfig}
 */
export function getUiConfig() {
    return getConfig().ui
}

/**
 * @param {string | number} playerId
 * @returns {string}
 */
export function getPlayerApiUrl(playerId) {
    const api = getApiConfig()
    return `${api.baseUrl}/${api.version}/player/${playerId}/landing`
}

/**
 * @param {string | number} team
 * @returns {string}
 */
export function getTeamLogoUrl(team) {
    const ui = getUiConfig()
    return `${ui.teamLogoCdnBaseUrl}/${String(team).toLowerCase()}.svg`
}

/**
 * @param {unknown} code
 * @returns {boolean}
 */
export function isFinnishNationalityCode(code) {
    if (!code || typeof code !== 'string') return false
    return getBusinessConfig().finnishNationalityCodes.includes(code.toUpperCase())
}

/**
 * @returns {ConfigHealth}
 */
export function getConfigHealth() {
    return {
        isHealthy: errors.length === 0,
        isInitialized: Boolean(configCache),
        hasConfigCache: Boolean(configCache),
        lastValidation,
        errors,
        warnings,
    }
}
