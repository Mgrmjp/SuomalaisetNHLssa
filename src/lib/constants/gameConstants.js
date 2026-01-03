/**
 * Game Constants
 *
 * Centralized constants for game-related logic
 */

/** Position type classifications for filtering and display */
export const POSITION_TYPES = {
    GOALIE: ['G', 'GOALIE'],
    DEFENSE: ['D', 'LD', 'RD', 'DEFENSE'],
    FORWARD: ['LW', 'RW', 'C', 'LEFT', 'RIGHT', 'CENTER'],
}

/** Minimum stat thresholds for filtering players */
export const STAT_THRESHOLDS = {
    POINTS: 1,
    GOALS: 1,
    ASSISTS: 1,
}

/** Date-related constants */
export const DATE_CONSTANTS = {
    /** Earliest prepopulated date in the system */
    EARLIEST_DATE: '2020-10-01',
    /** Date format used throughout the application */
    DATE_FORMAT: 'YYYY-MM-DD',
}

/** Animation constants for snowfall and other effects */
export const ANIMATION = {
    /** Snowflake distribution factor (137.5 = golden angle) */
    SNOWFLAKE_DISTRIBUTION: 137.5,
}
