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

<div class="flat-view min-h-screen">
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
    .back-link {
        display: inline-flex;
        align-items: center;
        gap: var(--space-2);
        margin-bottom: var(--space-6);
        color: var(--color-muted);
        font-size: 0.875rem;
        font-weight: 700;
        text-decoration: none;
    }

    .back-link:hover {
        color: var(--accent);
    }

    .standings-content {
        min-width: 0;
    }

    .flat-view :global(*) {
        border-radius: 0 !important;
        box-shadow: none !important;
    }

    .flat-view :global(.page-header__logo) {
        filter: none !important;
    }

    .flat-view :global(a:focus-visible),
    .flat-view :global(button:focus-visible),
    .flat-view :global(input:focus-visible) {
        outline: 3px solid var(--accent) !important;
        outline-offset: 2px;
    }
</style>
