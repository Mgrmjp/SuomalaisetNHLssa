<script>
    import { base } from "$app/paths";
    import Snowfall from "$lib/components/ui/Snowfall.svelte";

    /** @type {import('./$types').PageData} */
    export let data;

    const { winners } = data;
</script>

<svelte:head>
    <title>Suomalaiset NHL-mestarit - Stanley Cup voittajat</title>
    <meta
        name="description"
        content="Katso lista kaikista suomalaisista Stanley Cup -voittajista. Jari Kurri, Esa Tikkanen, Teemu Selänne ja muut suomalaiset NHL-mestarit."
    />
    <meta property="og:title" content="Suomalaiset NHL-mestarit - Stanley Cup voittajat" />
    <meta
        property="og:description"
        content="Katso lista kaikista suomalaisista Stanley Cup -voittajista. Jari Kurri, Esa Tikkanen, Teemu Selänne ja muut suomalaiset NHL-mestarit."
    />
    <meta property="og:url" content="https://suomalaisetnhlssa.fi/mestaruudet" />
</svelte:head>

<div class="min-h-screen bg-slate-50 relative overflow-hidden">
    <Snowfall count={8} />

    <div class="max-w-4xl mx-auto px-4 py-12 relative z-10">
        <div class="text-center mb-12">
            <a href="{base}/" class="inline-block mb-6 hover:opacity-80 transition-opacity">
                <img
                    src={base + "/logo.svg"}
                    alt="Suomalaiset NHL-pelaajat"
                    class="w-16 h-16 mx-auto"
                />
            </a>
            <h1 class="text-4xl font-bold text-slate-900 mb-4">
                Suomalaiset Stanley Cup -voittajat
            </h1>
            <p class="text-lg text-slate-600">
                Yhteensä {winners.length} suomalaista pelaajaa on voittanut himoitun Stanley Cupin.
            </p>
        </div>

        <div class="bg-white rounded-2xl shadow-xl overflow-hidden border border-slate-100">
            <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="bg-slate-50 border-b border-slate-200">
                            <th class="px-6 py-4 font-semibold text-slate-700">Pelaaja</th>
                            <th class="px-6 py-4 text-center font-semibold text-slate-700"
                                >Mestaruudet</th
                            >
                            <th class="px-6 py-4 font-semibold text-slate-700"
                                >Vuodet ja Joukkueet</th
                            >
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-100">
                        {#each winners as winner}
                            <tr class="hover:bg-slate-50/50 transition-colors">
                                <td class="px-6 py-4 font-bold text-slate-900">
                                    {winner.name}
                                </td>
                                <td class="px-6 py-4 text-center">
                                    <div class="flex flex-col items-center">
                                        <span
                                            class="inline-flex items-center justify-center w-8 h-8 rounded-full
                                            {winner.wins >= 5
                                                ? 'bg-yellow-100 text-yellow-700 ring-2 ring-yellow-200'
                                                : winner.wins > 1
                                                  ? 'bg-blue-100 text-blue-700 ring-2 ring-blue-200'
                                                  : 'bg-slate-100 text-slate-600'}"
                                        >
                                            {winner.wins}
                                        </span>
                                        {#if winner.validation?.verified && winner.validation?.hasCup}
                                            <span
                                                class="text-[10px] text-green-600 mt-1 flex items-center gap-0.5"
                                                title="Vahvistettu NHL API:sta"
                                            >
                                                <svg
                                                    xmlns="http://www.w3.org/2000/svg"
                                                    viewBox="0 0 20 20"
                                                    fill="currentColor"
                                                    class="w-3 h-3"
                                                >
                                                    <path
                                                        fill-rule="evenodd"
                                                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z"
                                                        clip-rule="evenodd"
                                                    />
                                                </svg>
                                                Vahvistettu
                                            </span>
                                        {/if}
                                    </div>
                                </td>
                                <td class="px-6 py-4 text-slate-600">
                                    <ul class="space-y-1">
                                        {#each winner.years as win}
                                            <li class="flex items-center gap-2">
                                                <span class="font-mono font-medium text-slate-800"
                                                    >{win.year}</span
                                                >
                                                <span class="text-slate-400">•</span>
                                                <span>{win.team}</span>
                                            </li>
                                        {/each}
                                    </ul>
                                </td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
            </div>
        </div>

        <div class="mt-8 text-center text-sm text-slate-500">
            <p>
                Lisäksi useita suomalaisia on voittanut Stanley Cupin valmennus- tai
                huoltotehtävissä.
            </p>
        </div>
    </div>
</div>
