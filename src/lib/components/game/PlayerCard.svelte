<script>
// @ts-nocheck
import { onMount } from 'svelte'
import { base } from '$app/paths'
import { correctFullName } from '$lib/utils/finnishNameUtils.js'
import {
    formatGameMatchup,
    formatGameScore,
    formatGameVenue,
} from '$lib/utils/gameFormatHelpers.mjs'
import { isPlayerGameLive, shouldShowGameResult } from '$lib/utils/gameStateHelpers.mjs'
import { getLocalHeadshotThumbUrl, getLocalHeadshotUrl } from '$lib/utils/playerHeadshots.js'
import { getTeamColorVariables } from '$lib/utils/teamColors.js'
import './PlayerCard.css'

/** @type {{ player: any }} */
const { player } = $props()

// Reactive variables for player photo
/** @type {string | null} */
let _playerPhotoUrl = $state(null)
let _photoError = $state(false)
let _imageLoading = $state(true)
/** @type {string | null} */
let _lqipUrl = $state(null)

// Get LQIP thumbnail URL (tiny placeholder)
/** @param {string} playerId */
function getLqipUrl(playerId) {
    const url = getLocalHeadshotThumbUrl(playerId)
    return url ? `${base}${url}` : null
}

// Load player image - try local WebP first, fallback to NHL CDN
/** @param {string} playerId */
function loadPlayerImage(playerId) {
    if (!playerId) return

    _imageLoading = true
    _photoError = false

    // Set LQIP placeholder immediately
    _lqipUrl = getLqipUrl(playerId)

    // Try local WebP first
    const localHeadshotUrl = getLocalHeadshotUrl(playerId)
    const localUrl = localHeadshotUrl ? `${base}${localHeadshotUrl}` : null
    const img = new Image()

    img.onload = () => {
        _playerPhotoUrl = localUrl
        _photoError = false
        _imageLoading = false
    }

    img.onerror = () => {
        // Fallback to NHL CDN if local not found
        if (player.headshot_url) {
            const fallbackImg = new Image()
            fallbackImg.onload = () => {
                _playerPhotoUrl = player.headshot_url
                _photoError = false
                _imageLoading = false
            }
            fallbackImg.onerror = () => {
                _photoError = true
                _playerPhotoUrl = null
                _imageLoading = false
            }
            fallbackImg.src = player.headshot_url
        } else {
            _photoError = true
            _playerPhotoUrl = null
            _imageLoading = false
        }
    }

    img.src = localUrl
}

// Load image when player changes
$effect(() => {
    if (player?.playerId) {
        loadPlayerImage(player.playerId)
    }
})
const _photoLoading = $state(true)

let showSeasonStats = $state(false)
let _showComprehensiveDetails = $state(false)
let isFlipped = $state(false)
let expanded = $state(false)
let _isPressed = $state(false)

// Team names are now fetched from API and stored in team_full field
/** @param {string} teamAbbrev */
function getTeamWithCity(teamAbbrev) {
    if (!teamAbbrev) return 'Unknown Team'
    const fullTeamName = player?.team_full || player?.opponent_full
    if (fullTeamName && fullTeamName !== teamAbbrev) {
        return fullTeamName
    }
    return teamAbbrev
}

/** @param {Event} event */
function _toggleSeasonStats(event) {
    if (event) {
        event.preventDefault()
        event.stopPropagation()
    }
    showSeasonStats = !showSeasonStats
}

/** @param {Event} event */
function _closeSeasonStats(event) {
    event.preventDefault()
    event.stopPropagation()
    showSeasonStats = false
}

/** @param {Event} [event] */
function _toggleComprehensiveDetails(event) {
    event?.stopPropagation()
    expanded = !expanded
    if (expanded) {
        _showComprehensiveDetails = true
    }
}

/** @param {Event} event */
function _handleBackdropClick(event) {
    if (event.target === event.currentTarget) {
        showSeasonStats = false
        _showComprehensiveDetails = false
        expanded = false
    }
}

function toggleFlip() {
    isFlipped = !isFlipped
}

/** @param {Event} event */
function _handleCardClick(event) {
    if (event.target.closest('button') || event.target.closest('a')) {
        return
    }
    toggleFlip()
}

function _handlePressStart() {
    _isPressed = true
}

function _handlePressEnd() {
    _isPressed = false
}

