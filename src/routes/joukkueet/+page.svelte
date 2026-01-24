<script>
    import NavTabs from "$lib/components/ui/NavTabs.svelte";
    import FinnishRoster from "$lib/components/game/FinnishRoster.svelte";
    import Snowfall from "$lib/components/ui/Snowfall.svelte";
    import { base } from "$app/paths";
    import { resetToDefault } from "$lib/stores/gameData.js";
</script>

<svelte:head>
    <title>Suomalaiset NHL-pelaajat - Joukkueet</title>
    <meta
        name="description"
        content="Katso suomalaisten NHL-pelaajien jako joukkueittain. Löydä kaikki suomalaispelaajat kullekin joukkueelle."
    />
    <meta property="og:title" content="Suomalaiset NHL-pelaajat - Joukkueittain" />
    <meta
        property="og:description"
        content="Katso suomalaisten NHL-pelaajien jako joukkueittain. Löydä kaikki suomalaispelaajat kullekin joukkueelle."
    />
    <meta property="og:url" content="https://suomalaisetnhlssa.fi/joukkueet" />

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
                name: "Joukkueet",
                item: "https://suomalaisetnhlssa.fi/joukkueet"
            }
        ]
    })}</script>`}
</svelte:head>

<div class="w-full max-w-6xl mx-auto px-4 py-8 relative" style="z-index: 1; position: relative;">
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
            <h1 class="text-3xl font-bold text-gray-900 hero-title">Suomalaiset Joukkueittain</h1>
        </div>
    </div>

    <!-- Navigation -->
    <NavTabs />

    <!-- Content -->
    <div class="bg-white/50 rounded-xl">
        <FinnishRoster />
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
