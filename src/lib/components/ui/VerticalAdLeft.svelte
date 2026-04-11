<script>
import { onDestroy, onMount } from 'svelte'

const ads = [
    {
        href: 'https://id.skruvat.fi/t/t?a=1483923855&as=2038972948&t=2&tk=1',
        src: 'https://track.adtraction.com/t/t?a=1483923855&as=2038972948&t=1&tk=1&i=1',
        width: 160,
        height: 600,
        alt: 'Mainos',
    },
    {
        href: 'https://to.bjornborg.com/t/t?a=1616919154&as=2038972948&t=2&tk=1',
        src: 'https://track.adtraction.com/t/t?a=1616919154&as=2038972948&t=1&tk=1&i=1',
        width: 120,
        height: 600,
        alt: 'Mainos',
    },
    {
        href: 'https://go.adt242.com/t/t?a=1875158502&as=2038972948&t=2&tk=1',
        src: 'https://track.adtraction.com/t/t?a=1875158502&as=2038972948&t=1&tk=1&i=1',
        width: 160,
        height: 600,
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
                    <img src={ad.src} width={ad.width} height={ad.height} alt={ad.alt} class="ad-img" />
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
        overflow: hidden;
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
        display: inline-block;
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
        width: auto;
        height: auto;
        max-width: 160px;
        max-height: 600px;
        border: 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border-radius: 8px;
        display: block;
    }

    .ad-disclaimer {
        position: absolute;
        top: 8px;
        left: 0;
        background: rgba(0, 0, 0, 0.6);
        color: #fff;
        font-size: 10px;
        font-weight: 600;
        padding: 3px 6px;
        border-radius: 0 4px 4px 0;
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
