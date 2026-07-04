<script>
// @ts-nocheck
import { onDestroy, onMount } from 'svelte'
import {
    AD_SPOTS,
    getMobileAds,
    getNextAdIndex,
    getRandomAdIndex,
    setAdSpotIndex,
} from '$lib/stores/ads.js'

const ads = getMobileAds()
let currentAdIndex = getRandomAdIndex(AD_SPOTS.MOBILE_MAIN, ads)
let _isTransitioning = false
let _isPaused = false
let interval

// Mark this spot as active
setAdSpotIndex(AD_SPOTS.MOBILE_MAIN, currentAdIndex)

function pauseAds() {
    _isPaused = true
}

function resumeAds() {
    _isPaused = false
}

function nextAd() {
    if (_isPaused) return
    _isTransitioning = true
    setTimeout(() => {
        currentAdIndex = getNextAdIndex(AD_SPOTS.MOBILE_MAIN, currentAdIndex, ads)
        setAdSpotIndex(AD_SPOTS.MOBILE_MAIN, currentAdIndex)
        setTimeout(() => {
            _isTransitioning = false
        }, 500)
    }, 500)
}

onMount(() => {
    setTimeout(() => {
        interval = setInterval(nextAd, 20000)
    }, 16000)
})

onDestroy(() => {
    if (interval) clearInterval(interval)
})
</script>

<div class="mobile-ad-container">
    <div 
        class="ad-wrapper"
        on:mouseenter={pauseAds}
        on:mouseleave={resumeAds}
        role="region"
        aria-label="Mainos"
    >
        <div class="support-message" aria-hidden="true">
            Näyttää siltä, että käytät mainostenestoa. Arvostamme suuresti, jos
            lisäät sivuston sallittujen listalle.
        </div>
        {#each ads as ad, index (ad.id)}
            <a
                href={ad.href}
                target="_blank"
                rel="noopener noreferrer"
                class="mobile-ad-link"
                class:active={index === currentAdIndex}
                class:fade-out={index !== currentAdIndex || _isTransitioning}
            >
                <img src={ad.src} alt="Mainos" class="mobile-ad-img" />
                <span class="ad-disclaimer">Mainos</span>
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

    @media (min-width: 768px) {
        .mobile-ad-container {
            display: none;
        }
    }

    .ad-wrapper {
        position: relative;
        width: min(300px, 100%);
        height: 250px;
        overflow: hidden;
    }

    .support-message {
        position: absolute;
        inset: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 1rem;
        border: 1px dashed rgba(0, 53, 128, 0.24);
        border-radius: 10px;
        background: rgba(238, 243, 251, 0.72);
        color: rgba(15, 23, 42, 0.72);
        font-size: 0.8rem;
        font-weight: 700;
        line-height: 1.35;
        text-align: center;
        pointer-events: none;
    }

    .mobile-ad-link {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 250px;
        display: block;
        border: none;
        opacity: 0;
        transition: opacity 1s ease-in-out;
        pointer-events: none;
        overflow: hidden;
        border-radius: 8px;
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
        object-fit: cover;
        border: 1px solid rgba(15, 23, 42, 0.85);
        border-radius: 10px;
        box-shadow:
            0 0 0 4px rgba(15, 23, 42, 0.16),
            0 14px 32px rgba(15, 23, 42, 0.18);
        position: relative;
        z-index: 1;
    }

    .ad-disclaimer {
        position: absolute;
        top: 0;
        left: 50%;
        transform: translate(-50%, -50%);
        background: rgba(0, 0, 0, 0.55);
        color: rgba(255, 255, 255, 0.9);
        border: 1px solid rgba(255, 255, 255, 0.18);
        border-radius: 999px;
        padding: 4px 10px;
        font-size: 10px;
        font-weight: 700;
        line-height: 1.2;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        backdrop-filter: blur(6px);
        pointer-events: none;
        z-index: 1;
    }

    @media (prefers-reduced-motion: reduce) {
        .mobile-ad-link {
            transition: none;
        }
    }

    @keyframes border-shimmer {
        0%, 72%, 100% { background-position: 140% 50%; opacity: 0; }
        78% { background-position: 60% 50%; opacity: 0.8; }
        84% { background-position: -20% 50%; opacity: 0; }
    }
</style>
