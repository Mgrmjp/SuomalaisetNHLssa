// @ts-nocheck
import { writable } from 'svelte/store'
import aaltoEnergiaDesktop from '../assets/ads/aalto-energia-desktop.svg'
import aaltoEnergiaMobile from '../assets/ads/aalto-energia-mobile.svg'
import bjornborgBlackweekDesktop from '../assets/ads/bjornborg-blackweek-desktop.svg'
import bjornborgBlackweekMobile from '../assets/ads/bjornborg-blackweek-mobile.svg'
import hehkuKiinteaDesktop from '../assets/ads/hehku-kiintea-12kk-desktop.svg'
import hehkuKiinteaMobile from '../assets/ads/hehku-kiintea-12kk-mobile.svg'
import hehkuPorssiDesktop from '../assets/ads/hehku-porssi-desktop.svg'
import hehkuPorssiMobile from '../assets/ads/hehku-porssi-mobile.svg'

const blackweekExpiresAt = '2026-12-01T00:00:00+02:00'

// Ad spot identifiers
export const AD_SPOTS = {
    BANNER: 'banner',
    MOBILE_MAIN: 'mobile-main',
    MOBILE_BANNER: 'mobile-banner',
}

// Track which ad index is showing in each spot
export const adSpotState = writable({
    [AD_SPOTS.BANNER]: 0,
    [AD_SPOTS.MOBILE_MAIN]: 0,
    [AD_SPOTS.MOBILE_BANNER]: 0,
})

// Standard IAB ad sizes:
// Desktop banner: 728x90 (leaderboard) or 980x120 (full banner)
// Mobile: 300x250 (medium rectangle)

