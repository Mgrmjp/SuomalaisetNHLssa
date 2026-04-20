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
        width: 300px;
        height: 250px;
        overflow: hidden;
    }

    .mobile-ad-link {
        position: absolute;
        top: 0;
        left: 0;
        width: 300px;
        height: 250px;
        display: block;
        border: none;
        opacity: 0;
        transition: opacity 1s ease-in-out;
        pointer-events: none;
        overflow: hidden;
        border-radius: 8px;
    }

    .mobile-ad-link.active {
        opacity: 1;
        pointer-events: auto;
    }

    .mobile-ad-link.fade-out {
        opacity: 0;
    }

    .mobile-ad-img {
        width: 300px;
        height: 250px;
        object-fit: cover;
        border: 0;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
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

    @media (prefers-reduced-motion: reduce) {
        .mobile-ad-link {
            transition: none;
        }
    }
</style>
