<script>
    import { onMount, onDestroy } from "svelte";

    const ads = [
        {
            href: "https://to.bjornborg.com/t/t?a=1616919154&as=2038972948&t=2&tk=1",
            src: "https://track.adtraction.com/t/t?a=1616919154&as=2038972948&t=1&tk=1&i=1",
            width: 120,
            height: 600,
            alt: "Mainos",
        },
        {
            href: "https://go.adt242.com/t/t?a=1875158502&as=2038972948&t=2&tk=1",
            src: "https://track.adtraction.com/t/t?a=1875158502&as=2038972948&t=1&tk=1&i=1",
            width: 160,
            height: 600,
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
        // Start with 2s delay to offset from other ad rotations
        setTimeout(() => {
            interval = setInterval(nextAd, 8000);
        }, 2000);
    });

    onDestroy(() => {
        if (interval) clearInterval(interval);
    });

    $: currentAd = ads[currentAdIndex];
</script>

<div class="vertical-ad-container-left">
    <div class="ad-wrapper">
        {#each ads as ad, index (index)}
            <a
                href={ad.href}
                target="_blank"
                rel="noopener noreferrer"
                class="ad-link"
                class:active={index === currentAdIndex}
                class:fade-out={index !== currentAdIndex || isTransitioning}
            >
                <img src={ad.src} width={ad.width} height={ad.height} alt={ad.alt} class="ad-img" />
                <span class="ad-disclaimer">Mainos</span>
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
    }

    @media (min-width: 1400px) {
        .vertical-ad-container-left {
            display: block;
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
        display: block;
        border: none;
        opacity: 0;
        transition: opacity 0.5s ease-in-out;
        pointer-events: none;
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
        border: 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border-radius: 8px;
        display: block;
    }

    .ad-disclaimer {
        position: absolute;
        top: 8px;
        left: 8px;
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