// Banner ads - shared across banner spots (728x90 or 980x120 only)
const bannerAds = [
    {
        id: 'hehku-porssi',
        href: 'https://go.adt246.net/t/t?a=2034103803&as=2038972948&t=2&tk=1',
        src: hehkuPorssiDesktop,
        width: 728,
        height: 90,
        alt: 'Hehku Pörssi – tutustu pörssisähköön.',
    },
    {
        id: 'hehku-kiintea-12kk',
        href: 'https://go.adt246.net/t/t?a=2034099817&as=2038972948&t=2&tk=1',
        src: hehkuKiinteaDesktop,
        width: 728,
        height: 90,
        alt: 'Hehku Kiinteä 12 kk – kiinteä sähkön hinta vuodeksi.',
    },
    {
        id: 'bjornborg-blackweek',
        href: 'https://to.bjornborg.com/t/t?a=1578028333&as=2038972948&t=2&tk=1&url=www.bjornborg.com',
        src: bjornborgBlackweekDesktop,
        width: 728,
        height: 90,
        alt: 'Björn Borg Black Week – löydä suosikkisi.',
        expiresAt: blackweekExpiresAt,
    },
    {
        id: 'aalto-energia',
        href: 'https://go.adt246.net/t/t?a=1875124667&as=2038972948&t=2&tk=1',
        src: aaltoEnergiaDesktop,
        width: 728,
        height: 90,
        alt: 'Aalto Energia – sähköä kotiisi. Tutustu sopimuksiin.',
    },
    {
        id: 'dna',
        href: 'https://go.adt246.net/t/t?a=1883588377&as=2038972948&t=2&tk=1',
        isCustom: 'dna',
    },
    {
        id: 'multitronic',
        href: 'https://go.adt253.net/t/t?a=1930975670&as=2038972948&t=2&tk=1',
        isCustom: 'multitronic',
    },
    {
        id: 'vattenfall',
        href: 'https://go.adt267.com/t/t?a=2027551069&as=2038972948&t=2&tk=1',
        isCustom: 'vattenfall',
    },
    {
        id: 'vattenfall-opiskelija',
        href: 'https://go.adt267.com/t/t?a=1969450188&as=2038972948&t=2&tk=1',
        isCustom: 'vattenfall-opiskelija',
    },
    {
        id: 'kahvikaveri',
        href: 'https://on.kahvikaveri.fi/t/t?a=1895089445&as=2038972948&t=2&tk=1',
        src: 'https://track.adtraction.com/t/t?a=1895089445&as=2038972948&t=1&tk=1&i=1',
        width: 980,
        height: 120,
    },
    {
        id: 'bjornborg',
        href: 'https://go.adt242.com/t/t?a=1875158487&as=2038972948&t=2&tk=1',
        src: 'https://track.adtraction.com/t/t?a=1875158487&as=2038972948&t=1&tk=1&i=1',
        width: 728,
        height: 90,
    },
    {
        id: 'bjornborg2',
        href: 'https://to.bjornborg.com/t/t?a=1616919148&as=2038972948&t=2&tk=1',
        src: 'https://track.adtraction.com/t/t?a=1616919148&as=2038972948&t=1&tk=1&i=1',
        width: 980,
        height: 120,
    },
    {
        id: 'adt228-banner',
        href: 'https://go.adt228.com/t/t?a=2059481696&as=2038972948&t=2&tk=1',
        src: 'https://track.adtraction.com/t/t?a=2059481696&as=2038972948&t=1&tk=1&i=1',
        width: 728,
        height: 90,
    },
    {
        id: 'kodin1',
        href: 'https://to.kodin1.com/t/t?a=1918740233&as=2038972948&t=2&tk=1',
        isCustom: 'kodin1',
    },
    {
        id: 'kvarn',
        href: 'https://track.adtraction.com/t/t?a=2083576457&as=2038972948&t=2&tk=1',
        src: 'https://track.adtraction.com/t/t?a=2083576457&as=2038972948&t=1&tk=1&i=1',
        width: 980,
        height: 120,
        alt: 'Kvarn X',
    },
    {
        id: 'onthatass',
        href: 'https://track.adtraction.com/t/t?a=2010251951&as=2038972948&t=2&tk=1',
        src: 'https://track.adtraction.com/t/t?a=2010251951&as=2038972948&t=1&tk=1&i=1',
        width: 728,
        height: 90,
        alt: 'ON THAT ASS',
    },
    {
        id: 'luhta',
        href: 'https://track.adtraction.com/t/t?a=1837189231&as=2038972948&t=2&tk=1',
        src: 'https://track.adtraction.com/t/t?a=1837189231&as=2038972948&t=1&tk=1&i=1',
        width: 980,
        height: 120,
        alt: 'Luhta',
    },
    {
        id: 'nordnet',
        href: 'https://track.adtraction.com/t/t?a=2084043368&as=2038972948&t=2&tk=1',
        src: 'https://track.adtraction.com/t/t?a=2084043368&as=2038972948&t=1&tk=1&i=1',
        width: 980,
        height: 120,
        alt: 'Nordnet',
    },
    {
        id: 'nordnet-banner',
        href: 'https://track.adtraction.com/t/t?a=2020652698&as=2038972948&t=2&tk=1',
        src: 'https://track.adtraction.com/t/t?a=2020652698&as=2038972948&t=1&tk=1&i=1',
        width: 980,
        height: 120,
        alt: 'Nordnet',
    },
    {
        id: 'skruvat',
        href: 'https://track.adtraction.com/t/t?a=1483923987&as=2038972948&t=2&tk=1',
        src: 'https://track.adtraction.com/t/t?a=1483923987&as=2038972948&t=1&tk=1&i=1',
        width: 980,
        height: 120,
        alt: 'Skruvat',
    },
    {
        id: 'seiska',
        href: 'https://track.adtraction.com/t/t?a=2091706133&as=2038972948&t=2&tk=1',
        src: 'https://track.adtraction.com/t/t?a=2091706133&as=2038972948&t=1&tk=1&i=1',
        width: 980,
        height: 120,
        alt: 'Seiska',
    },
    {
        id: 'viaplay',
        href: 'https://track.adtraction.com/t/t?a=2111833033&as=2038972948&t=2&tk=1',
        src: 'https://track.adtraction.com/t/t?a=2111833033&as=2038972948&t=1&tk=1&i=1',
        width: 980,
        height: 120,
        alt: 'Viaplay',
    },
    {
        id: 'finlayson',
        href: 'https://to.finlayson.fi/t/t?a=1914383795&as=2038972948&t=2&tk=1',
        src: 'https://track.adtraction.com/t/t?a=1914383795&as=2038972948&t=1&tk=1&i=1',
        width: 980,
        height: 120,
        alt: 'Finlayson',
    },
    {
        id: 'finlayson-banner',
        href: 'https://track.adtraction.com/t/t?a=1883158985&as=2038972948&t=2&tk=1',
        src: 'https://track.adtraction.com/t/t?a=1883158985&as=2038972948&t=1&tk=1&i=1',
        width: 980,
        height: 120,
        alt: 'Finlayson',
    },
    {
        id: 'finlayson-full',
        href: 'https://go.adt291.com/t/t?a=2066020464&as=2038972948&t=2&tk=1',
        src: 'https://track.adtraction.com/t/t?a=2066020464&as=2038972948&t=1&tk=1&i=1',
        width: 980,
        height: 120,
        alt: 'Mainos',
    },
]

