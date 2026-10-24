import { describe, expect, it, vi } from 'vitest'

vi.mock('$lib/server/playerStats.js', () => ({
    getCurrentSeasonId: () => '20262027',
    getStatsUpdatedAt: () => null,
    loadSkaterStatsFromDisk: () => {
        throw new Error('missing file')
    },
    loadRegularSeasonStatsFromDisk: () => {
        throw new Error('missing file')
    },
    fetchStats: () => Promise.reject(new Error('API unavailable')),
    fetchRegularSeasonStats: () => Promise.reject(new Error('API unavailable')),
}))

describe('season statistics page errors', () => {
    it('keeps the season label available when leaderboard data fails', async () => {
        const { load } = await import('../../routes/pisteporssi/+page.server.js')
        const result = await load(/** @type {any} */ ({ fetch: vi.fn() }))
        expect(result).toMatchObject({
            players: [],
            seasonId: '20262027',
            error: expect.any(String),
        })
    })

    it('keeps the season label available when player-list data fails', async () => {
        const { load } = await import('../../routes/pelaajat/+page.server.js')
        const result = await load(/** @type {any} */ ({ fetch: vi.fn() }))
        expect(result).toMatchObject({
            skaters: [],
            goalies: [],
            seasonId: '20262027',
            error: expect.any(String),
        })
    })
})
