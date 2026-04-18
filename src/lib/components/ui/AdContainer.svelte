<script>
// @ts-nocheck
import { onDestroy, onMount } from 'svelte'
import {
    AD_SPOTS,
    getBannerAds,
    getMobileAds,
    getMobileBannerAds,
    getNextAdIndex,
    getRandomAdIndex,
    setAdSpotIndex,
} from '$lib/stores/ads.js'

/**
 * @typedef {{ id: string, href: string, isCustom?: string, src?: string, width?: number, height?: number, alt?: string }} Ad
 */

// Desktop banner ads
/** @type {Ad[]} */
const bannerAds = getBannerAds()
let bannerIndex = getRandomAdIndex(AD_SPOTS.BANNER, bannerAds)
let bannerTransitioning = false
/** @type {ReturnType<typeof setInterval> | undefined} */
let bannerInterval

// Mobile square/rectangle ads
/** @type {Ad[]} */
const mobileAds = getMobileAds()
let mobileIndex = getRandomAdIndex(AD_SPOTS.MOBILE_MAIN, mobileAds)
let mobileTransitioning = false
/** @type {ReturnType<typeof setInterval> | undefined} */
let mobileInterval

// Mobile banner ads (horizontal, narrower)
/** @type {Ad[]} */
const mobileBannerAds = getMobileBannerAds()
let mobileBannerIndex = getRandomAdIndex(AD_SPOTS.MOBILE_BANNER, mobileBannerAds)
let mobileBannerTransitioning = false
/** @type {ReturnType<typeof setInterval> | undefined} */
let mobileBannerInterval

let isPaused = false
/** @type {boolean} */
let _isMobile = false

function checkMobile() {
    _isMobile = typeof window !== 'undefined' && window.innerWidth < 768
}

function _pauseAds() {
    isPaused = true
}

function _resumeAds() {
    isPaused = false
}

// --- Banner rotation ---
function nextBanner() {
    if (isPaused) return
    bannerTransitioning = true
    setTimeout(() => {
        bannerIndex = getNextAdIndex(AD_SPOTS.BANNER, bannerIndex, bannerAds)
        setAdSpotIndex(AD_SPOTS.BANNER, bannerIndex)
        setTimeout(() => {
            bannerTransitioning = false
        }, 500)
    }, 500)
}

// --- Mobile ad rotation ---
function nextMobile() {
    if (isPaused) return
    mobileTransitioning = true
    setTimeout(() => {
        mobileIndex = getNextAdIndex(AD_SPOTS.MOBILE_MAIN, mobileIndex, mobileAds)
        setAdSpotIndex(AD_SPOTS.MOBILE_MAIN, mobileIndex)
        setTimeout(() => {
            mobileTransitioning = false
        }, 500)
    }, 500)
}

// --- Mobile banner rotation ---
function nextMobileBanner() {
    if (isPaused) return
    mobileBannerTransitioning = true
    setTimeout(() => {
        mobileBannerIndex = getNextAdIndex(
            AD_SPOTS.MOBILE_BANNER,
            mobileBannerIndex,
            mobileBannerAds
        )
        setAdSpotIndex(AD_SPOTS.MOBILE_BANNER, mobileBannerIndex)
        setTimeout(() => {
            mobileBannerTransitioning = false
        }, 500)
    }, 500)
}

onMount(() => {
    checkMobile()

    // Start rotation intervals
    bannerInterval = setInterval(nextBanner, 20000)
    mobileInterval = setInterval(nextMobile, 20000)
    mobileBannerInterval = setInterval(nextMobileBanner, 20000)

    window.addEventListener('resize', checkMobile)
})

onDestroy(() => {
    if (bannerInterval) clearInterval(bannerInterval)
    if (mobileInterval) clearInterval(mobileInterval)
    if (mobileBannerInterval) clearInterval(mobileBannerInterval)
    if (typeof window !== 'undefined') {
        window.removeEventListener('resize', checkMobile)
    }
})

// Logo helper for custom banners
/** @param {Ad} ad */
function getLogoSrc(ad) {
    const name = ad.isCustom === 'vattenfall-opiskelija' ? 'vattenfall' : ad.isCustom
    const ext = ad.isCustom === 'kvarn' ? 'webp' : 'svg'
    return `/${name}-logo.${ext}`
}
</script>

<!--
  Unified ad container with reserved space at all breakpoints.
  - Desktop (>=768px): shows horizontal banner
  - Mobile (<768px): shows square/rectangle ad + horizontal banner below it
  Space is always reserved — zero layout shift.
