import { get } from 'svelte/store'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { getResultsForDate } from '../services/dataService.js'

vi.mock('$lib/services/dataService.js', () => ({ getResultsForDate: vi.fn() }))
vi.mock('$lib/services/standingsService.js', () => ({ StandingsService: class {} }))

/** @type {typeof import('../stores/gameData.js') | undefined} */
let stores

async function setup() {
    vi.useFakeTimers()
    vi.setSystemTime(new Date(2026, 9, 2, 12))
    vi.spyOn(document, 'visibilityState', 'get').mockReturnValue('visible')
    vi.stubGlobal(
        'fetch',
        vi.fn(async () => ({ ok: false }))
    )
    stores = await import('../stores/gameData.js')
    vi.mocked(getResultsForDate).mockResolvedValue({
        players: [{ name: 'Finn', points: 1 }],
        games: { games: [{ gameId: 1, homeScore: 1 }], findGameById: () => null },
    })
    await stores.resetToDefault()
    return stores
}

afterEach(() => {
    stores?.cleanupIntervals()
    vi.restoreAllMocks()
    vi.clearAllMocks()
    vi.unstubAllGlobals()
    vi.useRealTimers()
    vi.resetModules()
})

describe('automatic results refresh', () => {
    it('refreshes the selected date without hiding the current results', async () => {
        const stores = await setup()
        vi.mocked(getResultsForDate).mockResolvedValue({
            players: [{ name: 'Finn', points: 2 }],
            games: { games: [{ gameId: 1, homeScore: 2 }], findGameById: () => null },
        })
        await vi.advanceTimersByTimeAsync(60000)
        expect(get(stores.players)[0]?.points).toBe(2)
        expect(get(stores.games).games[0].homeScore).toBe(2)
        expect(get(stores.isLoading)).toBe(false)
    })

    it('keeps the last results when the background request fails', async () => {
        const stores = await setup()
        vi.mocked(getResultsForDate).mockRejectedValue(new Error('Network unavailable'))
        await vi.advanceTimersByTimeAsync(60000)
        expect(get(stores.players)[0]?.points).toBe(1)
        expect(get(stores.games).games[0].homeScore).toBe(1)
        expect(get(stores.isLoading)).toBe(false)
    })

    it('refreshes on returning to the tab', async () => {
        await setup()
        vi.mocked(getResultsForDate).mockClear()
        document.dispatchEvent(new Event('visibilitychange'))
        await vi.advanceTimersByTimeAsync(0)
        expect(getResultsForDate).toHaveBeenCalledWith('2026-10-01')
    })

    it('follows yesterday across midnight but preserves a manually chosen date', async () => {
        const stores = await setup()
        vi.setSystemTime(new Date(2026, 9, 3, 0, 1))
        await vi.advanceTimersByTimeAsync(60000)
        expect(get(stores.selectedDate)).toBe('2026-10-02')
        await stores.setDate('2026-09-30')
        vi.setSystemTime(new Date(2026, 9, 4, 0, 1))
        await vi.advanceTimersByTimeAsync(60000)
        expect(get(stores.selectedDate)).toBe('2026-09-30')
    })

    it('does not apply an old refresh after navigating to another date', async () => {
        const stores = await setup()
        /** @type {((value: Awaited<ReturnType<typeof getResultsForDate>>) => void) | undefined} */
        let resolveOld
        vi.mocked(getResultsForDate).mockImplementationOnce(
            () =>
                new Promise((resolve) => {
                    resolveOld = resolve
                })
        )
        const refreshing = stores.refreshSelectedDate()
        await stores.setDate('2026-09-30')
        if (!resolveOld) throw new Error('Background request did not start')
        resolveOld({
            players: [{ name: 'Wrong date', points: 99 }],
            games: { games: [], findGameById: () => null },
        })
        await refreshing
        expect(get(stores.selectedDate)).toBe('2026-09-30')
        expect(get(stores.players)[0]?.name).toBe('Finn')
    })
})
