// @ts-nocheck
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const article = {
    title: 'Aleksander Barkov returns to practice',
    summary: 'Barkov practised with the Panthers.',
    url: 'https://www.nhl.com/panthers/news/barkov',
    source: 'NHL.com',
    publishedAt: '2026-11-01T09:00:00Z',
    publicationVerified: true,
    publicationSource: 'article:published_time',
    matchedPlayers: ['Aleksander Barkov'],
}
const response = () => ({ ok: true, json: async () => ({ byDate: { '2026-11-01': [article] } }) })

beforeEach(() => {
    vi.resetModules()
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-11-01T12:00:00Z'))
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(response()))
})
afterEach(() => {
    vi.useRealTimers()
    vi.unstubAllGlobals()
})

describe('news index refresh', () => {
    it('loads once per hour and retries failed initial loads', async () => {
        const { getDailyFallbackNews } = await import('$lib/services/dailyNewsService.js')
        fetch.mockRejectedValueOnce(new Error('offline'))
        expect(await getDailyFallbackNews('2026-11-01')).toEqual([])
        expect(await getDailyFallbackNews('2026-11-01')).toHaveLength(1)
        await getDailyFallbackNews('2026-11-01')
        expect(fetch).toHaveBeenCalledTimes(2)
        vi.setSystemTime(new Date('2026-11-01T13:00:00Z'))
        await getDailyFallbackNews('2026-11-01')
        expect(fetch).toHaveBeenCalledTimes(3)
    })
    it('preserves good data on refresh failure but expires stories at 48 hours', async () => {
        const { getDailyFallbackNews } = await import('$lib/services/dailyNewsService.js')
        expect(await getDailyFallbackNews('2026-11-01')).toHaveLength(1)
        fetch.mockRejectedValue(new Error('offline'))
        vi.setSystemTime(new Date('2026-11-01T13:00:00Z'))
        expect(await getDailyFallbackNews('2026-11-01')).toHaveLength(1)
        vi.setSystemTime(new Date('2026-11-03T09:00:01Z'))
        expect(await getDailyFallbackNews('2026-11-03')).toEqual([])
    })
    it('does not replace a valid index with a malformed response', async () => {
        const { getDailyFallbackNews } = await import('$lib/services/dailyNewsService.js')
        await getDailyFallbackNews('2026-11-01')
        vi.setSystemTime(new Date('2026-11-01T13:00:00Z'))
        fetch.mockResolvedValue({ ok: true, json: async () => ({ byDate: [] }) })
        expect(await getDailyFallbackNews('2026-11-01')).toHaveLength(1)
    })
})
