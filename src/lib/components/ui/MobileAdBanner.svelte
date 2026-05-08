<script>
// @ts-nocheck
import { onDestroy, onMount } from 'svelte'
import {
    AD_SPOTS,
    getMobileBannerAds,
    getNextAdIndex,
    getRandomAdIndex,
    setAdSpotIndex,
} from '$lib/stores/ads.js'

const ads = getMobileBannerAds()
let currentAdIndex = getRandomAdIndex(AD_SPOTS.MOBILE_BANNER, ads)
let _isTransitioning = false
let _isPaused = false
let interval

// Mark this spot as active
setAdSpotIndex(AD_SPOTS.MOBILE_BANNER, currentAdIndex)

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
        currentAdIndex = getNextAdIndex(AD_SPOTS.MOBILE_BANNER, currentAdIndex, ads)
        setAdSpotIndex(AD_SPOTS.MOBILE_BANNER, currentAdIndex)
        setTimeout(() => {
            _isTransitioning = false
        }, 500)
    }, 500)
}

onMount(() => {
    setTimeout(() => {
        interval = setInterval(nextAd, 20000)
    }, 8000)
})

onDestroy(() => {
    if (interval) clearInterval(interval)
})
</script>

<div class="mobile-ad-banner">
    <div 
        class="ad-wrapper"
        on:mouseenter={pauseAds}
        on:mouseleave={resumeAds}
        role="region"
        aria-label="Mainos"
    >
        {#each ads as ad, index (ad.id)}
            <a
                href={ad.href}
                target="_blank"
                rel="noopener noreferrer"
                class="ad-link"
                class:active={index === currentAdIndex}
                class:fade-out={index !== currentAdIndex || _isTransitioning}
            >
                <img src={ad.src} width={ad.width} height={ad.height} alt="Mainos" class="ad-img" />
                <span class="ad-disclaimer">Mainos</span>
            </a>
        {/each}
    </div>
</div>

<style>
    .mobile-ad-banner {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 1rem 0;
        position: relative;
    }

    .ad-wrapper {
        position: relative;
        width: 100%;
        max-width: 300px;
        aspect-ratio: 1;
        overflow: visible;
    }

    .ad-link {
        position: absolute;
        top: 0;
        left: 0;
        display: block;
        border: none;
        opacity: 0;
        transition: opacity 1s ease-in-out;
        pointer-events: none;
        width: 100%;
        height: 100%;
        isolation: isolate;
    }

    .ad-link.active {
        position: relative;
        opacity: 1;
        pointer-events: auto;
    }

    .ad-link.fade-out {
        opacity: 0;
    }

    .ad-link.active::before {
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

    .ad-img {
        width: 100%;
        height: 100%;
        object-fit: contain;
        border: 1px solid rgba(15, 23, 42, 0.85);
        box-shadow:
            0 0 0 4px rgba(15, 23, 42, 0.16),
            0 14px 32px rgba(15, 23, 42, 0.18);
        border-radius: 10px;
        display: block;
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

    @media (min-width: 768px) {
        .mobile-ad-banner {
            display: none;
        }
    }

    @media (prefers-reduced-motion: reduce) {
        .ad-link {
            transition: none;
        }
    }

    @keyframes border-shimmer {
        0%, 72%, 100% { background-position: 140% 50%; opacity: 0; }
        78% { background-position: 60% 50%; opacity: 0.8; }
        84% { background-position: -20% 50%; opacity: 0; }
    }
</style>
