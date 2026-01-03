/**
 * Type definitions for Finnish NHL Player Tracker
 * These types provide better TypeScript support and code documentation
 */

// Recent game result type
export interface RecentGame {
    date: string
    opponent: string
    opponent_full: string
    team_score: number
    opponent_score: number
    result: 'W' | 'L' | 'OT' | 'SOW' | 'SOL' | 'OTW' | 'OTL'
    goals?: number
    assists?: number
    points?: number
}

// Player data types
export interface Player {
    name: string
    team: string
    team_full: string
    position: string
    goals: number
    assists: number
    points: number
    empty_net_goals?: number // Number of empty net goals scored (skaters) or allowed (goalies)
    opponent: string
    opponent_full: string
    game_score: string
    game_result: 'W' | 'L' | 'OT' | 'N/A'
    // Additional optional fields
    playerId?: number
    jersey_number?: number
    age?: number
    birth_date?: string
    birthplace?: string
    status?: string
    game_venue?: string
    game_city?: string
    game_id?: number
    game_date?: string
    game_status?: string
    headshot_url?: string
    saves?: number // For goalies
    shots_against?: number // For goalies
    save_percentage?: number // For goalies
    goals_against?: number // For goalies
    penalty_minutes?: number
    plus_minus?: number
    time_on_ice?: string
    shots?: number
    hits?: number
    blocked_shots?: number
    takeaways?: number
    giveaways?: number
    power_play_goals?: number
    short_handed_goals?: number
    even_strength_goals?: number
    shifts?: number
    created_at?: string
    recent_results?: RecentGame[] // Last 10 games
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
