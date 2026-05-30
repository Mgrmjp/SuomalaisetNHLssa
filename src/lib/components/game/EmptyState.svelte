<script>
// @ts-nocheck

import TeamLogo from '$lib/components/ui/TeamLogo.svelte'
import { displayDate } from '$lib/stores/gameData.js'

/**
 * @type {{
 *   variant?: 'no-games' | 'no-scorers' | 'break',
 *   relatedGames?: Array<{ gameId: number|string, homeTeam: string, awayTeam: string, startTime?: string, finnish_players_count?: number }>,
 *   relatedGamesLabel?: string,
 *   newsItems?: Array<{ translatedTitle?: string, translatedSummary?: string, title?: string, summary?: string, source?: string, url?: string }>,
 *   lineupCount?: number
 * }}
 */
let {
    variant = 'no-scorers',
    relatedGames = [],
    relatedGamesLabel = '',
    newsItems = [],
    lineupCount = 0,
} = $props()

const messages = {
    'no-games': {
        title: 'Ei otteluita tänään',
        text: 'NHL:ssä ei pelata tähän päivään otteluita.',
    },
    'no-scorers': {
        title: 'Suomalaiset pisteittä tänään',
        text: 'Kukaan suomalaispelaaja ei yltänyt tehopisteille tai tilastot eivät ole vielä päivittyneet.',
    },
    break: {
        title: 'NHL-tauko',
        text: 'NHL:ssä on meneillään tauko. Uudet ottelut alkavat pian.',
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
                class:empty-state-icon--premium={iconVariant === 'no-scorers'}
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

            {#if variant === 'no-scorers' && lineupCount > 0}
                <div class="lineup-context">
                    <span class="lineup-dot" aria-hidden="true"></span>
                    {lineupCount}
                    {lineupCount === 1 ? 'suomalainen' : 'suomalaista'}
                    oli kokoonpanossa.
                </div>
            {/if}

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
        max-width: 540px;
        width: 100%;
        background: #ffffff;
        border-radius: 18px;
        padding: 2.65rem 2.15rem 2.3rem;
        text-align: center;
        border: 1px solid #e0e7ff;
        box-shadow:
            0 1px 3px rgba(15, 23, 42, 0.04),
            0 14px 36px -10px rgba(15, 23, 42, 0.10);
        position: relative;
    }

    .empty-state-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(to right, #6366f1, #3b82f6);
        border-radius: 18px 18px 0 0;
        opacity: 0.85;
    }

    .empty-state-content {
        position: relative;
    }

    .empty-state-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 3.5rem;
        height: 3.5rem;
        margin: 0 auto 1.1rem;
        border-radius: 9999px;
        color: #fff;
        box-shadow:
            0 1px 2px rgba(0, 0, 0, 0.04),
            0 6px 16px rgba(63, 66, 243, 0.14);
    }

    .empty-state-icon--premium {
        /* Brand gradient matching the purple-blue logo "F" */
        background: linear-gradient(135deg, #6366f1 0%, #3b82f6 100%);
    }

    .empty-state-icon--break {
        background: #f59e0b;
        box-shadow:
            0 1px 2px rgba(0, 0, 0, 0.06),
            0 6px 16px rgba(245, 158, 11, 0.18);
    }

    .empty-state-icon svg {
        width: 1.7rem;
        height: 1.7rem;
    }

    .empty-state-title {
        font-size: 1.45rem;
        font-weight: 800;
        letter-spacing: -0.028em;
        color: #0f172a;
        margin-bottom: 0.55rem;
        line-height: 1.22;
    }

    .empty-state-text {
        font-size: 0.95rem;
        color: #475569;
        line-height: 1.6;
        max-width: 28.5rem;
        margin: 0 auto;
    }

    .empty-state-date {
        font-weight: 700;
        color: #4338ca;
        white-space: nowrap;
    }

    .lineup-context {
        margin-top: 0.7rem;
        font-size: 0.82rem;
        font-weight: 600;
        color: #64748b;
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.25rem 0.7rem;
        background: #f8fafc;
        border: 1px solid #e0e7ff;
        border-radius: 999px;
        white-space: nowrap;
    }

    .lineup-dot {
        width: 0.45rem;
        height: 0.45rem;
        background: #6366f1;
        border-radius: 999px;
        flex-shrink: 0;
    }

    /* Shared section styling */
    .empty-state-section {
        margin-top: 1.8rem;
        padding-top: 1.5rem;
        border-top: 1px solid #eef2f7;
        text-align: left;
    }

    .section-label {
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.012em;
        color: #64748b;
        margin-bottom: 0.95rem;
        text-align: center;
    }

    /* Related games – premium rows */
    .upcoming-games-list {
        display: flex;
        flex-direction: column;
        gap: 0.45rem;
    }

    .upcoming-game-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.9rem;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        background: #fdfdfe;
        padding: 0.82rem 1rem;
        transition:
            box-shadow 0.15s ease,
            border-color 0.15s ease,
            transform 0.12s ease;
    }

    .upcoming-game-row:hover {
        border-color: #c7d2fe;
        box-shadow: 0 4px 18px -6px rgba(15, 23, 42, 0.12);
        transform: translateY(-1px);
    }

    .team-pair {
        display: flex;
        align-items: center;
        gap: 0.55rem;
        min-width: 0;
        flex-wrap: wrap;
    }

    .team-chip {
        display: inline-flex;
        align-items: center;
        gap: 0.42rem;
        font-size: 0.93rem;
        font-weight: 700;
        color: #0f172a;
        letter-spacing: -0.01em;
    }

    .at-separator {
        color: #94a3b8;
        font-weight: 600;
        font-size: 0.78rem;
    }

    .upcoming-game-aside {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 0.35rem;
        flex-shrink: 0;
    }

    .upcoming-game-time {
        font-size: 0.78rem;
        font-weight: 600;
        color: #64748b;
        white-space: nowrap;
        letter-spacing: 0.01em;
    }

    .finn-count-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.28rem;
        padding: 0.08rem 0.6rem;
        border-radius: 999px;
        background: #f0f4ff;
        border: 1px solid #dbeafe;
        font-size: 0.725rem;
        font-weight: 700;
        letter-spacing: 0.02em;
        color: #3730a3;
        white-space: nowrap;
    }

    .finn-flag {
        font-size: 0.78rem;
        line-height: 1;
    }

    .upcoming-games-empty-note {
        margin-top: 1.6rem;
        padding-top: 1.5rem;
        border-top: 1px solid #eef2f7;
        font-size: 0.85rem;
        color: #64748b;
        line-height: 1.55;
        max-width: 29rem;
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
            padding: 1.75rem 1rem;
            min-height: 240px;
        }

        .empty-state-card {
            padding: 2.15rem 1.45rem 1.95rem;
        }

        .empty-state-icon {
            width: 3rem;
            height: 3rem;
        }

        .empty-state-icon svg {
            width: 1.45rem;
            height: 1.45rem;
        }

        .empty-state-title {
            font-size: 1.28rem;
        }

        .empty-state-text {
            font-size: 0.9rem;
        }

        .upcoming-game-row {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.55rem;
            padding: 0.78rem 0.95rem;
        }

        .upcoming-game-aside {
            flex-direction: row;
            align-items: center;
            align-self: stretch;
            justify-content: space-between;
        }
    }
</style>
