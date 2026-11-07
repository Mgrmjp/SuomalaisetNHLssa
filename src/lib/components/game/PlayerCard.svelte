<script>
// @ts-nocheck

import { MapPin, PanelsTopLeft, Rotate3D, X } from 'lucide-svelte'
import { tick } from 'svelte'
import { scale } from 'svelte/transition'
import { base } from '$app/paths'
import TeamLogo from '$lib/components/ui/TeamLogo.svelte'
import { games } from '$lib/stores/gameData.js'
import { dailyPlayerPoints } from '$lib/utils/dailyPlayers.js'
import { correctFullName } from '$lib/utils/finnishNameUtils.js'
import { fiAssists, fiGoals, fiPoints } from '$lib/utils/finnishPlural.js'
import {
    formatGameMatchup,
    formatGameScore,
    formatGameVenue,
} from '$lib/utils/gameFormatHelpers.mjs'
import { isPlayerGameLive, shouldShowGameResult } from '$lib/utils/gameStateHelpers.mjs'
import { getLocalHeadshotThumbUrl, getLocalHeadshotUrl } from '$lib/utils/playerHeadshots.js'
import ComprehensivePlayerDetails from './ComprehensivePlayerDetails.svelte'
import './PlayerCard.css'

const { player, highlight = null } = $props()
const cardId = $props.id()

// Reactive variables for player photo
let playerPhotoUrl = $state(null)
let _photoError = $state(false)
let _imageLoading = $state(true)
let _lqipUrl = $state(null)

// Get LQIP thumbnail URL (tiny placeholder)
function getLqipUrl(playerId) {
    const url = getLocalHeadshotThumbUrl(playerId)
    return url ? `${base}${url}` : null
}

// Load player image - try local WebP first, fallback to NHL CDN
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
        playerPhotoUrl = localUrl
        _photoError = false
        _imageLoading = false
    }

    img.onerror = () => {
        // Fallback to NHL CDN if local not found
        if (player.headshot_url) {
            const fallbackImg = new Image()
            fallbackImg.onload = () => {
                playerPhotoUrl = player.headshot_url
                _photoError = false
                _imageLoading = false
            }
            fallbackImg.onerror = () => {
                _photoError = true
                playerPhotoUrl = null
                _imageLoading = false
            }
            fallbackImg.src = player.headshot_url
        } else {
            _photoError = true
            playerPhotoUrl = null
            _imageLoading = false
        }
    }

    img.src = localUrl
}

let showSeasonStats = $state(false)

// Load season image only when it is needed.
$effect(() => {
    if (showSeasonStats && player?.playerId) {
        loadPlayerImage(player.playerId)
    }
})
let _photoLoading = $state(true)

let showComprehensiveDetails = $state(false)
let isFlipped = $state(false)
let frontCard = $state(null)
let backCard = $state(null)
let isPressed = $state(false)

// Team names are now fetched from API and stored in team_full field
function getTeamWithCity(teamAbbrev) {
    if (!teamAbbrev) return 'Unknown Team'
    const fullTeamName = player?.team_full || player?.opponent_full
    if (fullTeamName && fullTeamName !== teamAbbrev) {
        return fullTeamName
    }
    return teamAbbrev
}

function _toggleSeasonStats(event) {
    if (event) {
        event.preventDefault()
        event.stopPropagation()
    }
    showSeasonStats = !showSeasonStats
}

function _closeSeasonStats(event) {
    event.preventDefault()
    event.stopPropagation()
    showSeasonStats = false
}

function _handleBackdropClick(event) {
    if (event.target === event.currentTarget) {
        showSeasonStats = false
        showComprehensiveDetails = false
    }
}

function toggleFlip() {
    isFlipped = !isFlipped
}

function _flipFromControl(event) {
    event.stopPropagation()
    toggleFlip()
    tick().then(() => (isFlipped ? backCard : frontCard)?.focus())
}

function _handleCardClick(event) {
    if (event.target.closest('button') || event.target.closest('a')) {
        return
    }
    toggleFlip()
}

function _handleCardKeydown(event) {
    if (event.target !== event.currentTarget) return
    if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault()
        _flipFromControl(event)
    }
}

function _handlePressStart() {
    isPressed = true
}

