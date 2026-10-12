// NHL API Integration for Finnish Player Tracker
// Contains only validation functions and utility functions, no API calls
// All data is now loaded from JSON files in the browser

// Note: Previous API statistics and stub functions have been removed as they were no longer functional.

/**
 * Validate date string format and reject impossible calendar dates.
 * UTC-based, so the result does not depend on the runtime time zone.
 * @param {unknown} date - Date string to validate
 * @returns {boolean} True if date is a real calendar date in YYYY-MM-DD format
 */
export function isValidDateFormat(date) {
    if (!date || typeof date !== 'string') return false

    const match = date.match(/^(\d{4})-(\d{2})-(\d{2})$/)
    if (!match) return false

    const [, yearText, monthText, dayText] = match
    const year = Number(yearText)
    const month = Number(monthText)
    const day = Number(dayText)
    const parsedDate = new Date(`${date}T00:00:00Z`)

    return (
        !Number.isNaN(parsedDate.getTime()) &&
        parsedDate.getUTCFullYear() === year &&
        parsedDate.getUTCMonth() === month - 1 &&
        parsedDate.getUTCDate() === day
    )
}

/**
 * Get current season year range
 * @returns {string} Season string in format "2025-26"
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
 * Check if date is within the supported NHL data range
 * @param {string} date - Date string in YYYY-MM-DD format
 * @returns {boolean} True if date is within the supported range
 */
export function isWithinNhlSeasonRange(date) {
    if (!isValidDateFormat(date)) return false

    const parsedDate = new Date(`${date}T00:00:00Z`)

    return (
        parsedDate >= new Date('2015-10-01T00:00:00Z') &&
        parsedDate < new Date('2027-01-01T00:00:00Z')
    )
}
