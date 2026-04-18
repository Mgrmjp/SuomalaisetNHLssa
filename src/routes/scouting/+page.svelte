<script>
// @ts-nocheck
import { base } from '$app/paths'

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
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <!-- Header -->
        <div class="text-center mb-12">
            <a href="{base}/" class="inline-block mb-6 hover:opacity-80 transition-opacity">
                <img src="{base}/logo.svg" alt="Suomalaiset NHL-pelaajat" class="w-16 h-16 mx-auto" />
            </a>
            <h1 class="text-4xl font-bold text-slate-900 mb-4">Scouting Reports</h1>
            <p class="text-lg text-slate-600 max-w-2xl mx-auto">
                Yksityiskohtaiset analyysit Suomen lupaavimmista NHL-prospekteista ja tulevista draft-ikäluokista.
            </p>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <!-- Left column: Top 10 -->
            <div class="lg:col-span-1">
                <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                    <h2 class="text-xl font-bold text-slate-900 mb-4">Draft 2026 - Top 10</h2>
                    <p class="text-sm text-slate-500 mb-4">NHL Central Scouting - Eurooppalaiset</p>
                    
                    <div class="space-y-3">
                        {#each draftRankings.slice(0, 10) as player}
                            <div class="flex items-center gap-3 p-2 rounded-lg hover:bg-slate-50 transition-colors">
                                <div class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
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
                </div>

                <!-- Draft History Link -->
                <div class="mt-6 bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                    <h2 class="text-xl font-bold text-slate-900 mb-4">Draft-historia</h2>
                    <p class="text-sm text-slate-600 mb-4">
                        Tutustu suomalaisten NHL-varausten historiaan ja tilastoihin.
                    </p>
                    <a 
                        href={`${base}/drafts`}
                        class="inline-flex items-center text-blue-600 hover:text-blue-700 font-medium"
                    >
                        Näytä historia
                        <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                        </svg>
                    </a>
                </div>
            </div>

            <!-- Right column: Scouting Reports -->
            <div class="lg:col-span-2">
                <h2 class="text-2xl font-bold text-slate-900 mb-6">Yksityiskohtaiset raportit</h2>
                
                <div class="space-y-4">
                    {#each scoutingReports as report}
                        <a 
                            href="{base}/scouting/{report.slug}"
                            class="block bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden hover:shadow-md hover:border-blue-200 transition-all group"
                        >
                            <div class="p-6">
                                <div class="flex items-start justify-between gap-4">
                                    <div class="flex-1">
                                        <div class="flex items-center gap-2 mb-2">
                                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
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
                                    <svg 
                                        class="w-5 h-5 text-slate-400 group-hover:text-blue-500 transition-colors flex-shrink-0 mt-1"
                                        fill="none" 
                                        stroke="currentColor" 
                                        viewBox="0 0 24 24"
                                    >
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                                    </svg>
                                </div>
                            </div>
                        </a>
                    {/each}
                </div>

                <!-- More reports coming -->
                <div class="mt-8 p-6 bg-slate-100 rounded-xl border border-slate-200">
                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 rounded-full bg-slate-200 flex items-center justify-center">
                            <svg class="w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
                            </svg>
                        </div>
                        <div>
                            <h3 class="font-semibold text-slate-900">Lisää raportteja tulossa</h3>
                            <p class="text-sm text-slate-600">
                                Seuraamme jatkuvasti suomalaisia prospecteja ja julkaisemme uusia raportteja.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Back link -->
        <div class="mt-12 text-center">
            <a 
                href="{base}/lupaukset"
                class="inline-flex items-center text-slate-600 hover:text-slate-900 transition-colors"
            >
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
                </svg>
                Takaisin lupaukset-sivulle
            </a>
        </div>
    </div>
</div>