function _handlePressEnd() {
    isPressed = false
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
const gamesData = $derived($games)
const _isLive = $derived(isPlayerGameLive(player, gamesData))
const _game = $derived(gamesData?.findGameById?.(player?.game_id) || null)
const gameResult = $derived(player.game_result || player.gameResult || null)
const _showResult = $derived(shouldShowGameResult(player, gamesData) || Boolean(gameResult))
const _teamWithCity = $derived(getTeamWithCity(player.team || 'NHL'))
const _formattedScore = $derived(formatGameScore(player, gamesData))
const _venue = $derived(formatGameVenue(player))
const _matchup = $derived(formatGameMatchup(player, gamesData))
const _matchupTeams = $derived(_matchup.includes(' @ ') ? _matchup.split(' @ ') : null)
// The stored score is player-relative; align it with the away/home logos here.
const _matchupScore = $derived(
    _matchupTeams && _matchupTeams[0] !== player.team
        ? _formattedScore.split('-').reverse().join('–')
        : _formattedScore.replace('-', '–')
)
const _playerInitials = $derived(
    displayName
        .split(' ')
        .map((part) => part.charAt(0).toUpperCase())
        .join('')
        .slice(0, 2)
)

// Goalie helpers
const isGoalie = $derived(
    (player.position || '').toUpperCase() === 'G' ||
        (player.position || '').toUpperCase() === 'GOALIE'
)
const goalieSavePct = $derived(getSavePercentage(player))
const _hasENG = $derived((player.empty_net_goals || 0) > 0)

const _didWin = $derived(['W', 'OTW', 'SOW'].includes(gameResult))
const _didLose = $derived(['L', 'OTL', 'SOL'].includes(gameResult))
const _hasUnresolvedTiedExtraTime = $derived.by(() => {
    if (!_game) return false
    const tied = _game.awayScore === _game.homeScore
    const wentExtraTime = _game.isOT || _game.isSO
    const unresolvedResult = !gameResult || gameResult === 'T'
    return tied && wentExtraTime && unresolvedResult
})
const _gameExtraTimeLabel = $derived.by(() => {
    if (!_game || _hasUnresolvedTiedExtraTime) return ''
    if (_game.isSO) return 'VL'
    if (_game.isOT) return 'JA'
    return ''
})

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
    return `${player.goals || 0} + ${player.assists || 0}`
})