-->
<div
    class="ad-container"
    on:mouseenter={pauseAds}
    on:mouseleave={resumeAds}
    role="region"
    aria-label="Mainos"
>
    <!-- Desktop banner (hidden on mobile) -->
    <div class="ad-slot ad-slot--desktop">
        {#each bannerAds as ad, index (ad.id)}
            <a
                href={ad.href}
                target="_blank"
                rel="noopener noreferrer"
                class="ad-link"
                class:active={index === bannerIndex}
                class:fade-out={index !== bannerIndex || bannerTransitioning}
            >
                {#if ad.isCustom === 'dna'}
                    <div class="custom-banner dna">
                        <span class="firefly" style="top:20%;left:10%;width:2px;height:2px;--delay:0.3s"></span>
                        <span class="firefly" style="top:55%;right:8%;width:3px;height:3px;--delay:2.7s"></span>
                        <span class="firefly" style="bottom:25%;left:25%;width:2px;height:2px;--delay:5.1s"></span>
                        <span class="firefly" style="top:35%;left:60%;width:2px;height:2px;--delay:1.4s"></span>
                        <img src={getLogoSrc(ad)} alt="DNA" class="logo" on:error={(e) => { if (e.target instanceof HTMLElement) e.target.style.display='none'; }} />
                        <div class="content">Voita iPhone 17 Pro!</div>
                        <span class="cta">Lisätietoja</span>
                    </div>
                {:else if ad.isCustom === 'multitronic'}
                    <div class="custom-banner multitronic">
                        <span class="firefly" style="top:15%;left:12%;width:2px;height:2px;--delay:0.8s"></span>
                        <span class="firefly" style="top:60%;right:15%;width:2px;height:2px;--delay:3.5s"></span>
                        <span class="firefly" style="bottom:30%;left:30%;width:3px;height:3px;--delay:6.2s"></span>
                        <span class="firefly" style="top:40%;left:50%;width:2px;height:2px;--delay:1.9s"></span>
                        <img src={getLogoSrc(ad)} alt="Multitronic" class="logo" on:error={(e) => { if (e.target instanceof HTMLElement) e.target.style.display='none'; }} />
                        <div class="content">IT-tuotteet parhaaseen hintaan</div>
                        <span class="cta">Lisätietoja</span>
                    </div>
                {:else if ad.isCustom === 'vattenfall'}
                    <div class="custom-banner vattenfall">
                        <span class="firefly dark" style="top:18%;left:8%;width:2px;height:2px;--delay:1.1s"></span>
                        <span class="firefly dark" style="top:50%;right:12%;width:3px;height:3px;--delay:4.8s"></span>
                        <span class="firefly dark" style="bottom:22%;left:35%;width:2px;height:2px;--delay:7.3s"></span>
                        <span class="firefly dark" style="top:38%;left:55%;width:2px;height:2px;--delay:2.5s"></span>
                        <img src={getLogoSrc(ad)} alt="Vattenfall" class="logo" on:error={(e) => { if (e.target instanceof HTMLElement) e.target.style.display='none'; }} />
                        <div class="content">Kiinteä hinta 12 kk + CO₂-säästö</div>
                        <span class="cta">Lisätietoja</span>
                    </div>
                {:else if ad.isCustom === 'vattenfall-opiskelija'}
                    <div class="custom-banner vattenfall-opiskelija">
                        <span class="firefly yellow" style="top:22%;left:10%;width:2px;height:2px;--delay:0.6s"></span>
                        <span class="firefly yellow" style="top:58%;right:14%;width:2px;height:2px;--delay:3.2s"></span>
                        <span class="firefly yellow" style="bottom:28%;left:28%;width:3px;height:3px;--delay:5.9s"></span>
                        <span class="firefly yellow" style="top:42%;left:52%;width:2px;height:2px;--delay:1.7s"></span>
                        <img src={getLogoSrc(ad)} alt="Vattenfall" class="logo" on:error={(e) => { if (e.target instanceof HTMLElement) e.target.style.display='none'; }} />
                        <div class="content">Edullinen sähkö opiskelijalle</div>
                        <span class="cta">Lisätietoja</span>
                    </div>
                {:else if ad.isCustom === 'kvarn'}
                    <div class="custom-banner kvarn">
                        <span class="firefly green" style="top:20%;left:8%;width:2px;height:2px;--delay:2.3s"></span>
                        <span class="firefly green" style="top:52%;right:10%;width:2px;height:2px;--delay:5.6s"></span>
                        <span class="firefly green" style="bottom:24%;left:40%;width:3px;height:3px;--delay:0.4s"></span>
                        <span class="firefly green" style="top:35%;left:58%;width:2px;height:2px;--delay:7.1s"></span>
                        <img src={getLogoSrc(ad)} alt="Kvarn X" class="logo on-dark" on:error={(e) => { if (e.target instanceof HTMLElement) e.target.style.display='none'; }} />
                        <div class="content">Osakkeet & krypto Suomessa</div>
                        <span class="cta">Lisätietoja</span>
                    </div>
                {:else if ad.isCustom === 'kodin1'}
                    <div class="custom-banner kodin1">
                        <span class="firefly pink" style="top:18%;left:12%;width:2px;height:2px;--delay:1.3s"></span>
                        <span class="firefly pink" style="top:55%;right:16%;width:2px;height:2px;--delay:4.4s"></span>
                        <span class="firefly pink" style="bottom:26%;left:32%;width:2px;height:2px;--delay:6.8s"></span>
                        <span class="firefly pink" style="top:38%;left:48%;width:2px;height:2px;--delay:2.1s"></span>
                        <img src={getLogoSrc(ad)} alt="Kodin 1" class="logo" on:error={(e) => { if (e.target instanceof HTMLElement) e.target.style.display='none'; }} />
                        <div class="content">Sisusta kotisi edullisesti</div>
                        <span class="cta">Lisätietoja</span>
                    </div>
                {:else}
                    <img src={ad.src} width={ad.width} height={ad.height} alt={ad.alt || 'Mainos'} class="ad-img" />
                {/if}
                <span class="ad-disclaimer">Mainos</span>
            </a>
        {/each}
    </div>

    <!-- Mobile square/rectangle ad (hidden on desktop) -->
    <div class="ad-slot ad-slot--mobile-square">
        {#each mobileAds as ad, index (ad.id)}
            <a
                href={ad.href}
                target="_blank"
                rel="noopener noreferrer"
                class="ad-link ad-link--square"
                class:active={index === mobileIndex}
                class:fade-out={index !== mobileIndex || mobileTransitioning}
            >
                <img src={ad.src} width={ad.width} height={ad.height} alt="Mainos" class="ad-img ad-img--square" />
                <span class="ad-disclaimer">Mainos</span>
            </a>
        {/each}
    </div>

    <!-- Mobile horizontal banner (hidden on desktop) -->
    <div class="ad-slot ad-slot--mobile-banner">
        {#each mobileBannerAds as ad, index (ad.id)}
            <a
                href={ad.href}
                target="_blank"
                rel="noopener noreferrer"
                class="ad-link ad-link--mbanner"
                class:active={index === mobileBannerIndex}
                class:fade-out={index !== mobileBannerIndex || mobileBannerTransitioning}
            >
                <img src={ad.src} width={ad.width} height={ad.height} alt="Mainos" class="ad-img" />
                <span class="ad-disclaimer">Mainos</span>
            </a>
        {/each}
    </div>
</div>

<style>
    /* Base container — always takes up reserved space */
    .ad-container {
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 0;
    }

    /* Shared slot styles */
    .ad-slot {
        position: relative;
        display: flex;
        justify-content: center;
        align-items: center;
    }

    /* Ad link base — absolute positioning for crossfade */
    .ad-link {
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        display: block;
        border: none;
        opacity: 0;
        transition: opacity 0.8s ease-in-out;
        pointer-events: none;
    }

    .ad-link.active {
        position: relative;
        left: 0;
        transform: none;
        opacity: 1;
        pointer-events: auto;
    }

    .ad-link.fade-out { opacity: 0; }

    .ad-img {
        max-width: 100%;
        height: auto;
        border: 0;
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
        z-index: 10;
    }

    /* =====================
       DESKTOP (>=768px)
       Only banner visible
       ===================== */
    .ad-slot--desktop {
        width: 100%;
        max-width: 980px;
        /* Reserved height for desktop banner */
        min-height: 120px;
        padding: 1rem 0;
    }

    .ad-slot--mobile-square,
    .ad-slot--mobile-banner {
        display: none;
    }

    /* =====================
       MOBILE (<768px)
       Square ad + banner stacked, both with reserved space
       ===================== */
    @media (max-width: 767px) {
        .ad-slot--desktop {
            display: none;
        }

        .ad-slot--mobile-square {
            display: flex;
            width: 100%;
            /* Reserved: 300x250 IAB Medium Rectangle */
            min-height: 250px;
            max-width: 300px;
            padding: 0.75rem 0 0.5rem;
        }

        .ad-link--square {
            width: 300px;
            height: 250px;
        }

        .ad-img--square {
            width: 100%;
            height: 100%;
            object-fit: contain;
        }

        .ad-slot--mobile-banner {
            display: flex;
            width: 100%;
            /* Reserved: 300x250 IAB Medium Rectangle */
            min-height: 250px;
            max-width: 300px;
            padding: 0.5rem 0 0.75rem;
        }

        .ad-link--mbanner {
            width: 300px;
            height: 250px;
        }
    }

    /* Reduced motion */
    @media (prefers-reduced-motion: reduce) {
        .ad-link { transition: none; }
    }

    /* =====================
       Custom banner styles (shared with AdBanner)
       ===================== */
    .custom-banner {
        position: relative;
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1.75rem 1.25rem;
        border-radius: 6px;
        overflow: hidden;
        transition: transform 0.2s ease;
    }

    .custom-banner:hover { transform: translateY(-2px); }

    .logo { height: 56px; width: auto; flex-shrink: 0; }
    .logo.on-dark { background: #fff; padding: 4px; border-radius: 4px; }
    .content { font-size: 1.1rem; line-height: 1.4; }
    .cta {
        margin-left: auto;
        font-size: 0.8rem;
        font-weight: 500;
        padding: 0.4rem 0.75rem;
        border-radius: 4px;
        white-space: nowrap;
    }

    /* Firefly animation */
    .firefly {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.6);
        box-shadow: 0 0 4px 1px rgba(255, 255, 255, 0.3);
        opacity: 0;
        animation: firefly 8s ease-in-out infinite;
        animation-delay: var(--delay, 0s);
        pointer-events: none;
    }

    .firefly.dark { background: rgba(255, 214, 0, 0.4); box-shadow: 0 0 4px 1px rgba(255, 214, 0, 0.2); }
    .firefly.yellow { background: rgba(255, 214, 0, 0.4); box-shadow: 0 0 4px 1px rgba(255, 214, 0, 0.2); }
    .firefly.green { background: rgba(144, 255, 188, 0.4); box-shadow: 0 0 4px 1px rgba(144, 255, 188, 0.2); }
    .firefly.pink { background: rgba(233, 25, 108, 0.35); box-shadow: 0 0 4px 1px rgba(233, 25, 108, 0.2); }

    @keyframes firefly {
        0%, 100% { opacity: 0; transform: translate(0, 0); }
        25% { opacity: 0.5; }
        50% { opacity: 0.25; transform: translate(6px, -10px); }
        75% { opacity: 0.4; }
    }

    /* Color themes */
    .custom-banner.dna { background: linear-gradient(135deg, #da0070, #b0005a); border: 2px solid rgba(255,255,255,0.3); }
    .custom-banner.dna .cta { background: #fff; color: #da0070; }
    .custom-banner.dna .content { color: #fff; }

    .custom-banner.multitronic { background: linear-gradient(135deg, #1e293b, #0f172a); border: 1px solid rgba(255,255,255,0.15); }
    .custom-banner.multitronic .cta { background: #f97316; color: #fff; }
    .custom-banner.multitronic .content,
    .custom-banner.multitronic .content strong { color: #fff; }

    .custom-banner.vattenfall { background: linear-gradient(135deg, #ffd600, #f5c400); border: 2px solid #000; }
    .custom-banner.vattenfall .cta { background: #000; color: #fff; }

    .custom-banner.vattenfall-opiskelija { background: linear-gradient(135deg, #0a0a0a, #1a1a1a); border: 2px solid #ffd600; }
    .custom-banner.vattenfall-opiskelija .cta { background: #ffd600; color: #000; }
    .custom-banner.vattenfall-opiskelija .content,
    .custom-banner.vattenfall-opiskelija .content strong { color: #fff; }

    .custom-banner.kvarn { background: linear-gradient(135deg, #0f172a, #1e293b); border: 2px solid #5dde7d; }
    .custom-banner.kvarn .cta { background: #5dde7d; color: #0f172a; }
    .custom-banner.kvarn .content,
    .custom-banner.kvarn .content strong { color: #fff; }

    .custom-banner.kodin1 { background: linear-gradient(135deg, #fff, #fce4ec); border: 2px solid #e9196c; }
    .custom-banner.kodin1 .cta { background: #e9196c; color: #fff; }

    /* Responsive custom banners */
    @media (max-width: 768px) {
        .custom-banner {
            flex-direction: column;
            text-align: center;
            gap: 0.5rem;
            padding: 1rem 0.75rem;
        }
        .logo { height: 28px; }
        .content { font-size: 0.85rem; }
        .cta { margin-left: 0; width: 100%; text-align: center; }
        .firefly { display: none; }
    }
</style>