const displayName = $derived(
    correctFullName(
        player.name?.default ||
            player.name ||
            player.fullName ||
            player.skaterFullName ||
            'Unknown Player'
    )
)
/** @type {any} */
const gamesData = $derived(globalThis.$games)
const _isLive = $derived(isPlayerGameLive(player, gamesData))
const game = $derived(gamesData?.findGameById?.(player?.game_id) || null)
const gameResult = $derived(player.game_result || player.gameResult || null)
const _showResult = $derived(shouldShowGameResult(player, gamesData) || Boolean(gameResult))
const _teamWithCity = $derived(getTeamWithCity(player.team || 'NHL'))
const _formattedScore = $derived(formatGameScore(player, gamesData))
const _venue = $derived(formatGameVenue(player))
const _matchup = $derived(formatGameMatchup(player, gamesData))
const _playerInitials = $derived(
    displayName
        .split(' ')
        .map((/** @type {string} */ part) => part.charAt(0).toUpperCase())
        .join('')
        .slice(0, 2)
)

// Team color variables
/** @type {Record<string, string>} */
let _teamColorVars = $state({
    '--team-primary-color': '#3b82f6',
    '--team-secondary-color': '#60a5fa',
    '--team-accent-color': '#2563eb',
})

onMount(async () => {
    if (player?.team) {
        try {
            _teamColorVars = await getTeamColorVariables(player.team)
        } catch (_error) {
            // Silently ignore color loading errors
        }
    }
})

$effect(() => {
    if (player?.team) {
        loadTeamColors()
    }
})

async function loadTeamColors() {
    if (player?.team) {
        try {
            _teamColorVars = await getTeamColorVariables(player.team)
        } catch (_error) {
            // Silently ignore color loading errors
        }
    }
}

// Goalie helpers
const isGoalie = $derived(
    (player.position || '').toUpperCase() === 'G' ||
        (player.position || '').toUpperCase() === 'GOALIE'
)
const goalieSavePct = $derived(getSavePercentage(player))
const _hasENG = $derived((player.empty_net_goals || 0) > 0)
const didWin = $derived(['W', 'OTW', 'SOW'].includes(gameResult))
const didLose = $derived(['L', 'OTL', 'SOL'].includes(gameResult))
const _hasResolvedResult = $derived(didWin || didLose)
const hasUnresolvedTiedExtraTime = $derived.by(() => {
    if (!game) return false
    const tied = game.awayScore === game.homeScore
    const wentExtraTime = game.isOT || game.isSO
    const unresolvedResult = !gameResult || gameResult === 'T'
    return tied && wentExtraTime && unresolvedResult
})
const _gameExtraTimeLabel = $derived.by(() => {
    if (!game || hasUnresolvedTiedExtraTime) return ''
    if (game.isSO) return 'VL'
    if (game.isOT) return 'JA'
    return ''
})

/** @param {any} player */
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

const _skaterStatLine = $derived.by(() => {
    if (isGoalie) return ''
    return `${player.goals || 0}+${player.assists || 0}`
})

// Derived stat values for the card
const primaryStat = $derived.by(() => {
    if (isGoalie) {
        return goalieSavePct !== null
            ? { value: goalieSavePct, label: 'Torjunta%', unit: '%' }
            : null
    }
    if (player.points > 0) {
        return { value: player.points, label: 'Pisteet', unit: '' }
    }
    if ((player.plus_minus ?? 0) !== 0) {
        return { value: player.plus_minus ?? player.plusMinus, label: '+/-', unit: '' }
    }
    if ((player.penalty_minutes || 0) > 0) {
        return {
            value: player.penalty_minutes || player.penaltyMinutes,
            label: 'Rangaistusmin',
            unit: '',
        }
    }
    return null
})

// Ring progress: goalie SV% mapped 85-95 to 0-100%, skater points mapped 1-5
const _ringProgress = $derived.by(() => {
    if (!primaryStat) return 0
    if (isGoalie && goalieSavePct !== null) {
        return Math.min(Math.max((goalieSavePct - 85) / 10, 0), 1)
    }
    // Skater points: 1-5 points mapped to 0-100%
    return Math.min(Math.max((player.points - 0.5) / 4.5, 0), 1)
})

