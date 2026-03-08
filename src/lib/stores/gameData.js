import { derived, get, readonly, writable } from 'svelte/store'

import { getFinnishPlayersForDate, getGamesForDate } from '$lib/services/dataService.js'
import { StandingsService } from '$lib/services/standingsService.js'
import { formatDate as formatDateUtil } from '$lib/utils/dateUtils.js'
import logger from '$lib/utils/logger.js'

// Simple date formatting function
export const formatDate = formatDateUtil

// Simple browser check that works in test environment
const browser = typeof window !== 'undefined'

// Store for dynamically loaded available dates
const availableDatesStore = writable([])
let availableDatesLoaded = false

/**
 * Fetch available dates by scanning the data directory
 * This works on static sites by trying known date ranges
 */
import { base } from '$app/paths'

/**
 * Fetch available dates by scanning the data directory
 * This works on static sites by trying known date ranges
 */
const breaksStore = writable([])
export const breaks = readonly(breaksStore)

async function fetchBreaks() {
    try {
        const response = await fetch(`${base}/data/breaks.json`)
        if (response.ok) {
            const data = await response.json()
            breaksStore.set(data)
            logger.debug(`📅 Loaded ${data.length} schedule breaks`)
        }
    } catch (error) {
        logger.warn('Failed to load breaks:', error)
    }
}

async function fetchAvailableDates() {
    if (availableDatesLoaded) return

    // Load breaks in parallel
    fetchBreaks()

    try {
        // Try server API first (for dev mode or prerendered static API)
        const response = await fetch(`${base}/api/available-dates`)
        if (response.ok) {
            const dates = await response.json()
            availableDatesStore.set(dates)
            availableDatesLoaded = true
            logger.debug(`📅 Loaded ${dates.length} available game dates from API`)
            return
        }
    } catch (_error) {
        logger.debug('API not available, using fallback dates...')
    }

    // Hardcoded fallback if no dates found - updated to include latest dates
    const fallbackDates = [
        '2025-09-30',
        '2025-10-01',
        '2025-10-02',
        '2025-10-03',
        '2025-10-04',
        '2025-10-05',
        '2025-10-06',
        '2025-10-07',
        '2025-10-08',
        '2025-10-09',
        '2025-10-10',
        '2025-10-11',
        '2025-10-12',
        '2025-10-13',
        '2025-10-14',
        '2025-10-15',
        '2025-10-16',
        '2025-10-17',
        '2025-10-18',
        '2025-10-19',
        '2025-10-20',
        '2025-10-21',
        '2025-10-22',
        '2025-10-23',
        '2025-10-24',
        '2025-10-25',
        '2025-10-26',
        '2025-10-27',
        '2025-10-28',
        '2025-10-29',
        '2025-10-30',
        '2025-10-31',
        '2025-11-01',
        '2025-11-02',
        '2025-11-03',
        '2025-11-04',
        '2025-11-05',
        '2025-11-06',
        '2025-11-07',
        '2025-11-08',
        '2025-11-09',
        '2025-11-10',
        '2025-11-11',
        '2025-11-12',
        '2025-11-13',
        '2025-11-14',
        '2025-11-15',
        '2025-12-01',
        '2025-12-02',
        '2025-12-03',
        '2025-12-04',
        '2025-12-05',
        '2025-12-06',
        '2025-12-07',
        '2025-12-08',
        '2025-12-09',
        '2025-12-10',
        '2025-12-11',
        '2025-12-12',
        '2025-12-13',
        '2025-12-14',
        '2025-12-15',
        '2025-12-16',
        '2025-12-17',
        '2025-12-18',
        '2025-12-19',
        '2025-12-20',
        '2025-12-21',
        '2025-12-22',
        '2025-12-23',
        '2025-12-24',
        '2025-12-25',
        '2025-12-26',
        '2025-12-27',
        '2025-12-28',
        '2025-12-29',
        '2025-12-30',
        '2025-12-31',
        '2026-01-01',
        '2026-01-02',
        '2026-01-03',
        '2026-01-04',
        '2026-01-05',
        '2026-01-06',
        '2026-01-07',
        '2026-01-08',
        '2026-01-09',
        '2026-01-10',
        '2026-01-11',
        '2026-01-12',
        '2026-01-13',
        '2026-01-14',
        '2026-01-15',
        '2026-01-16',
        '2026-01-17',
        '2026-01-18',
        '2026-01-19',
        '2026-01-20',
        '2026-01-21',
        '2026-01-22',
        '2026-01-23',
        '2026-01-24',
        '2026-01-25',
        '2026-01-26',
        '2026-01-27',
        '2026-01-28',
        '2026-01-29',
        '2026-01-30',
        '2026-01-31',
        '2026-02-01',
        '2026-02-02',
        '2026-02-03',
        '2026-02-04',
        '2026-02-05',
        '2026-02-06',
        '2026-02-07',
        '2026-02-08',
        '2026-02-09',
        '2026-02-10',
        '2026-02-11',
        '2026-02-12',
        '2026-02-13',
        '2026-02-14',
        '2026-02-15',
        '2026-02-16',
        '2026-02-17',
        '2026-02-18',
        '2026-02-19',
        '2026-02-20',
        '2026-02-21',
        '2026-02-22',
        '2026-02-23',
        '2026-02-24',
        '2026-02-25',
        '2026-02-26',
        '2026-02-27',
        '2026-02-28',
        '2026-03-01',
        '2026-03-02',
        '2026-03-03',
        '2026-03-04',
        '2026-03-05',
        '2026-03-06',
        '2026-03-07',
        '2026-03-08',
        '2026-03-09',
        '2026-03-10',
        '2026-03-11',
        '2026-03-12',
        '2026-03-13',
        '2026-03-14',
        '2026-03-15',
        '2026-03-16',
        '2026-03-17',
        '2026-03-18',
        '2026-03-19',
        '2026-03-20',
        '2026-03-21',
        '2026-03-22',
        '2026-03-23',
        '2026-03-24',
        '2026-03-25',
        '2026-03-26',
        '2026-03-27',
        '2026-03-28',
        '2026-03-29',
        '2026-03-30',
        '2026-03-31',
        '2026-04-01',
        '2026-04-02',
        '2026-04-03',
        '2026-04-04',
        '2026-04-05',
        '2026-04-06',
        '2026-04-07',
        '2026-04-08',
        '2026-04-09',
        '2026-04-10',
        '2026-04-11',
        '2026-04-12',
        '2026-04-13',
        '2026-04-14',
        '2026-04-15',
        '2026-04-16',
        '2026-04-17',
        '2026-04-18',
        '2026-04-19',
        '2026-04-20',
        '2026-04-21',
        '2026-04-22',
        '2026-04-23',
        '2026-04-24',
        '2026-04-25',
        '2026-04-26',
        '2026-04-27',
        '2026-04-28',
        '2026-04-29',
        '2026-04-30',
        '2026-05-01',
        '2026-05-02',
        '2026-05-03',
        '2026-05-04',
        '2026-05-05',
        '2026-05-06',
        '2026-05-07',
        '2026-05-08',
        '2026-05-09',
        '2026-05-10',
        '2026-05-11',
        '2026-05-12',
        '2026-05-13',
        '2026-05-14',
        '2026-05-15',
        '2026-05-16',
        '2026-05-17',
        '2026-05-18',
        '2026-05-19',
        '2026-05-20',
        '2026-05-21',
        '2026-05-22',
        '2026-05-23',
        '2026-05-24',
        '2026-05-25',
        '2026-05-26',
        '2026-05-27',
        '2026-05-28',
        '2026-05-29',
        '2026-05-30',
        '2026-05-31',
        '2026-06-01',
        '2026-06-02',
        '2026-06-03',
        '2026-06-04',
        '2026-06-05',
        '2026-06-06',
        '2026-06-07',
        '2026-06-08',
        '2026-06-09',
        '2026-06-10',
    ]
    availableDatesStore.set(fallbackDates)
    availableDatesLoaded = true
    logger.debug(`📅 Using ${fallbackDates.length} fallback dates`)
}

