<script>
    import { onDestroy, onMount } from 'svelte'
    import { AD_SPOTS, getBannerAds, getRandomAdIndex, getNextAdIndex, setAdSpotIndex } from '$lib/stores/ads.js'

    const ads = getBannerAds()
    let currentAdIndex = getRandomAdIndex(AD_SPOTS.BANNER, ads)
    let _isTransitioning = false
    let _isPaused = false
    let interval

    setAdSpotIndex(AD_SPOTS.BANNER, currentAdIndex)

    function pauseAds() { _isPaused = true }
    function resumeAds() { _isPaused = false }

    function nextAd() {
        if (_isPaused) return
        _isTransitioning = true
        setTimeout(() => {
            currentAdIndex = getNextAdIndex(AD_SPOTS.BANNER, currentAdIndex, ads)
            setAdSpotIndex(AD_SPOTS.BANNER, currentAdIndex)
            setTimeout(() => { _isTransitioning = false }, 500)
        }, 500)
    }

    onMount(() => {
        setTimeout(() => { interval = setInterval(nextAd, 20000) }, 8000)
    })

    onDestroy(() => {
        if (interval) clearInterval(interval)
    })

    $: currentAd = ads[currentAdIndex]

    function getLogoSrc(ad) {
        const name = ad.isCustom === 'vattenfall-opiskelija' ? 'vattenfall' : ad.isCustom
        const ext = ad.isCustom === 'kvarn' ? 'webp' : 'svg'
        return `/${name}-logo.${ext}`
    }
</script>

