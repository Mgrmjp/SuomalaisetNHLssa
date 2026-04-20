export { getCurrentSeason } from './lib/api/nhlApi.js'

/**
 * @param {unknown} date
 * @returns {boolean}
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
 * @param {unknown} date
 * @returns {boolean}
 */
export function isWithinNhlSeasonRange(date) {
    if (!isValidDateFormat(date)) return false

    const parsedDate = new Date(`${date}T00:00:00Z`)

    return (
        parsedDate >= new Date('2015-10-01T00:00:00Z') &&
        parsedDate < new Date('2027-01-01T00:00:00Z')
    )
}
