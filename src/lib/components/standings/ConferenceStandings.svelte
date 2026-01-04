<script>
// biome-ignore lint/correctness/noUnusedImports: used in template
import DivisionStandings from '$lib/components/standings/DivisionStandings.svelte'
import { CONFERENCE_NAMES, calculateWildCardTeams } from '$lib/utils/nhlStructure.js'

const {
    conferenceData = {},
    conferenceName = '',
    loading = false,
    error = null,
    showAdvancedStats = false,
} = $props()

// Format conference name for display
const displayName = $derived(CONFERENCE_NAMES[conferenceName] || conferenceName)

// Check if conference has data
const hasData = $derived(conferenceData && Object.keys(conferenceData).length > 0)
const divisions = $derived(hasData ? Object.entries(conferenceData) : [])
const hasDivisions = $derived(divisions.length > 0)

// Calculate Wild Card teams for this conference
const allConferenceData = $derived(hasData ? { [conferenceName]: conferenceData } : {})
const wildCardData = $derived(hasData ? calculateWildCardTeams(allConferenceData) : {})
const wildCardTeams = $derived(wildCardData[conferenceName] || [])

// Loading state
const isLoading = $derived(loading || !hasData)

// Error state
// biome-ignore lint/correctness/noUnusedVariables: used in template
const hasError = $derived(error !== null)

// Debug logging
$effect(() => {
    console.log('🔍 ConferenceStandings:', {
        conferenceName,
        hasData,
        isLoading,
        loading,
        divisionsCount: divisions.length,
        conferenceDataKeys: Object.keys(conferenceData || {}).length,
    })
})
</script>

<div class="conference-standings">
    <!-- Conference Header -->
    {#if hasError}
        <div class="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div class="flex items-center space-x-3">
                <svg
                    class="w-5 h-5 text-red-600 flex-shrink-0"
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                >
                    <circle cx="12" cy="12" r="10" />
                    <line x1="12" y1="8" x2="12" y2="12" />
                    <line x1="12" y1="16" x2="12.01" y2="16" />
                </svg>
                <div>
                    <h3 class="text-sm font-medium text-red-800">
                        Virhe ladattaessa sarjataulukkoa
                    </h3>
                    <p class="text-xs text-red-700 mt-1">
                        {error}
                    </p>
                </div>
            </div>
        </div>
    {:else if isLoading}
        <div class="mb-6">
            <div class="flex items-center justify-center py-8">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
        </div>
    {/if}

    <!-- Conference Title -->
    {#if hasData && !hasError}
        <div class="mb-8">
            <h2 class="conference-title text-2xl font-bold mb-3 text-gray-900">
                {displayName}
            </h2>
            <p class="text-gray-600">Sarjataulukko ja pudotuspelipaikat</p>
        </div>

        <!-- Divisions Grid -->
        <div class="grid gap-6 lg:grid-cols-2 xl:grid-cols-1 w-full overflow-hidden">
            {#each divisions as [divisionName, teams]}
                <div class="min-w-0 w-full overflow-hidden">
                    <DivisionStandings
                        {teams}
                        {divisionName}
                        showPlayoffIndicator={true}
                        {wildCardTeams}
                        {showAdvancedStats}
                    />
                </div>
            {/each}
        </div>

        <!-- Conference Legend -->
        <div class="mt-8 p-4 bg-gray-50 border border-gray-200 rounded-lg">
            <h3 class="text-sm font-semibold text-gray-900 mb-3">Selitteet</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm text-gray-700">
                <div class="flex items-center space-x-2">
                    <span class="w-2 h-2 bg-gray-800 rounded-full"></span>
                    <span>Pudotuspelipaikka</span>
                </div>
                <div class="flex items-center space-x-2">
                    <span>O</span>
                    <span>V</span>
                    <span>H</span>
                    <span>JA</span>
                    <span class="text-gray-500">Ottelut • Voitot • Häviöt • Jälkieisa-häviöt</span>
                </div>
                <div class="flex items-center space-x-2">
                    <span>P</span>
                    <span class="text-gray-500">Pisteet (pisteprosentti)</span>
                </div>
                <div class="flex items-center space-x-2">
                    <span>Sarja</span>
                    <span class="text-gray-500">Tulossarja (V10 = Viimeiset 10)</span>
                </div>
            </div>
        </div>
    {:else if !isLoading && !hasError}
        <!-- Empty State -->
        <div class="text-center py-12">
            <svg
                class="mx-auto h-12 w-12 text-gray-400 mb-4"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
            >
                <path d="M9 9h6v6h-6z" />
                <path d="M3 3h18v18H3z" />
                <path d="M3 9h18" />
                <path d="M9 3v18" />
            </svg>
            <h3 class="text-lg font-medium text-gray-900 mb-2">Ei sarjataulukkoa saatavilla</h3>
            <p class="text-gray-600 max-w-md mx-auto">
                Sarjataulukko ladataan hetken kuluttua, kun ottelutiedot ovat saatavilla.
            </p>
        </div>
    {/if}
</div>

<style>
    .conference-standings {
        max-width: 100%;
        margin: 0 auto;
    }

    .conference-title {
        color: #1e40af;
        font-weight: 700;
    }

    .grid {
        display: grid;
        gap: 1rem;
    }
</style>
