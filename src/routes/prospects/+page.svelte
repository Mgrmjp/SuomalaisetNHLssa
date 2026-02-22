<script>
import { onMount } from 'svelte'
import { loadProspects } from '$lib/stores/gameData'

// View state
const _activeTab = 'prospects' // 'prospects' | 'draft'

// Sort options for prospects
let sortBy = 'points' // 'points', 'goals', 'assists', 'league'
let sortDirection = 'desc'

// Draft view state
const draftCategory = 'north_american_skaters' // 'north_american_skaters' | 'international_skaters'

onMount(() => {
    loadProspects()
})

// Derived prospects
$: sortedProspects = [...$prospects].sort((a, b) => {
    if (sortBy === 'league') {
        return sortDirection === 'asc'
            ? a.league.localeCompare(b.league)
            : b.league.localeCompare(a.league)
    }
    if (sortBy === 'age') {
        if (sortDirection === 'asc') {
            return b.birthDate.localeCompare(a.birthDate)
        }
        return a.birthDate.localeCompare(b.birthDate)
    }

    const valA = a.stats?.[sortBy] || 0
    const valB = b.stats?.[sortBy] || 0
    return sortDirection === 'asc' ? valA - valB : valB - valA
})

// Derived draft rankings
$: currentDraftList = $draftRankings[draftCategory] || []

function _setSort(field) {
    if (sortBy === field) {
        sortDirection = sortDirection === 'asc' ? 'desc' : 'asc'
    } else {
        sortBy = field
        sortDirection = field === 'age' ? 'asc' : 'desc'
    }
}

function _getSortIcon(field) {
    if (sortBy !== field) return ''
    return sortDirection === 'asc' ? '↑' : '↓'
}
</script>

<svelte:head>
    <title>Suomalaiset NHL-lupaukset - Varausprospectit ja tulevat tähdet</title>
    <meta name="description" content="Seuraa suomalaisten NHL-varausten ja tulevien huippujen otteita maailmalla." />
    <meta property="og:title" content="Suomalaiset NHL-lupaukset" />
    <meta property="og:description" content="Seuraa suomalaisten NHL-varausten ja tulevien huippujen otteita maailmalla." />
    <meta property="og:url" content="https://suomalaisetnhlssa.fi/prospects" />
</svelte:head>

