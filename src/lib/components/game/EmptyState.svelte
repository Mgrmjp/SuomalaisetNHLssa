<script>
// @ts-nocheck

import TeamLogo from '$lib/components/ui/TeamLogo.svelte'
import { displayDate } from '$lib/stores/gameData.js'

/**
 * @type {{
 *   variant?: 'no-games' | 'no-scorers' | 'break',
 *   relatedGames?: Array<{ gameId: number|string, homeTeam: string, awayTeam: string, startTime?: string, finnish_players_count?: number }>,
 *   relatedGamesLabel?: string,
 *   newsItems?: Array<{ translatedTitle?: string, translatedSummary?: string, title?: string, summary?: string, source?: string, url?: string }>
 * }}
 */
let { variant = 'no-scorers', relatedGames = [], relatedGamesLabel = '', newsItems = [] } = $props()

const messages = {
    'no-games': {
        title: 'Ei otteluita tänään',
        text: 'NHL:ssä ei pelata otteluita päivälle',
    },
    'no-scorers': {
        title: 'Ei suomalaista pisteidentekijää',
        text: 'Kukaan suomalaispelaaja ei tehnyt pisteitä, tai dataa ei ole vielä saatavilla päivälle',
    },
    break: {
        title: 'NHL-tauko',
        text: 'NHL:ssä on meneillään tauko. Pelit jatkuvat pian!',
    },
}

const currentMessage = $derived(messages[variant] || messages['no-scorers'])

const iconVariant = $derived(messages[variant] ? variant : 'no-scorers')

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
const hasNewsItems = $derived(Array.isArray(newsItems) && newsItems.length > 0)
</script>

