<script>
// @ts-nocheck
import { base } from '$app/paths'

const topPicks = [
    { year: 2016, rank: 2, name: 'Patrik Laine', team: 'Winnipeg', points: 367, games: 537 },
    { year: 2021, rank: 3, name: 'Anton Lundell', team: 'Florida', points: 156, games: 271 },
    { year: 2019, rank: 3, name: 'Kaapo Kakko', team: 'NY Rangers', points: 133, games: 327 },
    { year: 2016, rank: 3, name: 'Jesse Puljujärvi', team: 'Edmonton', points: 85, games: 331 },
    { year: 2018, rank: 6, name: 'Jesperi Kotkaniemi', team: 'Montreal', points: 188, games: 431 },
    { year: 2017, rank: 9, name: 'Miro Heiskanen', team: 'Dallas', points: 284, games: 438 },
    { year: 2015, rank: 9, name: 'Mikko Rantanen', team: 'Colorado', points: 509, games: 555 },
]

const yearlyStats = [
    { year: 2025, count: 28, top: '#12' },
    { year: 2024, count: 24, top: '#8' },
    { year: 2023, count: 22, top: '#17' },
    { year: 2022, count: 26, top: '#3' },
    { year: 2021, count: 21, top: '#3' },
    { year: 2020, count: 19, top: '#6' },
    { year: 2019, count: 23, top: '#3' },
    { year: 2018, count: 20, top: '#6' },
    { year: 2017, count: 18, top: '#9' },
    { year: 2016, count: 25, top: '#2' },
    { year: 2015, count: 17, top: '#9' },
    { year: 2014, count: 15, top: '#18' },
]
</script>

<svelte:head>
    <title>Draft-historia - Suomalaiset NHL:ssä</title>
    <meta name="description" content="Suomalaisten NHL-varausten historia ja tilastot." />
    <meta property="og:title" content="Draft-historia" />
    <meta property="og:description" content="Suomalaisten NHL-varausten historia ja tilastot." />
</svelte:head>

<div class="min-h-screen bg-slate-50">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <!-- Header -->
        <div class="text-center mb-12">
            <a href="{base}/" class="inline-block mb-6 hover:opacity-80 transition-opacity">
                <img src="{base}/logo.svg" alt="Suomalaiset NHL-pelaajat" class="w-16 h-16 mx-auto" />
            </a>
            <h1 class="text-4xl font-bold text-slate-900 mb-4">Draft-historia</h1>
            <p class="text-lg text-slate-600 max-w-2xl mx-auto">
                Suomalaisten pelaajien matka NHL:ään vuosikymmenten varrella.
            </p>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <!-- Left column: Stats -->
            <div class="lg:col-span-1 space-y-6">
                <!-- Summary card -->
                <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                    <h2 class="text-lg font-bold text-slate-900 mb-4">Yhteenveto</h2>
                    <div class="space-y-3">
                        <div class="flex justify-between items-center">
                            <span class="text-slate-600">Yhteensä varattu (2010-2025)</span>
                            <span class="font-bold text-slate-900">320+</span>
                        </div>
                        <div class="flex justify-between items-center">
                            <span class="text-slate-600">Top 10 -varaukset</span>
                            <span class="font-bold text-slate-900">15</span>
                        </div>
                        <div class="flex justify-between items-center">
                            <span class="text-slate-600">Ensimmäinen ykkösvaraus</span>
                            <span class="font-bold text-slate-900">-</span>
                        </div>
                    </div>
                </div>

                <!-- Yearly stats -->
                <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                    <h2 class="text-lg font-bold text-slate-900 mb-4">Varaukset vuosittain</h2>
                    <div class="space-y-2 max-h-80 overflow-y-auto">
                        {#each yearlyStats as stat}
                            <div class="flex items-center justify-between p-2 rounded-lg hover:bg-slate-50 transition-colors">
                                <span class="font-medium text-slate-900">{stat.year}</span>
                                <div class="flex items-center gap-4">
                                    <span class="text-sm text-slate-500">Top {stat.top}</span>
                                    <span class="w-12 text-right font-bold text-blue-600">{stat.count}</span>
                                </div>
                            </div>
                        {/each}
                    </div>
                </div>
            </div>

            <!-- Right column: Top picks -->
            <div class="lg:col-span-2">
                <h2 class="text-2xl font-bold text-slate-900 mb-6">Menestyneimmät top-varaukset</h2>
                
                <div class="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
                    <div class="overflow-x-auto">
                        <table class="w-full">
                            <thead class="bg-slate-50 border-b border-slate-200">
                                <tr>
                                    <th class="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Vuosi</th>
                                    <th class="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Varaus</th>
                                    <th class="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Pelaaja</th>
                                    <th class="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Joukkue</th>
                                    <th class="px-6 py-3 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">O</th>
                                    <th class="px-6 py-3 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">P</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-slate-100">
                                {#each topPicks as pick}
                                    <tr class="hover:bg-slate-50 transition-colors">
                                        <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-600">{pick.year}</td>
                                        <td class="px-6 py-4 whitespace-nowrap">
                                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                                #{pick.rank}
                                            </span>
                                        </td>
                                        <td class="px-6 py-4 whitespace-nowrap font-medium text-slate-900">{pick.name}</td>
                                        <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-600">{pick.team}</td>
                                        <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-mono text-slate-700">{pick.games}</td>
                                        <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-mono font-bold text-slate-900">{pick.points}</td>
                                    </tr>
                                {/each}
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Fun facts -->
                <div class="mt-8 grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="bg-blue-50 rounded-xl p-6 border border-blue-100">
                        <h3 class="font-bold text-blue-900 mb-2">Paras varausvuosi</h3>
                        <p class="text-sm text-blue-800">
                            <strong>2016</strong> tuotti eniten NHL-pelaajia: Patrik Laine, Jesse Puljujärvi, 
                            Mikko Rantanen, Sebastian Aho, Henri Jokiharju...
                        </p>
                    </div>
                    <div class="bg-emerald-50 rounded-xl p-6 border border-emerald-100">
                        <h3 class="font-bold text-emerald-900 mb-2">Eniten pisteitä</h3>
                        <p class="text-sm text-emerald-800">
                            <strong>Mikko Rantanen</strong> (2015, #9) on kerännyt eniten pisteitä 
                            suomalaisista draft-varauksista yli 500 pistettä.
                        </p>
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