// Initialize available dates on client side
if (browser) {
    fetchAvailableDates()
}

// Export available dates as a readable store
// Export available dates as a readable store
// Combine available dates with break dates so users can navigate to breaks
export const availableDates = derived(
    [availableDatesStore, breaksStore],
    ([$availableDates, $breaks]) => {
        const breakDates = []
        if ($breaks && $breaks.length > 0) {
            $breaks.forEach((b) => {
                const current = new Date(b.startDate)
                const end = new Date(b.endDate)
                while (current <= end) {
                    breakDates.push(current.toISOString().split('T')[0])
                    current.setDate(current.getDate() + 1)
                }
            })
        }

        // Merge and deduplicate
        const uniqueDates = new Set([...$availableDates, ...breakDates])
        return Array.from(uniqueDates).sort()
    }
)

// Earliest and latest dates (derived from available dates)
export const earliestPrepopulatedDate = derived(
    availableDates,
    ($availableDates) => $availableDates[0] || '2025-09-30'
)
export const latestPrepopulatedDate = derived(
    availableDates,
    ($availableDates) => $availableDates[$availableDates.length - 1] || '2026-01-03'
)

// Type definitions
/**
 * @typedef {Object} Player
 * @property {string} name
 * @property {string} team
 * @property {string} team_full
 * @property {string} position
 * @property {number} goals
 * @property {number} assists
 * @property {number} points
 * @property {number} penalty_minutes
 * @property {string} opponent
 * @property {string} opponent_full
 * @property {string} game_score
 * @property {string} game_result
 */

