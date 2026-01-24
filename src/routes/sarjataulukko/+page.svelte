<script>
    import NavTabs from "$lib/components/ui/NavTabs.svelte";
    import StandingsView from "$lib/components/standings/StandingsView.svelte";
    import Snowfall from "$lib/components/ui/Snowfall.svelte";
    import { base } from "$app/paths";
    import { resetToDefault } from "$lib/stores/gameData.js";
</script>

<svelte:head>
    <title>NHL Sarjataulukko - Suomalaiset NHL:ssä</title>
    <meta
        name="description"
        content="NHL sarjataulukko. Seuraa suomalaisten pelaajien joukkueiden sijoituksia."
    />
    <meta property="og:title" content="NHL Sarjataulukko - Suomalaiset NHL:ssä" />
    <meta
        property="og:description"
        content="NHL sarjataulukko. Seuraa suomalaisten pelaajien joukkueiden sijoituksia."
    />
    <meta property="og:url" content="https://suomalaisetnhlssa.fi/sarjataulukko" />

    <!-- Breadcrumb Schema -->
    {@html `<script type="application/ld+json">${JSON.stringify({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        itemListElement: [
            {
                "@type": "ListItem",
                position: 1,
                name: "Etusivu",
                item: "https://suomalaisetnhlssa.fi/"
            },
            {
                "@type": "ListItem",
                position: 2,
                name: "Sarjataulukko",
                item: "https://suomalaisetnhlssa.fi/sarjataulukko"
            }
        ]
    })}</script>`}
</svelte:head>

<div
    class="page-container w-full max-w-6xl mx-auto px-4 py-8 relative"
    style="z-index: 1; position: relative;"
>
    <div class="text-center mb-8 hero-header space-y-3 relative overflow-hidden">
        <Snowfall />
        <div class="relative space-y-3 p-6">
            <a
                href="{base}/"
                onclick={resetToDefault}
                class="logo-button focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2 rounded-xl transition-all duration-300 inline-block"
                aria-label="Palaa etusivulle"
            >
                <img
                    src={base + "/logo.svg"}
                    alt="Suomalaiset NHL-pelaajat"
                    class="w-12 h-12 mx-auto mb-4 logo-img"
                />
            </a>
            <h1 class="text-3xl font-bold text-gray-900 hero-title">NHL Sarjataulukko</h1>
        </div>
    </div>

    <!-- Navigation -->
    <NavTabs />

    <!-- Content -->
    <div
        class="standings-content-card bg-white rounded-xl shadow-sm border border-gray-100 p-3 md:p-6"
    >
        <StandingsView />
    </div>
</div>

<style>
    .logo-button:hover .logo-img {
        transform: scale(1.05) rotate(-2deg);
        filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.1));
    }
    .logo-img {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
</style>
