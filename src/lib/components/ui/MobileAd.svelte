<script>
    const href = "https://go.adt291.com/t/t?a=1998771852&as=2038972948&t=2&tk=1";
    const src = "https://track.adtraction.com/t/t?a=1998771852&as=2038972948&t=1&tk=1&i=1";
    const width = 320;
    const height = 320;
</script>

<div class="mobile-ad-container">
    <a {href} target="_blank" rel="noopener noreferrer" class="mobile-ad-link">
        <img {src} {width} {height} alt="Mainos" class="mobile-ad-img" />
        <span class="ad-disclaimer">Mainos</span>
    </a>
</div>

<style>
    .mobile-ad-container {
        width: 100%;
        display: flex;
        justify-content: center;
        padding: 1rem 0;
    }

    @media (min-width: 768px) {
        .mobile-ad-container {
            display: none;
        }
    }

    .mobile-ad-link {
        display: block;
        border: none;
        position: relative;
    }

    .mobile-ad-img {
        max-width: 100%;
        height: auto;
        border: 0;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
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
