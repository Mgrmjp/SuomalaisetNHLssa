<script>
// @ts-nocheck
import {
    ArrowUpRight,
    Calendar,
    CalendarDays,
    ChevronDown,
    Newspaper,
    Pause,
    Sun,
} from 'lucide-svelte'
import FinnishFlag from '$lib/components/ui/FinnishFlag.svelte'
import TeamLogo from '$lib/components/ui/TeamLogo.svelte'
import { displayDate } from '$lib/stores/gameData.js'
import YesterdayResult from './YesterdayResult.svelte'

/**
 * @type {{
 *   variant?: 'no-games' | 'no-scorers' | 'upcoming' | 'break' | 'offseason',
 *   relatedGames?: Array<{ gameId: number|string, homeTeam: string, awayTeam: string, startTime?: string, finnish_players_count?: number, finnishPlayers?: string[] }>,
 *   relatedGamesLabel?: string,
 *   newsItems?: Array<{ translatedTitle?: string, translatedSummary?: string, title?: string, summary?: string, source?: string, url?: string, publishedAt?: string }>,
 *   yesterdayDate?: string,
 *   lineupCount?: number
 * }}
 */
let {
    variant = 'no-scorers',
    relatedGames = [],
    relatedGamesLabel = '',
    newsItems = [],
    lineupCount = 0,
    yesterdayDate = '',
} = $props()

const messages = {
    'no-games': {
        title: 'Ei otteluita valittuna päivänä',
        text: 'Valitse toinen päivä nähdäksesi ottelut.',
    },
    upcoming: { title: 'Ottelut tulossa', text: 'Tilastot päivittyvät otteluiden alettua.' },
    'no-scorers': {
        title: 'Ei pelaajatilastoja',
        text: 'Tilastoja ei ole saatavilla valitulle päivälle.',
    },
    break: { title: 'NHL-tauko', text: 'NHL:ssä on tauko. Uudet ottelut alkavat pian.' },
    offseason: {
        title: 'Nähdään ensi kaudella!',
        text: 'Kausi on päättynyt. Seuraa pelaajien siirtoja ja sopimuksia alta.',
    },
}
const currentMessage = $derived(messages[variant] || messages['no-scorers'])
const hasRelatedGames = $derived(
    ['no-scorers', 'no-games', 'upcoming'].includes(variant) &&
        Array.isArray(relatedGames) &&
        relatedGames.length > 0
)
const hasNewsItems = $derived(Array.isArray(newsItems) && newsItems.length > 0)
const showUpcomingGames = $derived(['no-scorers', 'no-games', 'upcoming'].includes(variant))
const gamesTitle = 'Suomalaisten tulevat ottelut'

function formatStartTime(startTime, includeDate = false) {
    if (!startTime) return ''
    try {
        return new Intl.DateTimeFormat('fi-FI', {
            ...(includeDate ? { day: 'numeric', month: 'numeric' } : {}),
            hour: '2-digit',
            minute: '2-digit',
            timeZone: 'Europe/Helsinki',
        }).format(new Date(startTime))
    } catch {
        return ''
    }
}
</script>

<div
    class="empty-state-layout"
    class:empty-state-layout--with-options={showUpcomingGames || hasNewsItems}
    class:empty-state-layout--featured={Boolean(yesterdayDate)}
