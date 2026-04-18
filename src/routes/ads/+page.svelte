<script>
// @ts-nocheck
import { getBannerAds, getMobileAds, getMobileBannerAds } from '$lib/stores/ads.js'

/** @type {Array<{id: string, href: string, isCustom?: string, src?: string, width?: number, height?: number, alt?: string}>} */
const _bannerAds = getBannerAds()
/** @type {Array<{id: string, href: string, src: string, width: number, height: number, alt?: string}>} */
const _mobileAds = getMobileAds()
/** @type {Array<{id: string, href: string, src: string, width: number, height: number, alt?: string}>} */
const _mobileBannerAds = getMobileBannerAds()

/** @param {string} id */
function _getLogoSrc(id) {
    const name = id === 'vattenfall-opiskelija' ? 'vattenfall' : id
    const ext = id === 'kvarn' ? 'webp' : 'svg'
    return `/${name}-logo.${ext}`
}
</script>

<svelte:head>
    <title>Ad Debug - Suomalaiset NHL:ssä</title>
</svelte:head>

<div class="min-h-screen bg-gray-100 p-4">
    <div class="max-w-4xl mx-auto space-y-8">
        <h1 class="text-2xl font-bold text-gray-900">Ad Debug</h1>

        <section>
            <h2 class="text-lg font-semibold mb-4">Banner Ads ({bannerAds.length})</h2>
            <div class="space-y-3">
                {#each bannerAds as ad}
                    {#if ad.isCustom}
                        <a href={ad.href} target="_blank" class="block mb-3">
                            <div class="custom-banner {ad.isCustom}">
                                {#if ad.isCustom === 'dna'}
                                    <span class="firefly" style="top:20%;left:10%;width:2px;height:2px;--delay:0.3s"></span>
                                    <span class="firefly" style="top:55%;right:8%;width:3px;height:3px;--delay:2.7s"></span>
                                    <span class="firefly" style="bottom:25%;left:25%;width:2px;height:2px;--delay:5.1s"></span>
                                    <span class="firefly" style="top:35%;left:60%;width:2px;height:2px;--delay:1.4s"></span>
                                {:else if ad.isCustom === 'multitronic'}
                                    <span class="firefly" style="top:15%;left:12%;width:2px;height:2px;--delay:0.8s"></span>
                                    <span class="firefly" style="top:60%;right:15%;width:2px;height:2px;--delay:3.5s"></span>
                                    <span class="firefly" style="bottom:30%;left:30%;width:3px;height:3px;--delay:6.2s"></span>
                                    <span class="firefly" style="top:40%;left:50%;width:2px;height:2px;--delay:1.9s"></span>
                                {:else if ad.isCustom === 'vattenfall'}
                                    <span class="firefly dark" style="top:18%;left:8%;width:2px;height:2px;--delay:1.1s"></span>
                                    <span class="firefly dark" style="top:50%;right:12%;width:3px;height:3px;--delay:4.8s"></span>
                                    <span class="firefly dark" style="bottom:22%;left:35%;width:2px;height:2px;--delay:7.3s"></span>
                                    <span class="firefly dark" style="top:38%;left:55%;width:2px;height:2px;--delay:2.5s"></span>
                                {:else if ad.isCustom === 'vattenfall-opiskelija'}
                                    <span class="firefly yellow" style="top:22%;left:10%;width:2px;height:2px;--delay:0.6s"></span>
                                    <span class="firefly yellow" style="top:58%;right:14%;width:2px;height:2px;--delay:3.2s"></span>
                                    <span class="firefly yellow" style="bottom:28%;left:28%;width:3px;height:3px;--delay:5.9s"></span>
                                    <span class="firefly yellow" style="top:42%;left:52%;width:2px;height:2px;--delay:1.7s"></span>
                                {:else if ad.isCustom === 'kvarn'}
                                    <span class="firefly green" style="top:20%;left:8%;width:2px;height:2px;--delay:2.3s"></span>
                                    <span class="firefly green" style="top:52%;right:10%;width:2px;height:2px;--delay:5.6s"></span>
                                    <span class="firefly green" style="bottom:24%;left:40%;width:3px;height:3px;--delay:0.4s"></span>
                                    <span class="firefly green" style="top:35%;left:58%;width:2px;height:2px;--delay:7.1s"></span>
                                {:else if ad.isCustom === 'kodin1'}
                                    <span class="firefly pink" style="top:18%;left:12%;width:2px;height:2px;--delay:1.3s"></span>
                                    <span class="firefly pink" style="top:55%;right:16%;width:2px;height:2px;--delay:4.4s"></span>
                                    <span class="firefly pink" style="bottom:26%;left:32%;width:2px;height:2px;--delay:6.8s"></span>
                                    <span class="firefly pink" style="top:38%;left:48%;width:2px;height:2px;--delay:2.1s"></span>
                                {/if}
                                <img src={getLogoSrc(ad.isCustom)} alt={ad.isCustom} class="logo" />
                                {#if ad.isCustom === 'dna'}
                                    <div class="content">Voita iPhone 17 Pro!</div>
                                {:else if ad.isCustom === 'multitronic'}
                                    <div class="content">IT-tuotteet parhaaseen hintaan</div>
                                {:else if ad.isCustom === 'vattenfall'}
                                    <div class="content">Kiinteä hinta 12 kk + CO₂-säästö</div>
                                {:else if ad.isCustom === 'vattenfall-opiskelija'}
                                    <div class="content">Edullinen sähkö opiskelijalle</div>
                                {:else if ad.isCustom === 'kvarn'}
                                    <div class="content">Osakkeet & krypto Suomessa</div>
                                {:else if ad.isCustom === 'kodin1'}
                                    <div class="content">Sisusta kotisi edullisesti</div>
                                {/if}
                                <span class="cta">Lisätietoja</span>
                            </div>
                        </a>
                    {:else}
                        <div class="mb-3 flex justify-center">
                            <img src={ad.src} width={ad.width} height={ad.height} alt="Mainos" class="rounded" />
                        </div>
                    {/if}
                {/each}
            </div>
        </section>

        <section>
            <h2 class="text-lg font-semibold mb-4">Mobile Ads ({mobileAds.length})</h2>
            <div class="grid grid-cols-2 gap-3">
                {#each mobileAds as ad}
                    <div class="bg-white rounded shadow">
                        <p class="text-xs p-2 bg-gray-100 font-mono">{ad.id}</p>
                        <img src={ad.src} width={ad.width} height={ad.height} alt="Mainos" class="w-full" />
                    </div>
                {/each}
            </div>
        </section>

        <section>
            <h2 class="text-lg font-semibold mb-4">Mobile Banner Ads ({mobileBannerAds.length})</h2>
            <div class="grid grid-cols-2 gap-3">
                {#each mobileBannerAds as ad}
                    <div class="bg-white rounded shadow">
                        <p class="text-xs p-2 bg-gray-100 font-mono">{ad.id}</p>
                        <img src={ad.src} width={ad.width} height={ad.height} alt="Mainos" class="w-full" />
                    </div>
                {/each}
            </div>
        </section>
    </div>
</div>

<style>
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
    .custom-banner.kvarn { background: linear-gradient(135deg, #0f172a, #1e293b); border: 1px solid #5dde7d; }
    .custom-banner.kvarn .logo { background: #fff; padding: 4px; border-radius: 4px; }
    .custom-banner.kvarn .cta { background: #5dde7d; color: #0f172a; }
    .custom-banner.kvarn .content,
    .custom-banner.kvarn .content strong { color: #fff; }

    /* Kodin1 - white with pink border */
    .custom-banner.kodin1 { background: linear-gradient(135deg, #fff, #fce4ec); border: 2px solid #e9196c; }
    .custom-banner.kodin1 .cta { background: #e9196c; color: #fff; }

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
