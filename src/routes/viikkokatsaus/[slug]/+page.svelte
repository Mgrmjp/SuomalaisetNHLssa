<script>
// @ts-nocheck
import { ChevronLeft, ChevronRight } from 'lucide-svelte'

import { base } from '$app/paths'
import Card from '$lib/components/ui/Card.svelte'
import PageHeader from '$lib/components/ui/PageHeader.svelte'
import PageShell from '$lib/components/ui/PageShell.svelte'
import PlayerHeadshot from '$lib/components/ui/PlayerHeadshot.svelte'
import { jsonLdScript } from '$lib/utils/jsonLd.js'

/** @type {{ data: { article: {slug: string, title: string, date: string, week: number, year: number, content: string}, prevArticle: {slug: string, title: string} | null, nextArticle: {slug: string, title: string} | null } }} */
const { data: _data } = $props()

const data = _data
const articleUrl = $derived(`https://suomalaisetnhlssa.fi/viikkokatsaus/${data.article.slug}`)
const articleDescription = $derived(
    data.article.excerpt ||
        `Viikon ${data.article.week} katsaus suomalaisten NHL-pelaajien menestykseen.`
)
const articleImage = 'https://suomalaisetnhlssa.fi/og-image.svg'

function formatDate(dateStr) {
    return new Date(dateStr).toLocaleDateString('fi-FI', {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
    })
}
</script>

<svelte:head>
    <title>{data.article.title} - Suomalaiset NHL:ssä</title>
    <meta name="description" content={articleDescription} />
    <meta property="og:title" content={`${data.article.title} - Suomalaiset NHL:ssä`} />
    <meta property="og:description" content={articleDescription} />
    <meta property="og:type" content="article" />
    <meta property="og:url" content={articleUrl} />
    <meta property="og:image" content={articleImage} />
    <meta property="article:published_time" content={data.article.date} />
    <meta property="article:modified_time" content={data.article.date} />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content={`${data.article.title} - Suomalaiset NHL:ssä`} />
    <meta name="twitter:description" content={articleDescription} />
    <meta name="twitter:image" content={articleImage} />

    <!-- NewsArticle Schema -->
    {@html jsonLdScript({
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        headline: data.article.title,
        description: articleDescription,
        image: [articleImage],
        datePublished: data.article.date,
        dateModified: data.article.date,
        author: {
            "@type": "Organization",
            name: "Suomalaiset NHL:ssä"
        },
        publisher: {
            "@type": "Organization",
            name: "Suomalaiset NHL:ssä",
            url: "https://suomalaisetnhlssa.fi",
            logo: {
                "@type": "ImageObject",
                url: "https://suomalaisetnhlssa.fi/logo.svg"
            }
        },
        mainEntityOfPage: {
            "@type": "WebPage",
            "@id": articleUrl
        },
        inLanguage: "fi",
        articleSection: "Viikkokatsaus"
    })}

    <!-- Breadcrumb Schema for Article -->
    {@html jsonLdScript({
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
            },
            {
                "@type": "ListItem",
                position: 3,
                name: data.article.title,
                item: articleUrl
            }
        ]
    })}
</svelte:head>

