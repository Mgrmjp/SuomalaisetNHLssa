<script>
// @ts-nocheck

import { AlertCircle, ChevronLeft } from 'lucide-svelte'
import { fade } from 'svelte/transition'
import { base } from '$app/paths'
import Card from '$lib/components/ui/Card.svelte'
import PageHeader from '$lib/components/ui/PageHeader.svelte'
import PageShell from '$lib/components/ui/PageShell.svelte'
import TeamLogo from '$lib/components/ui/TeamLogo.svelte'

/** @type {import('./$types').PageData} */
export let data

const { players: _players, error: _error, seasonId } = data

const players = _players
const error = _error

// Helper to format season display (e.g. 2025-2026 -> 2025-26)
const formattedSeason = `${seasonId.substring(0, 4)}-${seasonId.substring(6, 8)}`
</script>

<svelte:head>
    <title>Suomalaisten Pistepörssi {formattedSeason} - Tilastot per kausi - NHL</title>
    <meta
        name="description"
        content="Kaikki suomalaiset NHL-pelaajat ja tilastot per kausi. Katso kuka johtaa suomalaisten pistepörssiä kaudella {formattedSeason}."
    />
    <meta
        property="og:title"
        content="Suomalaisten Pistepörssi {formattedSeason} - Tilastot per kausi - NHL"
    />
    <meta
        property="og:description"
        content="Kaikki suomalaiset NHL-pelaajat ja tilastot per kausi. Katso kuka johtaa suomalaisten pistepörssiä kaudella {formattedSeason}."
    />
    <meta property="og:url" content="https://suomalaisetnhlssa.fi/pisteporssi" />

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
                name: "Pistepörssi",
                item: "https://suomalaisetnhlssa.fi/pisteporssi"
            }
        ]
    })}</script>`}
</svelte:head>

<div class="flat-view min-h-screen">
    <PageShell width="wide">
        <a class="back-link" href={base + "/"}>
            <ChevronLeft class="h-4 w-4" aria-hidden="true" />
            Takaisin etusivulle
        </a>
        <PageHeader
            title="Suomalaisten Pistepörssi"
            subtitle={`NHL-kauden ${formattedSeason} tehokkaimmat suomalaispelaajat`}
        />

        {#if error}
            <div
                class="mx-auto max-w-lg border border-red-200 border-l-4 border-l-red-500 bg-red-50 p-4"
                role="alert"
            >
                <div class="flex">
                    <div class="flex-shrink-0">
                        <AlertCircle class="h-5 w-5 text-red-500" aria-hidden="true" />
                    </div>
                    <div class="ml-3">
                        <p class="text-sm text-red-700">{error}</p>
                    </div>
                </div>
            </div>
        {:else if players.length === 0}
            <div class="border border-slate-200 bg-white/60 py-12 text-center">
                <p class="text-slate-500">Ei tilastoja saatavilla tälle kaudelle vielä.</p>
            </div>
        {:else}
            <!-- Leaderboard Table -->
            <div in:fade={{ duration: 300 }}>
                <Card padding="none" accent>
                    <div class="leaderboard-scroll-area overflow-x-auto">
                    <table class="leaderboard-table w-full text-left text-sm whitespace-nowrap">
                        <thead>
                            <tr
                                class="bg-slate-50/80 border-b border-slate-200 text-xs uppercase tracking-wider text-slate-500 font-semibold"
                            >
                                <th scope="col" class="px-6 py-4 w-16 text-center">#</th>
                                <th scope="col" class="px-6 py-4">Pelaaja</th>
                                <th scope="col" class="px-6 py-4 text-center">Joukkue</th>
                                <th scope="col" class="px-6 py-4 text-center" title="Ottelut">GP</th
                                >
                                <th
                                    scope="col"
                                    class="px-6 py-4 text-center font-bold text-slate-700"
                                    title="Maalit">G</th
                                >
                                <th
                                    scope="col"
                                    class="px-6 py-4 text-center font-bold text-slate-700"
                                    title="Syötöt">A</th
                                >
                                <th
                                    scope="col"
                                    class="px-6 py-4 text-center text-base font-bold text-blue-600 bg-blue-50/30"
                                    title="Pisteet">P</th
                                >
                                <th
                                    scope="col"
                                    class="px-6 py-4 text-center hidden md:table-cell"
                                    title="Plus/Miinus">+/-</th
                                >
                                <th
                                    scope="col"
                                    class="px-6 py-4 text-center hidden md:table-cell"
                                    title="Rangaistusminuutit">PIM</th
                                >
                                <th
                                    scope="col"
                                    class="px-6 py-4 text-center hidden lg:table-cell"
                                    title="Peliaika keskimäärin">TOI/G</th
                                >
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-100">
                            {#each players as player, index}
                                <tr
                                    class="transition-colors duration-150 hover:bg-slate-50/80 {index <
                                    3 ? 'bg-yellow-50/30' : ''}"
                                >
                                    <td class="px-6 py-4 text-center font-medium text-slate-400">
                                        {#if index === 0}
                                            <span
                                                class="inline-flex h-6 w-6 items-center justify-center border border-yellow-200 bg-yellow-100 text-xs font-bold text-yellow-700"
                                                >1</span
                                            >
                                        {:else if index === 1}
                                            <span
                                                class="inline-flex h-6 w-6 items-center justify-center border border-slate-300 bg-slate-200 text-xs font-bold text-slate-700"
                                                >2</span
                                            >
                                        {:else if index === 2}
                                            <span
                                                class="inline-flex h-6 w-6 items-center justify-center border border-amber-200 bg-amber-100 text-xs font-bold text-amber-800"
                                                >3</span
                                            >
                                        {:else}
                                            {index + 1}
                                        {/if}
                                    </td>
                                    <td class="px-6 py-4">
                                        <div class="font-bold text-slate-900 text-base">
                                            {player.skaterFullName}
                                        </div>
                                        <div class="text-xs text-slate-500 md:hidden">
                                            {player.teamAbbrevs} • {player.positionCode}
                                        </div>
                                    </td>
                                    <td class="px-6 py-4 text-center">
                                        <div class="flex justify-center">
                                            <TeamLogo team={player.teamAbbrevs} size="32" />
                                        </div>
                                    </td>
                                    <td class="px-6 py-4 text-center text-slate-600 font-medium"
                                        >{player.gamesPlayed}</td
                                    >
                                    <td class="px-6 py-4 text-center text-slate-700 font-semibold"
                                        >{player.goals}</td
                                    >
                                    <td class="px-6 py-4 text-center text-slate-700 font-semibold"
                                        >{player.assists}</td
                                    >
                                    <td
                                        class="border-x border-dotted border-slate-100 bg-blue-50/30 px-6 py-4 text-center text-lg font-bold text-blue-600"
                                    >
                                        {player.points}
                                    </td>
                                    <td
                                        class="px-6 py-4 text-center hidden md:table-cell font-medium {player.plusMinus >
                                        0
                                            ? 'text-green-600'
                                            : player.plusMinus < 0
                                              ? 'text-red-500'
                                              : 'text-slate-400'}"
                                    >
                                        {player.plusMinus > 0 ? "+" : ""}{player.plusMinus}
                                    </td>
                                    <td
                                        class="px-6 py-4 text-center hidden md:table-cell text-slate-500"
                                        >{player.penaltyMinutes}</td
                                    >
                                    <td
                                        class="px-6 py-4 text-center hidden lg:table-cell text-xs tabular-nums text-slate-500"
                                    >
                                        {Math.floor(player.timeOnIcePerGame / 60)}:{Math.floor(
                                            player.timeOnIcePerGame % 60,
                                        )
                                            .toString()
                                            .padStart(2, "0")}
                                    </td>
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                    </div>
                </Card>
            </div>

            <div class="mt-8 text-center text-sm text-slate-400">
                <p class="mt-2 text-xs">
                    Päivitetty: {new Date(data.updatedAt).toLocaleString("fi-FI")}
                </p>
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
