<script>
    import { onMount, onDestroy } from 'svelte';
    import { base } from '$app/paths';

    const width = 160;
    const height = 600;

    const ads = [
        {
            href: "https://go.adt291.com/t/t?a=2028121988&as=2038972948&t=2&tk=1",
            src: "https://track.adtraction.com/t/t?a=2028121988&as=2038972948&t=1&tk=1&i=1",
            alt: "Mainos"
        },
        {
            href: "https://at.valco.fi/t/t?a=2020376424&as=2038972948&t=2&tk=1",
            src: `${base}/valco.jpg`,
            alt: "Mainos"
        }
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
        interval = setInterval(nextAd, 8000);
    });

    onDestroy(() => {
        if (interval) clearInterval(interval);
    });

    $: currentAd = ads[currentAdIndex];
</script>

<div class="vertical-ad-container">
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
                <img
                    src={ad.src}
                    {width}
                    {height}
                    alt={ad.alt}
                    class="ad-img"
                />
                <span class="ad-disclaimer">Mainos</span>
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
    }

    @media (min-width: 1400px) {
        .vertical-ad-container {
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
        width: 160px;
        height: 600px;
        border: 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
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
    }
</style>