// Current date (dynamic for European audience to show last night's NHL games)
// Use a store to ensure currentDate is always reactive
export const currentDate = writable(new Date())

// Yesterday's date in YYYY-MM-DD format
export const yesterdayDate = derived(currentDate, ($currentDate) => {
    const yesterday = new Date($currentDate)
    yesterday.setDate(yesterday.getDate() - 1)
    return yesterday.toISOString().split('T')[0]
})

// Memory Management: Store interval ID for cleanup
let currentDateInterval = null

// Update currentDate every minute to keep it current
if (browser) {
    currentDateInterval = setInterval(() => {
        currentDate.set(new Date())
    }, 60000) // Update every minute
}

// Memory Management: Cleanup function for intervals
export function cleanupIntervals() {
    if (currentDateInterval) {
        clearInterval(currentDateInterval)
        currentDateInterval = null
    }
}

// Core stores
const selectedDateStore = writable('')
const isLoadingStore = writable(undefined)
const errorStore = writable(/** @type {string|null} */ (null))

// Public readonly stores
export const selectedDate = readonly(selectedDateStore)
export const isLoading = readonly(isLoadingStore)
export const error = readonly(errorStore)
// Re-export currentDate as readonly for external use
export { currentDate as currentDateReadOnly }

// Note: Data is loaded from prepopulated JSON files - no API calls

export const players = writable([])
export const games = writable({}) // Store games data with findGameById function

// Derived store for checking if selected date is in a break
export const currentBreak = derived([selectedDate, breaks], ([$selectedDate, $breaks]) => {
    if (!$selectedDate || !$breaks || $breaks.length === 0) return null

    return $breaks.find((b) => $selectedDate >= b.startDate && $selectedDate <= b.endDate) || null
})

// Derived store for display date with formatting - European friendly
export const displayDate = derived([selectedDate, currentDate], ([$selectedDate, $currentDate]) => {
    if (!$selectedDate) return ''

    const date = new Date(`${$selectedDate}T00:00:00`)
    const day = String(date.getDate()).padStart(2, '0')
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const year = date.getFullYear()
    let displayText = `${day}.${month}.${year}`

    // Add European-friendly date indicators
    const today = $currentDate.toISOString().split('T')[0]
    const yesterday = new Date($currentDate)
    yesterday.setDate(yesterday.getDate() - 1)
    const yesterdayStr = yesterday.toISOString().split('T')[0]

    if ($selectedDate === today) {
        displayText += ' (Tänä iltana)'
    } else if ($selectedDate === yesterdayStr) {
        displayText += ' (Viime yönä)'
    }

    return displayText
})

// Store for calendar view visibility
export const showCalendarView = writable(false)

// Standings stores
const selectedViewStore = writable('players') // 'players' | 'standings' | 'roster'
const standingsStore = writable({})
const standingsLoadingStore = writable(false)

// Public readonly stores for standings
export const selectedView = readonly(selectedViewStore)
export const standings = readonly(standingsStore)
export const standingsLoading = readonly(standingsLoadingStore)

// Prospects store
const prospectsStore = writable([])
const prospectsLoadingStore = writable(false)
export const prospects = readonly(prospectsStore)
export const prospectsLoading = readonly(prospectsLoadingStore)

// Draft Rankings store
const draftRankingsStore = writable({ year: 2026, sources: [] })
export const draftRankings = readonly(draftRankingsStore)

export async function loadProspects() {
    prospectsLoadingStore.set(true)
    try {
        const [prospectsRes, rankingsRes] = await Promise.all([
            fetch(`${base}/data/finnish_prospects.json`),
            fetch(`${base}/data/finnish_draft_rankings.json`),
        ])

        if (prospectsRes.ok) {
            const data = await prospectsRes.json()
            prospectsStore.set(data)
            logger.debug(`Loaded ${data.length} prospects`)
        }

        if (rankingsRes.ok) {
            const rankings = await rankingsRes.json()
            draftRankingsStore.set(rankings)
            logger.debug(`Loaded draft rankings for ${rankings.year} with ${rankings.sources?.length || 0} sources`)
        }
    } catch (error) {
        logger.error('Failed to load prospects data:', error)
    } finally {
        prospectsLoadingStore.set(false)
    }
}

// Standings service instance
const standingsService = new StandingsService()

// Function to set the current view
export function setView(view) {
    if (view === 'players' || view === 'standings' || view === 'roster') {
        selectedViewStore.set(view)
    }
}

/**
 * Load standings data
 * @param {string} seasonStart - Season start date (YYYY-MM-DD)
 * @returns {Promise<object>} Standings data
 */
