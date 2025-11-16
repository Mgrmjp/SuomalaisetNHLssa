// NHL API Integration for Finnish Player Tracker
// Contains only validation functions and utility functions, no API calls
// All data is now loaded from JSON files in the browser

import logger from '$lib/utils/logger.js'

// Note: Previous API statistics and stub functions have been removed as they were no longer functional.

/**
 * Validate date string format
 * @param {string} date - Date string to validate
 * @returns {boolean} True if date is valid YYYY-MM-DD format
 */
export function isValidDateFormat(date) {
    if (!date || typeof date !== 'string') return false

    const dateRegex = /^\d{4}-\d{2}-\d{2}$/
    if (!dateRegex.test(date)) return false

    const parsedDate = new Date(`${date}T00:00:00`)
    return !Number.isNaN(parsedDate.getTime())
}

/**
 * Get current season year range
 * @returns {string} Season string in format "2024-25"
 */
export function getCurrentSeason() {
    const now = new Date()
    const currentYear = now.getFullYear()
    const currentMonth = now.getMonth()

    // NHL season typically starts in October
    const seasonYear = currentMonth < 9 ? currentYear - 1 : currentYear
    const nextYear = seasonYear + 1

    return `${seasonYear}-${nextYear.toString().slice(-2)}`
}

/**
 * Check if date is within reasonable range for NHL data
 * @param {string} date - Date string in YYYY-MM-DD format
 * @returns {boolean} True if date is within reasonable range
 */
export function isWithinNhlSeasonRange(date) {
    if (!isValidDateFormat(date)) return false

    const parsedDate = new Date(`${date}T00:00:00`)
    // Use a default date range since config service is removed
    const earliestDate = new Date('2020-10-01') // Start of 2020-21 season
    const today = new Date()

    return parsedDate >= earliestDate && parsedDate <= today
}

/**
 * Initialize NHL system
 */
export function initializeNhlApi() {
    logger.log('🚀 Initializing NHL system for local files')

    logger.log('✅ NHL system initialized for local files')
}
