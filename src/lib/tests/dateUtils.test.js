import { expect, it } from 'vitest'
import { getRelativeFinnishDate } from '$lib/utils/dateUtils.js'

it('uses calendar days across the Finnish daylight-saving change', () => {
    const previousTimeZone = process.env.TZ
    process.env.TZ = 'Europe/Helsinki'
    try {
        expect(getRelativeFinnishDate('2026-03-30', new Date(2026, 2, 29, 12))).toBe('huomenna')
        expect(getRelativeFinnishDate('2026-03-29', new Date(2026, 2, 30, 12))).toBe(
            'Viime illan / yön pelit'
        )
    } finally {
        if (previousTimeZone === undefined) delete process.env.TZ
        else process.env.TZ = previousTimeZone
    }
})
