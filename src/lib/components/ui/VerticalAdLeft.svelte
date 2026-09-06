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
let _isPaused = false
let interval
let failedAds = {}

function pauseAds() {
    _isPaused = true
}

function resumeAds() {
    _isPaused = false
}

function nextAd() {
    if (_isPaused) return
    currentAdIndex = (currentAdIndex + 1) % ads.length
}

function setAdFailed(index, failed) {
    failedAds = { ...failedAds, [index]: failed }
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
        onmouseenter={pauseAds}
        onmouseleave={resumeAds}
        role="region"
        aria-label="Mainos"
    >
        {#if failedAds[currentAdIndex]}
            <div class="support-message" aria-hidden="true">
                Näyttää siltä, että käytät mainostenestoa. Arvostamme suuresti, jos
                lisäät sivuston sallittujen listalle.
            </div>
        {/if}
        {#each ads as ad, index (index)}
            <a
                href={ad.href}
                target="_blank"
                rel="noopener noreferrer"
                class="ad-link"
                class:active={index === currentAdIndex}
                class:fade-out={index !== currentAdIndex}
            >
                <div class="ad-content-wrapper">
                    <img
                        src={ad.src}
                        alt={ad.alt}
                        class="ad-img"
                        onload={() => setAdFailed(index, false)}
                        onerror={() => setAdFailed(index, true)}
                    />
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
    @media (max-width: 1535px) {
        .vertical-ad-container-left {
            display: none !important;
        }
    }

    @media (min-width: 1536px) {
        .vertical-ad-container-left {
            display: block;
            position: fixed;
            left: 1rem;
            top: 50%;
            transform: translateY(-50%);
            width: 160px;
            max-height: 100vh;
            max-height: 100dvh;
            overflow: visible;
        }

        .ad-wrapper {
            width: 160px;
            height: 600px;
            max-height: calc(100dvh - 2rem);
        }

        .ad-link {
            position: absolute;
            width: 100%;
            max-height: 600px;
        }
    }

    .ad-wrapper {
        position: relative;
        width: 160px;
        height: 600px;
        max-height: calc(100dvh - 2rem);
        background: #ffffff;
        border-radius: 0;
        border: 1px solid rgba(16, 24, 40, 0.12);
        box-shadow:
            0 8px 22px rgba(0, 53, 128, 0.1),
            0 1px 4px rgba(16, 24, 40, 0.04);
        overflow: hidden;
    }

    .support-message {
        position: absolute;
        inset: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0.65rem;
        border: 1px dashed rgba(0, 53, 128, 0.24);
        background: rgba(238, 243, 251, 0.72);
        color: rgba(15, 23, 42, 0.72);
        font-size: 0.68rem;
        font-weight: 700;
        line-height: 1.35;
        text-align: center;
        pointer-events: none;
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
        transition: opacity 0.8s ease-in-out;
        pointer-events: none;
    }

    .ad-content-wrapper {
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 100%;
        line-height: 0;
        border-radius: 0;
        box-shadow: none;
        isolation: isolate;
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
        border: none;
        box-shadow: none;
        border-radius: 0;
        display: block;
        position: relative;
        z-index: 1;
    }

    .ad-disclaimer {
        position: absolute;
        top: 6px;
        left: 50%;
        transform: translateX(-50%);
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        background: var(--accent-ice, #eef3fb);
        color: var(--accent, #003580);
        border: 1px solid rgba(16, 24, 40, 0.14);
        border-radius: 999px;
        padding: 2px 7px 2px 5px;
        font-size: 8px;
        font-weight: 800;
        line-height: 1.2;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        box-shadow: 0 1px 2px rgba(0, 53, 128, 0.08);
        pointer-events: none;
        z-index: 1;
    }

    .ad-disclaimer::before {
        content: '';
        width: 4px;
        height: 4px;
        border-radius: 999px;
        background: var(--accent, #003580);
        box-shadow: 0 0 0 2px rgba(0, 53, 128, 0.12);
    }

    @media (prefers-reduced-motion: reduce) {
        .ad-link {
            transition: none;
        }
    }
</style>