<div class="empty-state-wrapper">
    <div class="empty-state-card">
        <div class="empty-state-content">
            <div
                class="empty-state-icon"
                class:empty-state-icon--break={iconVariant === 'break'}
                aria-hidden="true"
            >
                {#if iconVariant === 'no-games'}
                    <!-- Calendar -->
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="3" y="4" width="18" height="18" rx="2" />
                        <path d="M16 2v4M8 2v4M3 10h18" />
                    </svg>
                {:else if iconVariant === 'break'}
                    <!-- Pause -->
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="6" y="5" width="4" height="14" rx="1" />
                        <rect x="14" y="5" width="4" height="14" rx="1" />
                    </svg>
                {:else}
                    <!-- Puck / no scorers -->
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <ellipse cx="12" cy="8" rx="8" ry="3" />
                        <path d="M4 8v8c0 1.66 3.58 3 8 3s8-1.34 8-3V8" />
                    </svg>
                {/if}
            </div>
            <h3 class="empty-state-title">{currentMessage.title}</h3>
            <p class="empty-state-text">
                {currentMessage.text}
                <span class="empty-state-date">{$displayDate}</span>.
            </p>

            {#if hasRelatedGames}
                <div class="empty-state-section upcoming-games">
                    <p class="section-label">{relatedGamesLabel}</p>

                    <div class="upcoming-games-list">
                        {#each relatedGames as game (game.gameId)}
                            <div class="upcoming-game-row">
                                <div class="team-pair">
                                    <span class="team-chip">
                                        <TeamLogo team={game.awayTeam} size="22" />
                                        <span>{game.awayTeam}</span>
                                    </span>
                                    <span class="at-separator">@</span>
                                    <span class="team-chip">
                                        <TeamLogo team={game.homeTeam} size="22" />
                                        <span>{game.homeTeam}</span>
                                    </span>
                                </div>

                                <div class="upcoming-game-aside">
                                    <span class="upcoming-game-time">
                                        {formatStartTime(game.startTime, showRelatedGameDates)}
                                    </span>
                                    <span class="finn-count-badge">
                                        <span class="finn-flag" aria-hidden="true">🇫🇮</span>
                                        {game.finnish_players_count || 0}
                                    </span>
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

            {#if hasNewsItems}
                <div class="empty-state-section daily-news">
                    <p class="section-label">Päivän NHL-uutisia</p>

                    <div class="daily-news-list">
                        {#each newsItems as item, index (`${item.url || item.title || index}`)}
                            <article class="daily-news-item">
                                <h4 class="daily-news-title">
                                    {item.translatedTitle || item.title}
                                </h4>
                                <p class="daily-news-summary">
                                    {item.translatedSummary || item.summary}
                                </p>
                                <div class="daily-news-footer">
                                    {#if item.source}
                                        <span class="daily-news-source">{item.source}</span>
                                    {/if}
                                    {#if item.url}
                                        <a
                                            class="daily-news-link"
                                            href={item.url}
                                            target="_blank"
                                            rel="noreferrer"
                                        >
                                            Lue lisää
                                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                                                <path d="M7 17L17 7M9 7h8v8" />
                                            </svg>
                                        </a>
                                    {/if}
                                </div>
                            </article>
                        {/each}
                    </div>
                </div>
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
        max-width: 520px;
        width: 100%;
        background: #ffffff;
        border-radius: 16px;
        padding: 2.5rem 2rem;
        text-align: center;
        border: 1px solid #e2e8f0;
        box-shadow:
            0 1px 2px rgba(15, 23, 42, 0.04),
            0 8px 24px rgba(15, 23, 42, 0.06);
    }

    .empty-state-content {
        position: relative;
    }

    .empty-state-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 4rem;
        height: 4rem;
        margin: 0 auto 1.25rem;
        border-radius: 9999px;
        background: linear-gradient(180deg, #eff6ff 0%, #dbeafe 100%);
        color: #1d4ed8;
        border: 1px solid #bfdbfe;
    }

    .empty-state-icon--break {
        background: linear-gradient(180deg, #fef3c7 0%, #fde68a 100%);
        color: #b45309;
        border-color: #fcd34d;
    }

    .empty-state-icon svg {
        width: 1.875rem;
        height: 1.875rem;
    }

    .empty-state-title {
        font-size: 1.375rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 0.5rem;
        line-height: 1.25;
        letter-spacing: -0.01em;
    }

    .empty-state-text {
        font-size: 0.9375rem;
        color: #475569;
        line-height: 1.55;
        max-width: 28rem;
        margin: 0 auto;
    }

    .empty-state-date {
        font-weight: 700;
        color: #1d4ed8;
        white-space: nowrap;
    }

    /* Shared section styling for the related-games and news blocks */
    .empty-state-section {
        margin-top: 1.75rem;
        padding-top: 1.5rem;
        border-top: 1px solid #e2e8f0;
        text-align: left;
    }

    .section-label {
        font-size: 0.6875rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: #64748b;
        margin-bottom: 0.875rem;
        text-align: center;
    }

    /* Related games */
    .upcoming-games-list {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .upcoming-game-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.75rem;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        background: #f8fafc;
        padding: 0.75rem 0.875rem;
        transition:
            border-color 0.15s ease,
            background 0.15s ease;
    }

    .upcoming-game-row:hover {
        border-color: #cbd5e1;
        background: #f1f5f9;
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
        gap: 0.4rem;
        font-size: 0.875rem;
        font-weight: 700;
        color: #0f172a;
    }

    .at-separator {
        color: #94a3b8;
        font-weight: 700;
        font-size: 0.75rem;
    }

    .upcoming-game-aside {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 0.3rem;
        flex-shrink: 0;
    }

    .upcoming-game-time {
        font-size: 0.8125rem;
        font-weight: 700;
        color: #334155;
        white-space: nowrap;
    }

    .finn-count-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        padding: 0.1rem 0.45rem;
        border-radius: 9999px;
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        font-size: 0.75rem;
        font-weight: 700;
        color: #1d4ed8;
        white-space: nowrap;
    }

    .finn-flag {
        font-size: 0.8125rem;
        line-height: 1;
    }

    .upcoming-games-empty-note {
        margin-top: 1.5rem;
        padding-top: 1.5rem;
        border-top: 1px solid #e2e8f0;
        font-size: 0.8125rem;
        color: #64748b;
        line-height: 1.55;
        max-width: 28rem;
        margin-left: auto;
        margin-right: auto;
    }

    /* News */
    .daily-news-list {
        display: flex;
        flex-direction: column;
        gap: 0.625rem;
    }

    .daily-news-item {
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        background: #ffffff;
        padding: 0.95rem 1.05rem;
        transition: border-color 0.15s ease;
    }

    .daily-news-item:hover {
        border-color: #cbd5e1;
    }

    .daily-news-title {
        font-size: 0.9375rem;
        font-weight: 700;
        color: #0f172a;
        margin: 0 0 0.4rem;
        line-height: 1.4;
    }

    .daily-news-summary {
        font-size: 0.8125rem;
        color: #475569;
        margin: 0;
        line-height: 1.55;
        display: -webkit-box;
        -webkit-line-clamp: 3;
        line-clamp: 3;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }

    .daily-news-footer {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.5rem;
        margin-top: 0.7rem;
    }

    .daily-news-source {
        font-size: 0.6875rem;
        font-weight: 600;
        color: #64748b;
        padding: 0.1rem 0.45rem;
        border-radius: 6px;
        background: #f1f5f9;
        max-width: 60%;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .daily-news-link {
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        font-size: 0.8125rem;
        font-weight: 700;
        color: #1d4ed8;
        text-decoration: none;
        margin-left: auto;
        white-space: nowrap;
    }

    .daily-news-link svg {
        width: 0.875rem;
        height: 0.875rem;
    }

    .daily-news-link:hover {
        text-decoration: underline;
    }

    @media (max-width: 640px) {
        .empty-state-wrapper {
            padding: 2rem 1rem;
            min-height: 250px;
        }

        .empty-state-card {
            padding: 2rem 1.25rem;
        }

        .empty-state-icon {
            width: 3.5rem;
            height: 3.5rem;
        }

        .empty-state-icon svg {
            width: 1.625rem;
            height: 1.625rem;
        }

        .empty-state-title {
            font-size: 1.1875rem;
        }

        .empty-state-text {
            font-size: 0.875rem;
        }

        .upcoming-game-row {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.5rem;
        }

        .upcoming-game-aside {
            flex-direction: row;
            align-items: center;
            align-self: stretch;
            justify-content: space-between;
        }
    }
</style>
