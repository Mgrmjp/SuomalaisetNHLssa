<script>
// @ts-nocheck
import { AlertCircle, TableProperties } from 'lucide-svelte'
import DivisionStandings from '$lib/components/standings/DivisionStandings.svelte'
import { CONFERENCE_NAMES, calculateWildCardTeams } from '$lib/utils/nhlStructure.js'

const {
    conferenceData = {},
    conferenceName = '',
    loading = false,
    error = null,
    _showAdvancedStats = false,
} = $props()

// Format conference name for display
const _displayName = $derived(CONFERENCE_NAMES[conferenceName] || conferenceName)

// Check if conference has data
const hasData = $derived(conferenceData && Object.keys(conferenceData).length > 0)
const divisions = $derived(hasData ? Object.entries(conferenceData) : [])
const _hasDivisions = $derived(divisions.length > 0)

// Calculate Wild Card teams for this conference
const allConferenceData = $derived(hasData ? { [conferenceName]: conferenceData } : {})
const wildCardData = $derived(hasData ? calculateWildCardTeams(allConferenceData) : {})
const _wildCardTeams = $derived(wildCardData[conferenceName] || [])

// Loading state
const isLoading = $derived(loading || !hasData)

// Error state
const _hasError = $derived(error !== null)
</script>

<div class="conference-standings">
    <!-- Conference Header -->
    {#if _hasError}
        <div class="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div class="flex items-center space-x-3">
                <AlertCircle class="w-5 h-5 text-red-600 flex-shrink-0" aria-hidden="true" />
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
        <div class="conference-loading mb-6">
            <div class="flex items-center justify-center py-8">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
        </div>
    {/if}

    <!-- Conference Title -->
    {#if hasData && !_hasError}
        <div class="conference-header mb-8">
            <h2 class="conference-title text-2xl font-bold mb-3 text-gray-900">
                {_displayName}
            </h2>
            <p class="text-gray-600">Sarjataulukko ja pudotuspelipaikat</p>
        </div>

        <!-- Divisions Grid -->
        <div class="divisions-grid grid gap-6 lg:grid-cols-2 xl:grid-cols-1 w-full overflow-hidden">
            {#each divisions as [divisionName, teams]}
                <div class="division-card-wrapper min-w-0 w-full overflow-hidden">
                    <DivisionStandings
                        {teams}
                        {divisionName}
                        showPlayoffIndicator={true}
                        wildCardTeams={_wildCardTeams}
                        {_showAdvancedStats}
                    />
                </div>
            {/each}
        </div>

        <!-- Conference Legend -->
        <div class="standings-legend mt-8 p-4 bg-gray-50 border border-gray-200 rounded-lg">
            <h3 class="text-sm font-semibold text-gray-900 mb-3">Selitteet</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm text-gray-700">
                <div class="flex items-center space-x-2">
                    <span class="w-2 h-2 bg-gray-800 rounded-full"></span>
                    <span>Divisioonan johtaja (pudotuspelipaikka)</span>
                </div>
                <div class="flex items-center space-x-2">
                    <span class="w-2 h-2 bg-blue-500 rounded-full"></span>
                    <span>Wild Card (pudotuspelipaikka)</span>
                </div>
                <div class="flex items-center space-x-2">
                    <span>O</span>
                    <span>V</span>
                    <span>H</span>
                    <span>JA</span>
                    <span class="text-gray-500">Ottelut • Voitot • Häviöt • Jatkoaika-häviöt</span>
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
    {:else if !isLoading && !_hasError}
        <!-- Empty State -->
        <div class="text-center py-12">
            <TableProperties class="mx-auto h-12 w-12 text-gray-400 mb-4" aria-hidden="true" />
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
