<script>
// @ts-nocheck
import { ChevronLeft } from 'lucide-svelte'

import { base } from '$app/paths'
import Card from '$lib/components/ui/Card.svelte'
import PageHeader from '$lib/components/ui/PageHeader.svelte'
import PageShell from '$lib/components/ui/PageShell.svelte'
import { jsonLdScript } from '$lib/utils/jsonLd.js'

/** @type {{ data: { slug: string, content: string, metadata: { title: string, playerName: string, pageTitle: string, description: string, updated: string, url: string } } }} */
const { data } = $props()
const articleContent = $derived(data.content.replace(/^\s*<h1>.*?<\/h1>\s*/s, ''))

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

    {@html jsonLdScript(articleSchema)}
    {@html jsonLdScript(breadcrumbSchema)}
</svelte:head>

<div class="min-h-screen bg-slate-50">
    <PageShell width="content">
        <a
            href={base + "/scouting"}
            class="mb-6 inline-flex items-center text-sm font-semibold text-slate-600 transition-colors hover:text-slate-900"
        >
            <ChevronLeft class="mr-1 h-4 w-4" aria-hidden="true" />
            Scouting Reports
        </a>

        <PageHeader
            title={data.metadata.title}
            subtitle={data.metadata.description}
            size="compact"
            align="left"
        />

        <!-- Content -->
        <Card padding="none">
            <article class="p-8 md:p-12">
                <div class="prose prose-slate max-w-none">
                    {@html articleContent}
                </div>
            </article>
        </Card>

        <!-- Navigation -->
        <div class="mt-8 flex justify-between">
            <a 
                href="{base}/scouting"
                class="inline-flex items-center text-slate-600 hover:text-slate-900 transition-colors"
            >
                <ChevronLeft class="w-4 h-4 mr-1" aria-hidden="true" />
                Kaikki raportit
            </a>
        </div>
    </PageShell>
</div>
