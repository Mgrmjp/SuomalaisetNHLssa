<script>
import { onMount } from 'svelte'
import { fade } from 'svelte/transition'
import { loadProspects, prospects, draftRankings, prospectsLoading } from '$lib/stores/gameData'
import { base } from '$app/paths'


// Filter state
let activeFilter = $state('all') // 'all' | 'prospects' | 'draft2026'

// Sort options for prospects
let sortBy = $state('points') // 'points', 'goals', 'assists', 'league'
let sortDirection = $state('desc')

// Draft ranking source selection
let selectedRankingSlug = $state('nhl-central')
const selectedRankingSource = $derived($draftRankings.sources?.find(s => s.slug === selectedRankingSlug) || $draftRankings.sources?.[0])

onMount(() => {
    loadProspects()
})

// Filter active prospects based on season data and age
// A prospect is considered active if they:
// 1. Are under 35 years old
// 2. Are NOT established NHL regulars (20+ NHL games this season)
const ACTIVE_AGE_CUTOFF = 35
const NHL_REGULAR_GP_THRESHOLD = 20 // Players with 20+ NHL games are considered regulars, not prospects

// Track NHL regulars (loaded from stats)
let _nhlRegularIds = $state(new Set())

// Load NHL stats to identify regulars
$effect(() => {
    if ($prospects.length > 0) {
        fetch(`${base}/data/player-stats/skaters-20252026.json`)
            .then(r => r.ok ? r.json() : [])
            .then(skaters => {
                const regulars = new Set()
                for (const s of skaters) {
                    if (s.gamesPlayed >= NHL_REGULAR_GP_THRESHOLD) {
                        regulars.add(s.playerId)
                    }
                }
                // Also check goalies (lower threshold)
                return fetch(`${base}/data/player-stats/goalies-20252026.json`)
                    .then(r => r.ok ? r.json() : [])
                    .then(goalies => {
                        for (const g of goalies) {
                            if (g.gamesPlayed >= 10) { // Goalies: 10+ games = regular
                                regulars.add(g.playerId)
                            }
                        }
                        _nhlRegularIds = regulars
                    })
            })
            .catch(() => {
                // Silently ignore - will just show all prospects
            })
    }
})

const activeProspects = $derived($prospects.filter(p => {
    // Check age
    let age = null
    if (p.birthDate) {
        age = new Date().getFullYear() - new Date(p.birthDate).getFullYear()
    }
    const ageOk = age === null || age < ACTIVE_AGE_CUTOFF
    
    // Skip if NHL regular (established player, not a prospect)
    const playerId = parseInt(p.id, 10)
    if (_nhlRegularIds.has(playerId)) {
        return false
    }
    
    return ageOk
}))

// Derived prospects
// Combine all prospects: drafted prospects + draft rankings
const allPlayers = $derived(() => {
    const players = []
    
    // Add drafted prospects with stats
    for (const p of activeProspects) {
        players.push({
            ...p,
            type: 'prospect',
            sortKey: p.stats?.points || 0
        })
    }
    
    // Add 2026 draft rankings from selected source
    if (selectedRankingSource) {
        let draftPlayers = []
        if (selectedRankingSource.slug === 'nhl-central') {
            draftPlayers = [
                ...(selectedRankingSource.categories?.north_american || []),
                ...(selectedRankingSource.categories?.international || [])
            ]
        } else {
            draftPlayers = selectedRankingSource.players || []
        }

        for (const p of draftPlayers) {
            const firstName = p.firstName || p.name?.split(' ')[0] || ''
            const lastName = p.lastName || (p.name?.includes(' ') ? p.name.split(' ').slice(1).join(' ') : p.name) || ''
            const rank = p.midtermRank || p.rank
            
            players.push({
                id: `draft2026-${selectedRankingSource.slug}-${rank}`,
                name: p.name || `${firstName} ${lastName}`,
                position: p.positionCode || p.position,
                birthDate: p.birthDate,
                birthCity: p.birthCity,
                nhlRights: '2026',
                league: p.lastAmateurLeague?.replace('FINLAND-', '')?.replace('H-EAST', 'NCAA') || p.league?.replace('FINLAND-', '') || 'Jr',
                currentTeam: p.lastAmateurClub || p.team,
                draftRank: rank,
                height: p.heightInInches ? Math.round(p.heightInInches * 2.54) : (typeof p.height === 'number' ? p.height : null),
                weight: p.weightInPounds ? Math.round(p.weightInPounds * 0.453592) : (typeof p.weight === 'number' ? p.weight : null),
                headshot: p.playerId ? `https://assets.nhle.com/mugs/nhl/20262027/2026/${p.playerId}.png` : `https://assets.nhle.com/mugs/nhl/20262027/2026/${rank}.png`,
                stats: { gp: 0, goals: 0, assists: 0, points: 0, savePct: 0, gaa: 0, shutouts: 0 },
                type: 'draft2026',
                sortKey: 0
            })
        }
    }
    
    return players
})

