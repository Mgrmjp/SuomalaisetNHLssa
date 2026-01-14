<script>
    import { base } from "$app/paths";

    /** @type {{ data: { articles: Array<{slug: string, title: string, date: string, week: number, year: number, excerpt: string}> } }} */
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
</svelte:head>

<div class="w-full max-w-3xl mx-auto px-4 py-8">
    <div class="space-y-6">
        <!-- Back link -->
        <div class="mb-6">
            <a
                href={base + "/"}
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
                Takaisin etusivulle
            </a>
        </div>

        <!-- Main title -->
        <h1 class="text-3xl font-bold text-gray-900 mb-8">Viikkokatsaus</h1>

        <!-- Article list -->
        {#if data.articles.length === 0}
            <p class="text-gray-600">Ei vielä artikkeleita.</p>
        {:else}
            <div class="space-y-4">
                {#each data.articles as article}
                    <a
                        href={`${base}/viikkokatsaus/${article.slug}`}
                        class="block bg-white border border-gray-200 rounded-xl p-6 shadow-sm hover:shadow-md hover:border-blue-200 transition-all duration-200 group"
                    >
                        <div class="flex items-start justify-between gap-4">
                            <div class="flex items-start gap-4 flex-1">
                                {#if article.featured_player_id}
                                    <div class="w-16 h-16 rounded-full bg-gray-100 flex-shrink-0 overflow-hidden">
                                        <img
                                            src={`${base}/headshots/${article.featured_player_id}.webp`}
                                            alt="Viikon tähti"
                                            class="w-full h-full object-cover"
                                            loading="lazy"
                                        />
                                    </div>
                                {/if}
                                <div class="flex-1 min-w-0">
                                    <h2
                                        class="text-xl font-semibold text-gray-900 group-hover:text-blue-600 transition-colors mb-2"
                                    >
                                        {article.title}
                                    </h2>
                                    <p class="text-gray-600 text-sm mb-3">
                                        {formatDate(article.date)} · Viikko {article.week}
                                    </p>
                                    <p class="text-gray-700 leading-relaxed">
                                        {article.excerpt}
                                    </p>
                                </div>
                            </div>
                            <svg
                                class="w-5 h-5 text-gray-400 group-hover:text-blue-500 transition-colors flex-shrink-0 mt-1"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                            >
                                <path
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    stroke-width="2"
                                    d="M9 5l7 7-7 7"
                                />
                            </svg>
                        </div>
                    </a>
                {/each}
            </div>
        {/if}
    </div>
</div>

<style>
    a.block {
        border-left: 4px solid transparent;
    }

    a.block:hover {
        border-left-color: #3b82f6;
    }
</style>
