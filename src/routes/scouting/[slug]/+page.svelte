<script>
// @ts-nocheck
import { base } from '$app/paths'

/** @type {{ data: { slug: string, content: string, metadata: { title: string, playerName: string, pageTitle: string, description: string, updated: string, url: string } } }} */
const { data } = $props()

const articleSchema = $derived({
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: data.metadata.title,
    description: data.metadata.description,
    dateModified: data.metadata.updated || undefined,
    inLanguage: 'fi',
    author: {
        '@type': 'Organization',
        name: 'Suomalaiset NHL:ssä',
    },
    publisher: {
        '@type': 'Organization',
        name: 'Suomalaiset NHL:ssä',
        url: 'https://suomalaisetnhlssa.fi',
        logo: {
            '@type': 'ImageObject',
            url: 'https://suomalaisetnhlssa.fi/logo.svg',
        },
    },
    mainEntityOfPage: {
        '@type': 'WebPage',
        '@id': data.metadata.url,
    },
    about: data.metadata.playerName,
})

const breadcrumbSchema = $derived({
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
        {
            '@type': 'ListItem',
            position: 1,
            name: 'Etusivu',
            item: 'https://suomalaisetnhlssa.fi/',
        },
        {
            '@type': 'ListItem',
            position: 2,
            name: 'Scouting',
            item: 'https://suomalaisetnhlssa.fi/scouting',
        },
        {
            '@type': 'ListItem',
            position: 3,
            name: data.metadata.playerName,
            item: data.metadata.url,
        },
    ],
})
</script>

<svelte:head>
    <title>{data.metadata.pageTitle}</title>
    <meta name="description" content={data.metadata.description} />
    <meta property="og:title" content={data.metadata.pageTitle} />
    <meta property="og:description" content={data.metadata.description} />
    <meta property="og:type" content="article" />
    <meta property="og:url" content={data.metadata.url} />
    <meta property="og:image" content="https://suomalaisetnhlssa.fi/og-image.svg" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content={data.metadata.pageTitle} />
    <meta name="twitter:description" content={data.metadata.description} />
    <meta name="twitter:image" content="https://suomalaisetnhlssa.fi/og-image.svg" />

    {@html `<script type="application/ld+json">${JSON.stringify(articleSchema)}</script>`}
    {@html `<script type="application/ld+json">${JSON.stringify(breadcrumbSchema)}</script>`}
</svelte:head>

<div class="min-h-screen bg-slate-50">
    <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <!-- Back links -->
        <div class="mb-8 flex items-center gap-4">
            <a 
                href="{base}/scouting"
                class="inline-flex items-center text-sm text-slate-600 hover:text-slate-900 transition-colors"
            >
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
                </svg>
                Scouting Reports
            </a>
            <span class="text-slate-300">/</span>
            <a 
                href="{base}/lupaukset"
                class="inline-flex items-center text-sm text-slate-600 hover:text-slate-900 transition-colors"
            >
                Lupaukset
            </a>
        </div>

        <!-- Content -->
        <article class="bg-white rounded-xl shadow-sm border border-slate-200 p-8 md:p-12">
            <div class="prose prose-slate max-w-none">
                {@html data.content}
            </div>
        </article>

        <!-- Navigation -->
        <div class="mt-8 flex justify-between">
            <a 
                href="{base}/scouting"
                class="inline-flex items-center text-slate-600 hover:text-slate-900 transition-colors"
            >
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
                </svg>
                Kaikki raportit
            </a>
        </div>
    </div>
</div>

