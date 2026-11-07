<script>
// @ts-nocheck

import { X } from 'lucide-svelte'
import { base } from '$app/paths'
import TeamLogo from '$lib/components/ui/TeamLogo.svelte'

const { player, isOpen = false, onclose, venue = '' } = $props()

let _playerPhotoUrl = $state(null)
let _lqipUrl = $state(null)

function getLocalHeadshotUrl(playerId) {
    if (!playerId) return null
    return `${base}/headshots/${playerId}.webp`
}

function loadPlayerImage(playerId) {
    if (!playerId) return
    _lqipUrl = getLocalHeadshotUrl(playerId)

    const localUrl = getLocalHeadshotUrl(playerId)
    const img = new Image()

    img.onload = () => {
        _playerPhotoUrl = localUrl
    }

    img.onerror = () => {
        if (player.headshot_url) {
            _playerPhotoUrl = player.headshot_url
        } else {
            _playerPhotoUrl = null
        }
    }

    img.src = localUrl
}

$effect(() => {
    if (player?.playerId) {
        loadPlayerImage(player.playerId)
    }
})

function portal(node) {
    const placeholder = document.createElement('div')
    placeholder.className = 'portal-placeholder'
    placeholder.style.cssText = 'display: none;'
    node.parentNode.insertBefore(placeholder, node)
    node._portalPlaceholder = placeholder
    const previousFocus = document.activeElement
    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    document.body.appendChild(node)
    node.querySelector('button')?.focus()
    return {
        update() {
            if (node.parentNode !== document.body) {
                document.body.appendChild(node)
            }
        },
        destroy() {
            document.body.style.overflow = previousOverflow
            if (previousFocus?.isConnected) previousFocus.focus()
            if (document.body.contains(node)) {
                document.body.removeChild(node)
            }
            if (node._portalPlaceholder?.parentNode) {
                node._portalPlaceholder.parentNode.removeChild(node._portalPlaceholder)
            }
        },
    }
}

const displayName = $derived(player.name?.default || player.name || 'Unknown Player')
const _playerInitials = $derived(
    displayName
        .split(' ')
        .map((p) => p.charAt(0).toUpperCase())
        .join('')
        .slice(0, 2)
)
const isGoalie = $derived(
    (player.position || '').toUpperCase() === 'G' ||
        (player.position || '').toUpperCase() === 'GOALIE'
)
const _goalieSavePct = $derived(getSavePercentage(player))

function getSavePercentage(player) {
    const provided = player.save_percentage ?? player.savePercentage
    if (typeof provided === 'number' && provided > 0) {
        return Number(provided > 1 ? provided : (provided * 100).toFixed(1))
    }
    const saves = Number(player.saves ?? player.goalie_saves)
    const shotsAgainst = Number(player.shots_against ?? player.shotsAgainst)
    if (Number.isFinite(saves) && Number.isFinite(shotsAgainst) && shotsAgainst > 0) {
        return Number(((saves / shotsAgainst) * 100).toFixed(1))
    }
    return null
}

function handleBackdropClick(e) {
    if (e.target === e.currentTarget) {
        onclose?.()
    }
}

function handleKeydown(event) {
    if (event.key === 'Escape') {
        event.preventDefault()
        onclose?.()
    }
    if (event.key === 'Tab') {
        const buttons = event.currentTarget.querySelectorAll('button, a[href], [tabindex="0"]')
        const first = buttons[0]
        const last = buttons[buttons.length - 1]
        if (event.shiftKey && document.activeElement === first) {
            event.preventDefault()
            last?.focus()
        } else if (!event.shiftKey && document.activeElement === last) {
            event.preventDefault()
            first?.focus()
        }
    }
}
</script>

