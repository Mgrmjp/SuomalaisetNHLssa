<script>
// @ts-nocheck

import TeamLogo from '$lib/components/ui/TeamLogo.svelte'
import { displayDate } from '$lib/stores/gameData.js'

/**
 * @type {{
 *   variant?: 'no-games' | 'no-scorers' | 'break' | 'offseason',
 *   relatedGames?: Array<{ gameId: number|string, homeTeam: string, awayTeam: string, startTime?: string, finnish_players_count?: number, finnishPlayers?: string[] }>,
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
    offseason: {
        title: 'Nähdään ensi kaudella!',
        text: 'NHL-kausi on päättynyt. Uusi kausi alkaa lokakuussa – siihen asti voit seurata suomalaispelaajien siirtoja ja sopimuksia alta.',
    },
}

const currentMessage = $derived(messages[variant] || messages['no-scorers'])

const iconVariant = $derived(messages[variant] ? variant : 'no-scorers')

const isOffseason = $derived(variant === 'offseason')

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

const emptyStateStats = $derived.by(() => {
    const stats = []

    if (variant === 'no-scorers') {
        stats.push({
            value: '0',
            label: 'suomalaista pisteillä',
        })
    }

    if (variant === 'no-scorers' && lineupCount > 0) {
        stats.push({
            value: lineupCount,
            label: lineupCount === 1 ? 'suomalainen kokoonpanossa' : 'suomalaista kokoonpanossa',
        })
    }

    if (hasRelatedGames) {
        stats.push({
            value: relatedGames.length,
            label: showRelatedGameDates ? 'vertailuottelua' : 'tulevaa ottelua',
        })
    }

    return stats
})
</script>

<div class="empty-state-wrapper">
    <div class="empty-state-card">
        <div class="empty-state-content">
            <div
                class="empty-state-icon"
                class:empty-state-icon--break={iconVariant === 'break'}
                class:empty-state-icon--offseason={iconVariant === 'offseason'}
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
                {:else if iconVariant === 'offseason'}
                    <!-- Sun / offseason -->
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="5" />
                        <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" />
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
                {#if !isOffseason}
                    <span class="empty-state-date">{$displayDate}</span>.
                {/if}
            </p>

            {#if emptyStateStats.length > 0 && !isOffseason}
                <div class="empty-state-stats" role="list" aria-label="Päivän yhteenveto">
                    {#each emptyStateStats as stat}
                        <div class="empty-state-stat" role="listitem">
                            <strong>{stat.value}</strong>
                            <span>{stat.label}</span>
                        </div>
                    {/each}
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

                                {#if Array.isArray(game.finnishPlayers) && game.finnishPlayers.length > 0}
                                    <div class="finnish-players-line">
                                        <span class="finnish-players-flag" aria-hidden="true">🇫🇮</span>
                                        <span class="finnish-players-names">{game.finnishPlayers.join(', ')}</span>
                                    </div>
                                {/if}
                            </div>
                        {/each}
                    </div>
                </div>
            {:else if showNoRelatedGamesNote && !isOffseason}
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
        display: block;
        padding: 0;
        min-height: 0;
    }

    .empty-state-card {
        max-width: var(--rail-max, 920px);
        width: 100%;
        margin: 0 auto;
        background: var(--card-bg, rgba(255, 255, 255, 0.9));
        border-radius: var(--card-radius, 20px);
        padding: 2.25rem var(--card-padding-x, 1.5rem) 1.75rem;
        text-align: center;
        border: var(--card-border, 1px solid rgba(16, 24, 40, 0.08));
        box-shadow: var(--card-shadow, 0 24px 70px rgba(16, 24, 40, 0.08));
        backdrop-filter: blur(18px);
        position: relative;
        overflow: hidden;
    }

    .empty-state-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--card-accent, linear-gradient(90deg, #003580, #4f7dd8, #b9cdf0));
        border-radius: 20px 20px 0 0;
    }

    .empty-state-content {
        position: relative;
    }

    .empty-state-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 3.75rem;
        height: 3.75rem;
        margin: 0 auto 1rem;
        border-radius: 9999px;
        color: #fff;
        box-shadow:
            0 1px 2px rgba(0, 0, 0, 0.04),
            0 12px 28px rgba(0, 53, 128, 0.18);
    }

    .empty-state-icon--premium {
        background: linear-gradient(135deg, var(--accent, #003580) 0%, var(--accent-soft, #4f7dd8) 100%);
    }

    .empty-state-icon--break {
        background: #f59e0b;
        box-shadow:
            0 1px 2px rgba(0, 0, 0, 0.06),
            0 6px 16px rgba(245, 158, 11, 0.18);
    }

    .empty-state-icon--offseason {
        background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
        box-shadow:
            0 1px 2px rgba(0, 0, 0, 0.06),
            0 8px 20px rgba(249, 115, 22, 0.2);
    }

    .empty-state-icon svg {
        width: 1.85rem;
        height: 1.85rem;
    }

    .empty-state-title {
        font-size: clamp(1.25rem, 2.4vw, 1.5rem);
        font-weight: 800;
        letter-spacing: 0;
        color: var(--color-ink, #101828);
        margin-bottom: 0.5rem;
        line-height: 1.22;
        font-family: var(--font-display, "Sora", "Inter", system-ui, sans-serif);
    }

    .empty-state-text {
        font-size: 0.95rem;
        color: var(--color-muted, #667085);
        line-height: 1.6;
        max-width: 32rem;
        margin: 0 auto;
    }

    .empty-state-date {
        font-weight: 700;
        color: var(--accent, #003580);
        white-space: nowrap;
    }

    .empty-state-stats {
        display: flex;
        justify-content: center;
        gap: 0.5rem;
        flex-wrap: wrap;
        max-width: 36rem;
        margin: 1.1rem auto 0;
    }

    .empty-state-stat {
        min-width: 9rem;
        padding: 0.75rem 1rem;
        border: 1px solid rgba(0, 53, 128, 0.08);
        border-radius: var(--card-radius-sm, 14px);
        background: rgba(248, 250, 255, 0.7);
    }

    .empty-state-stat strong {
        display: block;
        color: var(--color-ink, #101828);
        font-size: 1.2rem;
        line-height: 1;
        font-weight: 800;
        font-variant-numeric: tabular-nums;
    }

    .empty-state-stat span {
        display: block;
        margin-top: 0.3rem;
        color: var(--color-muted, #667085);
        font-size: 0.72rem;
        font-weight: 700;
        line-height: 1.25;
    }

    .empty-state-section {
        margin-top: 1.5rem;
        padding-top: 1.25rem;
        border-top: 1px solid rgba(16, 24, 40, 0.06);
        text-align: left;
    }

    .section-label {
        font-size: var(--eyebrow-size, 0.72rem);
        font-weight: var(--eyebrow-weight, 800);
        letter-spacing: var(--eyebrow-track, 0.1em);
        text-transform: uppercase;
        color: var(--accent, #003580);
        margin-bottom: 0.85rem;
        text-align: center;
    }

    .upcoming-games-list {
        display: flex;
        flex-direction: column;
        gap: 0.4rem;
    }

    .upcoming-game-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 0.5rem 0.9rem;
        border: 1px solid rgba(0, 53, 128, 0.08);
        border-radius: var(--card-radius-sm, 14px);
        background: rgba(248, 250, 255, 0.5);
        padding: 0.7rem 0.95rem;
        transition:
            box-shadow 0.15s ease,
            border-color 0.15s ease,
            transform 0.12s ease,
            background 0.15s ease;
    }

    .upcoming-game-row:hover {
        border-color: rgba(0, 53, 128, 0.2);
        background: rgba(255, 255, 255, 0.9);
        box-shadow: 0 4px 18px -6px rgba(0, 53, 128, 0.15);
        transform: translateY(-1px);
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
        font-size: 0.92rem;
        font-weight: 700;
        color: var(--color-ink, #101828);
        letter-spacing: 0;
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
        gap: 0.3rem;
        flex-shrink: 0;
    }

    .upcoming-game-time {
        font-size: 0.78rem;
        font-weight: 600;
        color: var(--color-muted, #667085);
        white-space: nowrap;
        letter-spacing: 0.01em;
    }

    .finn-count-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        padding: 0.08rem 0.6rem;
        border-radius: 999px;
        background: var(--accent-ice, #eef3fb);
        border: 1px solid rgba(0, 53, 128, 0.12);
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.02em;
        color: var(--accent, #003580);
        white-space: nowrap;
    }

    .finn-flag {
        font-size: 0.78rem;
        line-height: 1;
    }

    .finnish-players-line {
        display: flex;
        align-items: baseline;
        gap: 0.4rem;
        width: 100%;
        padding-top: 0.45rem;
        margin-top: 0.15rem;
        border-top: 1px dashed rgba(0, 53, 128, 0.1);
        font-size: 0.78rem;
        line-height: 1.4;
        color: var(--color-muted, #475467);
    }

    .finnish-players-flag {
        font-size: 0.85rem;
        line-height: 1;
    }

    .finnish-players-names {
        font-weight: 600;
        color: var(--color-ink, #101828);
        word-break: break-word;
    }

    .upcoming-games-empty-note {
        margin-top: 1.4rem;
        padding-top: 1.25rem;
        border-top: 1px solid rgba(16, 24, 40, 0.06);
        font-size: 0.85rem;
        color: var(--color-muted, #667085);
        line-height: 1.55;
        max-width: 32rem;
        margin-left: auto;
        margin-right: auto;
    }

    .daily-news-list {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .daily-news-item {
        border: 1px solid rgba(0, 53, 128, 0.08);
        border-radius: 12px;
        background: #ffffff;
        padding: 0.85rem 1rem;
        transition: border-color 0.15s ease;
    }

    .daily-news-item:hover {
        border-color: rgba(0, 53, 128, 0.2);
    }

    .daily-news-title {
        font-size: 0.92rem;
        font-weight: 700;
        color: var(--color-ink, #101828);
        margin: 0 0 0.35rem;
        line-height: 1.4;
    }

    .daily-news-summary {
        font-size: 0.8rem;
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
        margin-top: 0.6rem;
    }

    .daily-news-source {
        font-size: 0.68rem;
        font-weight: 600;
        color: var(--color-muted, #667085);
        padding: 0.1rem 0.45rem;
        border-radius: 6px;
        background: var(--accent-ice, #eef3fb);
        max-width: 60%;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .daily-news-link {
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        font-size: 0.8rem;
        font-weight: 700;
        color: var(--accent, #003580);
        text-decoration: none;
        margin-left: auto;
        white-space: nowrap;
    }

    .daily-news-link svg {
        width: 0.85rem;
        height: 0.85rem;
    }

    .daily-news-link:hover {
        text-decoration: underline;
    }

    @media (max-width: 640px) {
        .empty-state-card {
            padding: 1.5rem 1.25rem 1.25rem;
        }

        .empty-state-icon {
            width: 3.25rem;
            height: 3.25rem;
        }

        .empty-state-icon svg {
            width: 1.55rem;
            height: 1.55rem;
        }

        .empty-state-text {
            font-size: 0.9rem;
        }

        .empty-state-stat {
            min-width: min(100%, 9rem);
            flex: 1 1 8rem;
        }

        .upcoming-game-row {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.5rem;
            padding: 0.7rem 0.85rem;
        }

        .upcoming-game-aside {
            flex-direction: row;
            align-items: center;
            align-self: stretch;
            justify-content: space-between;
        }
    }
</style>
