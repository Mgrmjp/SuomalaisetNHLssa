/**
 * Type definitions for Finnish NHL Player Tracker
 * These types provide better TypeScript support and code documentation
 */

// Player data types
export interface Player {
    name: string
    team: string
    team_full: string
    position: string
    goals: number
    assists: number
    points: number
    opponent: string
    opponent_full: string
    game_score: string
    game_result: 'W' | 'L' | 'OT' | 'N/A'
}

// Game data types
export interface GameTeam {
    abbreviation: string
    locationName: string
    teamName: string
}

export interface GameScores {
    [teamAbbreviation: string]: number
    overtime?: boolean
}

export interface Game {
    teams: {
        away: GameTeam
        home: GameTeam
    }
    scores: GameScores
    goals?: Goal[]
}

export interface Goal {
    scorer: {
        player: string
    }
    assists?: Array<{
        player: string
    }>
    team: string
}

// API response types
export interface GameScheduleResponse {
    games: Game[]
}

export interface ApiStats {
    requests: number
    cacheHits: number
    errors: number
    totalResponseTime: number
    averageResponseTime: number
    cacheHitRate: number
}

// Store types
export interface PlayerStats {
    totalPlayers: number
    totalGoals: number
    totalAssists: number
    totalPoints: number
}

export interface CalendarDay {
    date: Date
    dateStr: string
    isCurrentMonth: boolean
    isToday: boolean
    isSelected: boolean
    hasData: boolean
    isFuture: boolean
}

// Configuration types
export interface ApiConfig {
    MAX_RETRIES: number
    BASE_RETRY_DELAY: number
    REQUEST_TIMEOUT: number
    CACHE_TTL: number
}

// Error types
export interface ApiError extends Error {
    status?: number
    endpoint?: string
    timestamp: Date
}

// Theme types
export type Theme = 'light' | 'dark' | 'system'

// Component props types
export interface PlayerCardProps {
    player: Player
}

export interface ModalProps {
    show: boolean
    title: string
}

export interface DateControlsProps {
    selectedDate?: string
    onDateChange?: (date: string) => void
}

export interface MonthViewProps {
    availableDates: string[]
    selectedDate: string
    onDateSelect: (date: string) => void
}

// Utility types
export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>
export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>

// Event handler types
export type DateChangeHandler = (date: string) => void
export type ThemeChangeHandler = (theme: Theme) => void
export type ModalCloseHandler = () => void
