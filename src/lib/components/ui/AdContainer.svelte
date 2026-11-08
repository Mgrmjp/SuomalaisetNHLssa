<script>
// @ts-nocheck
import { onDestroy, onMount } from 'svelte'
import AdLabel from './AdLabel.svelte'
import {
    AD_SPOTS,
    getBannerAds,
    getNextAdIndex,
    getRandomAdIndex,
    setAdSpotIndex,
} from '$lib/stores/ads.js'

/**
 * @typedef {{ id: string, href: string, isCustom?: string, src?: string, width?: number, height?: number, alt?: string, expiresAt?: string }} Ad
 */

// Desktop banner ads
/** @type {Ad[]} */
let bannerAds = []
let bannerIndex = 0
/** @type {ReturnType<typeof setInterval> | undefined} */
let bannerInterval

let expiryTimeout
let isPaused = false
let loadedBannerAds = {}
$: readyBannerAds = bannerAds.filter((ad) => ad.isCustom || loadedBannerAds[ad.id])
$: activeBanner = readyBannerAds[bannerIndex] || readyBannerAds[0]

function getRefreshedIndex(spot, ads, previousId) {
    if (!previousId) return getRandomAdIndex(spot, ads)
    return Math.max(
        0,
        ads.findIndex((ad) => ad.id === previousId)
    )
}

function refreshAds() {
    const now = Date.now()
    const bannerId = activeBanner?.id
    bannerAds = getBannerAds(now)
    bannerIndex = getRefreshedIndex(AD_SPOTS.BANNER, readyBannerAds, bannerId)
    setAdSpotIndex(AD_SPOTS.BANNER, bannerIndex)

    if (expiryTimeout) clearTimeout(expiryTimeout)
    const nextExpiry = Math.min(
        ...bannerAds.filter((ad) => ad.expiresAt).map((ad) => Date.parse(ad.expiresAt))
    )
    if (Number.isFinite(nextExpiry)) {
        // Recheck long campaigns before the browser's maximum timeout delay.
        expiryTimeout = setTimeout(refreshAds, Math.min(nextExpiry - now, 2_147_483_647))
    }
}

// --- Banner rotation ---
function nextBanner() {
    if (isPaused || readyBannerAds.length === 0) return
    bannerIndex = getNextAdIndex(AD_SPOTS.BANNER, bannerIndex, readyBannerAds)
    setAdSpotIndex(AD_SPOTS.BANNER, bannerIndex)
}

function setBannerLoaded(ad, image) {
    loadedBannerAds = {
        ...loadedBannerAds,
        [ad.id]: image.naturalWidth > 1 && image.naturalHeight > 1,
    }
}

onMount(() => {
    refreshAds()

    // Start rotation intervals
    bannerInterval = setInterval(nextBanner, 20000)

    window.addEventListener('focus', refreshAds)
    document.addEventListener('visibilitychange', refreshAds)
})

