import { derived, readonly, writable } from 'svelte/store'

import { getFinnishPlayersForDate, getGamesForDate } from '$lib/services/dataService.js'
import { StandingsService } from '$lib/services/standingsService.js'
import logger from '$lib/utils/logger.js'
import { formatDate as formatDateUtil } from '$lib/utils/dateHelpers.js'

// Simple date formatting function
export const formatDate = formatDateUtil

// Simple browser check that works in test environment
const browser = typeof window !== 'undefined'

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
export const games = writable({})  // Store games data with findGameById function

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
const selectedViewStore = writable('players') // 'players' | 'standings'
const standingsStore = writable({})
const standingsLoadingStore = writable(false)

// Public readonly stores for standings
export const selectedView = readonly(selectedViewStore)
export const standings = readonly(standingsStore)
export const standingsLoading = readonly(standingsLoadingStore)

// Standings service instance
const standingsService = new StandingsService()

// Function to set the current view
export function setView(view) {
	if (view === 'players' || view === 'standings') {
		selectedViewStore.set(view)
	}
}

/**
 * Load standings data
 * @param {string} seasonStart - Season start date (YYYY-MM-DD)
 * @returns {Promise<object>} Standings data
 */
export async function loadStandings(seasonStart = '2025-10-01') {
	standingsLoadingStore.set(true)

	try {
		const standingsData = await standingsService.calculateSeasonStandings(seasonStart)
		standingsStore.set(standingsData)
		logger.log('✅ Standings loaded successfully')
		return standingsData
	} catch (error) {
		logger.log(`❌ Error loading standings: ${error.message}`)
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
export async function refreshStandings(seasonStart = '2025-10-01') {
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

// Store for available dates with data
export const availableDates = derived([currentDate], ([$currentDate]) => {
    // For real API, we can generate dates for the current season
    // This could be expanded to include more dates as needed
    const dates = []
    const today = new Date($currentDate)
    const seasonStart = new Date(today.getFullYear() - 1, 9, 1) // October 1 of last year

    const current = new Date(seasonStart)
    while (current <= today) {
        dates.push(formatDate(new Date(current)))
        current.setDate(current.getDate() + 1)
    }

    return dates.reverse()
})

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

    logger.log(`📊 Loading players for UI display for date: ${date}`)

    isLoadingStore.set(true)
    errorStore.set(null)

    try {
        // Get data from prepopulated JSON files only
        const [fetchedPlayers, gamesData] = await Promise.all([
            getFinnishPlayersForDate(date),
            getGamesForDate(date)
        ])

        // Update the players store
        players.set(fetchedPlayers)

        // Update the games store
        games.set(gamesData)

        logger.log(
            `✅ Loaded ${fetchedPlayers.length} players and ${gamesData.games.length} games from prepopulated data for ${date}`
        )

        return fetchedPlayers
    } catch (err) {
        console.error('Error loading player data:', err)

        // Provide more specific error messages based on the error type
        let errorMessage = 'Failed to load player data. Please try again.'

        if (err.message?.includes('fetch')) {
            errorMessage =
                'Unable to load prepopulated data. Please try again.'
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
