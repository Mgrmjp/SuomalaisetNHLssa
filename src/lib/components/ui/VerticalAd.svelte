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
    {
        href: 'https://do.younameit.fi/t/t?a=2066802230&as=2038972948&t=2&tk=1',
        src: 'https://track.adtraction.com/t/t?a=2066802230&as=2038972948&t=1&tk=1&i=1',
        alt: 'YouNameIt',
        width: 120,
        height: 600,
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
    }, 4000)
})

onDestroy(() => {
    if (interval) clearInterval(interval)
})
</script>

<div class="vertical-ad-container">
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
    .vertical-ad-container {
        position: fixed;
        right: 1rem;
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
        .vertical-ad-container {
            display: none !important;
        }
    }

    @media (min-width: 1536px) {
        .vertical-ad-container {
            display: block;
            position: fixed;
            right: 1rem;
            top: 50%;
            transform: translateY(-50%);
            width: 110px;
            max-height: 100vh;
            max-height: 100dvh;
            overflow: visible;
        }

        .ad-wrapper {
            width: 110px;
            height: 400px;
            max-height: 400px;
        }

        .ad-link {
            position: absolute;
            width: 110px;
            max-height: 400px;
        }

        .ad-img {
            width: 110px;
            max-height: 400px;
            object-fit: contain;
        }
    }

    .ad-wrapper {
        position: relative;
        width: 110px;
        height: 400px;
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
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 100%;
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