// Filter players
const filteredPlayers = $derived(() => {
    const all = allPlayers()
    if (activeFilter === 'prospects') return all.filter(p => p.type === 'prospect')
    if (activeFilter === 'draft2026') return all.filter(p => p.type === 'draft2026')
    return all
})

// Separate goalies and skaters
const goalies = $derived(filteredPlayers().filter(p => p.position === 'G'))
const skaters = $derived(filteredPlayers().filter(p => p.position !== 'G'))

// Sort options for goalies
let goalieSortBy = $state('savePct') // 'savePct', 'gaa', 'gp'
let goalieSortDirection = $state('desc')

// Sorted skaters (existing sort logic)
const sortedProspects = $derived([...skaters].sort((a, b) => {
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
}))

// Sorted goalies (goalie-specific sort logic)
const sortedGoalies = $derived([...goalies].sort((a, b) => {
    if (goalieSortBy === 'savePct') {
        const valA = a.stats?.savePct || 0
        const valB = b.stats?.savePct || 0
        return goalieSortDirection === 'asc' ? valA - valB : valB - valA
    }
    if (goalieSortBy === 'gaa') {
        // GAA: lower is better, so reverse the sort
        const valA = a.stats?.gaa || 99
        const valB = b.stats?.gaa || 99
        return goalieSortDirection === 'asc' ? valA - valB : valB - valA
    }
    const valA = a.stats?.[goalieSortBy] || 0
    const valB = b.stats?.[goalieSortBy] || 0
    return goalieSortDirection === 'asc' ? valA - valB : valB - valA
}))

function _setSort(field) {
    if (sortBy === field) {
        sortDirection = sortDirection === 'asc' ? 'desc' : 'asc'
    } else {
        sortBy = field
        sortDirection = field === 'age' ? 'asc' : 'desc'
    }
}

function _setGoalieSort(field) {
    if (goalieSortBy === field) {
        goalieSortDirection = goalieSortDirection === 'asc' ? 'desc' : 'asc'
    } else {
        goalieSortBy = field
        // For GAA, lower is better, so start with asc (best first)
        goalieSortDirection = field === 'gaa' ? 'asc' : 'desc'
    }
}

function getSortIcon(field) {
    if (sortBy !== field) return ''
    return sortDirection === 'asc' ? '↑' : '↓'
}

function getGoalieSortIcon(field) {
    if (goalieSortBy !== field) return ''
    return goalieSortDirection === 'asc' ? '↑' : '↓'
}
</script>

