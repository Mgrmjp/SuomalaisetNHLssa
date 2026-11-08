<script>
// @ts-nocheck
import { onDestroy, onMount } from 'svelte'
import AdLabel from './AdLabel.svelte'
import { AD_SPOTS, getMobileAds, releaseMobileAd, selectMobileAd } from '$lib/stores/ads.js'

export let spot = AD_SPOTS.MOBILE_MAIN
export let betweenGroups = false

// Populate after mounting so static HTML cannot hydrate expired campaign images.
let ads = []
let currentAdId = null
let _isPaused = false
let interval
let expiryTimeout
let loadedAds = {}
$: readyAds = ads.filter((ad) => loadedAds[ad.id])
$: currentAd = readyAds.find((ad) => ad.id === currentAdId)

function refreshAds() {
    const now = Date.now()
    ads = getMobileAds(now)
    if (!ads.some((ad) => ad.id === currentAdId && loadedAds[ad.id])) {
        currentAdId = selectMobileAd(
            spot,
            ads.filter((ad) => loadedAds[ad.id])
        )
    }

    if (expiryTimeout) clearTimeout(expiryTimeout)
    const nextExpiry = Math.min(
        ...ads.filter((ad) => ad.expiresAt).map((ad) => Date.parse(ad.expiresAt))
    )
    if (Number.isFinite(nextExpiry)) {
        expiryTimeout = setTimeout(refreshAds, Math.min(nextExpiry - now, 2_147_483_647))
    }
}

function pauseAds() {
    _isPaused = true
}

function resumeAds() {
    _isPaused = false
}

function nextAd() {
    if (_isPaused || readyAds.length === 0) return
    currentAdId = selectMobileAd(spot, readyAds, currentAdId)
}

function setAdLoaded(ad, image) {
    // Providers sometimes return a successful 1x1 tracking pixel for an unavailable creative.
    const wasLoaded = loadedAds[ad.id]
    const usable = image.naturalWidth > 1 && image.naturalHeight > 1
    loadedAds = { ...loadedAds, [ad.id]: usable }
    if ((usable && !wasLoaded) || (!usable && ad.id === currentAdId)) {
        currentAdId = selectMobileAd(
            spot,
            ads.filter((candidate) => loadedAds[candidate.id])
        )
    }
}

onMount(() => {
    refreshAds()
    interval = setInterval(nextAd, 20000)
    window.addEventListener('focus', refreshAds)
    document.addEventListener('visibilitychange', refreshAds)
})

onDestroy(() => {
    if (interval) clearInterval(interval)
    if (expiryTimeout) clearTimeout(expiryTimeout)
    if (typeof window !== 'undefined') {
        releaseMobileAd(spot)
        window.removeEventListener('focus', refreshAds)
        document.removeEventListener('visibilitychange', refreshAds)
    }
})
</script>

<div
    class="mobile-ad-container"
    class:mobile-ad-container--empty={!currentAd}
    class:mobile-ad-container--between={betweenGroups}
    data-ad-spot={spot}
>
    <div
        class="ad-wrapper"
        onpointerenter={(event) => {
            if (event.pointerType === 'mouse') pauseAds()
        }}
        onpointerleave={resumeAds}
        role="region"
        aria-label="Mainos"
    >
        <AdLabel />
        {#each ads as ad (ad.id)}
            <a
                href={ad.href}
                target="_blank"
                rel="noopener noreferrer"
                class="mobile-ad-link"
                class:active={ad.id === currentAd?.id}
                class:fade-out={ad.id !== currentAd?.id}
                tabindex={ad.id === currentAd?.id ? 0 : -1}
                aria-hidden={ad.id !== currentAd?.id}
            >
                <img
                    src={ad.src}
                    alt={ad.alt || 'Mainos'}
                    class="mobile-ad-img"
                    onload={(event) => setAdLoaded(ad, event.currentTarget)}
                    onerror={(event) => setAdLoaded(ad, event.currentTarget)}
                />
            </a>
        {/each}
    </div>
</div>

<style>
.mobile-ad-container {
    width: 100%;
    display: flex;
    justify-content: center;
    padding: 0;
}

.mobile-ad-container--between {
    margin-bottom: 2.25rem;
}

.mobile-ad-container--empty {
    display: none;
}

@media (min-width: 768px) {
    .mobile-ad-container {
        display: none;
    }
}

.ad-wrapper {
    position: relative;
    width: min(300px, 100%);
    height: 282px;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    overflow: visible;
    border-radius: 0;
}

.mobile-ad-link {
    position: absolute;
    top: 32px;
    left: 0;
    width: 100%;
    height: 250px;
    display: block;
    border: none;
    opacity: 0;
    transition: opacity 1s ease-in-out;
    pointer-events: none;
    overflow: visible;
    border-radius: 0;
    isolation: isolate;
}

.mobile-ad-link.active {
    opacity: 1;
    pointer-events: auto;
}

.mobile-ad-link.fade-out {
    opacity: 0;
}

.mobile-ad-link.active::before {
    content: '';
    position: absolute;
    inset: -2px;
    border-radius: inherit;
    background: linear-gradient(
        110deg,
        rgba(255, 255, 255, 0) 0%,
        rgba(255, 255, 255, 0) 42%,
        rgba(255, 255, 255, 0.38) 50%,
        rgba(255, 255, 255, 0) 58%,
        rgba(255, 255, 255, 0) 100%
    );
    background-size: 250% 100%;
    animation: border-shimmer 7s ease-in-out infinite;
    opacity: 0.8;
    pointer-events: none;
    z-index: 0;
}

.mobile-ad-img {
    width: 100%;
    height: 250px;
    object-fit: contain;
    display: block;
    border: 1px solid rgba(15, 23, 42, 0.85);
    border-radius: 0;
    position: relative;
    z-index: 1;
}

@media (prefers-reduced-motion: reduce) {
    .mobile-ad-link {
        transition: none;
    }
}

@keyframes border-shimmer {
    0%,
    72%,
    100% {
        background-position: 140% 50%;
        opacity: 0;
    }
    78% {
        background-position: 60% 50%;
        opacity: 0.8;
    }
    84% {
        background-position: -20% 50%;
        opacity: 0;
    }
}
</style>