// Mobile ads - 300x250 only (IAB Medium Rectangle)
const mobileAds = [
    {
        id: 'hehku-porssi-mobile',
        href: 'https://go.adt246.net/t/t?a=2034103803&as=2038972948&t=2&tk=1',
        src: hehkuPorssiMobile,
        width: 300,
        height: 250,
        alt: 'Hehku Pörssi – tutustu pörssisähköön.',
    },
    {
        id: 'hehku-kiintea-12kk-mobile',
        href: 'https://go.adt246.net/t/t?a=2034099817&as=2038972948&t=2&tk=1',
        src: hehkuKiinteaMobile,
        width: 300,
        height: 250,
        alt: 'Hehku Kiinteä 12 kk – kiinteä sähkön hinta vuodeksi.',
    },
    {
        id: 'bjornborg-blackweek-mobile',
        href: 'https://to.bjornborg.com/t/t?a=1578028333&as=2038972948&t=2&tk=1&url=www.bjornborg.com',
        src: bjornborgBlackweekMobile,
        width: 300,
        height: 250,
        alt: 'Björn Borg Black Week – löydä suosikkisi.',
        expiresAt: blackweekExpiresAt,
    },
    {
        id: 'aalto-energia-mobile',
        href: 'https://go.adt246.net/t/t?a=1875124667&as=2038972948&t=2&tk=1',
        src: aaltoEnergiaMobile,
        width: 300,
        height: 250,
        alt: 'Aalto Energia – sähköä kotiisi. Tutustu sopimuksiin.',
    },
    {
        id: 'skruvat-mobile',
        href: 'https://track.adtraction.com/t/t?a=1483923863&as=2038972948&t=2&tk=1',
        src: 'https://track.adtraction.com/t/t?a=1483923863&as=2038972948&t=1&tk=1&i=1',
        width: 300,
        height: 250,
        alt: 'Skruvat',
    },
    {
        id: 'nordnet-mobile',
        href: 'https://track.adtraction.com/t/t?a=2075791997&as=2038972948&t=2&tk=1',
        src: 'https://track.adtraction.com/t/t?a=2075791997&as=2038972948&t=1&tk=1&i=1',
        width: 300,
        height: 250,
        alt: 'Nordnet',
    },
    {
        id: 'onthatass-mobile',
        href: 'https://track.adtraction.com/t/t?a=2010251959&as=2038972948&t=2&tk=1',
        src: 'https://track.adtraction.com/t/t?a=2010251959&as=2038972948&t=1&tk=1&i=1',
        width: 300,
        height: 250,
        alt: 'ON THAT ASS',
    },
    {
        id: 'luhta-mobile',
        href: 'https://track.adtraction.com/t/t?a=1837189049&as=2038972948&t=2&tk=1',
        src: 'https://track.adtraction.com/t/t?a=1837189049&as=2038972948&t=1&tk=1&i=1',
        width: 300,
        height: 250,
        alt: 'Luhta',
    },
    {
        id: 'moi1',
        href: 'https://in.moi.fi/t/t?a=1551605636&as=2038972948&t=2&tk=1',
        src: 'https://track.adtraction.com/t/t?a=1551605636&as=2038972948&t=1&tk=1&i=1',
        width: 300,
        height: 250,
    },
    {
        id: 'moi2',
        href: 'https://in.moi.fi/t/t?a=1551605634&as=2038972948&t=2&tk=1',
        src: 'https://track.adtraction.com/t/t?a=1551605634&as=2038972948&t=1&tk=1&i=1',
        width: 300,
        height: 250,
    },
    {
        id: 'adt228-mobile',
        href: 'https://go.adt228.com/t/t?a=1726397781&as=2038972948&t=2&tk=1',
        src: 'https://track.adtraction.com/t/t?a=1726397781&as=2038972948&t=1&tk=1&i=1',
        width: 300,
        height: 250,
    },
    {
        id: 'blackhorse-mobile',
        href: 'https://id.blackhorse.fi/t/t?a=1775743329&as=2038972948&t=2&tk=1',
        src: 'https://track.adtraction.com/t/t?a=1775743329&as=2038972948&t=1&tk=1&i=1',
        width: 300,
        height: 250,
    },
]

