<script>
// @ts-nocheck
import DataTable from '$lib/components/ui/DataTable.svelte'
import TeamLogo from '$lib/components/ui/TeamLogo.svelte'

const { summary } = $props()
let showAllScorers = $state(false)
let showAllResults = $state(false)

const scorers = $derived(summary?.scorers || [])
const finnishResults = $derived(
    (summary?.games || []).filter((game) => game.finnishPlayers?.length)
)
const visibleScorers = $derived(showAllScorers ? scorers : scorers.slice(0, 5))
const visibleResults = $derived(showAllResults ? finnishResults : finnishResults.slice(0, 5))

const finnishDate = new Intl.DateTimeFormat('fi-FI', {
    timeZone: 'Europe/Helsinki',
    day: 'numeric',
    month: 'numeric',
})

function pointScorers(players) {
    const names = players
        .filter((player) => player.points > 0)
        .map((player) => `${player.name} ${player.goals}+${player.assists}`)
    return names.length
        ? names.join(', ')
        : `${players.length} ${players.length === 1 ? 'suomalainen' : 'suomalaista'} mukana`
}

function resultSuffix(game) {
    if (game.isSO) return 'VL'
    if (game.isOT) return 'JA'
    return ''
}
</script>

{#if summary?.completedGames > 0}
    <section class="panel panel--preseason" aria-labelledby="preseason-title">
        <div class="preseason-inner">
            <div class="panel__eyebrow rink-divider">Harjoituskausi</div>
            <div class="preseason-heading">
                <h2 id="preseason-title">Suomalaisten harjoituskausi {summary.seasonYear}–{String(summary.seasonYear + 1).slice(-2)}</h2>
                <p class="preseason-counts">
                    <span><strong>{summary.completedGames}</strong> ottelua</span>
                    <span><strong>{summary.finnishGames}</strong> ottelussa suomalaisia</span>
                </p>
            </div>

            <div class="preseason-block">
                <div class="block-heading">
                    <h3>Suomalaisten pistepörssi</h3>
                    <p>Harjoituskauden maalit ja syötöt</p>
                </div>
                {#if scorers.length}

                        <DataTable caption="Harjoituskauden suomalaisten pistepörssi" class="scorer-table" regionId="preseason-scorers">
                            <thead>
                                <tr>
                                    <th scope="col">Pelaaja</th>
                                    <th scope="col"><abbr title="Ottelut">O</abbr></th>
                                    <th scope="col"><abbr title="Maalit">M</abbr></th>
                                    <th scope="col"><abbr title="Syötöt">S</abbr></th>
                                    <th scope="col"><abbr title="Pisteet">P</abbr></th>
                                </tr>
                            </thead>
                            <tbody>
                                {#each visibleScorers as player (player.playerId)}
                                    <tr>
                                        <td>
                                            <span class="player-cell">
                                                <TeamLogo team={player.team} size="24" />
                                                <span>{player.name}</span>
                                            </span>
                                        </td>
                                        <td>{player.gamesPlayed}</td>
                                        <td>{player.goals}</td>
                                        <td>{player.assists}</td>
                                        <td class="points-cell">{player.points}</td>
                                    </tr>
                                {/each}
                            </tbody>
                        </DataTable>

                    {#if scorers.length > 5}
                        <button type="button" class="preseason-toggle" onclick={() => showAllScorers = !showAllScorers} aria-expanded={showAllScorers} aria-controls="preseason-scorers">
                            {showAllScorers ? 'Näytä vähemmän' : `Näytä kaikki ${scorers.length} pelaajaa`}
                        </button>
                    {/if}
                {:else}
                    <p class="preseason-empty">Suomalaisille ei ole merkitty pisteitä.</p>
                {/if}
            </div>

            <div class="preseason-block preseason-block--results">
                <div class="block-heading">
                    <h3>Ottelutulokset</h3>
                    <p>Ottelut, joissa pelasi suomalainen</p>
                </div>
                {#if finnishResults.length}
                    <div id="preseason-results" class="result-list">
                        {#each visibleResults as game (game.gameId)}
                            <div class="result-row">
                                <time datetime={game.startTime} class="result-date">{finnishDate.format(new Date(game.startTime))}</time>
                                <div class="result-matchup" aria-label={`${game.awayTeam} ${game.awayScore}, ${game.homeTeam} ${game.homeScore}`}>
                                    <span class="result-team"><TeamLogo team={game.awayTeam} size="24" />{game.awayTeam}</span>
                                    <strong class="result-score">{game.awayScore}–{game.homeScore}</strong>
                                    <span class="result-team"><TeamLogo team={game.homeTeam} size="24" />{game.homeTeam}</span>
                                    {#if resultSuffix(game)}<span class="result-extra">{resultSuffix(game)}</span>{/if}
                                </div>
                                <span class="result-finns">{pointScorers(game.finnishPlayers)}</span>
                            </div>
                        {/each}
                    </div>
                    {#if finnishResults.length > 5}
                        <button type="button" class="preseason-toggle" onclick={() => showAllResults = !showAllResults} aria-expanded={showAllResults} aria-controls="preseason-results">
                            {showAllResults ? 'Näytä vähemmän' : `Näytä kaikki ${finnishResults.length} tulosta`}
                        </button>
                    {/if}
                {:else}
                    <p class="preseason-empty">Suomalaisten ottelutuloksia ei vielä ole.</p>
                {/if}
            </div>
        </div>
    </section>
{/if}

<style>
    .panel--preseason {
        width: 100%;
        max-width: var(--rail-max);
        margin: 0 auto;
        border: var(--card-border);
        border-radius: var(--card-radius);
        background: var(--card-bg);
        box-shadow: none;
    }

    .preseason-inner {
        padding: var(--card-padding-y, 1.25rem) var(--card-padding-x, 1.5rem);
    }

    .panel__eyebrow {
        margin-bottom: 0.65rem;
    }

    .preseason-heading {
        display: flex;
        align-items: baseline;
        justify-content: space-between;
        gap: 0.75rem 1.5rem;
        flex-wrap: wrap;
    }

    h2,
    h3 {
        margin: 0;
        color: var(--color-ink);
        font-weight: 800;
    }

    h2 {
        font-size: 1.1rem;
        line-height: 1.3;
    }

    h3 {
        font-size: 0.95rem;
    }

    .preseason-counts {
        display: flex;
        flex-wrap: wrap;
        gap: 0.25rem 1rem;
        margin: 0;
        color: var(--color-muted);
        font-size: 0.8rem;
    }

    .preseason-counts strong {
        color: var(--color-ink);
    }

    .preseason-block {
        margin-top: 1.5rem;
    }

    .preseason-block--results {
        padding-top: 1.35rem;
        border-top: 1px solid rgba(16, 24, 40, 0.12);
    }

    .block-heading {
        display: flex;
        align-items: baseline;
        justify-content: space-between;
        gap: 0.25rem 1rem;
        flex-wrap: wrap;
        margin-bottom: 0.65rem;
    }

    .block-heading p {
        margin: 0;
        color: var(--color-muted);
        font-size: 0.79rem;
    }





    :global(.scorer-table) th:first-child,
    :global(.scorer-table) td:first-child {
        padding-left: 0;
        text-align: left;
    }





    :global(.scorer-table) tbody tr:first-child {
        background: rgba(16, 24, 40, 0.035);
    }

    .player-cell,
    .result-matchup,
    .result-team {
        display: flex;
        align-items: center;
    }

    .player-cell {
        gap: 0.55rem;
        color: var(--color-ink);
        font-weight: 700;
        white-space: nowrap;
    }

    .points-cell {
        color: var(--color-ink);
        font-weight: 800;
    }

    .result-list {
        border-top: 1px solid rgba(16, 24, 40, 0.1);
    }

    .result-row {
        display: grid;
        grid-template-columns: 3.25rem 15rem minmax(0, 1fr);
        align-items: center;
        gap: 0.5rem 0.75rem;
        padding: 0.7rem 0;
        border-bottom: 1px solid rgba(16, 24, 40, 0.08);
    }

    .result-date {
        color: var(--color-muted);
        font-size: 0.79rem;
        font-weight: 700;
    }

    .result-matchup {
        gap: 0.5rem;
        white-space: nowrap;
    }

    .result-team {
        gap: 0.25rem;
        color: var(--color-ink);
        font-size: 0.82rem;
        font-weight: 700;
    }

    .result-score {
        color: var(--color-ink);
        font-size: 0.92rem;
        font-weight: 800;
    }

    .result-extra {
        color: var(--color-muted);
        font-size: 0.7rem;
        font-weight: 700;
    }

    .result-finns {
        min-width: 0;
        color: var(--color-muted);
        font-size: 0.8rem;
        line-height: 1.4;
    }

    .preseason-toggle {
        margin-top: 0.7rem;
        padding: 0.35rem 0;
        border: 0;
        background: transparent;
        color: var(--accent);
        font-size: 0.82rem;
        font-weight: 700;
        cursor: pointer;
    }

    .preseason-toggle:hover {
        text-decoration: underline;
    }

    .preseason-toggle:focus-visible {
        outline: 2px solid var(--accent);
        outline-offset: 3px;
    }

    .preseason-empty {
        color: var(--color-muted);
        font-size: 0.85rem;
    }

    @media (max-width: 767px) {
        .preseason-inner {
            padding: 0.9rem;
        }

        .result-row {
            grid-template-columns: 3rem minmax(0, 1fr);
        }

        .result-finns {
            grid-column: 2;
        }
    }

    @media (max-width: 420px) {




        .player-cell {
            gap: 0.25rem;
            white-space: normal;
        }
    }
</style>
