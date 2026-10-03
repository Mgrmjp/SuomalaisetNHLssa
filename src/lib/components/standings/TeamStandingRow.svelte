<script>
// @ts-nocheck
import TeamLogo from '$lib/components/ui/TeamLogo.svelte'

const { teamData, isWildCard = false, showAdvancedStats = false } = $props()
const eligible = $derived(teamData.gamesPlayed > 0 && (teamData.divisionRank <= 3 || isWildCard))
const pct = $derived(
    teamData.pointsPercentage === null
        ? '–'
        : `${(teamData.pointsPercentage * 100).toLocaleString('fi-FI', { maximumFractionDigits: 1 })}%`
)
const perGame = (goals) =>
    teamData.gamesPlayed
        ? (goals / teamData.gamesPlayed).toLocaleString('fi-FI', {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
          })
        : '–'
const streak = $derived(teamData.streak.replace(/^W/, 'V').replace(/^L/, 'H').replace(/^OT/, 'JA'))
</script>

<tr class:standings-row--wildcard={isWildCard && eligible}>
    <td class="rank-cell">
        <span>{teamData.divisionRank}</span>
        {#if eligible}<i class="playoff-dot" class:playoff-dot--wildcard={isWildCard} title={isWildCard ? 'Tämänhetkinen Wild Card -sija' : 'Divisioonan kolmen parhaan joukossa'}></i>{/if}
    </td>
    <th scope="row" class="team-cell">
        <div class="team-identity">
            <TeamLogo team={teamData.team} size="28" />
            <span class="team-full-name">{teamData.teamName}</span><span class="team-abbrev">{teamData.team}</span>
            {#if teamData.clinchIndicator}<span class="clinch-badge" title="NHL:n varmistettu pudotuspelimerkintä">{teamData.clinchIndicator}</span>{/if}
        </div>
    </th>
    <td>{teamData.gamesPlayed}</td><td>{teamData.wins}</td><td>{teamData.losses}</td><td>{teamData.overtimeLosses}</td>
    <td class="points-cell">{teamData.points}</td><td>{pct}</td><td>{streak || '–'}</td><td>{teamData.last10 || '–'}</td>
    {#if showAdvancedStats}
        <td>{teamData.goalsFor}</td><td>{teamData.goalsAgainst}</td>
        <td>{teamData.goalDifferential > 0 ? '+' : ''}{teamData.goalDifferential}</td>
        <td>{perGame(teamData.goalsFor)}</td><td>{perGame(teamData.goalsAgainst)}</td>
    {/if}
</tr>

<style>
    tr { --row-bg: var(--color-panel); background: var(--row-bg); }
    tr:hover { --row-bg: var(--color-table-hover); }
    .standings-row--wildcard { --row-bg: var(--accent-ice); }
    .rank-cell { position: sticky; left: 0; z-index: 1; min-width: 3rem; width: 3rem; background: var(--row-bg); }
    .rank-cell span { margin-right: 0.25rem; }
    .team-cell { position: sticky; left: 3rem; z-index: 1; background: var(--row-bg); text-align: left; }
    .team-identity { display: flex; gap: var(--space-2); align-items: center; min-width: 12rem; }
    .team-abbrev { display: none; }
    .clinch-badge { font-size: 0.7rem; color: var(--color-muted); }
    @media (max-width: 640px) {
        .team-full-name { display: none; }
        .team-abbrev { display: inline; }
        .team-identity { min-width: 5.5rem; }
    }
</style>