export async function loadStandings(seasonStart = earliestPrepopulatedDate) {
    standingsLoadingStore.set(true)

    try {
        logger.debug('📊 Starting standings calculation from', seasonStart)
        const standingsData = await standingsService.calculateSeasonStandings(seasonStart)
        logger.debug('📊 Standings calculation result:', standingsData)
        logger.debug('📊 Eastern conference keys:', Object.keys(standingsData?.eastern || {}))
        logger.debug('📊 Western conference keys:', Object.keys(standingsData?.western || {}))
        standingsStore.set(standingsData)
        logger.success('Standings loaded successfully')
        return standingsData
    } catch (error) {
        logger.error('Error loading standings:', error)
        standingsStore.set({})
        throw error
    } finally {
        standingsLoadingStore.set(false)
    }
}

/**
 * Clear standings cache and reload
 * @param {string} seasonStart - Season start date
 * @returns {Promise<object>} Updated standings data
 */
export async function refreshStandings(seasonStart = earliestPrepopulatedDate) {
    standingsService.clearCache()
    return await loadStandings(seasonStart)
}

// Store for active button state - optimized
export const activeButton = derived(
    [selectedDate, currentDate],
    ([$selectedDate, $currentDate]) => {
        const today = $currentDate.toISOString().split('T')[0]
        const yesterday = new Date($currentDate)
        yesterday.setDate(yesterday.getDate() - 1)
        const yesterdayStr = yesterday.toISOString().split('T')[0]

        if ($selectedDate === today) return 'today'
        if ($selectedDate === yesterdayStr) return 'yesterday'
        return ''
    }
)

// Store for statistics
export const playerStats = derived([players], ([$players]) => {
    if (!$players || $players.length === 0) {
        return {
            totalPlayers: 0,
            totalGoals: 0,
            totalAssists: 0,
            totalPoints: 0,
        }
    }

    return $players.reduce(
        /** @param {{totalPlayers: number, totalGoals: number, totalAssists: number, totalPoints: number}} stats */
        /** @param {Player} player */
        (stats, player) => {
            stats.totalPlayers++
            stats.totalGoals += player.goals || 0
            stats.totalAssists += player.assists || 0
            stats.totalPoints += player.points || 0
            return stats
        },
        {
            totalPlayers: 0,
            totalGoals: 0,
            totalAssists: 0,
            totalPoints: 0,
        }
    )
})

/**
 * Load players for a specific date
 * @param {string} date - Date in YYYY-MM-DD format
 * @returns {Promise<Player[]>} Array of players
 */
export async function loadPlayersForDate(date) {
    if (!date) {
        players.set([])
        return []
    }

    // Validate that we're loading data for the currently selected date
    let currentSelectedDate
    const unsubscribe = selectedDateStore.subscribe((value) => {
        currentSelectedDate = value
    })
    unsubscribe()

    if (currentSelectedDate && currentSelectedDate !== date) {
        console.warn(
            `⚠️ Skipping UI update for ${date} because selected date is ${currentSelectedDate}`
        )
        // Still return the data but don't update the UI
        // Data is loaded from prepopulated files only
        return []
    }

    logger.debug(`📊 Loading players for UI display for date: ${date}`)

    isLoadingStore.set(true)
    errorStore.set(null)

    try {
        // Get data from prepopulated JSON files only
        const [fetchedPlayers, gamesData] = await Promise.all([
            getFinnishPlayersForDate(date),
            getGamesForDate(date),
        ])

        // Update the players store
        players.set(fetchedPlayers)

        // Update the games store
        games.set(gamesData)

        logger.success(
            `Loaded ${fetchedPlayers.length} players and ${gamesData.games.length} games from prepopulated data for ${date}`
        )

        return fetchedPlayers
    } catch (err) {
        logger.error('Error loading player data:', err)

        // Provide more specific error messages based on the error type
        let errorMessage = 'Failed to load player data. Please try again.'

        if (err.message?.includes('fetch')) {
            errorMessage = 'Unable to load prepopulated data. Please try again.'
        }

        errorStore.set(errorMessage)
        players.set([])
        return []
    } finally {
        isLoadingStore.set(false)
    }
}

// Function to set date and load data
/**
 * @param {string} date
 * @returns {Promise<Player[]>}
 */
export async function setDate(date) {
    selectedDateStore.set(date)
    return await loadPlayersForDate(date)
}

/**
 * Reset the application to its default state
 * (yesterday's date, players view, calendar closed)
 */
export async function resetToDefault() {
    const yesterday = get(yesterdayDate)
    const latestDate = get(latestPrepopulatedDate)

    // Reset view and calendar
    selectedViewStore.set('players')
    showCalendarView.set(false)

    // Reset date (prefer yesterday, fallback to latest prepopulated)
    const defaultDate = yesterday || latestDate
    if (defaultDate) {
        return await setDate(defaultDate)
    }
}
