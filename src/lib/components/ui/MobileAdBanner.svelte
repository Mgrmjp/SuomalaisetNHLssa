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
        overflow: hidden;
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
    }

    .ad-link.active {
        position: relative;
        opacity: 1;
        pointer-events: auto;
    }

    .ad-link.fade-out {
        opacity: 0;
    }

    .ad-img {
        width: 100%;
        height: 100%;
        object-fit: contain;
        border: 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border-radius: 8px;
        display: block;
    }

    .ad-disclaimer {
        position: absolute;
        top: 8px;
        right: 8px;
        background: rgba(0, 0, 0, 0.6);
        color: #fff;
        font-size: 10px;
        font-weight: 600;
        padding: 3px 6px;
        border-radius: 4px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        pointer-events: none;
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
</style>