{#if isOpen}
    <div
        use:portal
        class="player-details-backdrop dashboard-theme"
        onclick={handleBackdropClick}
        onkeydown={handleKeydown}
        role="presentation"
    >
        <div
            class="player-details-dialog"
            role="dialog"
            aria-modal="true"
            aria-labelledby="player-details-title"
            tabindex="-1"
        >
            <header class="details-header">
                {#if _playerPhotoUrl || _lqipUrl}
                    <img
                        src={_playerPhotoUrl || _lqipUrl}
                        alt=""
                        class="player-photo"
                        onerror={() => {
                            _playerPhotoUrl = null
                            _lqipUrl = null
                        }}
                    />
                {:else}
                    <div class="player-photo player-initials" aria-hidden="true">
                        {_playerInitials}
                    </div>
                {/if}
                <div class="player-identity">
                    <p class="details-kicker">Pelaajan ottelutilastot</p>
                    <h2 id="player-details-title">{displayName}</h2>
                    <p class="player-team">{player.team_full || player.team}</p>
                    {#if venue}<p class="player-venue">{venue}</p>{/if}
                </div>
                <button
                    class="details-close"
                    type="button"
                    onclick={onclose}
                    aria-label="Sulje pelaajan lisätiedot"
                    >Sulje <X size={16} aria-hidden="true" /></button
                >
            </header>

            <div class="details-body">
                <section class="details-panel" aria-labelledby="game-stats-title">
                    <h3 id="game-stats-title">Pelin tilastot</h3>
                    <dl class="stats-grid">
                        {#if isGoalie}
                            <div>
                                <dt>Torjunta-%</dt>
                                <dd>{_goalieSavePct === null ? '—' : _goalieSavePct + '%'}</dd>
                            </div>
                            <div>
                                <dt>Torjunnat</dt>
                                <dd>{player.saves || 0}</dd>
                            </div>
                            {#if player.shots_against !== undefined}<div>
                                    <dt>Laukaukset</dt>
                                    <dd>{player.shots_against}</dd>
                                </div>{/if}
                            <div>
                                <dt>Päästetyt</dt>
                                <dd>{player.goals_against || 0}</dd>
                            </div>
                        {:else}
                            <div>
                                <dt>Maalit</dt>
                                <dd>{player.goals || 0}</dd>
                            </div>
                            <div>
                                <dt>Syötöt</dt>
                                <dd>{player.assists || 0}</dd>
                            </div>
                            <div>
                                <dt>Pisteet</dt>
                                <dd>{player.points || 0}</dd>
                            </div>
                            <div>
                                <dt>Plus/miinus</dt>
                                <dd
                                    class:positive={player.plus_minus > 0}
                                    class:negative={player.plus_minus < 0}
                                >
                                    {player.plus_minus > 0 ? '+' : ''}{player.plus_minus ?? 0}
                                </dd>
                            </div>
                        {/if}
                        {#if player.time_on_ice}<div>
                                <dt>Peliaika</dt>
                                <dd>{player.time_on_ice}</dd>
                            </div>{/if}
                    </dl>
                </section>

                {#if !isGoalie && (player.shots || player.hits || player.blocked_shots || player.takeaways || player.giveaways)}
                    <section class="details-panel" aria-labelledby="additional-stats-title">
                        <h3 id="additional-stats-title">Muut tilastot</h3>
                        <dl class="stats-grid secondary-stats">
                            {#if player.shots > 0}<div>
                                    <dt>Laukaukset</dt>
                                    <dd>{player.shots}</dd>
                                </div>{/if}
                            {#if player.hits > 0}<div>
                                    <dt>Taklaukset</dt>
                                    <dd>{player.hits}</dd>
                                </div>{/if}
                            {#if player.blocked_shots > 0}<div>
                                    <dt>Blokit</dt>
                                    <dd>{player.blocked_shots}</dd>
                                </div>{/if}
                            {#if player.takeaways > 0}<div>
                                    <dt>Riistot</dt>
                                    <dd>{player.takeaways}</dd>
                                </div>{/if}
                            {#if player.giveaways > 0}<div>
                                    <dt>Menetykset</dt>
                                    <dd>{player.giveaways}</dd>
                                </div>{/if}
                        </dl>
                        {#if player.shots > 0 && player.goals > 0}
                            <p class="shooting-percentage">
                                Laukaisuprosentti <strong
                                    >{((player.goals / player.shots) * 100)
                                        .toFixed(1)
                                        .replace('.', ',')} %</strong
                                >
                            </p>
                        {/if}
                    </section>
                {/if}

                {#if player.recent_results?.length > 0}
                    <section class="recent-games" aria-labelledby="recent-games-title">
                        <h3 id="recent-games-title">
                            Viimeisimmät pelit <span class="game-count"
                                >{Math.min(player.recent_results.length, 5)}</span
                            >
                        </h3>
                        <div class="recent-games-list">
                            {#each player.recent_results.slice(0, 5) as game}
                                {@const isWin = ['W', 'OTW', 'SOW'].includes(game.result)}
                                <div class="recent-game">
                                    <time datetime={game.date}
                                        >{parseInt(game.date.split('-')[2])}.{parseInt(
                                            game.date.split('-')[1]
                                        )}.</time
                                    >
                                    <div class="opponent">
                                        <TeamLogo team={game.opponent} size="28" /><span
                                            >{game.opponent_full || game.opponent}</span
                                        >
                                    </div>
                                    <span
                                        class="game-score"
                                        class:win={isWin}
                                        class:loss={!isWin}
                                        aria-label={`${isWin ? 'Voitto' : 'Tappio'} ${game.team_score}–${game.opponent_score}`}
                                        >{game.team_score}–{game.opponent_score}</span
                                    >
                                    <dl class="recent-stats">
                                        {#if isGoalie}
                                            <div>
                                                <dt>Torj.</dt>
                                                <dd>{game.saves ?? 0}</dd>
                                            </div>
                                            <div>
                                                <dt>Pääst.</dt>
                                                <dd>{game.goals_against ?? 0}</dd>
                                            </div>
                                        {:else}
                                            <div>
                                                <dt>M</dt>
                                                <dd>{game.goals ?? 0}</dd>
                                            </div>
                                            <div>
                                                <dt>S</dt>
                                                <dd>{game.assists ?? 0}</dd>
                                            </div>
                                            <div>
                                                <dt>P</dt>
                                                <dd>{game.points ?? 0}</dd>
                                            </div>
                                        {/if}
                                    </dl>
                                </div>
                            {/each}
                        </div>
                    </section>
                {/if}
            </div>
        </div>
    </div>
{/if}

<style>
.player-details-backdrop {
    position: fixed;
    inset: 0;
    z-index: 100;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1rem;
    background: rgba(12, 36, 68, 0.32);
    backdrop-filter: blur(6px);
    color: var(--color-ink);
}
.player-details-dialog {
    width: min(100%, 42rem);
    max-height: calc(100dvh - 2rem);
    overflow-y: auto;
    overscroll-behavior: contain;
    background: var(--card-bg);
    border: 1px solid var(--color-panel-border);
    border-radius: var(--card-radius);
    box-shadow:
        0 20px 60px rgba(25, 64, 113, 0.24),
        inset 0 0 0 1px white;
}
.details-header {
    display: flex;
    align-items: center;
    gap: 0.875rem;
    padding: 1.25rem;
    border-bottom: 1px solid var(--color-panel-border);
    background: linear-gradient(115deg, #f8fbff, #e4f0ff);
}
.player-photo {
    width: 64px;
    height: 64px;
    flex-shrink: 0;
    object-fit: cover;
    border-radius: 50%;
    background: white;
    border: 1px solid var(--color-panel-border);
}
.player-initials {
    display: grid;
    place-items: center;
    font-weight: 700;
    color: var(--accent);
}
.player-identity {
    flex: 1;
    min-width: 0;
}
.details-kicker {
    margin: 0 0 0.2rem;
    font-size: 0.65rem;
    font-weight: 700;
    color: var(--accent);
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
h2 {
    margin: 0;
    font-family: var(--font-display);
    font-size: clamp(1rem, 3vw, 1.25rem);
    font-weight: 750;
    line-height: 1.3;
}
.player-team,
.player-venue {
    margin: 0.2rem 0 0;
    color: var(--color-muted);
    font-size: 0.8rem;
    line-height: 1.4;
}
.player-venue {
    font-size: 0.72rem;
}
.details-close {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.4rem;
    align-self: flex-start;
    min-height: 2.25rem;
    padding: 0.4rem 0.65rem;
    border: 1px solid var(--color-panel-border);
    border-radius: 8px;
    background: #f8fbff;
    color: var(--accent);
    font-size: 0.75rem;
    font-weight: 700;
    cursor: pointer;
}
.details-close:hover {
    background: #deebfc;
}
.details-close:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 3px;
}
.details-body {
    padding: 1rem 1.25rem 1.25rem;
    display: grid;
    gap: 0.875rem;
}
.details-panel {
    padding: 0.875rem;
    background: rgba(237, 246, 255, 0.7);
    border: 1px solid var(--color-panel-border);
    border-radius: 10px;
}
h3 {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin: 0 0 0.75rem;
    color: var(--accent-ink);
    font-size: 0.85rem;
    font-weight: 750;
}
dl {
    margin: 0;
}
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(4.5rem, 1fr));
    gap: 0.5rem;
}
.stats-grid > div {
    display: flex;
    flex-direction: column-reverse;
    align-items: center;
    justify-content: center;
    min-height: 3.5rem;
    padding: 0.4rem 0.2rem;
    border-radius: 6px;
    background: rgba(255, 255, 255, 0.65);
}
dt {
    color: var(--color-muted);
    font-size: 0.65rem;
}
dd {
    margin: 0;
    font-size: 1.3rem;
    font-weight: 750;
    font-variant-numeric: tabular-nums;
}
.positive {
    color: #087a29;
}
.negative {
    color: #c62828;
}
.secondary-stats dd {
    font-size: 1.05rem;
}
.shooting-percentage {
    display: flex;
    justify-content: space-between;
    margin: 0.75rem 0 0;
    padding-top: 0.65rem;
    border-top: 1px solid var(--color-panel-border);
    font-size: 0.72rem;
    color: var(--color-muted);
}
.shooting-percentage strong {
    color: var(--color-ink);
}
.game-count {
    display: inline-grid;
    place-items: center;
    min-width: 1.25rem;
    height: 1.25rem;
    border-radius: 5px;
    background: var(--accent);
    color: white;
    font-size: 0.7rem;
}
.recent-games-list {
    border: 1px solid var(--color-panel-border);
    border-radius: 10px;
    overflow: hidden;
    background: rgba(255, 255, 255, 0.45);
}
.recent-game {
    display: grid;
    grid-template-columns: 2.75rem minmax(0, 1fr) auto 6.5rem;
    align-items: center;
    gap: 0.65rem;
    padding: 0.65rem 0.75rem;
}
.recent-game + .recent-game {
    border-top: 1px solid #dce9f8;
}
time {
    color: var(--color-muted);
    font-size: 0.72rem;
    font-variant-numeric: tabular-nums;
}
.opponent {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    min-width: 0;
    font-size: 0.78rem;
    font-weight: 600;
}
.opponent span {
    overflow-wrap: anywhere;
}
.game-score {
    padding: 0.2rem 0.45rem;
    border-radius: 5px;
    font-size: 0.8rem;
    font-weight: 750;
    font-variant-numeric: tabular-nums;
    white-space: nowrap;
}
.win {
    color: #086227;
    background: #e1f7e5;
    border: 1px solid #c5edce;
}
.loss {
    color: #b42323;
    background: #fff0f0;
    border: 1px solid #ffd4d4;
}
.recent-stats {
    display: flex;
    justify-content: flex-end;
    gap: 0.65rem;
}
.recent-stats > div {
    display: flex;
    align-items: baseline;
    gap: 0.2rem;
}
.recent-stats dd {
    font-size: 0.8rem;
}
@media (max-width: 480px) {
    .details-header {
        padding: 1rem;
        gap: 0.65rem;
        flex-wrap: wrap;
    }
    .player-photo {
        width: 48px;
        height: 48px;
    }
    .details-close {
        margin-left: auto;
    }
    .details-body {
        padding: 0.875rem;
    }
    .recent-game {
        grid-template-columns: 2.5rem minmax(0, 1fr) auto;
        gap: 0.4rem;
    }
    .recent-stats {
        grid-column: 2 / -1;
        justify-content: flex-start;
    }
    .stats-grid {
        grid-template-columns: repeat(auto-fit, minmax(4rem, 1fr));
    }
}
</style>
