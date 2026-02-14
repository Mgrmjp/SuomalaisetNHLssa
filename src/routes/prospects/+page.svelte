<script>
    import { onMount } from 'svelte';
    import { prospects, draftRankings, loadProspects, prospectsLoading } from '$lib/stores/gameData';
    import { fade } from 'svelte/transition';
    
    // View state
    let activeTab = 'prospects'; // 'prospects' | 'draft'
    
    // Sort options for prospects
    let sortBy = 'points'; // 'points', 'goals', 'assists', 'league'
    let sortDirection = 'desc';
    
    // Draft view state
    let draftCategory = 'north_american_skaters'; // 'north_american_skaters' | 'international_skaters'

    onMount(() => {
        loadProspects();
    });
    
    // Derived prospects
    $: sortedProspects = [...$prospects].sort((a, b) => {
        if (sortBy === 'league') {
             return sortDirection === 'asc' 
                ? a.league.localeCompare(b.league)
                : b.league.localeCompare(a.league);
        }
        if (sortBy === 'age') {
            // Sort by birthDate. 
            // 'asc' direction: Youngest first (larger date string > smaller date string)
            // 'desc' direction: Oldest first
            if (sortDirection === 'asc') {
                return b.birthDate.localeCompare(a.birthDate);
            } else {
                return a.birthDate.localeCompare(b.birthDate);
            }
        }
        
        const valA = a.stats?.[sortBy] || 0;
        const valB = b.stats?.[sortBy] || 0;
        return sortDirection === 'asc' ? valA - valB : valB - valA;
    });

    // Derived draft rankings
    $: currentDraftList = $draftRankings[draftCategory] || [];

    function setSort(field) {
        if (sortBy === field) {
            sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            sortBy = field;
            // Default direction for stats is 'desc' (highest first)
            // Default direction for age/league can be 'asc' or 'desc'. 
            // For age, let's default to 'asc' (youngest first -> descending birthDate string, wait. Logic above: asc -> b.localeCompare(a). So asc = youngest.)
            sortDirection = field === 'age' ? 'asc' : 'desc';
        }
    }

    function getSortIcon(field) {
        if (sortBy !== field) return '';
        return sortDirection === 'asc' ? '↑' : '↓';
    }
</script>

