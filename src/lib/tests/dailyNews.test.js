import { describe, expect, it } from 'vitest'

import { getIsoWeekKey, selectDailyNews } from '$lib/utils/dailyNews.js'

describe('dailyNews helpers', () => {
    it('builds ISO week keys from daily dates', () => {
        expect(getIsoWeekKey('2026-04-13')).toBe('2026-W16')
        expect(getIsoWeekKey('2025-12-31')).toBe('2026-W01')
    })

    it('prefers exact-date news over weekly fallback', () => {
        const newsIndex = {
            byDate: {
                '2026-04-13': [{ id: 'exact-1' }, { id: 'exact-2' }],
            },
            byWeek: {
                '2026-W16': [{ id: 'week-1' }],
            },
        }

        expect(selectDailyNews(newsIndex, '2026-04-13')).toEqual([
            { id: 'exact-1' },
            { id: 'exact-2' },
        ])
    })

    it('falls back to weekly news when the exact date is missing', () => {
        const newsIndex = {
            byDate: {},
            byWeek: {
                '2026-W16': [
                    { id: 'week-1' },
                    { id: 'week-2' },
                    { id: 'week-3' },
                    { id: 'week-4' },
                ],
            },
        }

        expect(selectDailyNews(newsIndex, '2026-04-15')).toEqual([
            { id: 'week-1' },
            { id: 'week-2' },
            { id: 'week-3' },
        ])
    })
})
