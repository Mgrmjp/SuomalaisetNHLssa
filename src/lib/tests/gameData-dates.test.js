import { get } from 'svelte/store'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { getResultsForDate } from '../services/dataService.js'

vi.mock('$app/paths', () => ({ base: '' }))
vi.mock('$lib/services/dataService.js', () => ({
    getResultsForDate: vi.fn(),
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

    it('defaults to yesterday in the visitor timezone just after midnight', async () => {
        vi.stubGlobal(
            'fetch',
            vi.fn(async () => ({ ok: false }))
        )
        vi.mocked(getResultsForDate).mockResolvedValue({
            players: [],
            games: { games: [], findGameById: () => null },
        })
        stores = await import('../stores/gameData.js')
        stores.currentDate.set(new Date(2026, 9, 2, 0, 30))

        await stores.resetToDefault()

        expect(get(stores.selectedDate)).toBe('2026-10-01')
        expect(get(stores.displayDate)).toBe('01.10.2026 (Viime yönä)')
        expect(get(stores.activeButton)).toBe('yesterday')
        expect(getResultsForDate).toHaveBeenCalledWith('2026-10-01')
    })
})
