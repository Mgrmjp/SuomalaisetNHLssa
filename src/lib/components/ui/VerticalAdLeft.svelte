<script>
// @ts-nocheck
import { onDestroy, onMount } from 'svelte'

// Standard IAB vertical rectangle: 160x600
const SLOT_WIDTH = 160
const SLOT_HEIGHT = 600

const ads = [
    {
        href: 'https://id.skruvat.fi/t/t?a=1483923855&as=2038972948&t=2&tk=1',
        src: 'https://track.adtraction.com/t/t?a=1483923855&as=2038972948&t=1&tk=1&i=1',
        alt: 'Mainos',
    },
    {
        href: 'https://go.adt242.com/t/t?a=1875158502&as=2038972948&t=2&tk=1',
        src: 'https://track.adtraction.com/t/t?a=1875158502&as=2038972948&t=1&tk=1&i=1',
        alt: 'Mainos',
    },
]

let currentAdIndex = 0
let _isTransitioning = false
let _isPaused = false
let interval

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
        currentAdIndex = (currentAdIndex + 1) % ads.length
        setTimeout(() => {
            _isTransitioning = false
        }, 500)
    }, 500)
}

onMount(() => {
    setTimeout(() => {
        interval = setInterval(nextAd, 20000)
    }, 12000)
})

onDestroy(() => {
    if (interval) clearInterval(interval)
})
</script>

<div class="vertical-ad-container-left">
    <div 
        class="ad-wrapper"
        on:mouseenter={pauseAds}
        on:mouseleave={resumeAds}
        role="region"
        aria-label="Mainos"
    >
        {#each ads as ad, index (index)}
            <a
                href={ad.href}
                target="_blank"
                rel="noopener noreferrer"
                class="ad-link"
                class:active={index === currentAdIndex}
                class:fade-out={index !== currentAdIndex || _isTransitioning}
            >
                <div class="ad-content-wrapper">
                    <img src={ad.src} alt={ad.alt} class="ad-img" />
                    <span class="ad-disclaimer">Mainos</span>
                </div>
            </a>
        {/each}
    </div>
</div>

<style>
    .vertical-ad-container-left {
        position: fixed;
        left: 1rem;
        top: 50%;
        transform: translateY(-50%);
        z-index: 40;
        display: none;
        overflow: visible;
        max-height: 100vh;
        max-height: 100dvh;
    }

    /* Hide on tablet */
    @media (max-width: 1399px) {
        .vertical-ad-container-left {
            display: none !important;
        }
    }

    @media (min-width: 1400px) {
        .vertical-ad-container-left {
            display: block;
            position: fixed;
            left: 1rem;
            top: 50%;
            transform: translateY(-50%);
            width: 160px;
            height: 600px;
            max-height: 100vh;
            max-height: 100dvh;
            overflow: visible;
        }

        .ad-wrapper {
            width: 160px;
            height: 600px;
        }

        .ad-link {
            position: absolute;
            width: 160px;
            height: 600px;
        }
    }

    .ad-wrapper {
        position: relative;
        width: 160px;
        height: 600px;
    }

    .ad-link {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        border: none;
        opacity: 0;
        transition: opacity 1s ease-in-out;
        pointer-events: none;
    }

    .ad-content-wrapper {
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 160px;
        height: 600px;
        line-height: 0;
        border-radius: 12px;
        box-shadow:
            0 0 0 4px rgba(15, 23, 42, 0.16),
            0 14px 32px rgba(15, 23, 42, 0.18);
        isolation: isolate;
    }

    .ad-link.active {
        opacity: 1;
        pointer-events: auto;
    }

    .ad-link.fade-out {
        opacity: 0;
    }

    .ad-content-wrapper::before {
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
        width: 160px;
        height: 600px;
        object-fit: cover;
        border: 1px solid rgba(15, 23, 42, 0.85);
        box-shadow: none;
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
