<script>
    export const href = "https://on.kahvikaveri.fi/t/t?a=1895089445&as=2038972948&t=2&tk=1";
    export const src = "https://track.adtraction.com/t/t?a=1895089445&as=2038972948&t=1&tk=1&i=1";
    export const width = 980;
    export const height = 120;
</script>

<div class="ad-banner-container">
    <a {href} target="_blank" rel="noopener noreferrer" class="ad-banner-link">
        <img {src} {width} {height} alt="Mainos" class="ad-banner-img" />
        <span class="ad-disclaimer">Mainos</span>
    </a>
</div>

<style>
    .ad-banner-container {
        width: 100%;
        display: flex;
        justify-content: center;
        padding: 1rem 0;
    }

    .ad-banner-link {
        display: block;
        border: none;
        position: relative;
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
