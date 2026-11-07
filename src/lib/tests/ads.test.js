import { afterEach, describe, expect, it, vi } from 'vitest'
import { getBannerAds, getMobileAds } from '$lib/stores/ads.js'

describe('Black Week campaign availability', () => {
    afterEach(() => vi.useRealTimers())

    for (const { placement, getAds } of [
        { placement: 'desktop', getAds: getBannerAds },
        { placement: 'mobile', getAds: getMobileAds },
    ]) {
        it(`keeps ${placement} Black Week visible until the end of November in Finland`, () => {
            const ads = getAds(Date.parse('2026-11-30T23:59:59.999+02:00'))
            expect(ads.some((ad) => ad.id.startsWith('bjornborg-blackweek'))).toBe(true)
        })

        it(`removes ${placement} Black Week at Finnish midnight and keeps evergreen ads`, () => {
            for (const time of [
                '2026-11-30T22:00:00Z',
                '2026-12-15T12:00:00Z',
                '2027-11-07T12:00:00Z',
            ]) {
                const ads = getAds(Date.parse(time))
                expect(ads.some((ad) => ad.id.startsWith('bjornborg-blackweek'))).toBe(false)
                expect(ads.some((ad) => ad.id.startsWith('aalto-energia'))).toBe(true)
                expect(ads.some((ad) => ad.id.startsWith('hehku-porssi'))).toBe(true)
                expect(ads.some((ad) => ad.id.startsWith('hehku-kiintea-12kk'))).toBe(true)
            }
        })

        it(`uses the current clock for ${placement} campaigns without a supplied date`, () => {
            vi.useFakeTimers()
            vi.setSystemTime(new Date('2026-11-30T23:59:59+02:00'))
            expect(getAds().some((ad) => ad.id.startsWith('bjornborg-blackweek'))).toBe(true)
            vi.setSystemTime(new Date('2026-12-01T00:00:00+02:00'))
            expect(getAds().some((ad) => ad.id.startsWith('bjornborg-blackweek'))).toBe(false)
        })
    }
})
