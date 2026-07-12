<script>
// @ts-nocheck
import { ChevronLeft, ChevronRight, Plus } from 'lucide-svelte'

import { base } from '$app/paths'
import Card from '$lib/components/ui/Card.svelte'
import PageHeader from '$lib/components/ui/PageHeader.svelte'
import PageShell from '$lib/components/ui/PageShell.svelte'

const scoutingReports = [
    {
        slug: 'oliver-suvanto',
        name: 'Oliver Suvanto',
        rank: '#3 Eurooppa',
        team: 'Tappara',
        position: 'Keskushyökkääjä',
        born: '2008',
        height: '191 cm',
        draft: '2026',
    },
    {
        slug: 'juho-piiparinen',
        name: 'Juho Piiparinen',
        rank: '#6 Eurooppa',
        team: 'Tappara',
        position: 'Puolustaja',
        born: '2008',
        height: '185 cm',
        draft: '2026',
    },
    {
        slug: 'vilho-vanhatalo',
        name: 'Vilho Vanhatalo',
        rank: '#14 Eurooppa',
        team: 'Tappara Jr.',
        position: 'Oikea laita',
        born: '2008',
        height: '191 cm',
        draft: '2026',
    },
]

const draftRankings = [
    { rank: 3, name: 'Oliver Suvanto', position: 'C', team: 'Tappara' },
    { rank: 6, name: 'Juho Piiparinen', position: 'D', team: 'Tappara' },
    { rank: 14, name: 'Vilho Vanhatalo', position: 'RW', team: 'Tappara Jr.' },
    { rank: 19, name: 'Samu Alalauri', position: 'D', team: 'Pelicans Jr.' },
    { rank: 26, name: 'Luka Arkko', position: 'LW', team: 'Pelicans Jr.' },
    { rank: 44, name: 'Ossi Tukio', position: 'D', team: 'Ilves Jr.' },
    { rank: 48, name: 'Jiko Laitinen', position: 'C', team: 'Ilves Jr.' },
    { rank: 72, name: 'Joel Tarvainen', position: 'D', team: 'KalPa Jr.' },
    { rank: 74, name: 'Leo Tuuva', position: 'RW', team: 'Lukko' },
    { rank: 84, name: 'Vertti Svensk', position: 'D', team: 'SaiPa Jr.' },
]
</script>

<svelte:head>
    <title>Scouting Reports - Suomalaiset NHL-lupaukset</title>
    <meta name="description" content="Yksityiskohtaiset scouting-raportit suomalaisista NHL-prospekteista." />
    <meta property="og:title" content="Scouting Reports" />
    <meta property="og:description" content="Yksityiskohtaiset scouting-raportit suomalaisista NHL-prospekteista." />
</svelte:head>

<div class="min-h-screen bg-slate-50">
    <PageShell>
        <a
            href={base + "/lupaukset"}
            class="mb-6 inline-flex items-center text-sm font-semibold text-slate-600 transition-colors hover:text-slate-900"
        >
            <ChevronLeft class="mr-1 h-4 w-4" aria-hidden="true" />
            Takaisin lupaukset-sivulle
        </a>

        <PageHeader
            title="Scouting Reports"
            subtitle="Yksityiskohtaiset analyysit Suomen lupaavimmista NHL-prospekteista ja tulevista draft-ikäluokista."
        />

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <!-- Left column: Top 10 -->
            <div class="lg:col-span-1">
                <Card>
                    <h2 class="text-xl font-bold text-slate-900 mb-4">Draft 2026 - Top 10</h2>
                    <p class="text-sm text-slate-500 mb-4">NHL Central Scouting - Eurooppalaiset</p>
                    
                    <div class="space-y-3">
                        {#each draftRankings.slice(0, 10) as player}
                            <div class="flex items-center gap-3 p-2 transition-colors hover:bg-slate-50">
                                <div class="flex h-10 w-10 flex-shrink-0 items-center justify-center bg-blue-100">
                                    <span class="text-sm font-bold text-blue-700">#{player.rank}</span>
                                </div>
                                <div class="flex-1 min-w-0">
                                    <div class="font-semibold text-slate-900 text-sm truncate">{player.name}</div>
                                    <div class="text-xs text-slate-500">{player.position} · {player.team}</div>
                                </div>
                            </div>
                        {/each}
                    </div>
                    
                    <div class="mt-4 pt-4 border-t border-slate-200">
                        <p class="text-xs text-slate-400">
                            Lähde: NHL Central Scouting Midterm Rankings 2026
                        </p>
                    </div>
                </Card>

                <!-- Draft History Link -->
                <div class="mt-6">
                    <Card>
                        <h2 class="text-xl font-bold text-slate-900 mb-4">Draft-historia</h2>
                        <p class="text-sm text-slate-600 mb-4">
                            Tutustu suomalaisten NHL-varausten historiaan ja tilastoihin.
                        </p>
                        <a
                            href={`${base}/drafts`}
                            class="inline-flex items-center font-medium text-blue-600 hover:text-blue-700"
                        >
                            Näytä historia
                            <ChevronRight class="ml-1 h-4 w-4" aria-hidden="true" />
                        </a>
                    </Card>
                </div>
            </div>

            <!-- Right column: Scouting Reports -->
            <div class="lg:col-span-2">
                <h2 class="text-2xl font-bold text-slate-900 mb-6">Yksityiskohtaiset raportit</h2>
                
                <div class="space-y-4">
                    {#each scoutingReports as report}
                        <a 
                            href="{base}/scouting/{report.slug}"
                            class="group block overflow-hidden border border-slate-200 bg-white transition-colors hover:border-blue-300"
                        >
                            <div class="p-6">
                                <div class="flex items-start justify-between gap-4">
                                    <div class="flex-1">
                                        <div class="flex items-center gap-2 mb-2">
                                            <span class="inline-flex items-center bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-800">
                                                {report.rank}
                                            </span>
                                            <span class="text-xs text-slate-500">{report.draft} Draft</span>
                                        </div>
                                        <h3 class="text-xl font-bold text-slate-900 group-hover:text-blue-600 transition-colors mb-2">
                                            {report.name}
                                        </h3>
                                        <div class="flex flex-wrap gap-x-4 gap-y-1 text-sm text-slate-600">
                                            <span>{report.position}</span>
                                            <span class="text-slate-300">·</span>
                                            <span>{report.team}</span>
                                            <span class="text-slate-300">·</span>
                                            <span>Synt. {report.born}</span>
                                            <span class="text-slate-300">·</span>
                                            <span>{report.height}</span>
                                        </div>
                                    </div>
                                    <ChevronRight class="w-5 h-5 text-slate-400 group-hover:text-blue-500 transition-colors flex-shrink-0 mt-1" aria-hidden="true" />
                                </div>
                            </div>
                        </a>
                    {/each}
                </div>

                <!-- More reports coming -->
                <div class="mt-8">
                    <Card>
                        <div class="flex items-center gap-3">
                            <div class="flex h-10 w-10 items-center justify-center bg-slate-200">
                                <Plus class="h-5 w-5 text-slate-500" aria-hidden="true" />
                            </div>
                            <div>
                                <h3 class="font-semibold text-slate-900">Lisää raportteja tulossa</h3>
                                <p class="text-sm text-slate-600">
                                    Seuraamme jatkuvasti suomalaisia prospecteja ja julkaisemme uusia raportteja.
                                </p>
                            </div>
                        </div>
                    </Card>
                </div>
            </div>
        </div>

    </PageShell>
</div>
