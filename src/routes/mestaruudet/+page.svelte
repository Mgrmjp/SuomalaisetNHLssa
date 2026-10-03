<script>
// @ts-nocheck

import { BadgeCheck, ChevronLeft } from 'lucide-svelte'
import { base } from '$app/paths'
import Card from '$lib/components/ui/Card.svelte'
import DataTable from '$lib/components/ui/DataTable.svelte'
import PageHeader from '$lib/components/ui/PageHeader.svelte'
import PageShell from '$lib/components/ui/PageShell.svelte'

/** @type {import('./$types').PageData} */
export let data

const { winners: _winners } = data
const winners = _winners
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
                name: "Mestaruudet",
                item: "https://suomalaisetnhlssa.fi/mestaruudet"
            }
        ]
    })}</script>`}
</svelte:head>

<div class="public-view min-h-screen">
    <PageShell width="medium">
        <a class="back-link" href={base + "/"}>
            <ChevronLeft class="h-4 w-4" aria-hidden="true" />
            Takaisin etusivulle
        </a>
        <PageHeader
            title="Suomalaiset Stanley Cup -voittajat"
            subtitle={`Yhteensä ${winners.length} suomalaista pelaajaa on voittanut himoitun Stanley Cupin.`}
        />

        <Card padding="none" accent>

                <DataTable caption="Suomalaisten Stanley Cup -mestaruudet" class="w-full text-left border-collapse">
                    <thead>
                        <tr class="bg-slate-50 border-b border-slate-200">
                            <th scope="col" class="px-6 py-4 font-semibold text-slate-700">Pelaaja</th>
                            <th scope="col" class="px-6 py-4 text-center font-semibold text-slate-700"
                                >Mestaruudet</th
                            >
                            <th scope="col" class="px-6 py-4 font-semibold text-slate-700"
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
                                            class="inline-flex h-8 w-8 items-center justify-center border
                                            {winner.wins >= 5
                                                ? 'border-yellow-200 bg-yellow-100 text-yellow-700'
                                                : winner.wins > 1
                                                  ? 'border-blue-200 bg-blue-100 text-blue-700'
                                                  : 'border-slate-200 bg-slate-100 text-slate-600'}"
                                        >
                                            {winner.wins}
                                        </span>
                                        {#if winner.validation?.verified && winner.validation?.hasCup}
                                            <span
                                                class="text-[10px] text-green-600 mt-1 flex items-center gap-0.5"
                                                title="Vahvistettu paikallisesta datasta"
                                            >
                                                <BadgeCheck class="w-3 h-3" aria-hidden="true" />
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
                </DataTable>

        </Card>

        <div class="mt-8 text-center text-sm text-slate-500">
            <p>
                Lisäksi useita suomalaisia on voittanut Stanley Cupin valmennus- tai
                huoltotehtävissä.
            </p>
        </div>
    </PageShell>
</div>

<style>
</style>
