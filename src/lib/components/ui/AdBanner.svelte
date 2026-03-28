<script>
import { onDestroy, onMount } from 'svelte'

const ads = [
    {
        href: 'https://go.adt246.net/t/t?a=1883588377&as=2038972948&t=2&tk=1',
        src: null,
        width: 980,
        height: 120,
        alt: 'DNA iPhone 17 kampanja',
        isCustom: 'dna',
    },
    {
        href: 'https://go.adt253.net/t/t?a=1930975670&as=2038972948&t=2&tk=1',
        src: null,
        width: 980,
        height: 120,
        alt: 'Multitronic',
        isCustom: 'multitronic',
    },
    {
        href: 'https://on.kahvikaveri.fi/t/t?a=1895089445&as=2038972948&t=2&tk=1',
        src: 'https://track.adtraction.com/t/t?a=1895089445&as=2038972948&t=1&tk=1&i=1',
        width: 980,
        height: 120,
        alt: 'Mainos',
    },
    {
        href: 'https://go.adt242.com/t/t?a=1875158487&as=2038972948&t=2&tk=1',
        src: 'https://track.adtraction.com/t/t?a=1875158487&as=2038972948&t=1&tk=1&i=1',
        width: 728,
        height: 90,
        alt: 'Mainos',
    },
    {
        href: 'https://to.bjornborg.com/t/t?a=1616919148&as=2038972948&t=2&tk=1',
        src: 'https://track.adtraction.com/t/t?a=1616919148&as=2038972948&t=1&tk=1&i=1',
        width: 980,
        height: 120,
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
    }, 8000)
})

onDestroy(() => {
    if (interval) clearInterval(interval)
})
</script>

<div class="ad-banner-container">
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
                class="ad-banner-link"
                class:active={index === currentAdIndex}
                class:fade-out={index !== currentAdIndex || _isTransitioning}
            >
                {#if ad.isCustom === 'dna'}
                    <div class="dna-custom-banner" style="background-color: #DA0070; width: {ad.width}px; height: {ad.height}px;">
                        <img src="/dna-logo.svg" alt="DNA" class="dna-logo" />
                        <span class="dna-headline">Voita iPhone 17!</span>
                        <span class="dna-cta">Osallistu nyt →</span>
                    </div>
                {:else if ad.isCustom === 'multitronic'}
                    <div class="multitronic-custom-banner" style="width: {ad.width}px; height: {ad.height}px;">
                        <img src="/multitronic-logo.svg" alt="Multitronic" class="multitronic-logo" />
                        <span class="multitronic-headline">Tietokoneet & Komponentit</span>
                        <span class="multitronic-cta">Tutustu →</span>
                    </div>
                {:else}
                    <img
                        src={ad.src}
                        width={ad.width}
                        height={ad.height}
                        alt={ad.alt}
                        class="ad-banner-img"
                    />
                {/if}
                <span class="ad-disclaimer">Mainos</span>
            </a>
        {/each}
    </div>
</div>

<style>
    .ad-banner-container {
        width: 100%;
        display: flex;
        justify-content: center;
        padding: 1rem 0;
    }

    .ad-wrapper {
        position: relative;
        max-width: 980px;
        min-height: 120px;
    }

    .ad-banner-link {
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        display: block;
        border: none;
        opacity: 0;
        transition: opacity 1s ease-in-out;
        pointer-events: none;
    }

    .ad-banner-link.active {
        position: relative;
        left: 0;
        transform: none;
        opacity: 1;
        pointer-events: auto;
    }

    .ad-banner-link.fade-out {
        opacity: 0;
    }

    @media (prefers-reduced-motion: reduce) {
        .ad-banner-link {
            transition: none;
        }
    }

    .ad-banner-img {
        max-width: 100%;
        height: auto;
        border: 0;
        border-radius: 8px;
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

    @media (max-width: 639px) {
        .ad-wrapper {
            min-height: auto;
        }

        .ad-banner-container {
            padding: 0.5rem 0;
        }
    }

    .dna-custom-banner {
        display: flex;
        align-items: center;
        gap: 1.5rem;
        padding: 0 1.5rem;
        border-radius: 8px;
        color: white;
        width: 980px;
        height: 120px;
        box-sizing: border-box;
    }

    .dna-logo {
        width: 80px;
        height: 80px;
        flex-shrink: 0;
    }

    .dna-headline {
        font-size: 1.75rem;
        font-weight: 700;
    }

    .dna-cta {
        font-size: 1.125rem;
        font-weight: 600;
        opacity: 0.9;
        margin-left: auto;
    }

    @media (max-width: 1000px) {
        .dna-custom-banner {
            width: 728px;
            height: 90px;
            gap: 1rem;
            padding: 0 1rem;
        }

        .dna-logo {
            width: 60px;
            height: 60px;
        }

        .dna-headline {
            font-size: 1.25rem;
        }

        .dna-cta {
            font-size: 1rem;
        }
    }

    @media (max-width: 768px) {
        .dna-custom-banner {
            width: 100%;
            max-width: 728px;
            height: auto;
            min-height: 60px;
            padding: 0.5rem 1rem;
            gap: 0.75rem;
        }

        .dna-logo {
            width: 40px;
            height: 40px;
        }

        .dna-headline {
            font-size: 1rem;
        }

        .dna-cta {
            font-size: 0.875rem;
        }
    }

    .multitronic-custom-banner {
        display: flex;
        align-items: center;
        gap: 1.5rem;
        padding: 0 1.5rem;
        border-radius: 8px;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #333;
        color: white;
        box-sizing: border-box;
    }

    .multitronic-logo {
        height: 36px;
        width: auto;
        flex-shrink: 0;
    }

    .multitronic-headline {
        font-size: 1.5rem;
        font-weight: 700;
    }

    .multitronic-cta {
        font-size: 1.125rem;
        font-weight: 600;
        color: #F59200;
        margin-left: auto;
    }

    @media (max-width: 1000px) {
        .multitronic-custom-banner {
            width: 728px;
            height: 90px;
            gap: 1rem;
            padding: 0 1rem;
        }

        .multitronic-logo {
            height: 28px;
        }

        .multitronic-headline {
            font-size: 1.125rem;
        }

        .multitronic-cta {
            font-size: 1rem;
        }
    }

    @media (max-width: 768px) {
        .multitronic-custom-banner {
            width: 100%;
            max-width: 728px;
            height: auto;
            min-height: 60px;
            padding: 0.5rem 1rem;
            gap: 0.75rem;
        }

        .multitronic-logo {
            height: 24px;
        }

        .multitronic-headline {
            font-size: 0.875rem;
        }

        .multitronic-cta {
            font-size: 0.875rem;
        }
    }
</style>