// Derived stat values for the card
const _primaryStat = $derived.by(() => {
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

// Sub-label with breakdown
const _statBreakdown = $derived.by(() => {
    if (isGoalie)
        return `${player.saves ?? player.goalie_saves ?? 0}/${player.shots_against ?? player.shotsAgainst ?? 0} torjuntaa`
    if (player.points > 0 && player.goals > 0 && player.assists > 0) {
        return `${fiGoals(player.goals)} + ${fiAssists(player.assists)}`
    }
    if (player.points > 0 && player.goals > 0) return fiGoals(player.goals)
    if (player.points > 0 && player.assists > 0) return fiAssists(player.assists)
    return ''
})

// Action to portal element to body
function portal(node) {
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

<div class="game-player-card__container relative w-full" class:goalie-card={isGoalie}>
    <!-- Player Card -->
    <div class="game-player-card" class:flipped={isFlipped}>
        <!-- Spacer in normal flow to size container -->
        <div class="game-player-card__spacer" aria-hidden="true"></div>
        <div class="game-player-card__inner">
            <!-- Front of Card -->
            <div
                class="game-card ui-surface"
                bind:this={frontCard}
                class:game-card--win={_didWin}
                class:game-card--loss={_didLose}
                class:pressed={isPressed}
                class:flipped={isFlipped}
                onclick={_handleCardClick}
                onpointerdown={_handlePressStart}
                onpointerup={_handlePressEnd}
                onpointerleave={_handlePressEnd}
                role="button"
                tabindex="0"
                onkeydown={_handleCardKeydown}
                aria-label={highlight
                    ? `Päivän onnistuja: ${highlight.text}. Käännä pelaajakortti ja näytä lisää tilastoja`
                    : 'Käännä pelaajakortti ja näytä lisää tilastoja'}
                in:scale={{ duration: 220, start: 0.96 }}
            >
                <div class="card__watermark" aria-hidden="true">
                    <TeamLogo team={player.team || 'NHL'} size="160" />
                </div>

                <div class="card__content">
                    <!-- Player name -->
                    <div class="card__top">
                        <div class="card__player-info">
                            <h3 class="card__name card__name--interactive">
                                <button
                                    type="button"
                                    class="card__stats-btn"
                                    aria-label={`Avaa pelaajan ottelutilastot: ${displayName}`}
                                    aria-haspopup="dialog"
                                    aria-expanded={showComprehensiveDetails}
                                    title="Avaa ottelutilastot ikkunaan"
                                    onclick={(e) => {
                                        e.stopPropagation()
                                        showComprehensiveDetails = true
                                    }}
                                >
                                    <span class="card__name-label"
                                        >{displayName}&nbsp;<PanelsTopLeft
                                            class="card__name-icon"
                                            size={11}
                                            aria-hidden="true"
                                        /></span
                                    >
                                </button>
                            </h3>
                            <p class="card__team">
                                <span class="card__team-text">
                                    {#if player.jersey_number || player.jerseyNumber}
                                        #{player.jersey_number || player.jerseyNumber}
                                        <span class="card__dot">|</span>
                                    {/if}
                                    {player.position || player.positionCode || 'N/A'}
                                    <span class="card__team-abbrev"> · {player.team || 'NHL'}</span>
                                </span>
                            </p>
                        </div>
                    </div>

                    {#if _venue}
                        <p class="card__venue"><MapPin aria-hidden="true" />{_venue}</p>
                    {/if}

                    <!-- Primary stat -->
                    {#if !isGoalie}
                        <dl class="card__scoring">
                            <div>
                                <dt>maalia</dt>
                                <dd>{player.goals || 0}</dd>
                            </div>
                            <div>
                                <dt>syöttöä</dt>
                                <dd>{player.assists || 0}</dd>
                            </div>
                            <div>
                                <dt>pistettä</dt>
                                <dd>{dailyPlayerPoints(player)}</dd>
                            </div>
                            <div>
                                <dt>+/-</dt>
                                <dd
                                    class:card__scoring--positive={(player.plus_minus ??
                                        player.plusMinus ??
                                        0) > 0}
                                    class:card__scoring--negative={(player.plus_minus ??
                                        player.plusMinus ??
                                        0) < 0}
                                >
                                    {(player.plus_minus ?? player.plusMinus ?? 0) > 0
                                        ? '+'
                                        : ''}{player.plus_minus ?? player.plusMinus ?? 0}
                                </dd>
                            </div>
                            {#if (player.penalty_minutes ?? player.penaltyMinutes ?? 0) > 0}
                                <div>
                                    <dt>ran. min</dt>
                                    <dd>{player.penalty_minutes ?? player.penaltyMinutes}</dd>
                                </div>
                            {/if}
                        </dl>
                    {:else if _primaryStat}
                        <div class="card__stat card__stat--goalie">
                            <div
                                class="card__save-gauge"
                                class:card__save-gauge--strong={goalieSavePct >= 92 &&
                                    goalieSavePct < 100}
                                class:card__save-gauge--legendary={goalieSavePct === 100}
                                class:card__save-gauge--moderate={goalieSavePct >= 90 &&
                                    goalieSavePct < 92}
                                class:card__save-gauge--low={goalieSavePct < 90}
                            >
                                <svg
                                    class="card__save-arc"
                                    viewBox="0 0 260 150"
                                    fill="none"
                                    aria-hidden="true"
                                    focusable="false"
                                >
                                    <defs>
                                        <linearGradient
                                            id={`${cardId}-save-gradient`}
                                            x1="16"
                                            y1="132"
                                            x2="244"
                                            y2="132"
                                            gradientUnits="userSpaceOnUse"
                                        >
                                            {#if goalieSavePct === 100}
                                                <stop stop-color="#fef3c7" />
                                                <stop offset="0.22" stop-color="#d97706" />
                                                <stop offset="0.45" stop-color="#fbbf24" />
                                                <stop offset="0.55" stop-color="#fffbea" />
                                                <stop offset="0.65" stop-color="#fbbf24" />
                                                <stop offset="1" stop-color="#a16207" />
                                            {:else}
                                                <stop
                                                    stop-color="var(--save-gauge-color)"
                                                    stop-opacity="0.4"
                                                />
                                                <stop
                                                    offset="0.2"
                                                    stop-color="var(--save-gauge-color)"
                                                />
                                                <stop
                                                    offset="0.6"
                                                    stop-color="var(--save-gauge-color)"
                                                    stop-opacity="0.85"
                                                />
                                                <stop
                                                    offset="1"
                                                    stop-color="var(--save-gauge-color)"
                                                    stop-opacity="0.5"
                                                />
                                            {/if}
                                        </linearGradient>
                                    </defs>
                                    <path
                                        class="card__save-track"
                                        d="M16 132a114 114 0 0 1 228 0"
                                    />
                                    {#if goalieSavePct > 0}
                                        <path
                                            class="card__save-progress"
                                            d="M16 132a114 114 0 0 1 228 0"
                                            pathLength="100"
                                            stroke={`url(#${cardId}-save-gradient)`}
                                            stroke-dasharray={`${Math.min(100, Math.max(0, goalieSavePct))} 100`}
                                        />
                                    {/if}
                                </svg>
                                <div class="card__save-content">
                                    <span class="card__save-label">{_primaryStat.label}</span>
                                    <strong class="card__stat-value"
                                        >{_primaryStat.value}{_primaryStat.unit}</strong
                                    >
                                    {#if _statBreakdown}
                                        <small class="card__save-breakdown">{_statBreakdown}</small>
                                    {/if}
                                </div>
                            </div>
                        </div>
                    {:else}
                        <div class="card__stat">
                            <strong class="card__stat-value card__stat-value--empty">–</strong>
                            <div class="card__stat-meta">
                                <strong>Ei tilastoja</strong>
                            </div>
                        </div>
                    {/if}

                    <!-- Supporting stats row -->
                    <div class="card__sub-stats">
                        {#if isGoalie}
                            {#if player.time_on_ice || player.toi}
                                <div class="card__sub-stat" title="Peliaika">
                                    <span class="card__sub-stat-value"
                                        >{player.time_on_ice || player.toi}</span
                                    >
                                    <span class="card__sub-stat-label">peliaika</span>
                                </div>
                            {/if}
                            <div class="card__sub-stat" title="Päästetyt maalit">
                                <span
                                    class="card__sub-stat-value"
                                    style="color: {player.goals_against === 0
                                        ? 'var(--accent)'
                                        : player.goals_against >= 4
                                          ? '#ef4444'
                                          : undefined}">{player.goals_against}</span
                                >
                                <span class="card__sub-stat-label">pääst.</span>
                            </div>
                            {#if _hasENG}
                                <div class="card__sub-stat" title="Tyhjään maaliin">
                                    <span class="card__sub-stat-value text-red-500"
                                        >{player.empty_net_goals}</span
                                    >
                                    <span class="card__sub-stat-label">tyhjä</span>
                                </div>
                            {/if}
                        {/if}
                    </div>

                    <!-- Footer -->
                    <div class="card__footer">
                        <button type="button" class="card__footer-hint" onclick={_flipFromControl}>
                            <Rotate3D class="card__flip-icon" aria-hidden="true" />
                            Käännä kortti · Lisää tilastoja
                        </button>
                        <div
                            class="card__gamebar"
                            class:card__gamebar--live={_isLive}
                            class:card__gamebar--win={_didWin}
                            class:card__gamebar--loss={_didLose}
                        >
                            {#if _matchupTeams}
                                <span
                                    class="card__gamebar-team"
                                    aria-label={`Vierasjoukkue ${_matchupTeams[0]}`}
                                >
                                    <span aria-hidden="true"
                                        ><TeamLogo team={_matchupTeams[0]} size="28" /></span
                                    >
                                    {_matchupTeams[0]}
                                </span>
                            {:else}
                                <span class="card__gamebar-matchup">{_matchup}</span>
                            {/if}
                            <div class="card__gamebar-score-wrap">
                                {#if _formattedScore}
                                    <span
                                        class="card__gamebar-score"
                                        aria-label={_didWin
                                            ? `Voitto ${_matchupScore}`
                                            : _didLose
                                              ? `Tappio ${_matchupScore}`
                                              : _matchupScore}>{_matchupScore}</span
                                    >
                                {:else if _matchupTeams}
                                    <span class="card__gamebar-at" aria-label="vastaan">@</span>
                                {/if}
                                {#if _isLive}
                                    <span class="card__gamebar-status card__gamebar-status--live"
                                        >LIVE{#if Number.isInteger(_game?.period) && _game.period > 0}
                                            · {_game.isSO
                                                ? 'VL'
                                                : _game.period <= 3
                                                  ? `${_game.period}. erä`
                                                  : 'JA'}{/if}</span
                                    >
                                {:else if _showResult}
                                    <span class="card__gamebar-result"
                                        >{_didWin
                                            ? 'Voitto'
                                            : _didLose
                                              ? 'Tappio'
                                              : 'Päättynyt'}{#if _gameExtraTimeLabel}
                                            · {_gameExtraTimeLabel}{/if}</span
                                    >
                                {:else}
                                    <span class="card__gamebar-status">Tulossa</span>
                                {/if}
                            </div>
                            {#if _matchupTeams}
                                <span
                                    class="card__gamebar-team card__gamebar-team--home"
                                    aria-label={`Kotijoukkue ${_matchupTeams[1]}`}
                                >
                                    <span aria-hidden="true"
                                        ><TeamLogo team={_matchupTeams[1]} size="28" /></span
                                    >
                                    {_matchupTeams[1]}
                                </span>
                            {/if}
                        </div>
                    </div>
                </div>
            </div>

            <!-- Back of Card -->
            <div
                class="game-card ui-surface card--back"
                bind:this={backCard}
                class:pressed={isPressed}
                class:flipped={isFlipped}
                onclick={_handleCardClick}
                onpointerdown={_handlePressStart}
                onpointerup={_handlePressEnd}
                onpointerleave={_handlePressEnd}
                role="button"
                tabindex="0"
                onkeydown={_handleCardKeydown}
                aria-label="Käännä pelaajakortti takaisin"
            >
                <div class="card__watermark" aria-hidden="true">
                    <TeamLogo team={player.team || 'NHL'} size="160" />
                </div>

                <div class="card__content">
                    <!-- Header -->
                    <div class="card__top">
                        <div class="card__player-info">
                            <h3 class="card__name">{displayName}</h3>
                            <p class="card__team">{_teamWithCity}</p>
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
                                    <div class="card__back-stat-value">
                                        {player.faceoff_wins}/{player.faceoffs_taken}
                                    </div>
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
                    <div class="card__footer">
                        <button type="button" class="card__footer-hint" onclick={_flipFromControl}>
                            <Rotate3D class="card__flip-icon" aria-hidden="true" />
                            Takaisin
                        </button>
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
        onclick={_handleBackdropClick}
        role="button"
        tabindex="0"
        onkeydown={(e) => e.key === 'Escape' && _closeSeasonStats(e)}
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
                <div class="game-player-card__modal-avatar shrink-0">
                    {#if playerPhotoUrl && !_photoError}
                        <img
                            src={playerPhotoUrl || player.headshot_url}
                            alt={displayName}
                            class="game-player-card__modal-photo"
                            class:blurred={_photoLoading || _imageLoading}
                            onload={() => {
                                _photoLoading = false
                                _imageLoading = false
                            }}
                            onerror={() => {
                                _photoError = true
                                _photoLoading = false
                                _imageLoading = false
                            }}
                        />
                        {#if (_photoLoading || _imageLoading) && _lqipUrl}
                            <img src={_lqipUrl} alt="" class="game-player-card__modal-photo-lqip" />
                        {/if}
                    {:else if _lqipUrl}
                        <img src={_lqipUrl} alt="" class="game-player-card__modal-photo-lqip" />
                    {:else}
                        <div class="game-player-card__modal-initials">{_playerInitials}</div>
                    {/if}
                </div>
                <div>
                    <h3 id="season-stats-title" class="text-lg font-bold text-gray-900">
                        {displayName}
                    </h3>
                    <div class="text-sm text-gray-500 flex items-center gap-2">
                        <span>{_teamWithCity}</span>
                        <span>•</span>
                        <span>Kauden 2024-2025 tilastot</span>
                    </div>
                </div>
                <button
                    class="ml-auto p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
                    onclick={_closeSeasonStats}
                    aria-label="Sulje"
                >
                    <X class="h-5 w-5" aria-hidden="true" />
                </button>
            </div>
            <div class="p-6">
                <div class="grid grid-cols-2 gap-4">
                    <div class="bg-gray-50 p-4 rounded-lg text-center">
                        <div class="text-2xl font-bold text-gray-900">
                            {player.season_goals || 0}
                        </div>
                        <div class="text-xs text-gray-500 uppercase tracking-wider mt-1">
                            Maalit
                        </div>
                    </div>
                    <div class="bg-gray-50 p-4 rounded-lg text-center">
                        <div class="text-2xl font-bold text-gray-900">
                            {player.season_assists || 0}
                        </div>
                        <div class="text-xs text-gray-500 uppercase tracking-wider mt-1">
                            Syötöt
                        </div>
                    </div>
                    <div
                        class="bg-finnish-blue-50 p-4 rounded-lg text-center col-span-2 border border-finnish-blue-100"
                    >
                        <div class="text-3xl font-bold text-finnish-blue-600">
                            {player.season_points || 0}
                        </div>
                        <div
                            class="text-xs text-finnish-blue-600 uppercase tracking-wider mt-1 font-medium"
                        >
                            Pisteet yhteensä
                        </div>
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
        venue={_venue}
        onclose={() => (showComprehensiveDetails = false)}
    />
{/if}