// Sub-label with breakdown
const _statBreakdown = $derived.by(() => {
    if (isGoalie) return `${player.saves}/${player.shots_against || player.shotsAgainst}`
    if (player.points > 0 && player.goals > 0 && player.assists > 0) {
        return `${player.goals} maalia + ${player.assists} syöttöä`
    }
    if (player.points > 0 && player.goals > 0) return `${player.goals} maalia`
    if (player.points > 0 && player.assists > 0) return `${player.assists} syöttöä`
    return ''
})

// Action to portal element to body
/** @param {HTMLElement} node */
function _portal(node) {
    const placeholder = document.createElement('div')
    placeholder.className = 'portal-placeholder'
    placeholder.style.cssText = 'display: none;'
    node.parentNode.insertBefore(placeholder, node)
    node._portalPlaceholder = placeholder
    document.body.appendChild(node)

    return {
        update() {
            if (node.parentNode !== document.body) {
                document.body.appendChild(node)
            }
        },
        destroy() {
            if (document.body.contains(node)) {
                document.body.removeChild(node)
            }
            if (node._portalPlaceholder?.parentNode) {
                node._portalPlaceholder.parentNode.removeChild(node._portalPlaceholder)
            }
        },
    }
}

$effect(() => {
    if (showSeasonStats) {
        document.body.style.overflow = 'hidden'
    } else {
        document.body.style.overflow = ''
    }
    return () => {
        document.body.style.overflow = ''
    }
})
</script>

