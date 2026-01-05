<script>
    import { base } from "$app/paths";
    import { onMount } from "svelte";

    function initKofi() {
        if (typeof kofiwidget2 !== "undefined") {
            kofiwidget2.init("Support me on Ko-fi", "#3b82f6", "Z8Z16PHF0");
            kofiwidget2.draw();
        }
    }

    onMount(() => {
        initKofi();
    });
</script>

<svelte:head>
    <title>Tietoa - Suomalaiset NHL-pelaajat</title>
    <script src="https://storage.ko-fi.com/cdn/widget/Widget_2.js" on:load={initKofi}></script>
</svelte:head>

<div class="w-full max-w-3xl mx-auto px-4 py-8">
    <div class="space-y-6">
        <!-- Back link -->
        <div class="mb-6">
            <a
                href={base + "/"}
                class="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 transition-colors"
            >
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M15 19l-7-7 7-7"
                    />
                </svg>
                Takaisin etusivulle
            </a>
        </div>

        <!-- Main title -->
        <h1 class="text-3xl font-bold text-gray-900 mb-8">Tietoa sivustosta</h1>

        <!-- About section -->
        <section class="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
            <h2 class="text-xl font-semibold text-gray-900 mb-3">Sivustosta</h2>
            <p class="text-gray-700 leading-relaxed">
                Tämä sivusto seuraa suomalaisten NHL-pelaajien ottelutilastoja päivittäin. Voit
                valita minkä tahansa päivän ja nähdä kyseisenä iltana pelanneiden suomalaisten
                pelaajien maalit, syötöt, pisteet ja jääajat.
            </p>
        </section>

        <!-- Data sources section -->
        <section class="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
            <h2 class="text-xl font-semibold text-gray-900 mb-3">Tietolähteet</h2>
            <p class="text-gray-700 leading-relaxed">
                Pelaajatiedot haetaan NHL:n virallisista lähteistä (NHL.com API). Sivusto päivittyy
                automaattisesti kun uutta pelitietoa on saatavilla.
            </p>
        </section>

        <!-- Ad disclosure section -->
        <section class="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
            <h2 class="text-xl font-semibold text-gray-900 mb-3">Mainosilmoitus</h2>
            <div class="text-gray-700 leading-relaxed space-y-2">
                <p>
                    Tämä sivusto sisältää affiliate-mainoksia ja yhteistyölinkkejä. Sivusto voi
                    saada provission, jos käyttäjä klikkaa mainosta tai linkkiä ja tekee oston.
                </p>
                <p>Mainokset näkyvät mm. seuraavien mainosverkostojen kautta:</p>
                <ul class="list-disc list-inside text-gray-600 space-y-1 ml-4">
                    <li>Adtraction</li>
                    <li>Muut affiliate-verkostot</li>
                </ul>
                <p class="text-sm text-gray-500 mt-3">
                    Affiliate-yhteistyöt eivät vaikuta sivuston sisältöön tai näytettäviin
                    tilastoihin.
                </p>
            </div>
        </section>

        <!-- Ko-fi section -->
        <section
            class="bg-white border border-gray-200 rounded-xl p-6 shadow-sm flex flex-col items-center"
        >
            <h2 class="text-xl font-semibold text-gray-900 mb-4">Tue sivustoa</h2>
            <div id="kofi-widget-container"></div>
        </section>

        <!-- Footer -->
        <footer class="text-center py-6 text-sm text-gray-500">
            <p>&copy; {new Date().getFullYear()} Suomalaiset NHL-pelaajat</p>
        </footer>
    </div>
</div>

<style>
    section {
        border-left: 4px solid transparent;
        transition: all 0.2s ease;
    }

    section:hover {
        border-left-color: #3b82f6;
    }
</style>