<svelte:head>
    <title>Suomalaiset NHL-lupaukset - Varausprospectit ja tulevat tähdet</title>
    <meta name="description" content="Seuraa suomalaisten NHL-varausten ja tulevien huippujen otteita maailmalla." />
    <meta property="og:title" content="Suomalaiset NHL-lupaukset" />
    <meta property="og:description" content="Seuraa suomalaisten NHL-varausten ja tulevien huippujen otteita maailmalla." />
    <meta property="og:url" content="https://suomalaisetnhlssa.fi/lupaukset" />
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

            <!-- Filter Buttons -->
            <div class="flex justify-center gap-2 flex-wrap">
                <button 
                    class="px-4 py-2 rounded-lg text-sm font-semibold transition-all {activeFilter === 'all' ? 'bg-blue-600 text-white shadow-md' : 'bg-white text-slate-600 hover:text-slate-900 hover:bg-slate-50 border border-slate-200'}"
                    onclick={() => activeFilter = 'all'}
                >
                    Kaikki ({allPlayers().length})
                </button>
                <button 
                    class="px-4 py-2 rounded-lg text-sm font-semibold transition-all {activeFilter === 'prospects' ? 'bg-blue-600 text-white shadow-md' : 'bg-white text-slate-600 hover:text-slate-900 hover:bg-slate-50 border border-slate-200'}"
                    onclick={() => activeFilter = 'prospects'}
                >
                    NHL-varaukset
                </button>
                <button 
                    class="px-4 py-2 rounded-lg text-sm font-semibold transition-all {activeFilter === 'draft2026' ? 'bg-blue-600 text-white shadow-md' : 'bg-white text-slate-600 hover:text-slate-900 hover:bg-slate-50 border border-slate-200'}"
                    onclick={() => activeFilter = 'draft2026'}
                >
                    Draft 2026
                </button>
            </div>

            <!-- Ranking Source Selector (only visible when Draft 2026 is active) -->
            {#if activeFilter === 'draft2026' || activeFilter === 'all'}
                <div class="mt-8 max-w-xs mx-auto">
                    <label for="ranking-source" class="block text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">Rankings-lähde</label>
                    <select 
                        id="ranking-source"
                        bind:value={selectedRankingSlug}
                        class="block w-full bg-white border border-slate-200 text-slate-700 py-2 px-3 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all shadow-sm"
                    >
                        {#each $draftRankings.sources || [] as source}
                            <option value={source.slug}>{source.name}</option>
                        {/each}
                    </select>
                </div>
            {/if}
        </div>

        {#if $prospectsLoading}
            <div class="flex justify-center items-center h-64">
                <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
            </div>
        {:else}
            <div in:fade={{ duration: 300 }}>
                    <!-- Controls -->
                    <div class="flex justify-center gap-3 mb-8 flex-wrap">
                        <button 
                            class="px-4 py-2 rounded-full text-sm font-medium transition-all shadow-sm
                            {sortBy === 'points' ? 'bg-blue-600 text-white' : 'bg-white text-slate-700 border border-slate-200 hover:border-blue-300 hover:bg-slate-50'}"
                            onclick={() => _setSort('points')}
                        >
                            Pisteet {getSortIcon('points')}
                        </button>
                        <button 
                            class="px-4 py-2 rounded-full text-sm font-medium transition-all shadow-sm
                            {sortBy === 'goals' ? 'bg-blue-600 text-white' : 'bg-white text-slate-700 border border-slate-200 hover:border-blue-300 hover:bg-slate-50'}"
                            onclick={() => _setSort('goals')}
                        >
                            Maalit {getSortIcon('goals')}
                        </button>
                        <button 
                            class="px-4 py-2 rounded-full text-sm font-medium transition-all shadow-sm
                            {sortBy === 'league' ? 'bg-blue-600 text-white' : 'bg-white text-slate-700 border border-slate-200 hover:border-blue-300 hover:bg-slate-50'}"
                            onclick={() => _setSort('league')}
                        >
                            Liiga {getSortIcon('league')}
                        </button>
                        <button 
                            class="px-4 py-2 rounded-full text-sm font-medium transition-all shadow-sm
                            {sortBy === 'age' ? 'bg-blue-600 text-white' : 'bg-white text-slate-700 border border-slate-200 hover:border-blue-300 hover:bg-slate-50'}"
                            onclick={() => {
                                sortBy = 'age';
                                sortDirection = 'asc';
                            }}
                        >
                            Ikä {getSortIcon('age')}
                        </button>
                    </div>

                    <!-- Active prospects count -->
                    <div class="text-center mb-6">
                        <span class="text-sm text-slate-500">
                            Näytetään {sortedProspects.length} kenttäpelaajaa ja {sortedGoalies.length} maalivahtia
                        </span>
                    </div>

                    <!-- Skaters Grid -->
                    {#if sortedProspects.length === 0}
                        <div class="text-center text-slate-400 mt-12">
                            <p>Ei löytynyt lupauksia.</p>
                        </div>
                    {:else}
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                            {#each sortedProspects as player, index (`${player.id}-${index}`)}
                                <div 
                                    class="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden hover:shadow-md hover:border-blue-200 transition-all group p-4"
                                >
                                    <div class="flex items-center gap-4 mb-4">
                                        <div class="relative w-20 h-20 flex-shrink-0">
                                            <div class="w-full h-full rounded-full border-2 border-slate-100 overflow-hidden bg-slate-50 relative z-10">
                                                <img 
                                                    src={player.headshot} 
                                                    alt={player.name}
                                                    class="w-full h-full object-cover object-top"
                                                    loading="lazy"
                                                    onerror={(e) => e.target.style.display = 'none'} 
                                                />
                                            </div>
                                            <div class="absolute -bottom-1 -right-1 z-20 bg-white rounded-full p-1 shadow-sm border border-slate-100">
                                                <div class="w-7 h-7 flex items-center justify-center">
                                                    {#if player.type === 'draft2026'}
                                                        <span class="text-[10px] font-black text-amber-600">#{player.draftRank}</span>
                                                    {:else}
                                                        <span class="text-[10px] font-black text-slate-800">{player.nhlRights}</span>
                                                    {/if}
                                                </div>
                                            </div>
                                        </div>
                                        
                                        <div class="min-w-0">
                                            <div class="flex items-center gap-2 mb-1">
                                                <div class="inline-block bg-blue-600 text-white text-[10px] font-bold px-2 py-0.5 rounded-full">
                                                    {player.league}
                                                </div>
                                                {#if player.type === 'draft2026'}
                                                    <div class="inline-block bg-amber-500 text-white text-[10px] font-bold px-2 py-0.5 rounded-full">
                                                        Draft 2026
                                                    </div>
                                                {/if}
                                            </div>
                                            <h3 class="text-base font-bold text-slate-900 truncate">{player.name}</h3>
                                            <div class="flex items-center gap-2 text-xs text-slate-500">
                                                <span>{player.currentTeam}</span>
                                                {#if player.birthDate}
                                                    <span class="text-slate-300">•</span>
                                                    <span>{new Date().getFullYear() - new Date(player.birthDate).getFullYear()} vuotta</span>
                                                {/if}
                                            </div>
                                        </div>
                                    </div>

                                    {#if player.type === 'draft2026'}
                                        <!-- Draft prospect stats (height/weight instead of games) -->
                                        <div class="grid grid-cols-4 gap-2 bg-amber-50/50 rounded-lg p-3 text-center border border-amber-100/50">
                                            <div>
                                                <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Pituus</div>
                                                <div class="font-mono font-bold text-slate-700">{player.height || '-'}</div>
                                            </div>
                                            <div>
                                                <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Paino</div>
                                                <div class="font-mono font-bold text-slate-700">{player.weight || '-'}</div>
                                            </div>
                                            <div>
                                                <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Rank</div>
                                                <div class="font-mono font-bold text-amber-600">#{player.draftRank}</div>
                                            </div>
                                            <div>
                                                <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">P</div>
                                                <div class="font-mono font-bold text-slate-900">{player.position}</div>
                                            </div>
                                        </div>
                                    {:else}
                                        <!-- Regular prospect stats -->
                                        <div class="grid grid-cols-4 gap-2 bg-slate-50/50 rounded-lg p-3 text-center border border-slate-100/50">
                                            <div>
                                                <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">GP</div>
                                                <div class="font-mono font-bold text-slate-700">{player.stats?.gp || 0}</div>
                                            </div>
                                            <div>
                                                <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">G</div>
                                                <div class="font-mono font-bold text-emerald-600">{player.stats?.goals || 0}</div>
                                            </div>
                                            <div>
                                                <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">A</div>
                                                <div class="font-mono font-bold text-amber-600">{player.stats?.assists || 0}</div>
                                            </div>
                                            <div>
                                                <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">P</div>
                                                <div class="font-mono font-bold text-slate-900">{player.stats?.points || 0}</div>
                                            </div>
                                        </div>
                                    {/if}
                                </div>
                            {/each}
                        </div>
                    {/if}

                    <!-- Goalies Section -->
                    {#if sortedGoalies.length > 0}
                        <div class="mt-12">
                            <h2 class="text-2xl font-bold text-slate-900 mb-6 text-center">Maalivahdit</h2>
                            
                            <!-- Goalie Sort Controls -->
                            <div class="flex justify-center gap-3 mb-6 flex-wrap">
                                <button 
                                    class="px-4 py-2 rounded-full text-sm font-medium transition-all shadow-sm
                                    {goalieSortBy === 'savePct' ? 'bg-emerald-600 text-white' : 'bg-white text-slate-700 border border-slate-200 hover:border-emerald-300 hover:bg-slate-50'}"
                                    onclick={() => _setGoalieSort('savePct')}
                                >
                                    Torjunta-% {getGoalieSortIcon('savePct')}
                                </button>
                                <button 
                                    class="px-4 py-2 rounded-full text-sm font-medium transition-all shadow-sm
                                    {goalieSortBy === 'gaa' ? 'bg-emerald-600 text-white' : 'bg-white text-slate-700 border border-slate-200 hover:border-emerald-300 hover:bg-slate-50'}"
                                    onclick={() => _setGoalieSort('gaa')}
                                >
                                    Päästettyjen keskiarvo {getGoalieSortIcon('gaa')}
                                </button>
                                <button 
                                    class="px-4 py-2 rounded-full text-sm font-medium transition-all shadow-sm
                                    {goalieSortBy === 'gp' ? 'bg-emerald-600 text-white' : 'bg-white text-slate-700 border border-slate-200 hover:border-emerald-300 hover:bg-slate-50'}"
                                    onclick={() => _setGoalieSort('gp')}
                                >
                                    Ottelut {getGoalieSortIcon('gp')}
                                </button>
                            </div>

                            <!-- Goalies Grid -->
                            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                                {#each sortedGoalies as goalie, index (`${goalie.id}-${index}`)}
                                    <div 
                                        class="bg-white rounded-xl shadow-sm border border-emerald-200 overflow-hidden hover:shadow-md hover:border-emerald-300 transition-all group p-4"
                                    >
                                        <div class="flex items-center gap-4 mb-4">
                                            <div class="relative w-20 h-20 flex-shrink-0">
                                                <div class="w-full h-full rounded-full border-2 border-emerald-100 overflow-hidden bg-slate-50 relative z-10">
                                                    <img 
                                                        src={goalie.headshot} 
                                                        alt={goalie.name}
                                                        class="w-full h-full object-cover object-top"
                                                        loading="lazy"
                                                        onerror={(e) => e.target.style.display = 'none'} 
                                                    />
                                                </div>
                                                <div class="absolute -bottom-1 -right-1 z-20 bg-white rounded-full p-1 shadow-sm border border-emerald-100">
                                                    <div class="w-7 h-7 flex items-center justify-center">
                                                        {#if goalie.type === 'draft2026'}
                                                            <span class="text-[10px] font-black text-amber-600">#{goalie.draftRank}</span>
                                                        {:else}
                                                            <span class="text-[10px] font-black text-slate-800">{goalie.nhlRights}</span>
                                                        {/if}
                                                    </div>
                                                </div>
                                            </div>
                                            
                                            <div class="min-w-0">
                                                <div class="flex items-center gap-2 mb-1">
                                                    <div class="inline-block bg-emerald-600 text-white text-[10px] font-bold px-2 py-0.5 rounded-full">
                                                        {goalie.league}
                                                    </div>
                                                    {#if goalie.type === 'draft2026'}
                                                        <div class="inline-block bg-amber-500 text-white text-[10px] font-bold px-2 py-0.5 rounded-full">
                                                            Draft 2026
                                                        </div>
                                                    {/if}
                                                </div>
                                                <h3 class="text-base font-bold text-slate-900 truncate">{goalie.name}</h3>
                                                <div class="flex items-center gap-2 text-xs text-slate-500">
                                                    <span>{goalie.currentTeam}</span>
                                                    {#if goalie.birthDate}
                                                        <span class="text-slate-300">•</span>
                                                        <span>{new Date().getFullYear() - new Date(goalie.birthDate).getFullYear()} vuotta</span>
                                                    {/if}
                                                </div>
                                            </div>
                                        </div>

                                        {#if goalie.type === 'draft2026'}
                                            <!-- Draft prospect stats -->
                                            <div class="grid grid-cols-4 gap-2 bg-amber-50/50 rounded-lg p-3 text-center border border-amber-100/50">
                                                <div>
                                                    <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Pituus</div>
                                                    <div class="font-mono font-bold text-slate-700">{goalie.height || '-'}</div>
                                                </div>
                                                <div>
                                                    <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Paino</div>
                                                    <div class="font-mono font-bold text-slate-700">{goalie.weight || '-'}</div>
                                                </div>
                                                <div>
                                                    <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Rank</div>
                                                    <div class="font-mono font-bold text-amber-600">#{goalie.draftRank}</div>
                                                </div>
                                                <div>
                                                    <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">P</div>
                                                    <div class="font-mono font-bold text-slate-900">{goalie.position}</div>
                                                </div>
                                            </div>
                                        {:else}
                                            <!-- Regular goalie stats -->
                                            <div class="grid grid-cols-4 gap-2 bg-emerald-50/50 rounded-lg p-3 text-center border border-emerald-100/50">
                                                <div>
                                                    <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">GP</div>
                                                    <div class="font-mono font-bold text-slate-700">{goalie.stats?.gp || 0}</div>
                                                </div>
                                                <div>
                                                    <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">SV%</div>
                                                    <div class="font-mono font-bold text-emerald-600">{(goalie.stats?.savePct || 0).toFixed(3)}</div>
                                                </div>
                                                <div>
                                                    <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">GAA</div>
                                                    <div class="font-mono font-bold text-amber-600">{(goalie.stats?.gaa || 0).toFixed(2)}</div>
                                                </div>
                                                <div>
                                                    <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">SO</div>
                                                    <div class="font-mono font-bold text-slate-900">{goalie.stats?.shutouts || 0}</div>
                                                </div>
                                            </div>
                                        {/if}
                                    </div>
                                {/each}
                            </div>
                        </div>
                    {/if}
                </div>
            {/if}

            <!-- Related Links -->
            <div class="mt-12 grid grid-cols-1 md:grid-cols-2 gap-4">
                <a 
                    href="{base}/scouting"
                    class="flex items-center gap-4 bg-white rounded-xl border border-slate-200 p-6 hover:shadow-md hover:border-blue-200 transition-all group"
                >
                    <div class="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                        <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                        </svg>
                    </div>
                    <div class="flex-1">
                        <h3 class="font-semibold text-slate-900 group-hover:text-blue-600 transition-colors">Scouting Reports</h3>
                        <p class="text-sm text-slate-500">Yksityiskohtaiset analyysit lupaavimmista pelaajista</p>
                    </div>
                    <svg class="w-5 h-5 text-slate-400 group-hover:text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                    </svg>
                </a>
                
                <a 
                    href="{base}/drafts"
                    class="flex items-center gap-4 bg-white rounded-xl border border-slate-200 p-6 hover:shadow-md hover:border-blue-200 transition-all group"
                >
                    <div class="w-12 h-12 rounded-full bg-emerald-100 flex items-center justify-center flex-shrink-0">
                        <svg class="w-6 h-6 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 002 2h2a2 2 0 002-2z"/>
                        </svg>
                    </div>
                    <div class="flex-1">
                        <h3 class="font-semibold text-slate-900 group-hover:text-blue-600 transition-colors">Draft-historia</h3>
                        <p class="text-sm text-slate-500">Suomalaisten varausten historia ja tilastot</p>
                    </div>
                    <svg class="w-5 h-5 text-slate-400 group-hover:text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                    </svg>
                </a>
            </div>

            <!-- Data Sources -->
            <div class="mt-12 pt-8 border-t border-slate-200">
                <div class="text-center">
                    <h3 class="text-sm font-semibold text-slate-900 mb-3">Tietolähteet</h3>
                    <div class="flex flex-wrap justify-center gap-x-6 gap-y-2 text-xs text-slate-500">
                        <span>• NHL API: Pelaajatiedot & tilastot</span>
                        <span>• NHL Central Scouting: Draft 2026 ranking</span>
                        <span>• EliteProspects: Nuorten sarjatiedot</span>
                        <span>• Liiga, SHL, AHL: Kausitilastot</span>
                    </div>
                    <p class="text-xs text-slate-400 mt-4">
                        Päivitetty: {new Date().toLocaleDateString('fi-FI')} • 
                        Näytetään {activeProspects.length + (activeFilter === 'all' ? ($draftRankings.north_american_skaters?.length || 0) + ($draftRankings.international_skaters?.length || 0) : 0)} lupausta
                    </p>
                </div>
            </div>
        </div>
    </div>
