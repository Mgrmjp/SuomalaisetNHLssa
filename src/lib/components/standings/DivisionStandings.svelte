<script>
// @ts-nocheck

import Card from '$lib/components/ui/Card.svelte'
import DataTable from '$lib/components/ui/DataTable.svelte'
import { DIVISION_NAMES } from '$lib/utils/nhlStructure.js'
import TeamStandingRow from './TeamStandingRow.svelte'

const { teams = [], divisionName = '', wildCardTeams = [], showAdvancedStats = false } = $props()
const headers = $derived([
    'Sija',
    'Joukkue',
    'O',
    'V',
    'H',
    'JA',
    'P',
    'P%',
    'Sarja',
    'V10',
    ...(showAdvancedStats ? ['TM', 'VM', '+/−', 'TM/O', 'VM/O'] : []),
])
</script>

<Card padding="none">
    <div class="table-heading"><h3 class="section-title">{DIVISION_NAMES[divisionName] || divisionName}</h3></div>

        <DataTable caption={`${DIVISION_NAMES[divisionName]} – NHL-sarjataulukko`} class="standings-table">
            <thead><tr>{#each headers as header, index}<th scope="col" class:team-column={index === 1} class:rank-column={index === 0}>{header}</th>{/each}</tr></thead>
            <tbody>{#each teams as team (team.team)}<TeamStandingRow teamData={team} isWildCard={wildCardTeams.includes(team.team)} {showAdvancedStats} />{/each}</tbody>
        </DataTable>

</Card>

<style>
    .table-heading { padding: var(--space-4) var(--space-5); border-bottom: var(--card-border); }
    .table-heading h3 { margin: 0; }
    :global(.standings-table) :global(.rank-column) { width: 3rem; min-width: 3rem; position: sticky; left: 0; z-index: 2; background: var(--color-table-head); }
    :global(.standings-table) :global(.team-column) { position: sticky; left: 3rem; z-index: 2; text-align: left; background: var(--color-table-head); }
</style>
