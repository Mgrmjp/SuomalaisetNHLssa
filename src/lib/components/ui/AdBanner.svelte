<script>
    import { onMount, onDestroy } from "svelte";

    const ads = [
        {
            href: "https://on.kahvikaveri.fi/t/t?a=1895089445&as=2038972948&t=2&tk=1",
            src: "https://track.adtraction.com/t/t?a=1895089445&as=2038972948&t=1&tk=1&i=1",
            width: 980,
            height: 120,
            alt: "Mainos",
        },
        {
            href: "https://go.adt242.com/t/t?a=1875158487&as=2038972948&t=2&tk=1",
            src: "https://track.adtraction.com/t/t?a=1875158487&as=2038972948&t=1&tk=1&i=1",
            width: 728,
            height: 90,
            alt: "Mainos",
        },
    ];

    let currentAdIndex = 0;
    let isTransitioning = false;
    let interval;

    function nextAd() {
        isTransitioning = true;
        setTimeout(() => {
            currentAdIndex = (currentAdIndex + 1) % ads.length;
            setTimeout(() => {
                isTransitioning = false;
            }, 100);
        }, 500);
    }

    onMount(() => {
        // Start with 4s delay to offset from vertical ad rotation
        setTimeout(() => {
            interval = setInterval(nextAd, 8000);
        }, 4000);
    });

    onDestroy(() => {
        if (interval) clearInterval(interval);
    });

    $: currentAd = ads[currentAdIndex];
</script>

<div class="ad-banner-container">
    <div class="ad-wrapper">
        {#each ads as ad, index (index)}
            <a
                href={ad.href}
                target="_blank"
                rel="noopener noreferrer"
                class="ad-banner-link"
                class:active={index === currentAdIndex}
                class:fade-out={index !== currentAdIndex || isTransitioning}
            >
                <img
                    src={ad.src}
                    width={ad.width}
                    height={ad.height}
                    alt={ad.alt}
                    class="ad-banner-img"
                />
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
        transition: opacity 0.5s ease-in-out;
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
</style>
