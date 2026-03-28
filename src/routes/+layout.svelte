<script>
import '../app.css'
import { base } from '$app/paths'
import { page } from '$app/stores'
import ErrorBoundary from '$lib/components/ui/ErrorBoundary.svelte'
import VerticalAd from '$lib/components/ui/VerticalAd.svelte'
import VerticalAdLeft from '$lib/components/ui/VerticalAdLeft.svelte'

const { children } = $props()

const _siteUrl = 'https://suomalaisetnhlssa.fi'
const _siteName = 'Suomalaiset NHL:ssä'
const _defaultDescription =
    'Miten suomalaisilla kulkee NHL:ssä? Tutki päivän ottelut, pisteet ja onnistumiset.'
</script>

<svelte:head>
    <meta name="description" content={_defaultDescription} />
    <meta
        name="keywords"
        content="NHL, suomalaiset pelaajat, jääkiekko, pisteet, maalit, syötöt, Leijonat"
    />
    <meta name="language" content="fi" />

    <!-- Open Graph -->
    <meta property="og:site_name" content={_siteName} />
    <meta property="og:locale" content="fi_FI" />
    <meta property="og:type" content="website" />
    <meta property="og:image" content="{_siteUrl}/og-image.svg" />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="630" />
    <meta property="og:image:alt" content="Suomalaiset NHL:ssä - Suomalaisten NHL-pelaajien tilastot" />

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content={_siteName} />
    <meta name="twitter:description" content={_defaultDescription} />
    <meta name="twitter:image" content="{_siteUrl}/og-image.svg" />
    <meta name="twitter:image:alt" content="Suomalaiset NHL:ssä - Suomalaisten NHL-pelaajien tilastot" />

    <!-- Canonical URL -->
    <link rel="canonical" href="{_siteUrl}{$page.url.pathname}" />

    <link rel="icon" type="image/svg+xml" href={base + "/logo.svg"} />

    <!-- Note: Google Fonts loaded in app.html with async pattern -->

    <!-- JSON-LD Structured Data -->
    {@html `<script type="application/ld+json">${JSON.stringify({
        "@context": "https://schema.org",
        "@type": "WebSite",
        name: _siteName,
        url: _siteUrl,
        description: _defaultDescription,
        inLanguage: "fi",
    })}</script>`}

    <!-- Breadcrumb Schema -->
    {@html `<script type="application/ld+json">${JSON.stringify({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        itemListElement: [
            {
                "@type": "ListItem",
                position: 1,
                name: "Etusivu",
                item: _siteUrl + "/"
            }
        ]
    })}</script>`}
</svelte:head>

<div class="min-h-screen flex flex-col relative bg-gray-50" style="color-scheme: light;">
    <!-- Vertical Ad Sidebars -->
    <VerticalAd />
    <VerticalAdLeft />

    <!-- <Header /> -->
    <main class="flex-1 w-full relative z-10">
        <ErrorBoundary>
            {@render children()}
        </ErrorBoundary>
    </main>
    <!-- <Footer /> -->
</div>
