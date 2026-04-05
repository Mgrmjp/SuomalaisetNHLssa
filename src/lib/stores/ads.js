import { writable, derived } from 'svelte/store'

// Ad spot identifiers
export const AD_SPOTS = {
    BANNER: 'banner',
    MOBILE_MAIN: 'mobile-main',
    MOBILE_BANNER: 'mobile-banner'
}

// Track which ad index is showing in each spot
export const adSpotState = writable({
    [AD_SPOTS.BANNER]: 0,
    [AD_SPOTS.MOBILE_MAIN]: 0,
    [AD_SPOTS.MOBILE_BANNER]: 0
})

// Banner ads - shared across banner spots
const bannerAds = [
    { id: 'dna', href: 'https://go.adt246.net/t/t?a=1883588377&as=2038972948&t=2&tk=1', isCustom: 'dna' },
    { id: 'multitronic', href: 'https://go.adt253.net/t/t?a=1930975670&as=2038972948&t=2&tk=1', isCustom: 'multitronic' },
    { id: 'vattenfall', href: 'https://go.adt267.com/t/t?a=2027551069&as=2038972948&t=2&tk=1', isCustom: 'vattenfall' },
    { id: 'vattenfall-opiskelija', href: 'https://go.adt267.com/t/t?a=1969450188&as=2038972948&t=2&tk=1', isCustom: 'vattenfall-opiskelija' },
    { id: 'kahvikaveri', href: 'https://on.kahvikaveri.fi/t/t?a=1895089445&as=2038972948&t=2&tk=1', src: 'https://track.adtraction.com/t/t?a=1895089445&as=2038972948&t=1&tk=1&i=1', width: 980, height: 120 },
    { id: 'bjornborg', href: 'https://go.adt242.com/t/t?a=1875158487&as=2038972948&t=2&tk=1', src: 'https://track.adtraction.com/t/t?a=1875158487&as=2038972948&t=1&tk=1&i=1', width: 728, height: 90 },
    { id: 'bjornborg2', href: 'https://to.bjornborg.com/t/t?a=1616919148&as=2038972948&t=2&tk=1', src: 'https://track.adtraction.com/t/t?a=1616919148&as=2038972948&t=1&tk=1&i=1', width: 980, height: 120 },
    { id: 'adt228-banner', href: 'https://go.adt228.com/t/t?a=2059481696&as=2038972948&t=2&tk=1', src: 'https://track.adtraction.com/t/t?a=2059481696&as=2038972948&t=1&tk=1&i=1', width: 728, height: 90 },
    { id: 'kodin1', href: 'https://to.kodin1.com/t/t?a=1918740233&as=2038972948&t=2&tk=1', isCustom: 'kodin1' },
    { id: 'kvarn', href: 'https://go.kvarnx.com/t/t?a=1946750195&as=2038972948&t=2&tk=1', isCustom: 'kvarn' },
]

// Mobile ads - shared across mobile spots
const mobileAds = [
    { id: 'dna-mobile', href: 'https://go.adt291.com/t/t?a=1998771852&as=2038972948&t=2&tk=1', src: 'https://track.adtraction.com/t/t?a=1998771852&as=2038972948&t=1&tk=1&i=1', width: 320, height: 320 },
    { id: 'moi1', href: 'https://in.moi.fi/t/t?a=1551605636&as=2038972948&t=2&tk=1', src: 'https://track.adtraction.com/t/t?a=1551605636&as=2038972948&t=1&tk=1&i=1', width: 300, height: 300 },
    { id: 'moi2', href: 'https://in.moi.fi/t/t?a=1551605634&as=2038972948&t=2&tk=1', src: 'https://track.adtraction.com/t/t?a=1551605634&as=2038972948&t=1&tk=1&i=1', width: 300, height: 300 },
    { id: 'moi3', href: 'https://in.moi.fi/t/t?a=1727501623&as=2038972948&t=2&tk=1', src: 'https://track.adtraction.com/t/t?a=1727501623&as=2038972948&t=1&tk=1&i=1', width: 300, height: 280 },
    { id: 'adt228-mobile', href: 'https://go.adt228.com/t/t?a=1726397781&as=2038972948&t=2&tk=1', src: 'https://track.adtraction.com/t/t?a=1726397781&as=2038972948&t=1&tk=1&i=1', width: 300, height: 250 },
    { id: 'adt267-mobile', href: 'https://go.adt267.com/t/t?a=1538795918&as=2038972948&t=2&tk=1', src: 'https://track.adtraction.com/t/t?a=1538795918&as=2038972948&t=1&tk=1&i=1', width: 300, height: 100 },
]

// Mobile banner ads
const mobileBannerAds = [
    { id: 'bjornborg-mobile', href: 'https://to.bjornborg.com/t/t?a=1616919459&as=2038972948&t=2&tk=1', src: 'https://track.adtraction.com/t/t?a=1616919459&as=2038972948&t=1&tk=1&i=1', width: 300, height: 250 },
    { id: 'moi4', href: 'https://in.moi.fi/t/t?a=1551605636&as=2038972948&t=2&tk=1', src: 'https://track.adtraction.com/t/t?a=1551605636&as=2038972948&t=1&tk=1&i=1', width: 300, height: 300 },
    { id: 'moi5', href: 'https://in.moi.fi/t/t?a=1551605634&as=2038972948&t=2&tk=1', src: 'https://track.adtraction.com/t/t?a=1551605634&as=2038972948&t=1&tk=1&i=1', width: 300, height: 300 },
    { id: 'moi6', href: 'https://in.moi.fi/t/t?a=1727501623&as=2038972948&t=2&tk=1', src: 'https://track.adtraction.com/t/t?a=1727501623&as=2038972948&t=1&tk=1&i=1', width: 300, height: 280 },
    { id: 'adt267-mobile2', href: 'https://go.adt267.com/t/t?a=1538795918&as=2038972948&t=2&tk=1', src: 'https://track.adtraction.com/t/t?a=1538795918&as=2038972948&t=1&tk=1&i=1', width: 300, height: 100 },
]

export function getBannerAds() {
    return bannerAds
}

export function getMobileAds() {
    return mobileAds
}

export function getMobileBannerAds() {
    return mobileBannerAds
}

// Get a random index that doesn't conflict with other spots
export function getRandomAdIndex(spot, adList) {
    let index = Math.floor(Math.random() * adList.length)
    
    // Check current state and try to avoid showing same ad
    let currentState
    adSpotState.subscribe(s => currentState = s)()
    
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
export function getNextAdIndex(spot, currentIndex, adList) {
    let nextIndex = (currentIndex + 1) % adList.length
    
    let currentState
    adSpotState.subscribe(s => currentState = s)()
    
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
export function setAdSpotIndex(spot, index) {
    adSpotState.update(state => ({
        ...state,
        [spot]: index
    }))
}
