<script>
    const width = 120;
    const height = 600;

    const ad = {
        href: "https://to.bjornborg.com/t/t?a=1616919154&as=2038972948&t=2&tk=1",
        src: "https://track.adtraction.com/t/t?a=1616919154&as=2038972948&t=1&tk=1&i=1",
        alt: "Mainos"
    };
</script>

<div class="vertical-ad-container-left">
    <div class="ad-wrapper">
        <a
            href={ad.href}
            target="_blank"
            rel="noopener noreferrer"
            class="ad-link"
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
        width: 120px;
        height: 600px;
    }

    .ad-link {
        display: block;
        border: none;
    }

    .ad-img {
        width: 120px;
        height: 600px;
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
