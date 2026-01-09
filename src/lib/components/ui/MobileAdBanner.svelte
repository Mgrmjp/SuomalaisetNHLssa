<script>
    const ad = {
        href: "https://to.bjornborg.com/t/t?a=1616919459&as=2038972948&t=2&tk=1",
        src: "https://track.adtraction.com/t/t?a=1616919459&as=2038972948&t=1&tk=1&i=1",
        width: 300,
        height: 250,
        alt: "Mainos",
    };
</script>

<div class="mobile-ad-banner">
    <a href={ad.href} target="_blank" rel="noopener noreferrer" class="ad-link">
        <img src={ad.src} width={ad.width} height={ad.height} alt={ad.alt} class="ad-img" />
    </a>
    <span class="ad-disclaimer">Mainos</span>
</div>

<style>
    .mobile-ad-banner {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 1rem 0;
        position: relative;
    }

    .ad-link {
        display: block;
        border: none;
    }

    .ad-img {
        width: 300px;
        height: 250px;
        max-width: 100%;
        border: 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border-radius: 8px;
        display: block;
    }

    .ad-disclaimer {
        position: absolute;
        top: 1rem;
        right: calc(50% - 150px + 8px);
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

    @media (min-width: 768px) {
        .mobile-ad-banner {
            display: none;
        }
    }
</style>