>
    <div class="empty-state-card">
        <div class="empty-state-header">
            {#if ['no-games', 'break', 'offseason'].includes(variant)}
                <div class="empty-state-icon" aria-hidden="true">
                    {#if variant === 'no-games'}
                        <Calendar aria-hidden="true" />
                    {:else if variant === 'break'}
                        <Pause aria-hidden="true" />
                    {:else if variant === 'offseason'}
                        <Sun aria-hidden="true" />
                    {/if}
                </div>
            {/if}
            <div class="empty-state-content">
                <p class="empty-state-kicker">Kierroksen tilanne</p>
                <h2 class="empty-state-title">{currentMessage.title}</h2>
                <p class="empty-state-text">{currentMessage.text}</p>
                {#if variant !== 'offseason'}
                    <p class="empty-state-meta">
                        {$displayDate}
                        {#if variant === 'no-scorers' && lineupCount > 0}
                            · {lineupCount}
                            {lineupCount === 1
                                ? 'suomalainen kokoonpanossa'
                                : 'suomalaista kokoonpanossa'}
                        {/if}
                    </p>
                {/if}
            </div>
        </div>

        {#if yesterdayDate}
            <YesterdayResult date={yesterdayDate} />
        {/if}
    </div>

    {#if showUpcomingGames || hasNewsItems}
        <div class="empty-state-options">
            {#if showUpcomingGames}
                <details class="empty-state-details upcoming-games" open={Boolean(yesterdayDate)}>
                    <summary>
                        <span class="disclosure-label"
                            ><CalendarDays aria-hidden="true" /><span class="disclosure-title"
                                >{gamesTitle}</span
                            >{#if hasRelatedGames}<span class="detail-count"
                                    ><span class="detail-count-text">{relatedGames.length}</span
                                    ></span
                                >{/if}</span
                        >
                        {#if hasRelatedGames}
                            <span class="match-preview">
                                <TeamLogo team={relatedGames[0].awayTeam} size="20" />
                                <span class="preview-team">{relatedGames[0].awayTeam}</span>
                                <span class="preview-versus">vs</span>
                                <TeamLogo team={relatedGames[0].homeTeam} size="20" />
                                <span class="preview-team">{relatedGames[0].homeTeam}</span>
                            </span>
                        {/if}
                        <ChevronDown class="disclosure-chevron" aria-hidden="true" />
                    </summary>
                    <div class="empty-state-details-content">
                        {#if relatedGamesLabel}<p class="details-description">
                                {relatedGamesLabel}
                            </p>{/if}
                        {#if !hasRelatedGames}
                            <p class="details-description" role="status">
                                Tulevien otteluiden tietoja ei ole saatavilla.
                            </p>
                        {/if}
                        <div class="upcoming-games-list">
                            {#each relatedGames as game (game.gameId)}
                                <div class="upcoming-game-row">
                                    <div class="team-pair">
                                        <span class="team-chip"
                                            ><TeamLogo
                                                team={game.awayTeam}
                                                size="18"
                                            />{game.awayTeam}</span
                                        >
                                        <span class="at-separator">@</span>
                                        <span class="team-chip"
                                            ><TeamLogo
                                                team={game.homeTeam}
                                                size="18"
                                            />{game.homeTeam}</span
                                        >
                                    </div>
                                    <div class="upcoming-game-aside">
                                        <span>{formatStartTime(game.startTime, true)}</span>
                                        <span
                                            class="finn-count"
                                            aria-label={`Suomalaispelaajia: ${game.finnish_players_count || 0}`}
                                            ><FinnishFlag
                                                width={16}
                                            />{game.finnish_players_count || 0}</span
                                        >
                                    </div>
                                    {#if Array.isArray(game.finnishPlayers) && game.finnishPlayers.length > 0}
                                        <p class="finnish-players-names">
                                            {game.finnishPlayers.join(', ')}
                                        </p>
                                    {/if}
                                </div>
                            {/each}
                        </div>
                    </div>
                </details>
            {/if}

            {#if hasNewsItems}
                <details class="empty-state-details daily-news" open={Boolean(yesterdayDate)}>
                    <summary>
                        <span class="disclosure-label"
                            ><Newspaper aria-hidden="true" /><span class="disclosure-title"
                                >Suomalaiset NHL-uutisissa</span
                            ><span class="detail-count"
                                ><span class="detail-count-text">{newsItems.length}</span></span
                            ></span
                        >
                        {#if newsItems[0].source}<span class="news-preview"
                                >{newsItems[0].source}</span
                            >{/if}
                        <ChevronDown class="disclosure-chevron" aria-hidden="true" />
                    </summary>
                    <div class="empty-state-details-content daily-news-list">
                        {#each newsItems as item, index (`${item.url || item.title || index}`)}
                            <article class="daily-news-item">
                                <h4 class="daily-news-title">
                                    {#if item.url}
                                        <a href={item.url} target="_blank" rel="noreferrer">
                                            {item.translatedTitle || item.title}
                                            <ArrowUpRight aria-hidden="true" />
                                        </a>
                                    {:else}
                                        {item.translatedTitle || item.title}
                                    {/if}
                                </h4>
                                {#if item.translatedSummary || item.summary}
                                    <p class="daily-news-summary">
                                        {item.translatedSummary || item.summary}
                                    </p>
                                {/if}
                                <p class="daily-news-source">
                                    {item.source || ''}
                                    {#if item.publishedAt}
                                        · <time datetime={item.publishedAt}
                                            >{formatStartTime(item.publishedAt, true)}</time
                                        >
                                    {/if}
                                </p>
                            </article>
                        {/each}
                    </div>
                </details>
            {/if}
        </div>
    {/if}
</div>

<style>
.empty-state-card {
    width: 100%;
    padding: 0.875rem;
    text-align: left;
    overflow: hidden;
}
.empty-state-header {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
}
.empty-state-icon {
    display: grid;
    place-items: center;
    width: 2.25rem;
    height: 1.75rem;
    flex: 0 0 auto;
    color: var(--accent);
    margin-top: 0.2rem;
}
.empty-state-icon :global(.lucide-icon) {
    width: 1.25rem;
    height: 1.25rem;
}
.empty-state-content {
    min-width: 0;
}
.empty-state-kicker {
    margin: 0 0 0.2rem;
    color: var(--accent);
    font-size: 0.625rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.empty-state-title {
    margin: 0;
    font-family: var(--font-display);
    font-size: 1rem;
    font-weight: 700;
    line-height: 1.4;
    color: var(--color-ink);
}
.empty-state-text {
    margin: 0.2rem 0 0;
    font-size: 0.8125rem;
    line-height: 1.5;
    color: var(--color-muted);
}
.empty-state-meta {
    margin: 0.35rem 0 0;
    color: var(--color-muted);
    font-size: 0.6875rem;
    line-height: 1.5;
}
.empty-state-layout {
    min-width: 0;
}
.empty-state-options {
    min-width: 0;
    margin-top: 0.75rem;
    padding: 0.5rem;
    border: var(--card-border);
    border-radius: var(--card-radius);
    background: var(--card-bg);
    box-shadow: var(--card-shadow);
}
.empty-state-layout--featured .daily-news-list {
    grid-template-columns: minmax(0, 1fr);
}
.empty-state-layout--featured .empty-state-card {
    padding: 1.25rem;
}
.empty-state-layout--featured .empty-state-title {
    font-size: 1.15rem;
}
.empty-state-details {
    margin-top: 0;
    border: var(--card-border);
    border-radius: var(--card-radius-sm);
    background: var(--color-table-head);
}
.empty-state-details + .empty-state-details {
    margin-top: 0.4rem;
}
.empty-state-details > summary {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    min-height: 2.25rem;
    padding: 0.4rem 0.65rem;
    list-style: none;
    cursor: pointer;
    color: var(--accent);
    font-size: 0.8125rem;
    font-weight: 600;
    line-height: 1.4;
}
.empty-state-details > summary::-webkit-details-marker {
    display: none;
}
.empty-state-details > summary:hover {
    background: var(--accent-ice);
}
.disclosure-label {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
}
.disclosure-title,
.detail-count-text {
    display: block;
    text-box-trim: trim-both;
    text-box-edge: cap alphabetic;
}
.disclosure-label :global(svg) {
    width: 0.9rem;
    height: 0.9rem;
    color: var(--color-muted);
}
.empty-state-details :global(.disclosure-chevron) {
    width: 0.9rem;
    height: 0.9rem;
    margin-left: auto;
    color: var(--color-muted);
    transition: transform 160ms ease;
    flex-shrink: 0;
}
.empty-state-details[open] :global(.disclosure-chevron) {
    transform: rotate(180deg);
}
.match-preview {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex: 1;
    gap: 0.35rem;
    min-width: 0;
    height: 1.25rem;
    font-family: var(--font-body);
    font-size: 0.75rem;
    font-weight: 600;
    line-height: 1;
}
.preview-team,
.preview-versus {
    display: block;
    line-height: 1;
    text-box-trim: trim-both;
    text-box-edge: cap alphabetic;
}
.preview-team {
    color: var(--color-ink);
    letter-spacing: 0.025em;
}
.preview-versus {
    color: var(--color-muted);
    font-family: inherit;
    font-size: 0.6875rem;
    font-weight: 600;
    text-box-edge: ex alphabetic;
}
.news-preview {
    flex: 1;
    text-align: right;
    color: var(--color-muted);
    font-size: 0.6875rem;
    font-weight: 500;
}
.empty-state-details > summary:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
}
.detail-count {
    display: inline-grid;
    place-items: center;
    min-width: 1.2rem;
    height: 1.2rem;
    border-radius: var(--card-radius-sm);
    background: var(--accent);
    color: white;
    font-size: 0.625rem;
    font-weight: 600;
}
.empty-state-details-content {
    padding: 0.5rem 0.65rem 0.65rem;
    border-top: var(--card-border);
    background: var(--card-bg);
}
.details-description {
    margin: 0 0 0.4rem;
    color: var(--color-muted);
    font-size: 0.75rem;
    line-height: 1.5;
}
.upcoming-game-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 0.3rem 0.5rem;
    padding: 0.55rem 0;
    border-bottom: var(--card-border);
}
.upcoming-game-row:last-child {
    border-bottom: 0;
}
.team-pair,
.team-chip,
.upcoming-game-aside {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
}
.team-chip {
    color: var(--color-ink);
    font-size: 0.8125rem;
    font-weight: 600;
}
.at-separator {
    color: var(--color-muted);
    font-size: 0.75rem;
}
.upcoming-game-aside {
    gap: 0.75rem;
    color: var(--color-muted);
    font-size: 0.75rem;
    white-space: nowrap;
}
.finn-count {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.2rem 0.35rem;
    border: var(--card-border);
    border-radius: var(--card-radius-sm);
    color: var(--accent);
    font-weight: 600;
}
.finnish-players-names {
    width: 100%;
    margin: 0;
    color: var(--color-muted);
    font-size: 0.75rem;
    line-height: 1.5;
    overflow-wrap: anywhere;
}
.daily-news-list {
    display: grid;
    gap: 0.75rem;
}
.daily-news-item {
    min-width: 0;
}
.daily-news-title {
    margin: 0;
    font-size: 0.8125rem;
    font-weight: 600;
    line-height: 1.5;
}
.daily-news-title a {
    color: var(--accent);
    text-decoration: none;
}
.daily-news-title a:hover {
    text-decoration: underline;
}
.daily-news-title :global(svg) {
    display: inline;
    width: 0.8rem;
    height: 0.8rem;
    vertical-align: middle;
}
.daily-news-summary {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    margin: 0.2rem 0 0;
    color: var(--color-muted);
    font-size: 0.75rem;
    line-height: 1.5;
}
.daily-news-source {
    margin: 0.25rem 0 0;
    color: var(--color-muted);
    font-size: 0.6875rem;
}
@media (min-width: 768px) {
    .daily-news-list {
        grid-template-columns: repeat(3, minmax(0, 1fr));
    }
}
@media (min-width: 1024px) {
    .empty-state-layout--with-options {
        display: grid;
        grid-template-columns: minmax(0, 1.1fr) minmax(0, 1fr);
        gap: 1.5rem;
        align-items: start;
    }
    .empty-state-options {
        margin-top: 0;
    }
}
@media (max-width: 640px) {
    .empty-state-layout--featured .empty-state-card {
        padding: 0.875rem;
    }
    .match-preview,
    .news-preview {
        display: none;
    }
    .empty-state-details > summary {
        gap: 0.4rem;
    }
    .disclosure-label {
        gap: 0.35rem;
        font-size: 0.75rem;
    }
}
</style>
