<script>
// @ts-nocheck
import { ChevronLeft, ChevronRight } from 'lucide-svelte'

import { base } from '$app/paths'
import Card from '$lib/components/ui/Card.svelte'
import PageHeader from '$lib/components/ui/PageHeader.svelte'
import PageShell from '$lib/components/ui/PageShell.svelte'
import PlayerHeadshot from '$lib/components/ui/PlayerHeadshot.svelte'

/** @type {{ data: { articles: Array<{slug: string, title: string, date: string, week: number, year: number, excerpt: string}> } }} */
const { data: _data } = $props()

const data = _data

function formatDate(dateStr) {
    return new Date(dateStr).toLocaleDateString('fi-FI', {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
    })
}
</script>

<svelte:head>
    <title>Viikkokatsaus - Suomalaiset NHL:ssä</title>
    <meta
        name="description"
        content="Viikoittaiset katsaukset suomalaisten NHL-pelaajien menestykseen."
    />
    <meta property="og:title" content="Viikkokatsaus - Suomalaiset NHL:ssä" />
    <meta
        property="og:description"
        content="Viikoittaiset katsaukset suomalaisten NHL-pelaajien menestykseen."
    />
    <meta property="og:url" content="https://suomalaisetnhlssa.fi/viikkokatsaus" />

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
                name: "Viikkokatsaukset",
                item: "https://suomalaisetnhlssa.fi/viikkokatsaus"
            }
        ]
    })}</script>`}

    <!-- CollectionPage Schema for articles -->
    {@html `<script type="application/ld+json">${JSON.stringify({
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        name: "Viikkokatsaukset - Suomalaisten NHL-pelaajien viikoittaiset katsaukset",
        description: "Viikoittaiset katsaukset suomalaisten NHL-pelaajien menestykseen.",
        url: "https://suomalaisetnhlssa.fi/viikkokatsaus",
        inLanguage: "fi"
    })}</script>`}
</svelte:head>

<PageShell width="content" compact>
    <div class="editorial-page">
        <a href={base + "/"} class="back-link">
            <ChevronLeft size={16} aria-hidden="true" />
            Takaisin etusivulle
        </a>

        <PageHeader
            title="Viikkokatsaus"
            subtitle="Suomalaisten NHL-pelaajien viikon tärkeimmät tapahtumat ja tilastot."
            align="left"
            size="compact"
        />

        {#if data.articles.length === 0}
            <Card>
                <p class="empty-state">Ei vielä artikkeleita.</p>
            </Card>
        {:else}
            <div class="article-list">
                {#each data.articles as article}
                    <a href={`${base}/viikkokatsaus/${article.slug}`} class="article-link">
                        <Card>
                            <div class="article-row">
                                {#if article.featured_player_id}
                                    <div class="article-thumbnail">
                                        <PlayerHeadshot
                                            playerId={article.featured_player_id}
                                            alt="Viikon tähti"
                                            imageClass="article-thumbnail__image"
                                            loading="lazy"
                                        />
                                    </div>
                                {/if}
                                <div class="article-copy">
                                    <h2>{article.title}</h2>
                                    <p class="article-meta">
                                        {formatDate(article.date)} · Viikko {article.week}
                                    </p>
                                    <p class="article-excerpt">{article.excerpt}</p>
                                </div>
                                <ChevronRight
                                    class="article-arrow"
                                    size={20}
                                    aria-hidden="true"
                                />
                            </div>
                        </Card>
                    </a>
                {/each}
            </div>
        {/if}
    </div>
</PageShell>

<style>
    .editorial-page {
        display: grid;
        gap: var(--space-6);
    }

    .back-link {
        display: inline-flex;
        width: fit-content;
        align-items: center;
        gap: var(--space-2);
        color: var(--color-muted);
        font-size: 0.875rem;
        font-weight: 600;
        text-decoration: none;
        transition: color 0.16s ease;
    }

    .back-link:hover {
        color: var(--accent);
    }

    .back-link:focus-visible,
    .article-link:focus-visible {
        outline: 3px solid var(--accent-glow);
        outline-offset: 3px;
    }

    .article-list {
        display: grid;
        gap: var(--space-4);
    }

    .article-link {
        display: block;
        color: inherit;
        text-decoration: none;
    }

    .article-link :global(.card) {
        border-radius: 0 !important;
        box-shadow: none !important;
        transition: border-color 0.16s ease;
    }

    .article-link:hover :global(.card) {
        border-color: var(--accent-soft);
    }

    .article-row {
        display: grid;
        grid-template-columns: auto minmax(0, 1fr) auto;
        align-items: start;
        gap: var(--space-4);
    }

    .article-thumbnail {
        width: 4rem;
        height: 4rem;
        overflow: hidden;
        flex: none;
        border: 1px solid var(--color-panel-border);
        border-radius: 0;
        background: var(--accent-ice);
        box-shadow: none;
    }

    .article-thumbnail :global(.article-thumbnail__image) {
        width: 100%;
        height: 100%;
        border-radius: 0 !important;
        box-shadow: none !important;
        object-fit: cover;
    }

    .article-copy {
        min-width: 0;
    }

    h2 {
        margin: 0 0 var(--space-2);
        color: var(--color-ink);
        font-size: 1.2rem;
        font-weight: 700;
        line-height: 1.3;
        transition: color 0.16s ease;
    }

    .article-link:hover h2 {
        color: var(--accent);
    }

    .article-meta {
        margin: 0 0 var(--space-3);
        color: var(--color-muted);
        font-size: 0.82rem;
    }

    .article-excerpt,
    .empty-state {
        margin: 0;
        color: #344054;
        line-height: 1.65;
    }

    .article-row :global(.article-arrow) {
        margin-top: 0.15rem;
        color: var(--color-muted);
        transition: color 0.16s ease, transform 0.16s ease;
    }

    .article-link:hover :global(.article-arrow) {
        color: var(--accent);
        transform: translateX(2px);
    }

    @media (max-width: 520px) {
        .article-row {
            grid-template-columns: minmax(0, 1fr) auto;
        }

        .article-thumbnail {
            display: none;
        }
    }
</style>
