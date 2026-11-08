import { afterEach, describe, expect, it, vi } from 'vitest'
import { getBannerAds, getMobileAds, releaseMobileAd, selectMobileAd } from '$lib/stores/ads.js'

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

describe('Mobile ad selection', () => {
    const ads = [{ id: 'a' }, { id: 'b' }, { id: 'c' }]
    afterEach(() => {
        releaseMobileAd('first')
        releaseMobileAd('second')
        vi.restoreAllMocks()
    })

    it('uses randomness to select from loaded images', () => {
        vi.spyOn(Math, 'random').mockReturnValueOnce(0).mockReturnValueOnce(0.99)
        expect(selectMobileAd('first', ads)).toBe('a')
        expect(selectMobileAd('first', ads)).toBe('c')
    })

    it('avoids the other placement by creative ID when loaded pools differ', () => {
        vi.spyOn(Math, 'random').mockReturnValue(0)
        expect(selectMobileAd('first', ads.slice(1))).toBe('b')
        expect(selectMobileAd('second', ads)).toBe('a')
    })

    it('rotates randomly without immediately repeating or duplicating another placement', () => {
        vi.spyOn(Math, 'random').mockReturnValue(0)
        expect(selectMobileAd('first', ads)).toBe('a')
        expect(selectMobileAd('second', ads)).toBe('b')
        expect(selectMobileAd('first', ads, 'a')).toBe('c')
    })

    it('releases a placement when it disappears or has no usable images', () => {
        vi.spyOn(Math, 'random').mockReturnValue(0)
        selectMobileAd('first', ads)
        releaseMobileAd('first')
        expect(selectMobileAd('second', ads)).toBe('a')
        expect(selectMobileAd('second', [])).toBeNull()
        expect(selectMobileAd('first', ads)).toBe('a')
    })

    it('keeps displaying the only usable image when no alternative is available', () => {
        expect(selectMobileAd('first', ads.slice(0, 1), 'a')).toBe('a')
        expect(selectMobileAd('second', ads.slice(0, 1))).toBe('a')
    })
})