<div class="min-h-screen bg-slate-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <!-- Header -->
        <div class="text-center mb-12">
            <a href="{base}/" class="inline-block mb-6 hover:opacity-80 transition-opacity">
                <img
                    src={base + "/logo.svg"}
                    alt="Suomalaiset NHL-pelaajat"
                    class="w-16 h-16 mx-auto"
                />
            </a>
            <h1 class="text-4xl font-bold text-slate-900 mb-4">
                Suomalaiset Lupaukset
            </h1>
            <p class="text-lg text-slate-600 max-w-2xl mx-auto mb-8">
                Seuraa suomalaisten NHL-varausten ja tulevien huippujen otteita maailmalla.
            </p>

            <!-- Main Tabs -->
            <div class="flex justify-center">
                <div class="bg-white p-1.5 rounded-xl inline-flex shadow-sm border border-slate-200">
                    <button 
                        class="px-6 py-2.5 rounded-lg text-sm font-semibold transition-all {activeTab === 'prospects' ? 'bg-blue-600 text-white shadow-md' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'}"
                        on:click={() => activeTab = 'prospects'}
                    >
                        NHL-varaukset
                    </button>
                    <button 
                        class="px-6 py-2.5 rounded-lg text-sm font-semibold transition-all {activeTab === 'draft' ? 'bg-blue-600 text-white shadow-md' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'}"
                        on:click={() => activeTab = 'draft'}
                    >
                        Draft 2026
                    </button>
                </div>
            </div>
        </div>

        {#if $prospectsLoading}
            <div class="flex justify-center items-center h-64">
                <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
            </div>
        {:else}
            {#if activeTab === 'prospects'}
                <div in:fade={{ duration: 300 }}>
                    <!-- Controls -->
                    <div class="flex justify-center gap-3 mb-8 flex-wrap">
                        <button 
                            class="px-4 py-2 rounded-full text-sm font-medium transition-all shadow-sm
                            {sortBy === 'points' ? 'bg-blue-600 text-white' : 'bg-white text-slate-700 border border-slate-200 hover:border-blue-300 hover:bg-slate-50'}"
                            on:click={() => setSort('points')}
                        >
                            Pisteet {getSortIcon('points')}
                        </button>
                        <button 
                            class="px-4 py-2 rounded-full text-sm font-medium transition-all shadow-sm
                            {sortBy === 'goals' ? 'bg-blue-600 text-white' : 'bg-white text-slate-700 border border-slate-200 hover:border-blue-300 hover:bg-slate-50'}"
                            on:click={() => setSort('goals')}
                        >
                            Maalit {getSortIcon('goals')}
                        </button>
                        <button 
                            class="px-4 py-2 rounded-full text-sm font-medium transition-all shadow-sm
                            {sortBy === 'league' ? 'bg-blue-600 text-white' : 'bg-white text-slate-700 border border-slate-200 hover:border-blue-300 hover:bg-slate-50'}"
                            on:click={() => setSort('league')}
                        >
                            Liiga {getSortIcon('league')}
                        </button>
                        <button 
                            class="px-4 py-2 rounded-full text-sm font-medium transition-all shadow-sm
                            {sortBy === 'age' ? 'bg-blue-600 text-white' : 'bg-white text-slate-700 border border-slate-200 hover:border-blue-300 hover:bg-slate-50'}"
                            on:click={() => {
                                sortBy = 'age';
                                sortDirection = 'asc';
                            }}
                        >
                            Ikä {getSortIcon('age')}
                        </button>
                    </div>

                    <!-- Grid -->
                    {#if sortedProspects.length === 0}
                        <div class="text-center text-slate-400 mt-12">
                            <p>Ei löytynyt lupauksia.</p>
                        </div>
                    {:else}
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                            {#each sortedProspects as player (player.id)}
                                <div 
                                    class="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden hover:shadow-md hover:border-blue-200 transition-all group"
                                >
                                    <div class="relative h-48 bg-slate-100 overflow-hidden">
                                        <div class="absolute inset-0 bg-gradient-to-t from-slate-900/60 via-transparent to-transparent z-10"></div>
                                        <img 
                                            src={player.headshot} 
                                            alt={player.name}
                                            class="w-full h-full object-cover object-top transform group-hover:scale-105 transition-transform duration-500"
                                            loading="lazy"
                                            on:error={(e) => e.target.style.display = 'none'} 
                                        />
                                        <div class="absolute top-3 right-3 z-20 bg-white/95 backdrop-blur rounded-full px-3 py-1.5 shadow-sm border border-slate-100 flex items-center gap-1.5">
                                            <span class="text-xs font-medium text-slate-500">Varaus:</span>
                                            <span class="text-xs font-bold text-slate-800">{player.nhlRights}</span>
                                        </div>
                                    </div>

                                    <div class="p-4 relative">
                                        <div class="absolute -top-3 left-4 bg-blue-600 text-white text-xs font-bold px-3 py-1 rounded-full shadow-md">
                                            {player.league}
                                        </div>
                                        <h3 class="mt-2 text-lg font-bold text-slate-900 truncate">{player.name}</h3>
                                        <p class="text-sm text-slate-500 mb-4">{player.currentTeam}</p>
                                        <div class="grid grid-cols-4 gap-2 bg-slate-50 rounded-lg p-3 text-center border border-slate-100">
                                            <div>
                                                <div class="text-xs text-slate-400 uppercase font-medium">GP</div>
                                                <div class="font-mono font-bold text-slate-700">{player.stats?.gp || 0}</div>
                                            </div>
                                            <div>
                                                <div class="text-xs text-slate-400 uppercase font-medium">G</div>
                                                <div class="font-mono font-bold text-emerald-600">{player.stats?.goals || 0}</div>
                                            </div>
                                            <div>
                                                <div class="text-xs text-slate-400 uppercase font-medium">A</div>
                                                <div class="font-mono font-bold text-amber-600">{player.stats?.assists || 0}</div>
                                            </div>
                                            <div>
                                                <div class="text-xs text-slate-400 uppercase font-medium">P</div>
                                                <div class="font-mono font-bold text-slate-900 text-lg">{player.stats?.points || 0}</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            {/each}
                        </div>
                    {/if}
                </div>

            {:else if activeTab === 'draft'}
                <div in:fade={{ duration: 300 }}>
                    <!-- Sub Tabs -->
                    <div class="flex justify-center mb-8">
                        <div class="bg-white p-1 rounded-lg inline-flex shadow-sm border border-slate-200">
                            <button 
                                class="px-4 py-2 rounded-md text-sm font-medium transition-all {draftCategory === 'international_skaters' ? 'bg-slate-100 text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'}"
                                on:click={() => draftCategory = 'international_skaters'}
                            >
                                Eurooppa
                            </button>
                            <button 
                                class="px-4 py-2 rounded-md text-sm font-medium transition-all {draftCategory === 'north_american_skaters' ? 'bg-slate-100 text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'}"
                                on:click={() => draftCategory = 'north_american_skaters'}
                            >
                                Pohjois-Amerikka
                            </button>
                        </div>
                    </div>

                    <!-- List View -->
                    <div class="max-w-4xl mx-auto space-y-3">
                        {#each currentDraftList as player (player.firstName + player.lastName)}
                            <div class="bg-white rounded-xl p-4 border border-slate-200 shadow-sm flex items-center gap-4 hover:shadow-md hover:border-blue-200 transition-all">
                                <!-- Rank Circle -->
                                <div class="flex-shrink-0 w-12 h-12 rounded-full bg-blue-50 border border-blue-200 flex items-center justify-center">
                                    <span class="text-lg font-bold text-blue-600">#{player.midtermRank}</span>
                                </div>

                                <div class="flex-grow min-w-0">
                                    <h3 class="text-lg font-bold text-slate-900 truncate">{player.firstName} {player.lastName}</h3>
                                    <div class="flex flex-wrap gap-x-2 gap-y-1 text-sm text-slate-500">
                                        <span class="font-medium text-slate-600">{player.positionCode}</span>
                                        <span class="text-slate-300">•</span>
                                        <span>{player.heightInInches}" / {player.weightInPounds} lbs</span>
                                        <span class="text-slate-300 hidden sm:inline">•</span>
                                        <span class="hidden sm:inline truncate">{player.lastAmateurClub} ({player.lastAmateurLeague})</span>
                                    </div>
                                </div>
                                
                                <div class="hidden sm:block text-right flex-shrink-0">
                                    <div class="text-xs text-slate-400 uppercase font-medium mb-0.5">Syntynyt</div>
                                    <div class="text-sm font-mono text-slate-600">{player.birthDate}</div>
                                </div>
                            </div>
                        {:else}
                            <div class="text-center text-slate-400 py-12 bg-white rounded-xl border border-slate-200 border-dashed">
                                <p>Ei suomalaisia pelaajia tällä listalla.</p>
                            </div>
                        {/each}
                    </div>
                    
                    <div class="text-center mt-8 text-xs text-slate-400">
                        Lähde: NHL Central Scouting Midterm Rankings
                    </div>
                </div>
            {/if}
        {/if}
    </div>
</div>
