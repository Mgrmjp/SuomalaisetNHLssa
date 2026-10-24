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
    stores?.cleanupGameData()
    vi.unstubAllGlobals()
    vi.useRealTimers()
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
        stores.initializeGameData()
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

    it('retries a failed date index and picks up new dates in an open tab', async () => {
        vi.useFakeTimers()
        vi.setSystemTime(new Date(2026, 9, 22, 12))
        /** @type {string[] | null} */
        let dates = null
        const fetch = vi.fn(async (url) => {
            if (url.includes('breaks.json')) return { ok: true, json: async () => [] }
            return dates ? { ok: true, json: async () => dates } : { ok: false, status: 503 }
        })
        vi.stubGlobal('fetch', fetch)

        stores = await import('../stores/gameData.js')
        stores.initializeGameData()
        await vi.advanceTimersByTimeAsync(0)
        expect(get(stores.prepopulatedDates)).toEqual([])

        dates = ['2026-10-22']
        await vi.advanceTimersByTimeAsync(60000)
        expect(get(stores.prepopulatedDates)).toEqual(['2026-10-22'])

        dates = ['2026-10-22', '2026-10-23']
        await vi.advanceTimersByTimeAsync(5 * 60000)
        expect(get(stores.prepopulatedDates)).toEqual(dates)

        dates = null
        await vi.advanceTimersByTimeAsync(5 * 60000)
        expect(get(stores.prepopulatedDates)).toEqual(['2026-10-22', '2026-10-23'])
    })
})
