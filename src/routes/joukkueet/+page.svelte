<script>
// @ts-nocheck
import { ChevronLeft } from 'lucide-svelte'
import { base } from '$app/paths'
import FinnishRoster from '$lib/components/game/FinnishRoster.svelte'
import PageHeader from '$lib/components/ui/PageHeader.svelte'
import PageShell from '$lib/components/ui/PageShell.svelte'
import { resetToDefault } from '$lib/stores/gameData.js'
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

<div class="flat-view min-h-screen">
    <PageShell width="wide">
        <a class="back-link" href={base + "/"} onclick={resetToDefault}>
            <ChevronLeft class="h-4 w-4" aria-hidden="true" />
            Takaisin etusivulle
        </a>
        <PageHeader
            title="Suomalaiset joukkueittain"
            subtitle="NHL-joukkueiden suomalaispelaajat"
        />

        <section class="roster-content" aria-label="Suomalaispelaajat joukkueittain">
        <FinnishRoster />
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

    .roster-content {
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
