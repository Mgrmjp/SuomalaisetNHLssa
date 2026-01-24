<script>
    import { base } from "$app/paths";
    import Snowfall from "$lib/components/ui/Snowfall.svelte";
    import TeamLogo from "$lib/components/ui/TeamLogo.svelte";
    import { correctFullName } from "$lib/utils/finnishNameUtils.js";

    /** @type {import('./$types').PageData} */
    export let data;

    const { skaters, goalies, seasonId, error } = data;
    const formattedSeason = `${seasonId.substring(0, 4)}-${seasonId.substring(6, 8)}`;

    let searchTerm = "";

    $: allPlayers = [...skaters, ...goalies].sort((a, b) => {
        const nameA = a.skaterFullName || a.goalieFullName;
        const nameB = b.skaterFullName || b.goalieFullName;
        return nameA.localeCompare(nameB);
    });

    $: filteredPlayers = allPlayers.filter((player) => {
        const name = player.skaterFullName || player.goalieFullName;
        const team = player.teamAbbrevs;
        const search = searchTerm.toLowerCase();
        return name.toLowerCase().includes(search) || team.toLowerCase().includes(search);
    });

    function getPlayerName(player) {
        return correctFullName(player.skaterFullName || player.goalieFullName);
    }

    // Helper to convert name to URL-friendly slug
    function nameToSlug(name) {
        return name.toLowerCase()
            .replace(/ä/g, 'a')
            .replace(/ö/g, 'o')
            .replace(/å/g, 'o')
            .replace(/\s+/g, '-')
            .replace(/[^a-z0-9-]/g, '');
    }

    function getPlayerSlug(player) {
        return nameToSlug(getPlayerName(player));
    }
</script>

<svelte:head>
    <title>Kaikki suomalaiset NHL-pelaajat {formattedSeason} - Lista ja tilastot</title>
    <meta
        name="description"
        content="Katso lista kaikista suomalaisista NHL-pelaajista kaudella {formattedSeason}. Mukana kaikki kenttäpelaajat ja maalivahdit joukkueineen."
    />
    <meta property="og:title" content="Kaikki suomalaiset NHL-pelaajat {formattedSeason}" />
    <meta
        property="og:description"
        content="Katso lista kaikista suomalaisista NHL-pelaajista kaudella {formattedSeason}. Mukana kaikki kenttäpelaajat ja maalivahdit joukkueineen."
    />
    <meta property="og:url" content="https://suomalaisetnhlssa.fi/pelaajat" />

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
                name: "Pelaajat",
                item: "https://suomalaisetnhlssa.fi/pelaajat"
            }
        ]
    })}</script>`}

    <!-- CollectionPage Schema for players list -->
    {@html `<script type="application/ld+json">${JSON.stringify({
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        name: `Suomalaiset NHL-pelaajat ${formattedSeason}`,
        description: `Kaikki suomalaiset NHL-pelaajat kaudella ${formattedSeason}`,
        url: "https://suomalaisetnhlssa.fi/pelaajat",
        numberOfItems: filteredPlayers.length,
        inLanguage: "fi"
    })}</script>`}
</svelte:head>

<div class="min-h-screen bg-slate-50 relative overflow-hidden">
    <Snowfall count={8} />

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 relative z-10">
        <div class="text-center mb-12">
            <a href="{base}/" class="inline-block mb-6 hover:opacity-80 transition-opacity">
                <img
                    src={base + "/logo.svg"}
                    alt="Suomalaiset NHL-pelaajat"
                    class="w-16 h-16 mx-auto"
                />
            </a>
            <h1 class="text-4xl font-bold text-slate-900 mb-4">Kaikki suomalaiset NHL-pelaajat</h1>
            <p class="text-lg text-slate-600 mb-8">
                Kausi {formattedSeason}
            </p>

            <!-- Search -->
            <div class="max-w-md mx-auto">
                <input
                    type="text"
                    bind:value={searchTerm}
                    placeholder="Hae pelaajaa tai joukkuetta..."
                    class="w-full px-4 py-3 rounded-xl border border-slate-200 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                />
            </div>
        </div>

        {#if error}
            <div class="bg-red-50 text-red-700 p-4 rounded-lg text-center max-w-lg mx-auto">
                {error}
            </div>
        {:else}
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {#each filteredPlayers as player}
                    <a
                        href={`${base}/pelaajat/${getPlayerSlug(player)}`}
                        class="bg-white rounded-xl shadow-sm border border-slate-100 p-6 flex items-center gap-4 hover:shadow-md hover:border-blue-200 transition-all group"
                    >
                        <div
                            class="flex-shrink-0 w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center"
                        >
                            <TeamLogo team={player.teamAbbrevs} size="48" />
                        </div>
                        <div>
                            <h3 class="font-bold text-slate-900 text-lg leading-tight group-hover:text-blue-600 transition-colors">
                                {getPlayerName(player)}
                            </h3>
                            <div class="text-sm text-slate-500 mt-1">
                                {player.teamAbbrevs} • {player.positionCode}
                            </div>
                            <div class="text-xs text-slate-400 mt-2">
                                {player.gamesPlayed} ottelua
                            </div>
                        </div>
                    </a>
                {/each}
            </div>

            <div class="mt-8 text-center text-sm text-slate-400">
                Päivitetty: {new Date(data.updatedAt).toLocaleString("fi-FI")} <br />
                Yhteensä {filteredPlayers.length} pelaajaa
            </div>
        {/if}
    </div>
</div>
