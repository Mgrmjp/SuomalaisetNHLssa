import { afterEach, describe, expect, it, vi } from 'vitest'
import { getResultsForDate } from '../services/dataService.js'

afterEach(() => vi.unstubAllGlobals())

describe('results snapshots', () => {
    it('loads scores and players with one uncached request', async () => {
        const game = { gameId: 1, homeScore: 3, awayScore: 2 }
        const fetch = vi.fn(async () => ({
            ok: true,
            json: async () => ({ date: '2026-10-01', games: [game], players: [{ points: 1 }] }),
        }))
        vi.stubGlobal('fetch', fetch)
        const snapshot = await getResultsForDate('2026-10-01')
        expect(fetch).toHaveBeenCalledOnce()
        expect(fetch).toHaveBeenCalledWith(
            expect.stringMatching(/2026-10-01.json\?t=\d+/),
            expect.objectContaining({ cache: 'no-store' })
        )
        expect(snapshot.games.findGameById(1)).toEqual(game)
        expect(snapshot.players[0].points).toBe(1)
    })

    it('rejects HTTP errors so the caller can preserve the existing snapshot', async () => {
        vi.stubGlobal(
            'fetch',
            vi.fn(async () => ({ ok: false, status: 503 }))
        )
        await expect(getResultsForDate('2026-10-01')).rejects.toThrow('HTTP 503')
    })

    it('rejects a missing file instead of replacing results with an empty list', async () => {
        vi.stubGlobal(
            'fetch',
            vi.fn(async () => ({ ok: false, status: 404 }))
        )
        await expect(getResultsForDate('2026-10-01')).rejects.toThrow('HTTP 404')
    })

    it('rejects malformed data and data for another date', async () => {
        for (const data of [
            { date: '2026-10-01', games: [] },
            { date: '2026-09-30', games: [], players: [] },
        ]) {
            vi.stubGlobal(
                'fetch',
                vi.fn(async () => ({ ok: true, json: async () => data }))
            )
            await expect(getResultsForDate('2026-10-01')).rejects.toThrow('Incomplete results')
        }
    })
})
