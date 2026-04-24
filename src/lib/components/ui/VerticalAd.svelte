<script>
// @ts-nocheck
import { onDestroy, onMount } from 'svelte'
import { base } from '$app/paths'

// Standard IAB vertical rectangle: 160x600
const SLOT_WIDTH = 160
const SLOT_HEIGHT = 600

const ads = [
    {
        href: 'https://go.adt291.com/t/t?a=2028121988&as=2038972948&t=2&tk=1',
        src: 'https://track.adtraction.com/t/t?a=2028121988&as=2038972948&t=1&tk=1&i=1',
        alt: 'Mainos',
    },
    {
        href: 'https://go.adt242.com/t/t?a=2050880477&as=2038972948&t=2&tk=1',
        src: 'https://track.adtraction.com/t/t?a=2050880477&as=2038972948&t=1&tk=1&i=1',
        alt: 'Mainos',
    },
    {
        href: 'https://at.valco.fi/t/t?a=2020376424&as=2038972948&t=2&tk=1',
        src: `${base}/valco.jpg`,
        alt: 'Mainos',
    },
    {
        href: 'https://id.blackhorse.fi/t/t?a=1775743331&as=2038972948&t=2&tk=1',
        src: 'https://track.adtraction.com/t/t?a=1775743331&as=2038972948&t=1&tk=1&i=1',
        alt: 'Black Horse',
        width: 120,
        height: 600,
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
    }, 4000)
})

onDestroy(() => {
    if (interval) clearInterval(interval)
})
</script>

<div class="vertical-ad-container">
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
                <div
                    class="ad-content-wrapper"
                    style={`--ad-width:${ad.width || SLOT_WIDTH}px; --ad-height:${ad.height || SLOT_HEIGHT}px;`}
                >
                    <img
                        src={ad.src}
                        alt={ad.alt}
                        width={ad.width || SLOT_WIDTH}
                        height={ad.height || SLOT_HEIGHT}
                        class="ad-img"
                    />
                    <span class="ad-disclaimer">Mainos</span>
                </div>
            </a>
        {/each}
    </div>
</div>

<style>
    .vertical-ad-container {
        position: fixed;
        right: 1rem;
        top: 50%;
        transform: translateY(-50%);
        z-index: 40;
        display: none;
        overflow: hidden;
        max-height: 100vh;
        max-height: 100dvh;
    }

    /* Hide on tablet */
    @media (max-width: 1399px) {
        .vertical-ad-container {
            display: none !important;
        }
    }

    @media (min-width: 1400px) {
        .vertical-ad-container {
            display: block;
            position: fixed;
            right: 1rem;
            top: 50%;
            transform: translateY(-50%);
            width: 160px;
            height: 600px;
            max-height: 100vh;
            max-height: 100dvh;
            overflow: hidden;
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

        .ad-img {
            width: 160px;
            height: 600px;
            object-fit: cover;
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
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 100%;
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
        width: var(--ad-width, 160px);
        height: var(--ad-height, 600px);
        line-height: 0;
    }

    .ad-link.active {
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
        right: 0;
        background: rgba(0, 0, 0, 0.6);
        color: #fff;
        font-size: 10px;
        font-weight: 600;
        padding: 3px 6px;
        border-radius: 4px 0 0 4px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        pointer-events: none;
        z-index: 1;
    }

    @media (prefers-reduced-motion: reduce) {
        .ad-link {
            transition: none;
        }
    }
</style>