// Mobile banner ads - 300x250 only
const mobileBannerAds = [
    {
        id: 'bjornborg-mobile',
        href: 'https://to.bjornborg.com/t/t?a=1616919459&as=2038972948&t=2&tk=1',
        src: 'https://track.adtraction.com/t/t?a=1616919459&as=2038972948&t=1&tk=1&i=1',
        width: 300,
        height: 250,
    },
    {
        id: 'moi4',
        href: 'https://in.moi.fi/t/t?a=1551605636&as=2038972948&t=2&tk=1',
        src: 'https://track.adtraction.com/t/t?a=1551605636&as=2038972948&t=1&tk=1&i=1',
        width: 300,
        height: 250,
    },
    {
        id: 'moi5',
        href: 'https://in.moi.fi/t/t?a=1551605634&as=2038972948&t=2&tk=1',
        src: 'https://track.adtraction.com/t/t?a=1551605634&as=2038972948&t=1&tk=1&i=1',
        width: 300,
        height: 250,
    },
]

export function getBannerAds(now = Date.now()) {
    return bannerAds.filter((ad) => !ad.expiresAt || now < Date.parse(ad.expiresAt))
}

export function getMobileAds(now = Date.now()) {
    return mobileAds.filter((ad) => !ad.expiresAt || now < Date.parse(ad.expiresAt))
}

export function getMobileBannerAds(now = Date.now()) {
    return mobileBannerAds.filter((ad) => !ad.expiresAt || now < Date.parse(ad.expiresAt))
}

// Get a random index that doesn't conflict with other spots
/** @param {string} spot
 *  @param {Array<{id: string, href: string, isCustom?: string, src?: string, width?: number, height?: number}>} adList
 *  @returns {number}
 */
export function getRandomAdIndex(spot, adList) {
    let index = Math.floor(Math.random() * adList.length)

    // Check current state and try to avoid showing same ad
    let currentState
    adSpotState.subscribe((s) => {
        currentState = s
    })()

    // Get all other spots using the same ad pool
    const otherSpots = Object.entries(currentState)
        .filter(([s]) => s !== spot)
        .map(([, i]) => i)

    // If there's a conflict, try a different index
    const maxAttempts = adList.length - 1
    let attempts = 0
    while (otherSpots.includes(index) && attempts < maxAttempts) {
        index = (index + 1) % adList.length
        attempts++
    }

    return index
}

// Advance to next ad for a spot, ensuring no conflicts
/** @param {string} spot
 *  @param {number} currentIndex
 *  @param {Array<{id: string, href: string, isCustom?: string, src?: string, width?: number, height?: number}>} adList
 *  @returns {number}
 */
export function getNextAdIndex(spot, currentIndex, adList) {
    let nextIndex = (currentIndex + 1) % adList.length

    let currentState
    adSpotState.subscribe((s) => {
        currentState = s
    })()

    const otherSpots = Object.entries(currentState)
        .filter(([s]) => s !== spot)
        .map(([, i]) => i)

    // Skip indices that are used by other spots
    let attempts = 0
    while (otherSpots.includes(nextIndex) && attempts < adList.length - 1) {
        nextIndex = (nextIndex + 1) % adList.length
        attempts++
    }

    return nextIndex
}

// Update the state when ad changes
/** @param {string} spot
 *  @param {number} index
 */
export function setAdSpotIndex(spot, index) {
    adSpotState.update((state) => ({
        ...state,
        [spot]: index,
    }))
}
