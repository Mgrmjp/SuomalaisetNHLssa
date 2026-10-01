import { get } from 'svelte/store'
import { afterEach, describe, expect, it, vi } from 'vitest'

vi.mock('$app/paths', () => ({ base: '' }))
vi.mock('$lib/services/dataService.js', () => ({
    getFinnishPlayersForDate: vi.fn(),
    getGamesForDate: vi.fn(),
}))
vi.mock('$lib/services/standingsService.js', () => ({
    StandingsService: class {},
}))

/** @type {typeof import("../stores/gameData.js") | undefined} */
let stores

afterEach(() => {
    stores?.cleanupIntervals()
    vi.unstubAllGlobals()
    vi.resetModules()
})

describe('game file dates', () => {
    it('excludes navigation-only break dates from game file lookups', async () => {
        vi.stubGlobal(
            'fetch',
            vi.fn(async (url) => ({
                ok: true,
                json: async () =>
                    url.endsWith('/breaks.json')
                        ? [{ startDate: '2026-09-28', endDate: '2026-09-28', type: 'offseason' }]
                        : ['2026-09-30', '2026-10-01'],
            }))
        )

        const loadedStores = await import('../stores/gameData.js')
        stores = loadedStores
        await vi.waitFor(() => {
            expect(get(loadedStores.availableDates)).toContain('2026-09-28')
        })

        expect(stores.prepopulatedDates).toBeDefined()
        expect(get(stores.prepopulatedDates)).toEqual(['2026-09-30', '2026-10-01'])
    })
})
