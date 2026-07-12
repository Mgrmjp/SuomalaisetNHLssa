<script>
// @ts-nocheck
import { ChevronLeft } from 'lucide-svelte'
import { base } from '$app/paths'
import PageHeader from '$lib/components/ui/PageHeader.svelte'
import PageShell from '$lib/components/ui/PageShell.svelte'
import TeamLogo from '$lib/components/ui/TeamLogo.svelte'
import { correctFullName } from '$lib/utils/finnishNameUtils.js'

/** @type {{ data: { skaters: any[], goalies: any[], seasonId: string, error: string | null, updatedAt: string } }} */
const { data } = $props()

const { skaters, goalies, seasonId, error: _error } = data
const _formattedSeason = `${seasonId.substring(0, 4)}-${seasonId.substring(6, 8)}`

let searchTerm = $state('')

const allPlayers = $derived(
    [...skaters, ...goalies].sort((a, b) => {
        const nameA = a.skaterFullName || a.goalieFullName
        const nameB = b.skaterFullName || b.goalieFullName
        return nameA.localeCompare(nameB)
    })
)

const filteredPlayers = $derived(
    allPlayers.filter((player) => {
        const name = correctFullName(player.skaterFullName || player.goalieFullName)
        const team = player.teamAbbrevs
        const search = searchTerm.toLowerCase()
        return name.toLowerCase().includes(search) || team.toLowerCase().includes(search)
    })
)

function getPlayerName(player) {
    return correctFullName(player.skaterFullName || player.goalieFullName)
}

// Helper to convert name to URL-friendly slug
function nameToSlug(name) {
    return name
        .toLowerCase()
        .replace(/ä/g, 'a')
        .replace(/ö/g, 'o')
        .replace(/å/g, 'o')
        .replace(/\s+/g, '-')
        .replace(/[^a-z0-9-]/g, '')
}

function getPlayerSlug(player) {
    return nameToSlug(getPlayerName(player))
}
</script>

<svelte:head>
    <title>Kaikki suomalaiset NHL-pelaajat {_formattedSeason} - Lista ja tilastot</title>
    <meta
        name="description"
        content="Katso lista kaikista suomalaisista NHL-pelaajista kaudella {_formattedSeason}. Mukana kaikki kenttäpelaajat ja maalivahdit joukkueineen."
    />
    <meta property="og:title" content="Kaikki suomalaiset NHL-pelaajat {_formattedSeason}" />
    <meta
        property="og:description"
        content="Katso lista kaikista suomalaisista NHL-pelaajista kaudella {_formattedSeason}. Mukana kaikki kenttäpelaajat ja maalivahdit joukkueineen."
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
        name: `Suomalaiset NHL-pelaajat ${_formattedSeason}`,
        description: `Kaikki suomalaiset NHL-pelaajat kaudella ${_formattedSeason}`,
        url: "https://suomalaisetnhlssa.fi/pelaajat",
        numberOfItems: filteredPlayers.length,
        inLanguage: "fi"
    })}</script>`}
</svelte:head>

<div class="flat-view min-h-screen">
    <PageShell width="wide">
        <a class="back-link" href={base + "/"}>
            <ChevronLeft class="h-4 w-4" aria-hidden="true" />
            Takaisin etusivulle
        </a>
        <PageHeader title="Kaikki suomalaiset NHL-pelaajat" subtitle={`Kausi ${_formattedSeason}`}>
            <!-- Search -->
            <div class="max-w-md mx-auto">
                <label class="sr-only" for="player-search">Hae pelaajaa tai joukkuetta</label>
                <input
                    id="player-search"
                    type="text"
                    bind:value={searchTerm}
                    placeholder="Hae pelaajaa tai joukkuetta..."
                    class="w-full border border-slate-300 bg-white/70 px-4 py-3 transition-colors focus:border-blue-700 focus:outline-none"
                />
            </div>
        </PageHeader>

        {#if _error}
            <div class="mx-auto max-w-lg border border-red-200 border-l-4 border-l-red-500 bg-red-50 p-4 text-center text-red-700">
                {_error}
            </div>
        {:else}
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {#each filteredPlayers as player}
                    <a
                        href={`${base}/pelaajat/${getPlayerSlug(player)}`}
                        class="player-card group flex items-center gap-4 border border-slate-200 bg-white/60 p-6 transition-colors hover:border-blue-700 hover:bg-white"
                    >
                        <div
                            class="flex h-16 w-16 flex-shrink-0 items-center justify-center border border-slate-200 bg-slate-50"
                        >
                            <TeamLogo team={player.teamAbbrevs} size="48" />
                        </div>
                        <div>
                            <h3 class="font-bold text-slate-900 text-lg leading-tight group-hover:text-blue-600 transition-colors">
                                {getPlayerName(player)}
                            </h3>
                            <div class="text-sm text-slate-500 mt-1">
                                {player.teamAbbrevs} • {player.positionCode}
                                {#if player.birthDate || player.age}
                                    • {player.age || (new Date().getFullYear() - new Date(player.birthDate).getFullYear())}v
                                {/if}
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

    .player-card {
        position: relative;
        color: inherit;
        text-decoration: none;
    }

    .player-card::before {
        content: "";
        position: absolute;
        inset: 0 auto 0 0;
        width: 3px;
        background: var(--accent);
        opacity: 0;
        transition: opacity 0.16s ease;
    }

    .player-card:hover::before,
    .player-card:focus-visible::before {
        opacity: 1;
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
