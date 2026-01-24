<script>
    import ErrorBoundary from "$lib/components/ui/ErrorBoundary.svelte";
    import VerticalAd from "$lib/components/ui/VerticalAd.svelte";
    import VerticalAdLeft from "$lib/components/ui/VerticalAdLeft.svelte";
    import { base } from "$app/paths";
    import { page } from "$app/stores";
    import "../app.css";
    // import PlayerPatternBackground from '$lib/components/ui/PlayerPatternBackground.svelte'
    // import Footer from '$lib/components/ui/Footer.svelte'

    const siteUrl = "https://suomalaisetnhlssa.fi";
    const siteName = "Suomalaiset NHL:ssä";
    const defaultDescription =
        "Miten suomalaisilla kulkee NHL:ssä? Tutki päivän ottelut, pisteet ja onnistumiset.";
</script>

<svelte:head>
    <meta name="description" content={defaultDescription} />
    <meta
        name="keywords"
        content="NHL, suomalaiset pelaajat, jääkiekko, pisteet, maalit, syötöt, Leijonat"
    />
    <meta name="language" content="fi" />

    <!-- Open Graph -->
    <meta property="og:site_name" content={siteName} />
    <meta property="og:locale" content="fi_FI" />
    <meta property="og:type" content="website" />
    <meta property="og:image" content="{siteUrl}/logo.svg" />

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary" />

    <!-- Canonical URL -->
    <link rel="canonical" href="{siteUrl}{$page.url.pathname}" />

    <link rel="icon" type="image/svg+xml" href={base + "/logo.svg"} />

    <!-- Note: Google Fonts loaded in app.html with async pattern -->

    <!-- JSON-LD Structured Data -->
    {@html `<script type="application/ld+json">${JSON.stringify({
        "@context": "https://schema.org",
        "@type": "WebSite",
        name: siteName,
        url: siteUrl,
        description: defaultDescription,
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
                item: siteUrl + "/"
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
            <slot />
        </ErrorBoundary>
    </main>
    <!-- <Footer /> -->
</div>
