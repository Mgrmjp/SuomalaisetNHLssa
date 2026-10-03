<script>
// @ts-nocheck

import { ChevronLeft } from 'lucide-svelte'
import { fade } from 'svelte/transition'
import { base } from '$app/paths'
import Card from '$lib/components/ui/Card.svelte'
import DataTable from '$lib/components/ui/DataTable.svelte'
import Notice from '$lib/components/ui/Notice.svelte'
import PageHeader from '$lib/components/ui/PageHeader.svelte'
import PageShell from '$lib/components/ui/PageShell.svelte'
import TeamLogo from '$lib/components/ui/TeamLogo.svelte'
import ViewMetadata from '$lib/components/ui/ViewMetadata.svelte'
import ViewState from '$lib/components/ui/ViewState.svelte'

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

<div class="public-view min-h-screen">
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
            <Notice variant="error">{error}</Notice>
        {:else if players.length === 0}
            <ViewState message="Ei tilastoja saatavilla tälle kaudelle vielä." />
        {:else}
            <!-- Leaderboard Table -->
            <div in:fade={{ duration: 300 }}>
                <Card padding="none" accent>

                    <DataTable caption={`Suomalaisten pistepörssi ${formattedSeason}`} class="leaderboard-table w-full text-left text-sm whitespace-nowrap" scrollClass="leaderboard-scroll-area">
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
                    </DataTable>

                </Card>
            </div>

            <ViewMetadata class="mt-8">
                <p class="mt-2 text-xs">
                    Päivitetty: {new Date(data.updatedAt).toLocaleString("fi-FI")}
                </p>
            </ViewMetadata>
        {/if}
    </PageShell>
</div>

<style>
</style>