<div class="ad-banner-container">
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
                class="ad-banner-link"
                class:active={index === currentAdIndex}
                class:fade-out={index !== currentAdIndex || _isTransitioning}
            >
                {#if ad.isCustom === 'dna'}
                    <div class="custom-banner dna">
                        <span class="firefly" style="top:20%;left:10%;width:2px;height:2px;--delay:0.3s"></span>
                        <span class="firefly" style="top:55%;right:8%;width:3px;height:3px;--delay:2.7s"></span>
                        <span class="firefly" style="bottom:25%;left:25%;width:2px;height:2px;--delay:5.1s"></span>
                        <span class="firefly" style="top:35%;left:60%;width:2px;height:2px;--delay:1.4s"></span>
                        <img src={getLogoSrc(ad)} alt="DNA" class="logo" on:error={(e) => e.target.style.display='none'} />
                        <div class="content">Voita iPhone 17 Pro!</div>
                        <span class="cta">Lisätietoja</span>
                    </div>
                {:else if ad.isCustom === 'multitronic'}
                    <div class="custom-banner multitronic">
                        <span class="firefly" style="top:15%;left:12%;width:2px;height:2px;--delay:0.8s"></span>
                        <span class="firefly" style="top:60%;right:15%;width:2px;height:2px;--delay:3.5s"></span>
                        <span class="firefly" style="bottom:30%;left:30%;width:3px;height:3px;--delay:6.2s"></span>
                        <span class="firefly" style="top:40%;left:50%;width:2px;height:2px;--delay:1.9s"></span>
                        <img src={getLogoSrc(ad)} alt="Multitronic" class="logo" on:error={(e) => e.target.style.display='none'} />
                        <div class="content">IT-tuotteet parhaaseen hintaan</div>
                        <span class="cta">Lisätietoja</span>
                    </div>
                {:else if ad.isCustom === 'vattenfall'}
                    <div class="custom-banner vattenfall">
                        <span class="firefly dark" style="top:18%;left:8%;width:2px;height:2px;--delay:1.1s"></span>
                        <span class="firefly dark" style="top:50%;right:12%;width:3px;height:3px;--delay:4.8s"></span>
                        <span class="firefly dark" style="bottom:22%;left:35%;width:2px;height:2px;--delay:7.3s"></span>
                        <span class="firefly dark" style="top:38%;left:55%;width:2px;height:2px;--delay:2.5s"></span>
                        <img src={getLogoSrc(ad)} alt="Vattenfall" class="logo" on:error={(e) => e.target.style.display='none'} />
                        <div class="content">Kiinteä hinta 12 kk + CO₂-säästö</div>
                        <span class="cta">Lisätietoja</span>
                    </div>
                {:else if ad.isCustom === 'vattenfall-opiskelija'}
                    <div class="custom-banner vattenfall-opiskelija">
                        <span class="firefly yellow" style="top:22%;left:10%;width:2px;height:2px;--delay:0.6s"></span>
                        <span class="firefly yellow" style="top:58%;right:14%;width:2px;height:2px;--delay:3.2s"></span>
                        <span class="firefly yellow" style="bottom:28%;left:28%;width:3px;height:3px;--delay:5.9s"></span>
                        <span class="firefly yellow" style="top:42%;left:52%;width:2px;height:2px;--delay:1.7s"></span>
                        <img src={getLogoSrc(ad)} alt="Vattenfall" class="logo" on:error={(e) => e.target.style.display='none'} />
                        <div class="content">Edullinen sähkö opiskelijalle</div>
                        <span class="cta">Lisätietoja</span>
                    </div>
                {:else if ad.isCustom === 'kvarn'}
                    <div class="custom-banner kvarn">
                        <span class="firefly green" style="top:20%;left:8%;width:2px;height:2px;--delay:2.3s"></span>
                        <span class="firefly green" style="top:52%;right:10%;width:2px;height:2px;--delay:5.6s"></span>
                        <span class="firefly green" style="bottom:24%;left:40%;width:3px;height:3px;--delay:0.4s"></span>
                        <span class="firefly green" style="top:35%;left:58%;width:2px;height:2px;--delay:7.1s"></span>
                        <img src={getLogoSrc(ad)} alt="Kvarn X" class="logo on-dark" on:error={(e) => e.target.style.display='none'} />
                        <div class="content">Osakkeet & krypto Suomessa</div>
                        <span class="cta">Lisätietoja</span>
                    </div>
                {:else if ad.isCustom === 'kodin1'}
                    <div class="custom-banner kodin1">
                        <span class="firefly pink" style="top:18%;left:12%;width:2px;height:2px;--delay:1.3s"></span>
                        <span class="firefly pink" style="top:55%;right:16%;width:2px;height:2px;--delay:4.4s"></span>
                        <span class="firefly pink" style="bottom:26%;left:32%;width:2px;height:2px;--delay:6.8s"></span>
                        <span class="firefly pink" style="top:38%;left:48%;width:2px;height:2px;--delay:2.1s"></span>
                        <img src={getLogoSrc(ad)} alt="Kodin 1" class="logo" on:error={(e) => e.target.style.display='none'} />
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
        width: 100%;
    }

    .ad-banner-link {
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        display: block;
        border: none;
        opacity: 0;
        transition: opacity 0.5s ease;
        pointer-events: none;
        width: 100%;
    }

    .ad-banner-link.active {
        position: relative;
        left: 0;
        transform: none;
        opacity: 1;
        pointer-events: auto;
    }

    .ad-banner-link.fade-out { opacity: 0; }

    @media (prefers-reduced-motion: reduce) {
        .ad-banner-link { transition: none; }
    }

    .ad-img { max-width: 100%; height: auto; border: 0; border-radius: 8px; display: block; margin: 0 auto; }

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

    @media (max-width: 639px) {
        .ad-banner-container { padding: 0.5rem 0; }
    }

    /* Custom banner base */
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

    .custom-banner:hover {
        transform: translateY(-2px);
    }

    .logo {
        height: 56px;
        width: auto;
        flex-shrink: 0;
    }

    .logo.on-dark {
        background: #fff;
        padding: 4px;
        border-radius: 4px;
    }

    .content {
        font-size: 1.1rem;
        line-height: 1.4;
    }

    .content strong {
        font-weight: 600;
    }

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
        0%, 100% { opacity: 0; transform: translate(0, 0); }
        25% { opacity: 0.5; }
        50% { opacity: 0.25; transform: translate(6px, -10px); }
        75% { opacity: 0.4; }
    }

    /* DNA - magenta */
    .custom-banner.dna { background: linear-gradient(135deg, #da0070, #b0005a); border: 2px solid rgba(255,255,255,0.3); }
    .custom-banner.dna .cta { background: #fff; color: #da0070; }
    .custom-banner.dna .content { color: #fff; }

    /* Multitronic - dark */
    .custom-banner.multitronic { background: linear-gradient(135deg, #1e293b, #0f172a); border: 1px solid rgba(255,255,255,0.15); }
    .custom-banner.multitronic .cta { background: #f97316; color: #fff; }
    .custom-banner.multitronic .content,
    .custom-banner.multitronic .content strong { color: #fff; }

    /* Vattenfall - yellow */
    .custom-banner.vattenfall { background: linear-gradient(135deg, #ffd600, #f5c400); border: 2px solid #000; }
    .custom-banner.vattenfall .cta { background: #000; color: #fff; }

    /* Vattenfall Student - black */
    .custom-banner.vattenfall-opiskelija { background: linear-gradient(135deg, #0a0a0a, #1a1a1a); border: 2px solid #ffd600; }
    .custom-banner.vattenfall-opiskelija .cta { background: #ffd600; color: #000; }
    .custom-banner.vattenfall-opiskelija .content,
    .custom-banner.vattenfall-opiskelija .content strong { color: #fff; }

    /* Kvarn - dark teal */
    .custom-banner.kvarn { background: linear-gradient(135deg, #0f172a, #1e293b); border: 2px solid #5dde7d; }
    .custom-banner.kvarn .cta { background: #5dde7d; color: #0f172a; }
    .custom-banner.kvarn .content,
    .custom-banner.kvarn .content strong { color: #fff; }

    /* Kodin1 - white with pink border */
    .custom-banner.kodin1 { background: linear-gradient(135deg, #fff, #fce4ec); border: 2px solid #e9196c; }
    .custom-banner.kodin1 .cta { background: #e9196c; color: #fff; }

    /* Responsive */
    @media (max-width: 768px) {
        .custom-banner {
            flex-direction: column;
            text-align: center;
            gap: 0.5rem;
        }
        .logo { height: 28px; }
        .content { font-size: 0.85rem; }
        .cta { margin-left: 0; width: 100%; text-align: center; }
        .firefly { display: none; }
    }
</style>
