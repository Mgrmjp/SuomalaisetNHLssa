// @ts-nocheck
import { describe, expect, it } from 'vitest'
import {
    previousCalendarDate,
    selectYesterdayResult,
    shouldShowYesterdayResult,
} from '../utils/yesterdayResult.js'

const date = '2026-10-31'
const game = (gameId, extra = {}) => ({
    gameId,
    awayTeam: 'CAR',
    homeTeam: 'FLA',
    awayScore: 2,
    homeScore: 3,
    gameState: 'OFF',
    ...extra,
})
const player = (game_id, extra = {}) => ({
    playerId: game_id,
    game_id,
    name: 'Pelaaja',
    position: 'C',
    time_on_ice: '18:00',
    goals: 0,
    assists: 0,
    ...extra,
})

describe('yesterday result', () => {
    it('uses calendar days across month, year and DST boundaries', () => {
        expect(previousCalendarDate('2026-11-01')).toBe('2026-10-31')
        expect(previousCalendarDate('2026-01-01')).toBe('2025-12-31')
        expect(previousCalendarDate('2026-03-30')).toBe('2026-03-29')
        expect(previousCalendarDate('2026-10-26')).toBe('2026-10-25')
    })

    it('shows the preview only on today before games have started', () => {
        expect(
            shouldShowYesterdayResult('2026-11-01', '2026-11-01', [game(1, { gameState: 'FUT' })])
        ).toBe(true)
        expect(shouldShowYesterdayResult('2026-10-31', '2026-11-01', [])).toBe(false)
        for (const gameState of ['LIVE', 'CRIT', 'IRT', 'OFF', 'FINAL']) {
            expect(
                shouldShowYesterdayResult('2026-11-01', '2026-11-01', [game(1, { gameState })])
            ).toBe(false)
        }
    })

    it('randomly selects among finished games with actual Finnish participants', () => {
        const data = {
            date,
            games: [
                game(1),
                game(2, { gameState: 'FINAL' }),
                game(3, { gameState: 'LIVE' }),
                game(4),
            ],
            players: [
                player(1, { goals: 1 }),
                player('2'),
                player(3),
                player(4, { time_on_ice: '00:00' }),
            ],
        }
        expect(selectYesterdayResult(data, date, 0).game.gameId).toBe(1)
        const result = selectYesterdayResult(data, date, 0.999)
        expect(result.game.gameId).toBe(2)
        expect(result.players.map((p) => p.game_id)).toEqual(['2'])
        expect(data.games).toHaveLength(4)
    })

    it('rejects missing, wrong-date, unfinished and malformed results', () => {
        expect(selectYesterdayResult(null, date)).toBeNull()
        expect(selectYesterdayResult({ date, games: [], players: [] }, date)).toBeNull()
        const data = { date, games: [game(1)], players: [player(1)] }
        expect(selectYesterdayResult(data, '2026-10-30')).toBeNull()
        for (const extra of [
            { gameState: 'FUT' },
            { homeScore: null },
            { awayScore: -1 },
            { homeScore: 'x' },
        ]) {
            expect(selectYesterdayResult({ ...data, games: [game(1, extra)] }, date)).toBeNull()
        }
    })
})
