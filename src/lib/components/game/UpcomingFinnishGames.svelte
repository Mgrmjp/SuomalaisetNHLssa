<script>
// @ts-nocheck
import { onMount } from 'svelte'
import TeamLogo from '$lib/components/ui/TeamLogo.svelte'

const { games = [] } = $props()
let now = $state(0)
const upcomingGames = $derived(
    games.filter((game) => new Date(game.startTime).getTime() > now).slice(0, 4)
)

onMount(() => {
    now = Date.now()
    const timer = setInterval(() => {
        now = Date.now()
    }, 60_000)
    return () => clearInterval(timer)
})

const finnishTime = new Intl.DateTimeFormat('fi-FI', {
    timeZone: 'Europe/Helsinki',
    weekday: 'short',
    day: 'numeric',
    month: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
})

function playerSummary(players) {
    const names = players
        .slice(0, 3)
        .map((player) => player.name)
        .join(', ')
    const more = players.length - 3
    return more > 0 ? `${names} +${more}` : names
}

function finnCountLabel(count) {
    return `${count} ${count === 1 ? 'suomalainen' : 'suomalaista'} joukkueissa`
}
</script>

{#if upcomingGames.length > 0}
    <section class="panel panel--upcoming" aria-labelledby="upcoming-title">
        <div class="upcoming-inner">
            <div class="panel__eyebrow rink-divider">Tulossa</div>
            <h2 id="upcoming-title">Suomalaisia tulevissa NHL-otteluissa</h2>
            <p class="upcoming-intro">Joukkueiden suomalaiset pelaajat · kokoonpanot vahvistuvat ottelupäivänä</p>

            <div class="upcoming-list">
                {#each upcomingGames as game (game.gameId)}
                    <div class="upcoming-row">
                        <time datetime={game.startTime} class="upcoming-time">
                            {finnishTime.format(new Date(game.startTime))}
                        </time>
                        <div class="upcoming-matchup" aria-label={`${game.awayTeam} vastaan ${game.homeTeam}`}>
                            <span class="upcoming-team"><TeamLogo team={game.awayTeam} size="26" />{game.awayTeam}</span>
                            <span class="upcoming-separator" aria-hidden="true">–</span>
                            <span class="upcoming-team"><TeamLogo team={game.homeTeam} size="26" />{game.homeTeam}</span>
                        </div>
                        <div class="upcoming-finns">
                            <strong>{finnCountLabel(game.finnishPlayers.length)}</strong>
                            <span>{playerSummary(game.finnishPlayers)}</span>
                        </div>
                    </div>
                {/each}
            </div>
        </div>
    </section>
{/if}

<style>
    .panel--upcoming {
        width: 100%;
        max-width: var(--rail-max);
        margin: 0 auto;
        border: var(--card-border);
        border-radius: var(--card-radius);
        background: var(--card-bg);
        box-shadow: none;
    }

    .upcoming-inner {
        padding: var(--card-padding-y, 1.25rem) var(--card-padding-x, 1.5rem);
    }

    .panel__eyebrow {
        margin-bottom: 0.5rem;
    }

    h2 {
        margin: 0;
        color: var(--color-ink);
        font-size: 1.1rem;
        font-weight: 800;
        line-height: 1.3;
    }

    .upcoming-intro {
        margin: 0.25rem 0 1rem;
        color: var(--color-muted);
        font-size: 0.82rem;
    }

    .upcoming-list {
        border-top: 1px solid rgba(16, 24, 40, 0.1);
    }

    .upcoming-row {
        display: grid;
        grid-template-columns: 7.5rem 12rem minmax(0, 1fr);
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem 0;
        border-bottom: 1px solid rgba(16, 24, 40, 0.08);
    }

    .upcoming-time {
        color: var(--color-muted);
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: capitalize;
    }

    .upcoming-matchup,
    .upcoming-team {
        display: flex;
        align-items: center;
    }

    .upcoming-matchup {
        gap: 0.5rem;
        white-space: nowrap;
    }

    .upcoming-team {
        gap: 0.25rem;
        color: var(--color-ink);
        font-size: 0.82rem;
        font-weight: 800;
    }

    .upcoming-separator {
        color: var(--color-muted);
        font-size: 0.9rem;
        font-weight: 700;
        flex: none;
    }

    .upcoming-finns {
        min-width: 0;
        display: grid;
        gap: 0.1rem;
        font-size: 0.79rem;
        line-height: 1.35;
    }

    .upcoming-finns strong {
        color: var(--color-ink);
        font-weight: 700;
    }

    .upcoming-finns span {
        color: var(--color-muted);
    }

    @media (max-width: 767px) {
        .upcoming-inner {
            padding: 0.9rem;
        }

        .upcoming-row {
            grid-template-columns: 1fr auto;
            gap: 0.4rem 0.75rem;
        }

        .upcoming-time {
            grid-column: 1 / -1;
        }

        .upcoming-matchup {
            grid-column: 1;
        }

        .upcoming-finns {
            grid-column: 1 / -1;
        }
    }

    @media (max-width: 420px) {
        .upcoming-row {
            grid-template-columns: 1fr;
        }

        .upcoming-finns {
            grid-column: 1;
            text-align: left;
        }
    }
</style>
