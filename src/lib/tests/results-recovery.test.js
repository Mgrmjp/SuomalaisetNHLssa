import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { getResultsForDate } from '../services/dataService.js'
import { isPlayerGameLive, shouldShowGameResult } from '../utils/gameStateHelpers.mjs'

const date = '2026-11-19'
const game = {
    gameId: 2026020357,
    awayTeam: 'VAN',
    homeTeam: 'SEA',
    awayScore: 1,
    homeScore: 1,
    gameState: 'LIVE',
    period: 2,
    startTime: '2026-11-20T02:40:00Z',
}
const player = {
    team: 'VAN',
    game_id: game.gameId,
    game_date: date,
    game_status: 'OFF',
    game_result: 'T',
    game_score: '1-1',
    saves: 28,
}
const snapshot = {
    date,
    generated_at: '2026-11-20T04:01:42.822728',
    games: [game],
    players: [player],
}
const event = {
    date: '2026-11-20T02:40Z',
    competitions: [
        {
            competitors: [
                { homeAway: 'home', team: { abbreviation: 'SEA' }, score: '5' },
                { homeAway: 'away', team: { abbreviation: 'VAN' }, score: '1' },
            ],
            status: {
                period: 3,
                type: { name: 'STATUS_FINAL', state: 'post', completed: true },
            },
        },
    ],
}
/** @param {unknown} data */
const jsonResponse = (data) => ({ ok: true, json: async () => data })
const fetchMock = vi.fn()

beforeEach(() => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-11-20T09:00:00Z'))
    fetchMock.mockReset()
    vi.stubGlobal('fetch', fetchMock)
})

afterEach(() => {
    vi.unstubAllGlobals()
    vi.useRealTimers()
})

describe('results recovery during a missed deployment', () => {
    it('uses the game state even if a legacy player record says finished', async () => {
        fetchMock.mockResolvedValueOnce(
            jsonResponse({ ...snapshot, generated_at: '2026-11-20T08:59:00Z' })
        )
        const result = await getResultsForDate(date)
        expect(isPlayerGameLive(player, result.games)).toBe(true)
        expect(shouldShowGameResult(player, result.games)).toBe(false)
        expect(fetchMock).toHaveBeenCalledTimes(1)
    })

    it('flags overdue results when no matching final can be verified', async () => {
        fetchMock
            .mockResolvedValueOnce(jsonResponse(snapshot))
            .mockResolvedValueOnce(
                jsonResponse({ events: [{ ...event, date: '2026-11-19T02:40Z' }] })
            )
        const result = await getResultsForDate(date)
        expect(result.games.games[0]).toMatchObject({
            gameState: 'LIVE',
            homeScore: 1,
            resultDelayed: true,
        })
        expect(isPlayerGameLive(player, result.games)).toBe(false)
        expect(shouldShowGameResult(player, result.games)).toBe(false)
    })

    it('keeps the last score and player stats when the scoreboard request fails', async () => {
        fetchMock
            .mockResolvedValueOnce(jsonResponse(snapshot))
            .mockRejectedValueOnce(new Error('Scoreboard unavailable'))
        const result = await getResultsForDate(date)
        expect(result.games.games[0]).toEqual({ ...game, resultDelayed: true })
        expect(result.players[0]).toEqual(player)
    })

    it('preserves a verified final when a newer snapshot still has incomplete stats', async () => {
        const finalSnapshot = {
            ...snapshot,
            games: [{ ...game, gameState: 'OFF', homeScore: 5, period: 3 }],
            players: [{ ...player, game_score: '1-5', game_result: 'L', saves: 38 }],
        }
        fetchMock
            .mockResolvedValueOnce(jsonResponse(snapshot))
            .mockResolvedValueOnce(jsonResponse({ events: [event] }))
            .mockResolvedValueOnce(
                jsonResponse({ ...snapshot, generated_at: '2026-11-20T08:59:00Z' })
            )
            .mockResolvedValueOnce(jsonResponse(finalSnapshot))

        for (let attempt = 0; attempt < 2; attempt++) {
            const result = await getResultsForDate(date)
            expect(result.games.games[0]).toMatchObject({
                gameState: 'FINAL',
                homeScore: 5,
                period: 3,
                playerStatsPending: true,
            })
            expect(result.players[0]).toMatchObject({
                game_score: '1-5',
                game_result: 'L',
                saves: 28,
            })
        }

        const result = await getResultsForDate(date)
        expect(result.games.games[0]).toEqual(finalSnapshot.games[0])
        expect(result.players[0].saves).toBe(38)
        expect(fetchMock).toHaveBeenCalledTimes(4)
    })
})