<div class="player-card__container relative w-full" class:goalie-card={isGoalie}>
    <!-- Player Card -->
    <div class="player-card" class:flipped={isFlipped}>
        <!-- Spacer in normal flow to size container -->
        <div class="player-card__spacer" aria-hidden="true"></div>
        <div class="player-card__inner">
            <!-- Front of Card -->
            <div
                class="card"
                class:pressed={isPressed}
                class:expanded
                class:flipped={isFlipped}
                style="--accent: {teamColorVars['--team-primary-color']}"
                onclick={handleCardClick}
                onpointerdown={handlePressStart}
                onpointerup={handlePressEnd}
                onpointerleave={handlePressEnd}
                role="button"
                tabindex="0"
                onkeydown={(e) => e.key === "Enter" && handleCardClick(e)}
                aria-label="Click to flip player card"
                in:scale={{ duration: 220, start: 0.96 }}
            >
                <!-- Team color glow -->
                <div class="card__glow" aria-hidden="true"></div>

                <!-- Faint background logo watermark -->
                <div class="card__watermark" aria-hidden="true">
                    <TeamLogo team={player.team || "NHL"} size="120" />
                </div>

                <!-- Top accent stripe -->
                <div class="card__stripe" aria-hidden="true"></div>

                <div class="card__content">
                    <!-- Header: name + badges -->
                    <div class="card__top">
                        <div class="card__player-info">
                            <h3 class="card__name">{displayName}</h3>
                            <p class="card__team">
                                {player.position || player.positionCode || "N/A"}
                                {#if player.jersey_number || player.jerseyNumber}
                                    <span class="card__dot">·</span>
                                    <span>#{player.jersey_number || player.jerseyNumber}</span>
                                {/if}
                            </p>
                        </div>
                        <div class="card__corner-logo">
                            <TeamLogo team={player.team || "NHL"} size="36" />
                        </div>
                    </div>

                    <!-- Team row -->
                    <div class="card__team-row">
                        <span class="card__team-name-text">{teamWithCity}</span>
                    </div>

                    {#if venue}
                        <div class="card_venue">{venue}</div>
                    {/if}

                    <!-- Game summary -->
                    <div
                        class="card__gamebar"
                        class:card__gamebar--live={isLive}
                        class:card__gamebar--win={didWin}
                        class:card__gamebar--loss={didLose}
                    >
                        <div class="card__gamebar-main">
                            <span class="card__gamebar-matchup">{matchup}</span>
                            {#if isLive}
                                <span class="card__gamebar-status card__gamebar-status--live">LIVE</span>
                            {/if}
                        </div>
                        {#if formattedScore}
                            <div class="card__gamebar-score-wrap">
                                {#if !isLive && hasResolvedResult}
                                    <span
                                        class="card__gamebar-result"
                                        class:card__gamebar-result--win={didWin}
                                        class:card__gamebar-result--loss={didLose}
                                    >
                                        {didWin ? 'V' : didLose ? 'H' : ''}
                                    </span>
                                {/if}
                                <span class="card__gamebar-score">{formattedScore}</span>
                                {#if gameExtraTimeLabel}
                                    <span class="card__gamebar-extra-time">{gameExtraTimeLabel}</span>
                                {/if}
                            </div>
                        {/if}
                    </div>

                    <!-- Primary stat -->
                    {#if !isGoalie && primaryStat}
                        <div class="card__hero card__hero--skater">
                            <div class="card__hero-value-wrap">
                                <span class="card__hero-value">{primaryStat.value}</span>
                                <span class="card__hero-unit">p</span>
                            </div>
                            <div class="card__hero-meta">
                                <strong>{skaterStatLine}</strong>
                                {#if statBreakdown}
                                    <small>{statBreakdown}</small>
                                {/if}
                            </div>
                        </div>
                    {:else if primaryStat}
                        <div class="card__stat">
                            <div class="card__ring" style="--accent: {teamColorVars['--team-primary-color']}; --progress: {ringProgress * 360}deg">
                                <span>{primaryStat.value}{primaryStat.unit}</span>
                            </div>
                            <div class="card__stat-meta">
                                <strong>{primaryStat.label}</strong>
                                {#if statBreakdown}
                                    <small>{statBreakdown}</small>
                                {/if}
                            </div>
                        </div>
                    {:else}
                        <div class="card__stat">
                            <div class="card__ring card__ring--empty">
                                <span>–</span>
                            </div>
                            <div class="card__stat-meta">
                                <strong>Ei tilastoja</strong>
                            </div>
                        </div>
                    {/if}

                    <!-- Supporting stats row -->
                    <div class="card__sub-stats">
                        {#if isGoalie}
                            <div class="card__sub-stat" title="Päästetyt maalit">
                                <span
                                    class="card__sub-stat-value"
                                    style="color: {player.goals_against === 0 ? 'var(--accent)' : player.goals_against >= 4 ? '#ef4444' : undefined}"
                                >{player.goals_against}</span>
                                <span class="card__sub-stat-label">pääst.</span>
                            </div>
                            {#if hasENG}
                                <div class="card__sub-stat" title="Tyhjään maaliin">
                                    <span class="card__sub-stat-value text-red-500">{player.empty_net_goals}</span>
                                    <span class="card__sub-stat-label">tyhjä</span>
                                </div>
                            {/if}
                        {:else}
                            {#if player.goals > 0}
                                <div class="card__sub-stat" title="Maalit">
                                    <span class="card__sub-stat-value">{player.goals}</span>
                                    <span class="card__sub-stat-label">maalit</span>
                                </div>
                            {/if}
                            {#if player.assists > 0}
                                <div class="card__sub-stat" title="Syötöt">
                                    <span class="card__sub-stat-value">{player.assists}</span>
                                    <span class="card__sub-stat-label">syötöt</span>
                                </div>
                            {/if}
                            {#if (player.plus_minus ?? 0) !== 0}
                                <div class="card__sub-stat" title="Plus-miinus">
                                    <span
                                        class="card__sub-stat-value"
                                        style="color: {(player.plus_minus ?? 0) >= 0 ? '#10b981' : '#ef4444'}"
                                    >{(player.plus_minus ?? 0) > 0 ? '+' : ''}{player.plus_minus ?? player.plusMinus}</span>
                                    <span class="card__sub-stat-label">+/-</span>
                                </div>
                            {/if}
                            {#if (player.penalty_minutes || 0) > 0}
                                <div class="card__sub-stat" title="Rangaistusminuutit">
                                    <span class="card__sub-stat-value text-amber-600">{player.penalty_minutes || player.penaltyMinutes}</span>
                                    <span class="card__sub-stat-label">jäähyt</span>
                                </div>
                            {/if}
                        {/if}
                    </div>

                    <!-- Expanded details -->
                    {#if expanded}
                        <div class="card__details" transition:fly={{ y: 8, duration: 180 }}>
                            {#if venue}
                                <div class="card__detail-row">
                                    <span class="card__detail-label">Paikka</span>
                                    <span>{venue}</span>
                                </div>
                            {/if}
                            {#if player.time_on_ice}
                                <div class="card__detail-row">
                                    <span class="card__detail-label">Aika</span>
                                    <span>{player.time_on_ice}</span>
                                </div>
                            {/if}
                            {#if !isGoalie && player.shots !== undefined}
                                <div class="card__detail-row">
                                    <span class="card__detail-label">Laukaukset</span>
                                    <span>{player.shots}</span>
                                </div>
                            {/if}
                            <div class="card__detail-actions">
                                <button
                                    class="card__detail-btn"
                                    onclick={(e) => { e.stopPropagation(); showComprehensiveDetails = true; }}
                                >
                                    Avaa kaikki tiedot
                                </button>
                            </div>
                        </div>
                    {/if}

                    <!-- Footer -->
                    <div class="card__footer">
                        <span class="card__footer-hint">Napauta kääntääksesi</span>
                        <button
                            class="card__footer-btn"
                            onclick={(e) => { e.stopPropagation(); toggleComprehensiveDetails(e); }}
                            aria-label="Näytä tarkemmat tiedot"
                        >
                            Tiedot
                        </button>
                    </div>
                </div>
            </div>

            <!-- Back of Card -->
            <div
                class="card card--back"
                class:pressed={isPressed}
                class:expanded
                class:flipped={isFlipped}
                style="--accent: {teamColorVars['--team-primary-color']}"
                onclick={handleCardClick}
                onpointerdown={handlePressStart}
                onpointerup={handlePressEnd}
                onpointerleave={handlePressEnd}
                role="button"
                tabindex="0"
                onkeydown={(e) => e.key === "Enter" && handleCardClick(e)}
                aria-label="Click to flip player card back"
            >
                <!-- Team color glow -->
                <div class="card__glow" aria-hidden="true"></div>

                <!-- Team logo watermark -->
                <div class="card__watermark" aria-hidden="true">
                    <TeamLogo team={player.team || "NHL"} size="100" />
                </div>

                <!-- Top accent stripe -->
                <div class="card__stripe" aria-hidden="true"></div>

                <div class="card__content">
                    <!-- Header -->
                    <div class="card__top">
                        <div class="card__player-info">
                            <h3 class="card__name">{displayName}</h3>
                            <p class="card__team">{teamWithCity}</p>
                        </div>
                    </div>

                    <!-- Back card additional stats -->
                    <div class="card__back-stats">
                        {#if isGoalie}
                            <div class="card__back-stat" title="Torjunnat">
                                <div class="card__back-stat-value">{player.saves}</div>
                                <div class="card__back-stat-label">Torjunnat</div>
                            </div>
                            {#if player.shots_against !== undefined}
                                <div class="card__back-stat" title="Laukaukset kohti">
                                    <div class="card__back-stat-value">{player.shots_against}</div>
                                    <div class="card__back-stat-label">Laukaukset</div>
                                </div>
                            {/if}
                            <div class="card__back-stat" title="Päästetyt maalit">
                                <div class="card__back-stat-value">{player.goals_against}</div>
                                <div class="card__back-stat-label">Päästetyt</div>
                            </div>
                            {#if goalieSavePct !== null}
                                <div class="card__back-stat" title="Torjuntaprosentti">
                                    <div class="card__back-stat-value">{goalieSavePct}%</div>
                                    <div class="card__back-stat-label">Torjunta%</div>
                                </div>
                            {/if}
                        {:else}
                            {#if player.shots !== undefined && player.shots >= 0}
                                <div class="card__back-stat">
                                    <div class="card__back-stat-value">{player.shots}</div>
                                    <div class="card__back-stat-label">Laukaukset</div>
                                </div>
                            {/if}
                            {#if player.hits !== undefined && player.hits >= 0}
                                <div class="card__back-stat">
                                    <div class="card__back-stat-value">{player.hits}</div>
                                    <div class="card__back-stat-label">Taklaukset</div>
                                </div>
                            {/if}
                            {#if player.blocked_shots !== undefined && player.blocked_shots >= 0}
                                <div class="card__back-stat">
                                    <div class="card__back-stat-value">{player.blocked_shots}</div>
                                    <div class="card__back-stat-label">Blokit</div>
                                </div>
                            {/if}
                            {#if player.takeaways !== undefined && player.takeaways >= 0}
                                <div class="card__back-stat">
                                    <div class="card__back-stat-value">{player.takeaways}</div>
                                    <div class="card__back-stat-label">Riistot</div>
                                </div>
                            {/if}
                            {#if player.giveaways !== undefined && player.giveaways >= 0}
                                <div class="card__back-stat">
                                    <div class="card__back-stat-value">{player.giveaways}</div>
                                    <div class="card__back-stat-label">Menetykset</div>
                                </div>
                            {/if}
                            {#if player.faceoff_wins !== undefined && player.faceoffs_taken !== undefined && player.faceoffs_taken > 0}
                                <div class="card__back-stat">
                                    <div class="card__back-stat-value">{player.faceoff_wins}/{player.faceoffs_taken}</div>
                                    <div class="card__back-stat-label">Aloitukset</div>
                                </div>
                            {/if}
                        {/if}
                        {#if player.time_on_ice}
                            <div class="card__time-on-ice">
                                Aika kentällä: <strong>{player.time_on_ice}</strong>
                            </div>
                        {/if}
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Season Stats Modal -->
{#if showSeasonStats}
    <div
        use:portal
        class="fixed inset-0 bg-black/50 backdrop-blur-sm z-[100] flex modal-safe-overlay modal-overlay-mobile md:modal-overlay-desktop pointer-events-auto"
        onclick={handleBackdropClick}
        role="button"
        tabindex="0"
        onkeydown={(e) => e.key === "Escape" && closeSeasonStats(e)}
        aria-label="Close modal"
    >
        <div
            class="bg-white shadow-2xl w-full max-w-lg max-h-[100vh] overflow-y-auto relative modal-dialog-mobile md:rounded-xl"
            role="dialog"
            tabindex="-1"
            aria-modal="true"
            aria-labelledby="season-stats-title"
        >
            <div class="bg-gray-50 px-6 py-4 border-b border-gray-100 flex items-center gap-4">
                <div class="player-card__modal-avatar shrink-0">
                    {#if playerPhotoUrl && !photoError}
                        <img
                            src={playerPhotoUrl || player.headshot_url}
                            alt={displayName}
                            class="player-card__modal-photo"
                            class:blurred={photoLoading || imageLoading}
                            onload={() => { photoLoading = false; imageLoading = false; }}
                            onerror={() => { photoError = true; photoLoading = false; imageLoading = false; }}
                        />
                        {#if (photoLoading || imageLoading) && lqipUrl}
                            <img src={lqipUrl} alt="" class="player-card__modal-photo-lqip" />
                        {/if}
                    {:else if lqipUrl}
                        <img src={lqipUrl} alt="" class="player-card__modal-photo-lqip" />
                    {:else}
                        <div class="player-card__modal-initials">{playerInitials}</div>
                    {/if}
                </div>
                <div>
                    <h3 id="season-stats-title" class="text-lg font-bold text-gray-900">{displayName}</h3>
                    <div class="text-sm text-gray-500 flex items-center gap-2">
                        <span>{teamWithCity}</span>
                        <span>•</span>
                        <span>Kauden 2024-2025 tilastot</span>
                    </div>
                </div>
                <button
                    class="ml-auto p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
                    onclick={closeSeasonStats}
                    aria-label="Sulje"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                    </svg>
                </button>
            </div>
            <div class="p-6">
                <div class="grid grid-cols-2 gap-4">
                    <div class="bg-gray-50 p-4 rounded-lg text-center">
                        <div class="text-2xl font-bold text-gray-900">{player.season_goals || 0}</div>
                        <div class="text-xs text-gray-500 uppercase tracking-wider mt-1">Maalit</div>
                    </div>
                    <div class="bg-gray-50 p-4 rounded-lg text-center">
                        <div class="text-2xl font-bold text-gray-900">{player.season_assists || 0}</div>
                        <div class="text-xs text-gray-500 uppercase tracking-wider mt-1">Syötöt</div>
                    </div>
                    <div class="bg-finnish-blue-50 p-4 rounded-lg text-center col-span-2 border border-finnish-blue-100">
                        <div class="text-3xl font-bold text-finnish-blue-600">{player.season_points || 0}</div>
                        <div class="text-xs text-finnish-blue-600 uppercase tracking-wider mt-1 font-medium">Pisteet yhteensä</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
{/if}

{#if showComprehensiveDetails}
    <ComprehensivePlayerDetails
        {player}
        isOpen={showComprehensiveDetails}
        onclose={() => (showComprehensiveDetails = false)}
    />
{/if}
