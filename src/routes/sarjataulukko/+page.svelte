<script>
// @ts-nocheck
import { ChevronLeft } from 'lucide-svelte'
import { base } from '$app/paths'
import StandingsView from '$lib/components/standings/StandingsView.svelte'
import PageHeader from '$lib/components/ui/PageHeader.svelte'
import PageShell from '$lib/components/ui/PageShell.svelte'
import { resetToDefault } from '$lib/stores/gameData.js'
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

<div class="public-view min-h-screen">
    <PageShell width="wide">
        <a class="back-link" href={base + "/"} onclick={resetToDefault}>
            <ChevronLeft class="h-4 w-4" aria-hidden="true" />
            Takaisin etusivulle
        </a>
        <PageHeader title="NHL Sarjataulukko" subtitle="Konferenssit ja divisioonat" />

        <section class="standings-content" aria-label="NHL-sarjataulukot">
        <StandingsView />
        </section>
    </PageShell>
</div>

<style>

    .standings-content {
        min-width: 0;
    }
</style>