<PageShell width="content" compact>
    <div class="article-page">
        <a href={base + "/viikkokatsaus"} class="back-link">
            <ChevronLeft size={16} aria-hidden="true" />
            Takaisin viikkokatsauksiin
        </a>

        <PageHeader
            title={data.article.title}
            subtitle={`${formatDate(data.article.date)} · Viikko ${data.article.week}, ${data.article.year}`}
            align="left"
            size="compact"
        >
            {#if data.article.featured_player_id}
                <div class="featured-player">
                    <div class="featured-player__image">
                        <PlayerHeadshot
                            playerId={data.article.featured_player_id}
                            alt="Viikon tähti"
                            imageClass="featured-player__photo"
                            loading="eager"
                        />
                    </div>
                    <p class="featured-player__label">Viikon tähti</p>
                </div>
            {/if}
        </PageHeader>

        <div class="article-surface">
            <Card>
                <article class="article-content">
                    {@html data.article.content}
                </article>
            </Card>
        </div>

        <nav class="article-nav" aria-label="Viikkokatsausten selaus">
            {#if data.prevArticle}
                <a
                    href={`${base}/viikkokatsaus/${data.prevArticle.slug}`}
                    class="article-nav__link article-nav__link--previous"
                >
                    <ChevronLeft size={16} aria-hidden="true" />
                    <span class="article-nav__desktop">{data.prevArticle.title}</span>
                    <span class="article-nav__mobile">Edellinen</span>
                </a>
            {:else}
                <div aria-hidden="true"></div>
            {/if}

            {#if data.nextArticle}
                <a
                    href={`${base}/viikkokatsaus/${data.nextArticle.slug}`}
                    class="article-nav__link article-nav__link--next"
                >
                    <span class="article-nav__desktop">{data.nextArticle.title}</span>
                    <span class="article-nav__mobile">Seuraava</span>
                    <ChevronRight size={16} aria-hidden="true" />
                </a>
            {:else}
                <div aria-hidden="true"></div>
            {/if}
        </nav>
    </div>
</PageShell>

<style>
    .article-page {
        display: grid;
        min-width: 0;
        gap: var(--space-6);
    }

    .article-page > :global(*) {
        min-width: 0;
        max-width: 100%;
    }

    .back-link,
    .article-nav__link {
        display: inline-flex;
        align-items: center;
        gap: var(--space-2);
        color: var(--color-muted);
        font-size: 0.875rem;
        font-weight: 600;
        text-decoration: none;
        transition: color 0.16s ease;
    }

    .back-link {
        width: fit-content;
    }

    .back-link:hover,
    .article-nav__link:hover {
        color: var(--accent);
    }

    .back-link:focus-visible,
    .article-nav__link:focus-visible {
        outline: 3px solid var(--accent-glow);
        outline-offset: 3px;
    }

    .featured-player {
        display: inline-flex;
        align-items: center;
        gap: var(--space-3);
    }

    .featured-player__image {
        width: 5rem;
        height: 5rem;
        overflow: hidden;
        border: 1px solid var(--color-panel-border);
        border-radius: 0;
        background: var(--accent-ice);
        box-shadow: none;
    }

    .featured-player__image :global(.featured-player__photo) {
        width: 100%;
        height: 100%;
        border-radius: 0 !important;
        box-shadow: none !important;
        object-fit: cover;
    }

    .featured-player__label {
        margin: 0;
        color: var(--accent);
        font-size: var(--eyebrow-size);
        font-weight: var(--eyebrow-weight);
        letter-spacing: var(--eyebrow-track);
        text-transform: uppercase;
    }

    .article-surface :global(.card) {
        border-radius: 0 !important;
        box-shadow: none !important;
    }

    .article-surface {
        min-width: 0;
    }

    .article-content {
        min-width: 0;
        overflow-x: auto;
    }

    .article-content :global(h2) {
        margin: 2.5rem 0 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--accent-ice);
        color: var(--color-ink);
        font-size: 1.75rem;
        font-weight: 700;
        line-height: 1.25;
    }

    .article-content :global(h2:first-child) {
        margin-top: 0;
    }

    .article-content :global(h3) {
        margin: 1.5rem 0 0.5rem;
        color: #1d2939;
        font-size: 1.25rem;
        font-weight: 600;
        line-height: 1.35;
    }

    .article-content :global(p) {
        margin: 0 0 1.25rem;
        color: #344054;
        line-height: 1.8;
    }

    .article-content :global(table) {
        width: 100%;
        margin: 1.5rem 0;
        overflow: hidden;
        border: 1px solid var(--color-panel-border);
        border-collapse: collapse;
        border-radius: 0 !important;
        box-shadow: none !important;
        font-size: 0.95rem;
    }

    .article-content :global(th) {
        padding: 0.75rem 1rem;
        border-bottom: 2px solid #d0d5dd;
        background: var(--accent-ice);
        color: var(--color-ink);
        font-weight: 600;
        text-align: left;
    }

    .article-content :global(td) {
        padding: 0.75rem 1rem;
        border-bottom: 1px solid #eaecf0;
        color: #475467;
    }

    .article-content :global(tr:last-child td) {
        border-bottom: 0;
    }

    .article-content :global(tr:hover td) {
        background: #f9fafb;
    }

    .article-content :global(hr) {
        margin: 2rem 0;
        border: 0;
        border-top: 1px solid #d0d5dd;
    }

    .article-content :global(em) {
        color: var(--color-muted);
        font-size: 0.875rem;
        font-style: italic;
    }

    .article-content :global(ul),
    .article-content :global(ol) {
        margin: 0 0 1.5rem 1.5rem;
        color: #344054;
    }

    .article-content :global(ul) {
        list-style-type: none;
    }

    .article-content :global(ul li) {
        position: relative;
        padding-left: 1.5rem;
    }

    .article-content :global(ul li::before) {
        position: absolute;
        left: 0;
        color: var(--accent);
        content: "•";
        font-weight: 700;
    }

    .article-content :global(ol) {
        list-style-type: decimal;
    }

    .article-content :global(li) {
        margin-bottom: 0.75rem;
        line-height: 1.6;
    }

    .article-content :global(strong) {
        color: var(--color-ink);
        font-weight: 600;
    }

    .article-content :global(img),
    .article-content :global(video),
    .article-content :global(iframe),
    .article-content :global(button) {
        border-radius: 0 !important;
        box-shadow: none !important;
    }

    .article-nav {
        display: grid;
        grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
        align-items: start;
        gap: var(--space-4);
        padding-top: var(--space-6);
        border-top: 1px solid #d0d5dd;
    }

    .article-nav__link--next {
        justify-self: end;
        text-align: right;
    }

    .article-nav__mobile {
        display: none;
    }

    @media (max-width: 640px) {
        .article-nav__desktop {
            display: none;
        }

        .article-nav__mobile {
            display: inline;
        }

        .article-content :global(table) {
            font-size: 0.82rem;
        }

        .article-content :global(th),
        .article-content :global(td) {
            padding: 0.6rem 0.7rem;
            white-space: nowrap;
        }
    }
</style>
