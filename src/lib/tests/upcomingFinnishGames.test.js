// @ts-nocheck
import { describe, expect, it } from 'vitest'
import { selectUpcomingFinnishGames } from '$lib/utils/upcomingFinnishGames.js'

describe('upcoming Finnish games in the empty state', () => {
    const scheduled = [
        { gameId: 1, startTime: '2026-10-01T23:00:00Z', finnishPlayers: [{ name: 'Player One' }] },
        { gameId: 2, startTime: '2026-10-02T01:00:00Z', finnishPlayers: [{ name: 'Player Two' }] },
    ]
    const now = new Date('2026-10-01T12:00:00Z').getTime()

    it('shows roster-based upcoming games before boxscore lineups exist', () => {
        expect(selectUpcomingFinnishGames(scheduled, '2026-10-01', now)).toEqual([
            {
                ...scheduled[0],
                gameState: 'FUT',
                finnish_players_count: 1,
                finnishPlayers: ['Player One'],
            },
            {
                ...scheduled[1],
                gameState: 'FUT',
                finnish_players_count: 1,
                finnishPlayers: ['Player Two'],
            },
        ])
    })

    it('excludes started games and games before the selected date', () => {
        expect(selectUpcomingFinnishGames(scheduled, '2026-10-02', now)).toHaveLength(1)
        expect(
            selectUpcomingFinnishGames(
                scheduled,
                '2026-10-01',
                new Date('2026-10-02T02:00:00Z').getTime()
            )
        ).toEqual([])
    })

    it('never turns a completed game into an upcoming game even if its time is in the future', () => {
        const games = ['OFF', 'FINAL', 'LIVE', 'CRIT', 'IRT'].map((gameState, index) => ({
            ...scheduled[0],
            gameId: index,
            gameState,
        }))
        expect(selectUpcomingFinnishGames(games, '2026-10-01', now)).toEqual([])
    })

    it('merges lineup and roster sources without duplicate games or unnamed players', () => {
        const games = [
            { ...scheduled[0], finnishPlayers: ['Player One'], gameState: 'PRE' },
            scheduled[0],
            { ...scheduled[1], finnishPlayers: [{ name: '' }] },
        ]
        const result = selectUpcomingFinnishGames(games, '2026-10-01', now)
        expect(result).toHaveLength(1)
        expect(result[0].finnishPlayers).toEqual(['Player One'])
        expect(result[0].finnish_players_count).toBe(1)
    })

    it('sorts and limits games with known Finnish players', () => {
        const games = Array.from({ length: 6 }, (_, index) => ({
            gameId: index,
            startTime: `2026-10-0${index + 1}T23:00:00Z`,
            finnishPlayers: [{ name: 'Player One' }],
        })).reverse()
        games.push({ gameId: 7, startTime: '2026-10-01T23:00:00Z', finnishPlayers: [] })
        expect(
            selectUpcomingFinnishGames(games, '2026-10-01', now).map((game) => game.gameId)
        ).toEqual([0, 1, 2, 3])
    })
})
