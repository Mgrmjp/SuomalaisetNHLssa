<script>
// @ts-nocheck
import DivisionStandings from './DivisionStandings.svelte'

const {
    conferenceData = {},
    conferenceName = '',
    wildCardTeams = [],
    showAdvancedStats = false,
} = $props()
</script>

<div class="conference-standings">
    {#each Object.entries(conferenceData) as [divisionName, teams]}
        <DivisionStandings {teams} {divisionName} {wildCardTeams} {showAdvancedStats} />
    {/each}
    <div class="standings-legend view-description">
        <span><i class="playoff-dot"></i> Divisioonan kolme parasta</span>
        <span><i class="playoff-dot playoff-dot--wildcard"></i> Wild Card</span>
        <p>Merkinnät kuvaavat tämänhetkisiä pudotuspelisijoja, eivät varmistettuja paikkoja. O = ottelut, V = voitot, H = häviöt, JA = jatkoaika- ja voittolaukaustappiot, P = pisteet, P% = pisteprosentti, V10 = viimeiset 10 ottelua.</p>
    </div>
</div>

<style>
    .conference-standings { display: grid; gap: var(--space-6); min-width: 0; }
    .standings-legend { display: flex; flex-wrap: wrap; gap: var(--space-3); }
    .standings-legend span { display: inline-flex; align-items: center; gap: var(--space-2); }
    .standings-legend p { flex-basis: 100%; margin: 0; }
</style>
