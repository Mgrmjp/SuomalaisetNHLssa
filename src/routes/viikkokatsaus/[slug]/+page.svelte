<script>
    import { base } from "$app/paths";

    /** @type {{ data: { article: {slug: string, title: string, date: string, week: number, year: number, content: string}, prevArticle: {slug: string, title: string} | null, nextArticle: {slug: string, title: string} | null } }} */
    let { data } = $props();

    function formatDate(dateStr) {
        return new Date(dateStr).toLocaleDateString("fi-FI", {
            day: "numeric",
            month: "long",
            year: "numeric",
        });
    }
</script>

<svelte:head>
    <title>{data.article.title} - Suomalaiset NHL:ssä</title>
    <meta
        name="description"
        content={`Viikon ${data.article.week} katsaus suomalaisten NHL-pelaajien menestykseen.`}
    />
    <meta property="og:title" content={`${data.article.title} - Suomalaiset NHL:ssä`} />
    <meta
        property="og:description"
        content={`Viikon ${data.article.week} katsaus suomalaisten NHL-pelaajien menestykseen.`}
    />
    <meta
        property="og:url"
        content={`https://suomalaisetnhlssa.fi/viikkokatsaus/${data.article.slug}`}
    />
</svelte:head>

<div class="w-full max-w-3xl mx-auto px-4 py-8">
    <div class="space-y-6">
        <!-- Back link -->
        <div class="mb-6">
            <a
                href={base + "/viikkokatsaus"}
                class="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 transition-colors"
            >
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M15 19l-7-7 7-7"
                    />
                </svg>
                Takaisin viikkokatsauksiin
            </a>
        </div>

        <!-- Featured player hero -->
        {#if data.article.featured_player_id}
            <div
                class="mb-8 flex items-center gap-6 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-100"
            >
                <div
                    class="w-24 h-24 sm:w-32 sm:h-32 rounded-full bg-white shadow-lg border-4 border-white flex-shrink-0 overflow-hidden"
                >
                    <img
                        src={`${base}/headshots/${data.article.featured_player_id}.webp`}
                        alt="Viikon tähti"
                        class="w-full h-full object-cover"
                        loading="eager"
                    />
                </div>
                <div class="flex-1 min-w-0">
                    <p class="text-sm font-semibold text-blue-600 uppercase tracking-wide mb-1">
                        Viikon tähti
                    </p>
                    <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">
                        {data.article.title}
                    </h1>
                    <p class="text-gray-600 text-sm">
                        {formatDate(data.article.date)} · Viikko {data.article.week}, {data.article
                            .year}
                    </p>
                </div>
            </div>
        {:else}
            <!-- Article header (fallback without featured player) -->
            <header class="mb-8">
                <h1 class="text-3xl font-bold text-gray-900 mb-3">{data.article.title}</h1>
                <p class="text-gray-500 text-sm">
                    {formatDate(data.article.date)} · Viikko {data.article.week}, {data.article
                        .year}
                </p>
            </header>
        {/if}

        <!-- Article content -->
        <article
            class="article-content bg-white border border-gray-200 rounded-xl p-6 sm:p-8 shadow-sm"
        >
            {@html data.article.content}
        </article>

        <!-- Navigation -->
        <nav class="flex justify-between items-center pt-6 border-t border-gray-200">
            {#if data.prevArticle}
                <a
                    href={`${base}/viikkokatsaus/${data.prevArticle.slug}`}
                    class="inline-flex items-center text-sm text-gray-600 hover:text-blue-600 transition-colors"
                >
                    <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M15 19l-7-7 7-7"
                        />
                    </svg>
                    <span class="hidden sm:inline">{data.prevArticle.title}</span>
                    <span class="sm:hidden">Edellinen</span>
                </a>
            {:else}
                <div></div>
            {/if}

            {#if data.nextArticle}
                <a
                    href={`${base}/viikkokatsaus/${data.nextArticle.slug}`}
                    class="inline-flex items-center text-sm text-gray-600 hover:text-blue-600 transition-colors"
                >
                    <span class="hidden sm:inline">{data.nextArticle.title}</span>
                    <span class="sm:hidden">Seuraava</span>
                    <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M9 5l7 7-7 7"
                        />
                    </svg>
                </a>
            {:else}
                <div></div>
            {/if}
        </nav>
    </div>
</div>

<style>
    .article-content :global(h2) {
        font-size: 1.75rem;
        font-weight: 700;
        color: #111827;
        margin-top: 2.5rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #f3f4f6;
    }

    .article-content :global(h3) {
        font-size: 1.25rem;
        font-weight: 600;
        color: #1f2937;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }

    .article-content :global(p) {
        color: #374151;
        line-height: 1.8;
        margin-bottom: 1.25rem;
    }

    /* Table styling */
    .article-content :global(table) {
        width: 100%;
        border-collapse: collapse;
        margin: 1.5rem 0;
        font-size: 0.95rem;
        border-radius: 0.5rem;
        overflow: hidden;
        border: 1px solid #e5e7eb;
    }

    .article-content :global(th) {
        background-color: #f9fafb;
        color: #111827;
        font-weight: 600;
        text-align: left;
        padding: 0.75rem 1rem;
        border-bottom: 2px solid #e5e7eb;
    }

    .article-content :global(td) {
        padding: 0.75rem 1rem;
        border-bottom: 1px solid #f3f4f6;
        color: #4b5563;
    }

    .article-content :global(tr:last-child td) {
        border-bottom: none;
    }

    .article-content :global(tr:hover td) {
        background-color: #f9fafb;
    }

    /* Horizontal rules */
    .article-content :global(hr) {
        border: 0;
        border-top: 1px solid #e5e7eb;
        margin: 2rem 0;
    }

    /* Source citations */
    .article-content :global(em) {
        font-style: italic;
        color: #6b7280;
        font-size: 0.875rem;
    }

    .article-content :global(ul),
    .article-content :global(ol) {
        margin-left: 1.5rem;
        margin-bottom: 1.5rem;
        color: #374151;
    }

    .article-content :global(ul) {
        list-style-type: none;
    }

    .article-content :global(ul li) {
        position: relative;
        padding-left: 1.5rem;
    }

    .article-content :global(ul li::before) {
        content: "•";
        position: absolute;
        left: 0;
        color: #3b82f6;
        font-weight: bold;
    }

    .article-content :global(ol) {
        list-style-type: decimal;
    }

    .article-content :global(li) {
        margin-bottom: 0.75rem;
        line-height: 1.6;
    }

    .article-content :global(strong) {
        font-weight: 600;
        color: #111827;
    }
</style>
