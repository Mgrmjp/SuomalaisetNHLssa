<script>
    import { base } from "$app/paths";
    import { fade } from "svelte/transition";
    import Snowfall from "$lib/components/ui/Snowfall.svelte";

    import NavTabs from "$lib/components/ui/NavTabs.svelte";
    import TeamLogo from "$lib/components/ui/TeamLogo.svelte";
    import { resetToDefault } from "$lib/stores/gameData.js";

    /** @type {import('./$types').PageData} */
    export let data;

    const { players, error, seasonId } = data;

    // Helper to format season display (e.g. 2025-2026 -> 2025-26)
    const formattedSeason = `${seasonId.substring(0, 4)}-${seasonId.substring(6, 8)}`;
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

<div
    class="page-background min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 relative overflow-hidden"
>
    <Snowfall count={8} />

    <div class="page-container max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 relative z-10">
        <!-- Header -->
        <div class="page-header text-center mb-12">
            <a
                href="{base}/"
                onclick={resetToDefault}
                class="logo-button focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2 rounded-xl transition-all duration-300 inline-block mb-6"
                aria-label="Palaa etusivulle"
            >
                <img
                    src={base + "/logo.svg"}
                    alt="Suomalaiset NHL-pelaajat"
                    class="w-16 h-16 mx-auto logo-img"
                />
            </a>

            <h1 class="text-4xl md:text-5xl font-bold text-slate-900 mb-4 tracking-tight">
                Suomalaisten Pistepörssi
            </h1>
            <p class="text-lg text-slate-600 max-w-2xl mx-auto mb-8">
                NHL-kauden {formattedSeason} tehokkaimmat suomalaispelaajat
            </p>

            <!-- Navigation -->
            <NavTabs />
        </div>

        {#if error}
            <div
                class="bg-red-50 border-l-4 border-red-500 p-4 rounded-md mx-auto max-w-lg shadow-sm"
                role="alert"
            >
                <div class="flex">
                    <div class="flex-shrink-0">
                        <svg class="h-5 w-5 text-red-500" viewBox="0 0 20 20" fill="currentColor">
                            <path
                                fill-rule="evenodd"
                                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                                clip-rule="evenodd"
                            />
                        </svg>
                    </div>
                    <div class="ml-3">
                        <p class="text-sm text-red-700">{error}</p>
                    </div>
                </div>
            </div>
        {:else if players.length === 0}
            <div class="text-center py-12 bg-white rounded-2xl shadow-sm border border-slate-100">
                <p class="text-slate-500">Ei tilastoja saatavilla tälle kaudelle vielä.</p>
            </div>
        {:else}
            <!-- Leaderboard Table -->
            <div
                class="leaderboard-card bg-white rounded-2xl shadow-xl overflow-hidden border border-slate-100 ring-1 ring-slate-900/5"
                in:fade={{ duration: 300 }}
            >
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
                                    class="hover:bg-slate-50/80 transition-colors duration-150 {index <
                                    3
                                        ? 'bg-gradient-to-r from-yellow-50/30 to-transparent'
                                        : ''}"
                                >
                                    <td class="px-6 py-4 text-center font-medium text-slate-400">
                                        {#if index === 0}
                                            <span
                                                class="inline-flex items-center justify-center w-6 h-6 rounded-full bg-yellow-100 text-yellow-700 ring-1 ring-yellow-200 font-bold text-xs"
                                                >1</span
                                            >
                                        {:else if index === 1}
                                            <span
                                                class="inline-flex items-center justify-center w-6 h-6 rounded-full bg-slate-200 text-slate-700 ring-1 ring-slate-300 font-bold text-xs"
                                                >2</span
                                            >
                                        {:else if index === 2}
                                            <span
                                                class="inline-flex items-center justify-center w-6 h-6 rounded-full bg-amber-100 text-amber-800 ring-1 ring-amber-200 font-bold text-xs"
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
                                        class="px-6 py-4 text-center font-bold text-lg text-blue-600 bg-blue-50/30 shadow-sm border-x border-slate-100 border-dotted"
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
            </div>

            <div class="mt-8 text-center text-sm text-slate-400">
                <p class="mt-2 text-xs">
                    Päivitetty: {new Date(data.updatedAt).toLocaleString("fi-FI")}
                </p>
            </div>
        {/if}
    </div>
</div>
