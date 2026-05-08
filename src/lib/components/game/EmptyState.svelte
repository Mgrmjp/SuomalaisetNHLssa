<script>
// @ts-nocheck

import TeamLogo from '$lib/components/ui/TeamLogo.svelte'
import { displayDate } from '$lib/stores/gameData.js'

/**
 * @type {{
 *   variant?: 'no-games' | 'no-scorers' | 'break',
 *   relatedGames?: Array<{ gameId: number|string, homeTeam: string, awayTeam: string, startTime?: string, finnish_players_count?: number }>,
 *   relatedGamesLabel?: string
 * }}
 */
let { variant = 'no-scorers', relatedGames = [], relatedGamesLabel = '' } = $props()

const messages = {
    'no-games': {
        title: 'Ei otteluita tänään',
        text: 'NHL:ssä ei pelata otteluita päivälle',
    },
    'no-scorers': {
        title: 'Ei suomalaista pisteidentekijää',
        text: 'Yhtään suomalaispelaajaa ei ole merkitty pisteille tai dataa ei ole vielä saatavilla päivälle',
    },
    break: {
        title: 'NHL-tauko',
        text: 'NHL:ssä on meneillään tauko. Pelit jatkuvat pian!',
    },
}

const currentMessage = $derived(messages[variant] || messages['no-scorers'])

function formatStartTime(startTime, includeDate = false) {
    if (!startTime) return ''

    try {
        return new Intl.DateTimeFormat(
            'fi-FI',
            includeDate
                ? {
                      day: 'numeric',
                      month: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                      timeZone: 'Europe/Helsinki',
                  }
                : {
                      hour: '2-digit',
                      minute: '2-digit',
                      timeZone: 'Europe/Helsinki',
                  }
        ).format(new Date(startTime))
    } catch {
        return ''
    }
}

const hasRelatedGames = $derived(
    variant === 'no-scorers' && Array.isArray(relatedGames) && relatedGames.length > 0
)

const showNoRelatedGamesNote = $derived(
    variant === 'no-scorers' && Array.isArray(relatedGames) && relatedGames.length === 0
)

const showRelatedGameDates = $derived(relatedGamesLabel.toLowerCase().includes('viimeksi'))
</script>

<div class="empty-state-wrapper">
    <div class="empty-state-card">
        <div class="empty-state-content">
            <h3 class="empty-state-title">{currentMessage.title}</h3>
            <p class="empty-state-text">
                {currentMessage.text}
                <span class="empty-state-date">{$displayDate}</span>.
            </p>

            {#if hasRelatedGames}
                <div class="upcoming-games">
                    <p class="upcoming-games-label">{relatedGamesLabel}</p>

                    <div class="upcoming-games-list">
                        {#each relatedGames as game (game.gameId)}
                            <div class="upcoming-game-row">
                                <div class="upcoming-game-matchup">
                                    <div class="team-pair">
                                        <span class="team-chip">
                                            <TeamLogo team={game.awayTeam} size="20" />
                                            <span>{game.awayTeam}</span>
                                        </span>
                                        <span class="at-separator">@</span>
                                        <span class="team-chip">
                                            <TeamLogo team={game.homeTeam} size="20" />
                                            <span>{game.homeTeam}</span>
                                        </span>
                                    </div>
                                    <span class="upcoming-game-time">
                                        {formatStartTime(game.startTime, showRelatedGameDates)}
                                    </span>
                                </div>

                                <div class="upcoming-game-meta">
                                    {game.finnish_players_count || 0} suomalaista
                                </div>
                            </div>
                        {/each}
                    </div>
                </div>
            {:else if showNoRelatedGamesNote}
                <p class="upcoming-games-empty-note">
                    Tulevia tai viimeisimpiä suomalaispelaajien otteluita ei löytynyt paikallisesta
                    datasta.
                </p>
            {/if}
        </div>
    </div>
</div>

<style>
    .empty-state-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 3rem 1rem;
        min-height: 300px;
    }

    .empty-state-card {
        max-width: 500px;
        width: 100%;
        background: white;
        border-radius: 12px;
        padding: 2.5rem 2rem;
        text-align: center;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
    }

    .empty-state-content {
        position: relative;
    }

    .empty-state-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 0.5rem;
        line-height: 1.3;
    }

    .empty-state-text {
        font-size: 0.875rem;
        color: #6b7280;
        line-height: 1.5;
        max-width: 26rem;
        margin: 0 auto;
    }

    .upcoming-games {
        margin-top: 1.5rem;
        text-align: left;
    }

    .upcoming-games-label {
        font-size: 0.8125rem;
        font-weight: 600;
        color: #334155;
        margin-bottom: 0.75rem;
        text-align: center;
    }

    .upcoming-games-list {
        display: flex;
        flex-direction: column;
        gap: 0.625rem;
    }

    .upcoming-game-row {
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        background: #f8fafc;
        padding: 0.75rem 0.875rem;
    }

    .upcoming-game-matchup {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.75rem;
    }

    .team-pair {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        min-width: 0;
        flex-wrap: wrap;
    }

    .team-chip {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        font-size: 0.875rem;
        font-weight: 700;
        color: #0f172a;
    }

    .at-separator {
        color: #64748b;
        font-weight: 700;
        font-size: 0.75rem;
    }

    .upcoming-game-time {
        font-size: 0.8125rem;
        font-weight: 700;
        color: #1d4ed8;
        white-space: nowrap;
    }

    .upcoming-game-meta {
        margin-top: 0.4rem;
        font-size: 0.75rem;
        color: #64748b;
    }

    .upcoming-games-empty-note {
        margin-top: 1.25rem;
        font-size: 0.8125rem;
        color: #64748b;
        line-height: 1.5;
        max-width: 28rem;
        margin-left: auto;
        margin-right: auto;
    }

    .empty-state-date {
        font-weight: 600;
        color: #1e40af;
    }

    @media (max-width: 640px) {
        .empty-state-wrapper {
            padding: 2rem 1rem;
            min-height: 250px;
        }

        .empty-state-card {
            padding: 2rem 1.5rem;
        }

        .empty-state-title {
            font-size: 1.125rem;
        }

        .empty-state-text {
            font-size: 0.8125rem;
        }

        .upcoming-game-matchup {
            align-items: flex-start;
            flex-direction: column;
        }

        .upcoming-game-time {
            margin-left: 1.7rem;
        }
    }
</style>