onDestroy(() => {
    if (bannerInterval) clearInterval(bannerInterval)
    if (expiryTimeout) clearTimeout(expiryTimeout)
    if (typeof window !== 'undefined') {
        window.removeEventListener('focus', refreshAds)
        document.removeEventListener('visibilitychange', refreshAds)
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

<div
    class="ad-container"
    onmouseenter={() => (isPaused = true)}
    onmouseleave={() => (isPaused = false)}
    role="region"
    aria-label="Mainos"
>
    <!-- Desktop banner (hidden on mobile) -->
    <div class="ad-slot ad-slot--desktop" class:ad-slot--empty={!activeBanner}>
        <AdLabel />
        {#each bannerAds as ad (ad.id)}
            <a
                href={ad.href}
                target="_blank"
                rel="noopener noreferrer"
                class="ad-link"
                class:active={ad.id === activeBanner?.id}
                class:fade-out={ad.id !== activeBanner?.id}
                tabindex={ad.id === activeBanner?.id ? 0 : -1}
                aria-hidden={ad.id !== activeBanner?.id}
            >
                {#if ad.isCustom === 'dna'}
                    <div class="custom-banner dna">
                        <span
                            class="firefly"
                            style="top:20%;left:10%;width:2px;height:2px;--delay:0.3s"
                        ></span>
                        <span
                            class="firefly"
                            style="top:55%;right:8%;width:3px;height:3px;--delay:2.7s"
                        ></span>
                        <span
                            class="firefly"
                            style="bottom:25%;left:25%;width:2px;height:2px;--delay:5.1s"
                        ></span>
                        <span
                            class="firefly"
                            style="top:35%;left:60%;width:2px;height:2px;--delay:1.4s"
                        ></span>
                        <img
                            src={getLogoSrc(ad)}
                            alt="DNA"
                            class="logo"
                            onerror={(e) => {
                                if (e.target instanceof HTMLElement) e.target.style.display = 'none'
                            }}
                        />
                        <div class="content">Voita iPhone 17 Pro!</div>
                        <span class="cta">Lisätietoja</span>
                    </div>
                {:else if ad.isCustom === 'multitronic'}
                    <div class="custom-banner multitronic">
                        <span
                            class="firefly"
                            style="top:15%;left:12%;width:2px;height:2px;--delay:0.8s"
                        ></span>
                        <span
                            class="firefly"
                            style="top:60%;right:15%;width:2px;height:2px;--delay:3.5s"
                        ></span>
                        <span
                            class="firefly"
                            style="bottom:30%;left:30%;width:3px;height:3px;--delay:6.2s"
                        ></span>
                        <span
                            class="firefly"
                            style="top:40%;left:50%;width:2px;height:2px;--delay:1.9s"
                        ></span>
                        <img
                            src={getLogoSrc(ad)}
                            alt="Multitronic"
                            class="logo"
                            onerror={(e) => {
                                if (e.target instanceof HTMLElement) e.target.style.display = 'none'
                            }}
                        />
                        <div class="content">IT-tuotteet parhaaseen hintaan</div>
                        <span class="cta">Lisätietoja</span>
                    </div>
                {:else if ad.isCustom === 'vattenfall'}
                    <div class="custom-banner vattenfall">
                        <span
                            class="firefly dark"
                            style="top:18%;left:8%;width:2px;height:2px;--delay:1.1s"
                        ></span>
                        <span
                            class="firefly dark"
                            style="top:50%;right:12%;width:3px;height:3px;--delay:4.8s"
                        ></span>
                        <span
                            class="firefly dark"
                            style="bottom:22%;left:35%;width:2px;height:2px;--delay:7.3s"
                        ></span>
                        <span
                            class="firefly dark"
                            style="top:38%;left:55%;width:2px;height:2px;--delay:2.5s"
                        ></span>
                        <img
                            src={getLogoSrc(ad)}
                            alt="Vattenfall"
                            class="logo"
                            onerror={(e) => {
                                if (e.target instanceof HTMLElement) e.target.style.display = 'none'
                            }}
                        />
                        <div class="content">Kiinteä hinta 12 kk + CO₂-säästö</div>
                        <span class="cta">Lisätietoja</span>
                    </div>
                {:else if ad.isCustom === 'vattenfall-opiskelija'}
                    <div class="custom-banner vattenfall-opiskelija">
                        <span
                            class="firefly yellow"
                            style="top:22%;left:10%;width:2px;height:2px;--delay:0.6s"
                        ></span>
                        <span
                            class="firefly yellow"
                            style="top:58%;right:14%;width:2px;height:2px;--delay:3.2s"
                        ></span>
                        <span
                            class="firefly yellow"
                            style="bottom:28%;left:28%;width:3px;height:3px;--delay:5.9s"
                        ></span>
                        <span
                            class="firefly yellow"
                            style="top:42%;left:52%;width:2px;height:2px;--delay:1.7s"
                        ></span>
                        <img
                            src={getLogoSrc(ad)}
                            alt="Vattenfall"
                            class="logo"
                            onerror={(e) => {
                                if (e.target instanceof HTMLElement) e.target.style.display = 'none'
                            }}
                        />
                        <div class="content">Edullinen sähkö opiskelijalle</div>
                        <span class="cta">Lisätietoja</span>
                    </div>
                {:else if ad.isCustom === 'kvarn'}
                    <div class="custom-banner kvarn">
                        <span
                            class="firefly green"
                            style="top:20%;left:8%;width:2px;height:2px;--delay:2.3s"
                        ></span>
                        <span
                            class="firefly green"
                            style="top:52%;right:10%;width:2px;height:2px;--delay:5.6s"
                        ></span>
                        <span
                            class="firefly green"
                            style="bottom:24%;left:40%;width:3px;height:3px;--delay:0.4s"
                        ></span>
                        <span
                            class="firefly green"
                            style="top:35%;left:58%;width:2px;height:2px;--delay:7.1s"
                        ></span>
                        <img
                            src={getLogoSrc(ad)}
                            alt="Kvarn X"
                            class="logo on-dark"
                            onerror={(e) => {
                                if (e.target instanceof HTMLElement) e.target.style.display = 'none'
                            }}
                        />
                        <div class="content">Osakkeet & krypto Suomessa</div>
                        <span class="cta">Lisätietoja</span>
                    </div>
                {:else if ad.isCustom === 'kodin1'}
                    <div class="custom-banner kodin1">
                        <span
                            class="firefly pink"
                            style="top:18%;left:12%;width:2px;height:2px;--delay:1.3s"
                        ></span>
                        <span
                            class="firefly pink"
                            style="top:55%;right:16%;width:2px;height:2px;--delay:4.4s"
                        ></span>
                        <span
                            class="firefly pink"
                            style="bottom:26%;left:32%;width:2px;height:2px;--delay:6.8s"
                        ></span>
                        <span
                            class="firefly pink"
                            style="top:38%;left:48%;width:2px;height:2px;--delay:2.1s"
                        ></span>
                        <img
                            src={getLogoSrc(ad)}
                            alt="Kodin 1"
                            class="logo"
                            onerror={(e) => {
                                if (e.target instanceof HTMLElement) e.target.style.display = 'none'
                            }}
                        />
                        <div class="content">Sisusta kotisi edullisesti</div>
                        <span class="cta">Lisätietoja</span>
                    </div>
                {:else}
                    <img
                        src={ad.src}
                        alt={ad.alt || 'Mainos'}
                        class="ad-img"
                        onload={(event) => setBannerLoaded(ad, event.currentTarget)}
                        onerror={() => (loadedBannerAds = { ...loadedBannerAds, [ad.id]: false })}
                    />
                {/if}
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
    align-items: flex-start;
}

/* Ad link base — absolute positioning for crossfade */
.ad-link {
    position: absolute;
    top: 32px;
    left: 0;
    width: 100%;
    height: 90px;
    display: block;
    border: none;
    opacity: 0;
    transition: opacity 0.8s ease-in-out;
    pointer-events: none;
    overflow: visible;
    border-radius: 0;
    isolation: isolate;
}

.ad-link.active {
    opacity: 1;
    pointer-events: auto;
}

.ad-link.fade-out {
    opacity: 0;
}

.ad-link.active::before,
.custom-banner::before {
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
    object-fit: cover;
    border: 1px solid rgba(15, 23, 42, 0.85);
    border-radius: 0;
    display: block;
    position: relative;
    z-index: 1;
}

/* =====================
       DESKTOP (>=768px)
       Only banner visible - 728x90 IAB leaderboard
       ===================== */
.ad-slot--desktop {
    position: relative;
    width: 100%;
    max-width: 728px;
    height: 122px;
    margin: 0 auto;
}

@media (max-width: 767px) {
    .ad-slot--desktop {
        display: none;
    }
}

.ad-slot--empty {
    display: none;
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
    .ad-link {
        transition: none;
    }
}

/* =====================
       Custom banner styles
       ===================== */
.custom-banner {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.75rem;
    padding: 0 1rem;
    border-radius: 0;
    overflow: visible;
    transition: transform 0.2s ease;
    isolation: isolate;
    z-index: 1;
    /* Fixed IAB standard height */
    height: 90px;
    width: 100%;
    box-sizing: border-box;
}

.custom-banner > * {
    flex-shrink: 0;
}

.custom-banner:hover {
    transform: translateY(-2px);
}

.logo {
    height: 48px;
    width: auto;
    object-fit: contain;
}
.logo.on-dark {
    background: #fff;
    padding: 4px;
    border-radius: 0;
}
.content {
    font-size: 0.9rem;
    line-height: 1.2;
    flex: 1;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.cta {
    font-size: 0.75rem;
    font-weight: 500;
    padding: 0.3rem 0.6rem;
    border-radius: 4px;
    white-space: nowrap;
    flex-shrink: 0;
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

.firefly.dark {
    background: rgba(255, 214, 0, 0.4);
    box-shadow: 0 0 4px 1px rgba(255, 214, 0, 0.2);
}
.firefly.yellow {
    background: rgba(255, 214, 0, 0.4);
    box-shadow: 0 0 4px 1px rgba(255, 214, 0, 0.2);
}
.firefly.green {
    background: rgba(144, 255, 188, 0.4);
    box-shadow: 0 0 4px 1px rgba(144, 255, 188, 0.2);
}
.firefly.pink {
    background: rgba(233, 25, 108, 0.35);
    box-shadow: 0 0 4px 1px rgba(233, 25, 108, 0.2);
}

@keyframes firefly {
    0%,
    100% {
        opacity: 0;
        transform: translate(0, 0);
    }
    25% {
        opacity: 0.5;
    }
    50% {
        opacity: 0.25;
        transform: translate(6px, -10px);
    }
    75% {
        opacity: 0.4;
    }
}

@keyframes border-shimmer {
    0%,
    72%,
    100% {
        background-position: 140% 50%;
        opacity: 0;
    }
    78% {
        background-position: 60% 50%;
        opacity: 0.8;
    }
    84% {
        background-position: -20% 50%;
        opacity: 0;
    }
}

/* Color themes */
.custom-banner.dna {
    background: linear-gradient(135deg, #da0070, #b0005a);
    border: 2px solid rgba(255, 255, 255, 0.3);
}
.custom-banner.dna .cta {
    background: #fff;
    color: #da0070;
}
.custom-banner.dna .content {
    color: #fff;
}

.custom-banner.multitronic {
    background: linear-gradient(135deg, #1e293b, #0f172a);
    border: 1px solid rgba(255, 255, 255, 0.15);
}
.custom-banner.multitronic .cta {
    background: #f97316;
    color: #fff;
}
.custom-banner.multitronic .content {
    color: #fff;
}

.custom-banner.vattenfall {
    background: linear-gradient(135deg, #ffd600, #f5c400);
    border: 2px solid #000;
}
.custom-banner.vattenfall .cta {
    background: #000;
    color: #fff;
}

.custom-banner.vattenfall-opiskelija {
    background: linear-gradient(135deg, #0a0a0a, #1a1a1a);
    border: 2px solid #ffd600;
}
.custom-banner.vattenfall-opiskelija .cta {
    background: #ffd600;
    color: #000;
}
.custom-banner.vattenfall-opiskelija .content {
    color: #fff;
}

.custom-banner.kvarn {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    border: 2px solid #5dde7d;
}
.custom-banner.kvarn .cta {
    background: #5dde7d;
    color: #0f172a;
}
.custom-banner.kvarn .content {
    color: #fff;
}

.custom-banner.kodin1 {
    background: linear-gradient(135deg, #fff, #fce4ec);
    border: 2px solid #e9196c;
}
.custom-banner.kodin1 .cta {
    background: #e9196c;
    color: #fff;
}

/* Responsive custom banners - 300x250 IAB medium rectangle */
@media (max-width: 767px) {
    .custom-banner {
        flex-direction: column;
        text-align: center;
        justify-content: center;
        gap: 0.5rem;
        padding: 0.5rem;
        height: 250px;
    }
    .logo {
        height: 48px;
    }
    .content {
        font-size: 0.85rem;
        white-space: normal;
    }
    .cta {
        width: auto;
        text-align: center;
    }
    .firefly {
        display: none;
    }
}
</style>