<div class="container mx-auto px-4 py-8 text-white min-h-screen">
    <header class="mb-8 text-center">
        <h1 class="text-3xl md:text-5xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-white">
            Suomalaiset Lupaukset
        </h1>
        <p class="text-gray-400 max-w-2xl mx-auto mb-6">
            Seuraa suomalaisten NHL-varausten ja tulevien huippujen otteita maailmalla.
        </p>

        <!-- Main Tabs -->
        <div class="flex justify-center mb-8">
            <div class="bg-gray-800/50 p-1 rounded-xl inline-flex">
                <button 
                    class="px-6 py-2 rounded-lg text-sm font-bold transition-all {activeTab === 'prospects' ? 'bg-blue-600 text-white shadow-lg' : 'text-gray-400 hover:text-white'}"
                    on:click={() => activeTab = 'prospects'}
                >
                    NHL-varaukset
                </button>
                <button 
                    class="px-6 py-2 rounded-lg text-sm font-bold transition-all {activeTab === 'draft' ? 'bg-blue-600 text-white shadow-lg' : 'text-gray-400 hover:text-white'}"
                    on:click={() => activeTab = 'draft'}
                >
                    Draft 2026
                </button>
            </div>
        </div>
    </header>

    {#if $prospectsLoading}
        <div class="flex justify-center items-center h-64">
            <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
    {:else}
        {#if activeTab === 'prospects'}
            <div in:fade={{ duration: 300 }}>
                <!-- Controls -->
                <div class="flex justify-center gap-4 mb-8 flex-wrap">
                    <button 
                        class="px-4 py-2 rounded-full text-sm font-medium transition-colors 
                        {sortBy === 'points' ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-300 hover:bg-gray-700'}"
                        on:click={() => setSort('points')}
                    >
                        Pisteet {getSortIcon('points')}
                    </button>
                    <button 
                        class="px-4 py-2 rounded-full text-sm font-medium transition-colors
                        {sortBy === 'goals' ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-300 hover:bg-gray-700'}"
                        on:click={() => setSort('goals')}
                    >
                        Maalit {getSortIcon('goals')}
                    </button>
                    <button 
                        class="px-4 py-2 rounded-full text-sm font-medium transition-colors
                        {sortBy === 'league' ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-300 hover:bg-gray-700'}"
                        on:click={() => setSort('league')}
                    >
                        Liiga {getSortIcon('league')}
                    </button>
                    <button 
                        class="px-4 py-2 rounded-full text-sm font-medium transition-colors
                        {sortBy === 'age' ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-300 hover:bg-gray-700'}"
                        on:click={() => {
                            sortBy = 'age';
                            sortDirection = 'asc'; // Default to youngest first (desc birthdate means youngest, but let's handle logic in sort function)
                        }}
                    >
                        Ikä {getSortIcon('age')}
                    </button>
                </div>

                <!-- Grid -->
                {#if sortedProspects.length === 0}
                    <div class="text-center text-gray-500 mt-12">
                        <p>Ei löytynyt lupauksia.</p>
                    </div>
                {:else}
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                        {#each sortedProspects as player (player.id)}
                            <div 
                                class="bg-gray-800/50 backdrop-blur-sm rounded-xl overflow-hidden border border-gray-700 hover:border-blue-500/50 transition-all hover:shadow-lg hover:shadow-blue-500/10 group"
                            >
                                <div class="relative h-48 bg-gray-900 overflow-hidden">
                                    <div class="absolute inset-0 bg-gradient-to-t from-gray-900 via-transparent to-transparent z-10"></div>
                                    <img 
                                        src={player.headshot} 
                                        alt={player.name}
                                        class="w-full h-full object-cover object-top transform group-hover:scale-105 transition-transform duration-500"
                                        loading="lazy"
                                        on:error={(e) => e.target.style.display = 'none'} 
                                    />
                                    <div class="absolute top-2 right-2 z-20 bg-black/60 backdrop-blur rounded-full px-2 py-1 border border-gray-700 flex items-center gap-1">
                                        <span class="text-xs font-bold text-gray-300">Varaus:</span>
                                        <span class="text-xs font-bold text-white">{player.nhlRights}</span>
                                    </div>
                                </div>

                                <div class="p-4 relative">
                                    <div class="absolute -top-3 left-4 bg-blue-600 text-white text-xs font-bold px-3 py-1 rounded-full shadow-lg">
                                        {player.league}
                                    </div>
                                    <h3 class="mt-2 text-xl font-bold text-white truncate">{player.name}</h3>
                                    <p class="text-sm text-gray-400 mb-4">{player.currentTeam}</p>
                                    <div class="grid grid-cols-4 gap-2 bg-gray-900/50 rounded-lg p-2 text-center">
                                        <div>
                                            <div class="text-xs text-gray-500 uppercase">GP</div>
                                            <div class="font-mono font-bold">{player.stats?.gp || 0}</div>
                                        </div>
                                        <div>
                                            <div class="text-xs text-gray-500 uppercase">G</div>
                                            <div class="font-mono font-bold text-green-400">{player.stats?.goals || 0}</div>
                                        </div>
                                        <div>
                                            <div class="text-xs text-gray-500 uppercase">A</div>
                                            <div class="font-mono font-bold text-yellow-400">{player.stats?.assists || 0}</div>
                                        </div>
                                        <div>
                                            <div class="text-xs text-gray-500 uppercase">P</div>
                                            <div class="font-mono font-bold text-white text-lg">{player.stats?.points || 0}</div>
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
                     <div class="bg-gray-800/30 p-1 rounded-lg inline-flex">
                        <button 
                            class="px-4 py-1.5 rounded-md text-sm font-medium transition-all {draftCategory === 'international_skaters' ? 'bg-gray-700 text-white' : 'text-gray-400 hover:text-white'}"
                            on:click={() => draftCategory = 'international_skaters'}
                        >
                            Eurooppa
                        </button>
                         <button 
                            class="px-4 py-1.5 rounded-md text-sm font-medium transition-all {draftCategory === 'north_american_skaters' ? 'bg-gray-700 text-white' : 'text-gray-400 hover:text-white'}"
                            on:click={() => draftCategory = 'north_american_skaters'}
                        >
                            Pohjois-Amerikka
                        </button>
                    </div>
                </div>

                <!-- List View -->
                <div class="max-w-4xl mx-auto space-y-4">
                    {#each currentDraftList as player (player.firstName + player.lastName)}
                         <div class="bg-gray-800/40 backdrop-blur rounded-xl p-4 border border-gray-700/50 flex items-center gap-4 hover:bg-gray-800/60 transition-colors">
                            <!-- Rank Circle -->
                            <div class="flex-shrink-0 w-12 h-12 rounded-full bg-blue-900/50 border border-blue-500/30 flex items-center justify-center">
                                <span class="text-xl font-bold text-blue-400">#{player.midtermRank}</span>
                            </div>

                            <div class="flex-grow">
                                <h3 class="text-lg font-bold text-white">{player.firstName} {player.lastName}</h3>
                                <div class="flex gap-2 text-sm text-gray-400">
                                    <span>{player.positionCode}</span>
                                    <span>•</span>
                                    <span>{player.heightInInches}" / {player.weightInPounds} lbs</span>
                                    <span>•</span>
                                    <span>{player.lastAmateurClub} ({player.lastAmateurLeague})</span>
                                </div>
                            </div>
                            
                            <div class="hidden sm:block text-right">
                                <div class="text-xs text-gray-500 uppercase mb-1">Syntynyt</div>
                                <div class="text-sm font-mono text-gray-300">{player.birthDate}</div>
                            </div>
                         </div>
                    {:else}
                         <div class="text-center text-gray-500 py-12">
                            Ei suomalaisia pelaajia tällä listalla.
                         </div>
                    {/each}
                </div>
                
                 <div class="text-center mt-8 text-xs text-gray-500">
                    Lähde: NHL Central Scouting Midterm Rankings
                </div>
            </div>
        {/if}
    {/if}
</div>
